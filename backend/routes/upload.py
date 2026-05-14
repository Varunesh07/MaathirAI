from fastapi import APIRouter, UploadFile, File
from services import ocr_service, memory_service
import os

router = APIRouter(prefix='/upload', tags=['upload'])

@router.post('/')
async def upload_file(files: list[UploadFile] = File(...)):
    combined_raw_text = ""

    for file in files:
        contents = await file.read()
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext == '.pdf':
            text = ocr_service.extract_text_from_pdf(contents)
        else:
            text = ocr_service.extract_text_from_image(contents)

        combined_raw_text += text + "\n"

    file_names = ", ".join([f.filename for f in files])
    file_msg = f"[FILE: {file_names}]"
    memory_service.add_chat_message('user', file_msg)

    # Save raw text to system memory so LangChain Agent can see it
    system_msg = f"[System: User uploaded document(s). Raw OCR text:]\n{combined_raw_text}"
    memory_service.add_chat_message('system', system_msg)

    return {"status": "success", "message": "File processed."}
