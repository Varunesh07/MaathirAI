# MaathirAI - Medical Interaction Assistant

MaathirAI is an intelligent, full-stack medical awareness assistant built specifically for Indian patients and caregivers. It helps you understand your medications, decode medical reports, and safely check for dangerous drug-drug interactions — all in one place.
 
Whether you're an elderly patient managing multiple prescriptions, a working adult tracking your own medicines, or a caregiver handling a family member's health — MaathirAI works the same way: upload a photo or PDF, and let the AI do the heavy lifting.
 
> **The name comes from *Maathirai* (மாத்திரை) — the Tamil word for *tablet*. Since MaathirAI uses AI to identify and analyse tablets and medicines, the name is a natural fit: Maathirai + AI = MaathirAI.**

---
 
## 🎯 What MaathirAI Actually Does
 
### 1. Autonomous Agentic Reasoning
Powered by **LangChain**, MaathirAI uses an "Agentic" architecture. It doesn't just chat; it *reasons*. It autonomously decides when to look up an Indian brand name, when to check for a drug-drug interaction, and when to dig into your medical history.

### 2. Medical RAG (Retrieval-Augmented Generation)
We've integrated **ChromaDB** and **Sentence-Transformers** to give the AI a "long-term memory." Every time you upload a report, it is chunked, vectorized, and stored. Even if you clear your chat history, the AI can still "retrieve" specific details like your blood sugar level or past test results from its vector database.

### 3. Resolves Indian Brand Names
Most drug databases are US-centric. MaathirAI maps Indian brands like *Telma 40* or *Glimestar M2* to their generic ingredients (Telmisartan, Metformin, etc.) using a local database of ~20,000 products, ensuring accurate interaction checks.

### 4. Smart Profile Management
The AI is trained to be your medical secretary. If it spots a new medication, allergy, or condition in a report, it automatically updates your profile. It uses a **bulk-saving logic** to ensure that multiple findings in a single report are all captured accurately.

---

## 🌟 Key Features
 
- **Agentic Search:** Uses the `search_medical_history` tool to query past reports in real-time.
- **Vectorized OCR Pipeline:** Automatically indexes PDFs and images into a local ChromaDB store upon upload.
- **Natural Conversations:** Designed with a "Short & Sweet" persona—it speaks like a friendly neighborhood doctor, avoiding heavy jargon and internal technical details.
- **Interactive Sidebar:** Real-time sync between the AI's "thoughts" and the visual UI (Medications list, Interaction table).
- **Privacy First:** Includes a "Clear Memory" function that wipes both your JSON profile and your vectorized ChromaDB history.

---

## 🛠️ Technology Stack

**Frontend:**
- React + Vite & Tailwind CSS
- Lucide React (Icons) & React-Markdown

**Backend:**
- FastAPI (Python)
- **LangChain** (Agentic Framework)
- **ChromaDB** (Vector Database for RAG)
- **Sentence-Transformers** (`all-MiniLM-L6-v2` for Embeddings)
- Groq Cloud API (`llama-3.1-8b-instant` for ultra-fast reasoning)
- EasyOCR & PyMuPDF (Document processing)

---

## 🚀 How to Run Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# Set your GROQ_API_KEY in a .env file
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔮 Roadmap (Phase 4 & Beyond)

- **Phase 4: SQL Migration:** Moving from JSON storage to a robust SQL backend for multi-user support.
- **Multi-Language Support:** Localizing the AI to speak Tamil, Hindi, and other Indian languages.
- **Voice Interaction:** Allowing elderly users to speak to the assistant directly.
- **PDF Report Generation:** Generating a clinical summary for users to show their doctors.

---

## ⚠️ Disclaimer
**MaathirAI is a developmental project and not a substitute for professional medical advice.** Always consult a healthcare professional or pharmacist before making medical decisions. AI-estimated interactions must always be clinically verified.
