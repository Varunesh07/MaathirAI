from fastapi import APIRouter
from services import drug_interaction_service, memory_service
from services.agent_tools import resolve_indian_brand_names

router = APIRouter(prefix='/interactions', tags=['interactions'])

@router.get('/')
async def get_interactions():
    med_names = memory_service.get_medication_names_only()
    if not med_names:
        return {'status': 'success', 'medications': [], 'interactions': [], 'message': 'No medications in memory.'}

    # Resolve brand names to generic ingredients using .invoke() for the LangChain tool
    try:
        generic_ingredients = resolve_indian_brand_names.invoke({"brand_names": med_names})
    except Exception as e:
        # Fallback to raw names if resolution fails
        generic_ingredients = med_names

    if len(generic_ingredients) < 2:
        return {'status': 'success', 'medications': med_names, 'generic_ingredients': generic_ingredients, 'interactions': [],
                'message': 'Need at least 2 ingredients to check interactions.'}

    interactions = drug_interaction_service.check_interactions(generic_ingredients)
    return {'status': 'success', 'medications': med_names, 'generic_ingredients': generic_ingredients, 'interactions': interactions}

@router.get('/memory')
async def get_memory():
    memory = memory_service.get_medical_memory()
    med_names = memory_service.get_medication_names_only()
    
    # Resolve for the profile view as well
    try:
        generic_ingredients = resolve_indian_brand_names.invoke({"brand_names": med_names})
        interactions = drug_interaction_service.check_interactions(generic_ingredients)
    except:
        interactions = []
    
    return {
        "medical_profile": memory,
        "interactions": interactions
    }

@router.delete('/memory')
async def clear_memory():
    memory_service.clear_medical_memory()
    memory_service.clear_chat_history()
    return {'status': 'cleared'}
