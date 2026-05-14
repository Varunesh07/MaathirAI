import os
import json
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from services.agent_tools import resolve_indian_brand_names, check_drug_interactions, save_medication, save_condition_or_allergy
from services import memory_service

def _get_agent_executor():
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=os.environ.get("GROQ_API_KEY"))
    tools = [resolve_indian_brand_names, check_drug_interactions, save_medication, save_condition_or_allergy]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are MaathirAI, a professional and highly intelligent medical AI assistant designed to help Indian patients. 
You have access to tools that can look up Indian brand names, check drug interactions, and save medical entities to the user's profile.

User's CURRENT stored profile:
Medications: {stored_meds}
Conditions: {conditions}
Allergies: {allergies}

Instructions:
1. If the user asks a question, answer it directly.
2. If the user uploads a document, the OCR text will appear in the chat history. Carefully analyze it.
3. If you find medications in the OCR text, ALWAYS resolve them to their generic ingredients first using `resolve_indian_brand_names`. Then, check for interactions using `check_drug_interactions`. Finally, save them to the user's profile using `save_medication`.
4. Save any new conditions or allergies using `save_condition_or_allergy`.
5. Synthesize everything into a helpful, easy-to-read response using Markdown. Use simple terms.
6. Do not hallucinate medical advice. End with a reminder to consult a healthcare professional.
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
