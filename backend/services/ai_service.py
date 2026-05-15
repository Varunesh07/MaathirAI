import os
import json
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from services.agent_tools import (
    resolve_indian_brand_names, 
    check_drug_interactions, 
    save_medications, 
    save_condition_or_allergy,
    search_medical_history
)
from services import memory_service

def _get_agent_executor():
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, api_key=os.environ.get("GROQ_API_KEY"))
    tools = [
        resolve_indian_brand_names, 
        check_drug_interactions, 
        save_medications, 
        save_condition_or_allergy,
        search_medical_history
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are MaathirAI, a professional and highly intelligent medical AI assistant designed to help Indian patients. 
You have access to tools that can look up Indian brand names, check drug interactions, save medical entities, and search through long medical history records stored in a vector database.

User's CURRENT stored profile:
Medications: {stored_meds}
Conditions: {conditions}
Allergies: {allergies}

Instructions:
1. ROLE: You are MaathirAI, a friendly medical assistant. Be empathetic and concise.
2. RAG/SEARCH: If the user asks about past history, test results, or sugar levels not in the profile above, you MUST use `search_medical_history` to find the info.
3. OCR: If OCR text is in the history, resolve brand names with `resolve_indian_brand_names`, check interactions with `check_drug_interactions`, and save all meds with `save_medications`.
4. SAVING: Automatically save new conditions or allergies using `save_condition_or_allergy`.
5. STYLE: Keep answers "Short & Sweet". Do not explain your technical steps or which tools you are using.
6. ABSTRACTION: Never mention tool names, code, or databases. Just say "I've checked your records" or "I've saved that."
7. SAFETY: Always end with: "Please consult a doctor for official medical advice."
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def answer_chat_question_stream(user_message: str, medical_memory: dict, chat_history: list):
    executor = _get_agent_executor()
    
    stored_meds = ", ".join([m.get("name", m) if isinstance(m, dict) else m for m in medical_memory.get("medications", [])]) or "none on file"
    conditions = ", ".join(medical_memory.get("conditions", [])) or "none on file"
    allergies = ", ".join(medical_memory.get("allergies", [])) or "none on file"
    
    formatted_history = []
    # Only take the last 30 messages to avoid context overflow, but ensure we keep recent OCR
    for msg in chat_history[-30:]:
        role = msg.get("role")
        content = msg.get("message", "")
        if role == "user":
            formatted_history.append(HumanMessage(content=content))
        elif role == "system":
            formatted_history.append(SystemMessage(content=content))
        else:
            formatted_history.append(AIMessage(content=content))
            
    full_text = ""
    # Execute the agent and stream the final output
    async for event in executor.astream_events(
        {
            "input": user_message, 
            "stored_meds": stored_meds, 
            "conditions": conditions, 
            "allergies": allergies, 
            "chat_history": formatted_history
        },
        version="v2"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content and isinstance(content, str):
                full_text += content
                yield content
                
    memory_service.add_chat_message("assistant", full_text)
