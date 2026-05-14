# MaathirAI - Medical Interaction Assistant

MaathirAI is an intelligent, full-stack medical awareness assistant built specifically for Indian patients and caregivers. It helps you understand your medications, decode medical reports, and safely check for dangerous drug-drug interactions — all in one place.
 
Whether you're an elderly patient managing multiple prescriptions, a working adult tracking your own medicines, or a caregiver handling a family member's health — MaathirAI works the same way: upload a photo or PDF, and let the AI do the heavy lifting.
 
> **The name comes from *Maathirai* (மாத்திரை) — the Tamil word for *tablet*. Since MaathirAI uses AI to identify and analyse tablets and medicines, the name is a natural fit: Maathirai + AI = MaathirAI.**

---
 
## 🎯 What MaathirAI Actually Does
 
### 1. Autonomous Agentic Reasoning (New!)
Unlike standard chatbots, MaathirAI now uses a **LangChain-powered Agentic Architecture**. When you upload a document or ask a question, the AI doesn't just respond; it *thinks* and *acts*. It autonomously decides which tools to call (e.g., resolving a brand name or checking a database) based on the context of your request.

### 2. Understands Indian Brand Names
Most drug interaction databases are US-centric and have no idea what *Telma 40*, *Crocin Advance*, or *Combiflam* are. MaathirAI solves this by mapping Indian brand names to their active generic ingredients using a specialized tool that queries a local Indian medicine database of ~20,000 products.

### 3. Real-Time Interaction Checking
MaathirAI checks every medication against a local Drug-Drug Interaction (DDI) database. It flags interactions as **Safe**, **Moderate**, or **Severe** with a plain-English explanation. For drugs not in the structured database, the Agent uses its medical reasoning to provide an estimated interaction.

### 4. Continuous Medical Profile Management
The Agent actively manages your medical profile. If it sees a condition (like "Diabetes") or an allergy in a report, it automatically saves it to your `medical_memory.json`. When you upload a new prescription next month, it already remembers your previous history and cross-references everything instantly.

---

## 🌟 Key Features
 
- **Autonomous Tool-Use:** Powered by LangChain's `create_tool_calling_agent`, the AI uses specialized tools for brand resolution, interaction checking, and profile saving.
- **Multi-Modal Document Processing:** Uses `PyMuPDF` for digital PDFs and `EasyOCR` (with dynamic upscaling) to read complex, multi-page prescriptions and pill strips.
- **Thread-Safe Memory Management:** Implements a robust locking system to handle multiple parallel tool calls (e.g., saving three medicines at once) without data corruption.
- **Streaming Response:** Token-by-token streaming from the Agent to the frontend for a fast, responsive user experience.
- **Indian Context First:** Built from the ground up to handle regional pharmaceutical naming conventions and Indian lab report formats.

---

## 🛠️ Technology Stack

**Frontend:**
- React + Vite
- Tailwind CSS (v3)
- Lucide React (Icons)
- Axios & React-Markdown

**Backend:**
- Python 3 + FastAPI
- **LangChain & LangChain-Groq** (Agentic reasoning and tool-calling framework)
- Groq Cloud API (`llama-3.3-70b-versatile` for high-speed reasoning)
- EasyOCR & PyMuPDF (Document processing)
- TheFuzz (Fuzzy string matching for drug resolution)
- Pandas (Structured data processing)

**Data Sources:**
- Indian Medicine Dataset — brand name to active ingredient mapping
- Mendeley DDI Dataset — DrugBank v5.1 drug-drug interaction pairs

---

## 🚀 How to Run Locally

### 1. Backend Setup
Open a terminal and navigate to the `backend` folder:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup
Open a **new** terminal and navigate to the `frontend` folder:
```bash
cd frontend
npm install
npm run dev
```

---

## 🔮 Roadmap (What's Next?)

- **Phase 3: RAG Implementation:** Adding vector databases (ChromaDB/LanceDB) for deep search across long medical histories and clinical knowledge bases.
- **Phase 4: SQL Migration:** Moving from JSON-based memory to a robust SQL backend for multi-user support.
- **Enhanced OCR:** Specialized pipelines for handwritten doctor prescriptions.
- **Multi-Profile Support:** Manage separate health profiles for different family members.

---

## ⚠️ Disclaimer
**MaathirAI is a developmental project and not a substitute for professional medical advice.** Always consult a healthcare professional or pharmacist before making medical decisions. AI-estimated interactions must always be clinically verified.
