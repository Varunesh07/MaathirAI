import pandas as pd
from thefuzz import process as fuzz_process
from typing import Optional

DDI_CSV = 'storage/DDI_data.csv'
FUZZY_THRESHOLD = 85

_ddi_df = None
_drug_names = None


def _load_ddi():
    global _ddi_df, _drug_names
    if _ddi_df is not None:
        return
    try:
        _ddi_df = pd.read_csv(DDI_CSV, dtype=str).fillna('')
        # Build unique drug name list from both columns for fuzzy matching
        names1 = _ddi_df['drug1_name'].str.lower().str.strip().tolist()
        names2 = _ddi_df['drug2_name'].str.lower().str.strip().tolist()
        _drug_names = list(set(names1 + names2))
    except FileNotFoundError:
        print(f'WARNING: {DDI_CSV} not found. Interaction check will use AI fallback only.')
        _ddi_df = pd.DataFrame()
        _drug_names = []


def _normalize_drug_name(name: str) -> Optional[str]:
    # Fuzzy match input name against known DDI drug names
    if not _drug_names:
        return None
    result = fuzz_process.extractOne(name.lower().strip(), _drug_names)
    match, score = result[0], result[1]
    return match if score >= FUZZY_THRESHOLD else None

def get_known_ingredient(name: str) -> Optional[str]:
    _load_ddi()
    if not _drug_names:
        return None
    result = fuzz_process.extractOne(name.lower().strip(), _drug_names)
    match, score = result[0], result[1]
    return match.title() if score >= 95 else None


def check_interactions(ingredient_names: list) -> list:
    # ingredient_names: plain strings like ['Paracetamol', 'Warfarin', 'Metformin']
    # Returns list of interaction description strings
    _load_ddi()

    if len(ingredient_names) < 2:
        return []

    # Normalize all names against DDI database
    normalized = {}
    for name in ingredient_names:
        norm = _normalize_drug_name(name)
        if norm:
            normalized[name] = norm

    if len(normalized) < 2:
        # Not enough known drugs for structured check — fall back to AI
        return _ai_interaction_fallback(ingredient_names)

    interactions = []
    norm_list = list(normalized.values())

    # Check every pair
    for i in range(len(norm_list)):
        for j in range(i + 1, len(norm_list)):
            a = norm_list[i]
            b = norm_list[j]

            # Search DDI dataframe both directions
            mask = (
                (_ddi_df['drug1_name'].str.lower().str.strip() == a) &
                (_ddi_df['drug2_name'].str.lower().str.strip() == b)
            ) | (
                (_ddi_df['drug1_name'].str.lower().str.strip() == b) &
                (_ddi_df['drug2_name'].str.lower().str.strip() == a)
            )

            matches = _ddi_df[mask]
            for _, row in matches.iterrows():
                d1 = row.get('drug1_name', a).title()
                d2 = row.get('drug2_name', b).title()
                itype = row.get('interaction_type', 'interaction detected')
                interactions.append(f'{d1} + {d2}: {itype}')

    # If structured check found nothing, use AI fallback for safety
    if not interactions:
        return _ai_interaction_fallback(ingredient_names)

    return interactions


def _ai_interaction_fallback(ingredient_names: list) -> list:
    # Used when drugs are not found in DDI_data.csv
    # Calls Groq to estimate interactions
    try:
        import os
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv()
        client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

        prompt = f"""List any known drug-drug interactions between these medications: {', '.join(ingredient_names)}.
For each interaction found, state:
- Which two drugs interact
- Type of interaction (pharmacokinetic or pharmacodynamic)
- Severity if known (mild, moderate, severe)
- Brief description (one sentence)
If no interactions are known, say: No known interactions found.
Format each interaction on its own line starting with a dash.
Do not include medical advice or treatment recommendations."""

        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        # Tag every line as AI-estimated
        lines = [l.strip() for l in raw.split('\n') if l.strip()]
        return [f'[AI-ESTIMATED] {l.lstrip("- ")}' for l in lines]
    except Exception as e:
        print(f"AI fallback failed: {e}")
        return ['[AI-ESTIMATED] Interaction data unavailable for these medications.']
