import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# Using versatile 70b model as requested
MODEL = "llama-3.3-70b-versatile"

EXTRACTION_SYSTEM = """You are a medical data extraction assistant.
You ONLY extract and organize medical information from text.
You do NOT diagnose diseases, prescribe treatment, or give medical advice.
Always respond in valid JSON only. No markdown, no explanation, no extra text."""

ASSISTANT_SYSTEM = """You are a medical interaction awareness assistant.
You explain drug interaction information in simple, clear English.
You do NOT diagnose diseases or prescribe treatment.
You always end your response by recommending the user consult a healthcare professional."""


def extract_medical_entities(ocr_text: str) -> dict:
    prompt = f"""Extract all medical information from the text below.
Return ONLY a JSON object in this exact structure:

{{
  "medications": [
    {{"name": "Drug Name", "dosage": "500mg or null"}}
  ],
  "conditions": ["condition1"],
  "allergies": ["allergy1"]
}}

Rules:
- Only include actual drug names, not dosage forms like tablet/capsule/syrup
- Normalize names to title case (metformin -> Metformin)
- Set dosage to null if not mentioned
- CRITICAL: Do NOT extract conditions from generic drug warning labels, side effects, or contraindications printed on packaging (e.g. "when pregnancy is detected"). Only extract conditions if clearly diagnosed for the patient.
- Use empty arrays if nothing found
- Return ONLY the JSON object

Text:
{ocr_text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if Groq wraps response
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"medications": [], "conditions": [], "allergies": []}


def generate_explanation(
    stored_medications: list,
    new_medications: list,
    interaction_data: list,
    user_message: str = ""
) -> str:

    stored_str = ", ".join(stored_medications) if stored_medications else "none on file"
    new_str = ", ".join(new_medications) if new_medications else "none detected"

    if interaction_data:
        interaction_str = "\n".join(f"- {i}" for i in interaction_data)
    else:
        interaction_str = "No interactions detected between these medications."

    prompt = f"""Medications already on file: {stored_str}
Newly uploaded medications: {new_str}

Drug interaction check results:
{interaction_str}

User message: {user_message if user_message else "Summarize the interaction check."}

Write a clear response that:
1. If no new medications were detected (i.e., it was just a medical report), briefly summarize the report's purpose and state you have saved it and are ready for questions.
2. If medications were found, confirm what medications were found.
3. Explains any interactions in plain English (avoid medical jargon).
4. Mentions severity if known.
5. Ends with a reminder to consult a healthcare professional.
Keep it under 200 words.
If there are [AI-ESTIMATED] interactions, clearly state: "Some interactions are AI-estimated and not from a clinical database. These must be verified with a pharmacist or doctor before acting on them."
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ASSISTANT_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def answer_chat_question(user_message: str, medical_memory: dict, chat_history: list) -> str:
    meds = ", ".join(
        m.get("name", m) if isinstance(m, dict) else m
        for m in medical_memory.get("medications", [])
    ) or "none on file"
    conditions = ", ".join(medical_memory.get("conditions", [])) or "none on file"
    allergies = ", ".join(medical_memory.get("allergies", [])) or "none on file"

    history_str = ""
    for msg in chat_history:
        history_str += f"{msg.get('role', 'user')}: {msg.get('message', '')}\n"

    prompt = f"""User medical profile:
- Medications: {meds}
- Conditions: {conditions}
- Allergies: {allergies}

Recent conversation:
{history_str}
User asks: {user_message}

Answer helpfully using the profile above.
Do not diagnose or prescribe.
End with a reminder to consult a healthcare professional."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ASSISTANT_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
