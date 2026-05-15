from langchain_core.tools import tool
from services import india_drug_service, drug_interaction_service, memory_service, vector_store

@tool
def resolve_indian_brand_names(brand_names: list[str]) -> list[str]:
    """
    Use this tool to find the generic active ingredients for a list of Indian medicine brand names.
    Always use this when you extract a medication name from a user's uploaded document to verify its active ingredients.
    Returns a list of generic ingredients.
    """
    ingredients = []
    for brand in brand_names:
        resolved = india_drug_service.brand_to_ingredients(brand)
        if resolved:
            ingredients.extend(resolved)
        else:
            # If not found, it might already be generic, or our DB lacks it
            # We use fuzzy matching to see if it's already a known generic
            known = drug_interaction_service.get_known_ingredient(brand)
            ingredients.append(known if known else brand)
    return list(set(ingredients))

@tool
def check_drug_interactions(ingredients: list[str]) -> list[str]:
    """
    Use this tool to check for dangerous drug-drug interactions between a list of active generic ingredients.
    You MUST provide the full list of the user's active ingredients (both newly found and previously stored).
    Returns a list of interaction warnings.
    """
    return drug_interaction_service.check_interactions(ingredients)

@tool
def save_medications(medications: list[dict]) -> str:
    """
    Use this tool to save multiple newly discovered medications to the user's persistent profile at once.
    Each item in the list must be a dictionary with:
    - "brand_name": The name on the package (e.g. 'Dolo 650')
    - "generic_ingredients": A list of active ingredients (e.g. ['Paracetamol'])
    """
    for med in medications:
        brand_name = med.get("brand_name")
        generic_ingredients = med.get("generic_ingredients", [])
        memory_service.add_to_medical_memory({
            "medications": [{
                "name": brand_name,
                "resolved_ingredients": generic_ingredients
            }]
        })
    return f"Successfully saved {len(medications)} medications."

@tool
def save_condition_or_allergy(entity_type: str, value: str) -> str:
    """
    Use this tool to save a discovered condition or allergy to the user's persistent profile.
    entity_type must be exactly 'condition' or 'allergy'.
    value is the name (e.g., 'Diabetes' or 'Penicillin').
    """
    if entity_type == 'condition':
        memory_service.add_to_medical_memory({"conditions": [value]})
        return f"Successfully saved condition {value}."
    elif entity_type == 'allergy':
        memory_service.add_to_medical_memory({"allergies": [value]})
        return f"Successfully saved allergy {value}."
    return "Error: type must be condition or allergy."

@tool
def search_medical_history(query: str) -> str:
    """Use this tool to search the user's past medical reports, sugar levels, and test results from the database."""
    # Retrieve top 3 relevant chunks
    results = vector_store.search(collection_name="medical_reports", query=query, top_k=3)
    if not results:
        return "No relevant information found in medical history."
    # Join chunks with spacing for readability
    return "\n\n---\n\n".join(results)
