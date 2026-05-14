import pandas as pd
import re
from thefuzz import process as fuzz_process
from typing import Optional

INDIAN_MED_CSV = 'storage/indian_medicines.csv' # Wait, the folder contains indian_medicine_data.csv according to earlier list_dir
# I need to fix the filename to match the actual file present!
INDIAN_MED_CSV = 'storage/indian_medicine_data.csv'
FUZZY_THRESHOLD = 80  # 0-100, lower = more lenient matching

# Load CSV into memory once at startup
_df = None
_name_list = None


def _load():
    global _df, _name_list
    if _df is not None:
        return
    try:
        _df = pd.read_csv(INDIAN_MED_CSV, dtype=str).fillna('')
        # Normalize name column to lowercase for matching
        _df['name_lower'] = _df['name'].str.lower().str.strip()
        _name_list = _df['name_lower'].tolist()
    except FileNotFoundError:
        print(f'WARNING: {INDIAN_MED_CSV} not found. Indian brand lookup disabled.')
        _df = pd.DataFrame()
        _name_list = []


def _parse_ingredient(composition_str: str) -> Optional[str]:
    # Input:  'Amoxycillin (500mg)'
    # Output: 'Amoxycillin'
    if not composition_str or composition_str.strip() == '':
        return None
    # Strip dosage in parentheses: 'Paracetamol (650mg)' -> 'Paracetamol'
    name = re.sub(r'\(.*?\)', '', composition_str).strip()
    # Strip trailing dosage without parens: 'Paracetamol 650mg' -> 'Paracetamol'
    name = re.sub(r'\s+\d+\.?\d*(mg|mcg|g|ml|iu|%)', '', name, flags=re.IGNORECASE).strip()
    return name if name else None


def brand_to_ingredients(brand_name: str) -> list:
    # Returns list of plain ingredient name strings
    # Example: 'Augmentin 625' -> ['Amoxycillin', 'Clavulanic Acid']
    # Example: 'Dolo 650' -> ['Paracetamol']
    # Example: 'Unknown Brand' -> [] (not found)
    _load()
    if not _name_list:
        return []

    query = brand_name.lower().strip()

    # Try exact match first
    exact = _df[_df['name_lower'] == query]
    if not exact.empty:
        row = exact.iloc[0]
        return _extract_ingredients_from_row(row)

    # Fuzzy match for OCR typos (Dol0 650, Aug mentin etc)
    if _name_list:
        result = fuzz_process.extractOne(query, _name_list)
        match, score = result[0], result[1]
    else:
        match, score = None, 0

    if match and score >= FUZZY_THRESHOLD:
        row = _df[_df['name_lower'] == match].iloc[0]
        return _extract_ingredients_from_row(row)

    return []


def _extract_ingredients_from_row(row) -> list:
    ingredients = []
    for col in ['short_composition1', 'short_composition2']:
        val = str(row.get(col, '')).strip()
        if val and val != 'nan':
            parsed = _parse_ingredient(val)
            if parsed:
                ingredients.append(parsed)
    return ingredients


def is_indian_brand(brand_name: str) -> bool:
    # Returns True if the name is found in the Indian medicine dataset
    _load()
    if not _name_list:
        return False
    query = brand_name.lower().strip()
    if _name_list:
        result = fuzz_process.extractOne(query, _name_list)
        score = result[1]
    else:
        score = 0
    return score >= FUZZY_THRESHOLD
