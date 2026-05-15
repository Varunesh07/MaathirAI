from fastapi import APIRouter
from services import drug_interaction_service, memory_service
from services.agent_tools import resolve_indian_brand_names

router = APIRouter(prefix='/interactions', tags=['interactions'])

@router.get('/')
async def get_interactions():
    med_names = memory_service.get_medication_names_only()
    if len(med_names) < 2:
        return {'status': 'success', 'medications': med_names, 'interactions': [],
                'message': 'Need at least 2 medications to check interactions.'}
    # Resolve brand names to generic ingredients
    generic_ingredients = resolve_indian_brand_names(med_names)
    interactions = drug_interaction_service.check_interactions(generic_ingredients)
    return {'status': 'success', 'medications': med_names, 'generic_ingredients': generic_ingredients, 'interactions': interactions}

@router.get('/memory')
async def get_memory():
    memory = memory_service.get_medical_memory()
    med_names = memory_service.get_medication_names_only()
    interactions = drug_interaction_service.check_interactions(med_names)
    
    return {
        "medical_profile": memory,
        "interactions": interactions
    }

@router.delete('/memory')
async def clear_memory():
    memory_service.clear_medical_memory()
    memory_service.clear_chat_history()
    return {'status': 'cleared'}
