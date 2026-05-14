from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List
import tempfile, os, shutil
from services import ocr_service, ai_service, memory_service
from services import india_drug_service, drug_interaction_service

router = APIRouter(prefix='/upload', tags=['upload'])
ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']

@router.post('/')
async def upload_file(
    files: list[UploadFile] = File(...),
    message: str = Form(None),
    skip_explanation: bool = Form(False)
):
    combined_raw_text = ""

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f'Unsupported file type: {ext} for file {file.filename}')

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            # 1. OCR
            text = ocr_service.extract_text_from_file(tmp_path)
            combined_raw_text += text + "\n\n"
        finally:
            os.unlink(tmp_path)

    # Inject the raw document text directly into the chat memory so the AI remembers the report metrics
    memory_service.add_chat_message('system', f"[System: User uploaded document(s). Raw OCR text:]\n{combined_raw_text}")

    # 2. AI extraction (returns brand names as OCR found them)
    extracted = ai_service.extract_medical_entities(combined_raw_text)

    # 3. NEW: Resolve brand names to active ingredients
    all_ingredients = []
    for med in extracted.get('medications', []):
        brand = med.get('name', med) if isinstance(med, dict) else med
        
        # Safety Check: If the AI extracted the generic ingredient directly, don't look it up as a brand!
        known_ing = drug_interaction_service.get_known_ingredient(brand)
        if known_ing:
            all_ingredients.append(known_ing)
            if isinstance(med, dict):
                med['resolved_ingredients'] = [known_ing]
            continue

        ingredients = india_drug_service.brand_to_ingredients(brand)
        if ingredients:
            # Found in Indian dataset - use resolved ingredients
            all_ingredients.extend(ingredients)
            # Store resolved name in extracted for memory
            if isinstance(med, dict):
                med['resolved_ingredients'] = ingredients
        else:
            # Not an Indian brand - treat the name itself as ingredient
            all_ingredients.append(brand)

    # 4. Get currently stored ingredients
    stored_ingredients = memory_service.get_medication_names_only()

    # 5. Save new data to memory (stores brand names + ingredients)
    memory_service.add_to_medical_memory(extracted)

    # 6. Interaction check on ingredients (not brand names)
    all_to_check = list(set(stored_ingredients + all_ingredients))
    interactions = drug_interaction_service.check_interactions(all_to_check)

    # 7. AI explanation
    new_names = [
        m.get('name', m) if isinstance(m, dict) else m
        for m in extracted.get('medications', [])
    ]
    
    file_names = ", ".join([f.filename for f in files])
    file_msg = f"[FILE: {file_names}]"
    
    memory_service.add_chat_message('user', file_msg)
    
    if skip_explanation:
        return {"status": "success", "message": "File processed."}
    
    if message:
        memory_service.add_chat_message('user', message)
        explanation = ai_service.answer_chat_question(
            user_message=message,
            medical_memory=memory_service.get_medical_memory(),
            chat_history=memory_service.get_chat_history()
        )
    else:
        memory_service.add_chat_message('user', file_msg)
        explanation = ai_service.generate_explanation(
            stored_medications=stored_ingredients,
            new_medications=new_names,
            interaction_data=interactions
        )

    # 8. Save to chat history
    memory_service.add_chat_message('assistant', explanation)

    return JSONResponse({
        'status': 'success',
        'extracted': extracted,
        'resolved_ingredients': all_ingredients,
        'interactions': interactions,
        'message': explanation,
        'raw_ocr_preview': combined_raw_text[:300]
    })
