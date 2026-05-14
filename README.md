# MaathirAI - Medical Interaction Assistant

MaathirAI is an intelligent, full-stack medical awareness assistant built specifically for Indian patients and caregivers. It helps you understand your medications, decode medical reports, and safely check for dangerous drug-drug interactions — all in one place.
 
Whether you're an elderly patient managing multiple prescriptions, a working adult tracking your own medicines, or a caregiver handling a family member's health — MaathirAI works the same way: upload a photo or PDF, and let the AI do the heavy lifting.
 
> **The name comes from *Maathirai* (மாத்திரை) — the Tamil word for *tablet*. Since MaathirAI uses AI to identify and analyse tablets and medicines, the name is a natural fit: Maathirai + AI = MaathirAI.**

---
 
## 🎯 What MaathirAI Actually Does
 
### 1. Reads your medicine strips, prescriptions, and reports
Upload a blurry photo of a Dolo 650 strip, a typed prescription PDF, or a blood test report. MaathirAI uses OCR to pull out all the text, then uses an LLM to identify what's medically relevant — medication names, dosages, diagnosed conditions, and listed allergies.
 
### 2. Understands Indian brand names
Most drug interaction databases are US-centric and have no idea what *Telma 40*, *Crocin Advance*, or *Combiflam* are. MaathirAI solves this by mapping Indian brand names to their active generic ingredients (e.g. *Dolo 650 → Paracetamol 650mg*, *Augmentin 625 → Amoxycillin + Clavulanic Acid*) using a local Indian medicine CSV database before any interaction check happens.
 
### 3. Checks for dangerous drug combinations
Once the active ingredients are known, MaathirAI checks every pair against a local Drug-Drug Interaction (DDI) database extracted from DrugBank v5.1. It flags interactions as **Safe**, **Moderate**, or **Severe** with a plain-English explanation. If a drug isn't in the structured database, Groq AI provides an estimated interaction — always clearly labelled as `[AI-ESTIMATED]`.
 
### 4. Builds and remembers your medication profile
Every uploaded document adds to a persistent medical profile stored across sessions. MaathirAI remembers what medicines you've previously added, your listed conditions, and your allergies — so when you upload a new prescription, it checks against your entire history, not just the current file.
 
### 5. Lets you ask questions naturally
The chat interface lets you ask things like *"Can I take ibuprofen with my current medicines?"* or *"What does my Warfarin interact with?"* — and MaathirAI answers using your stored profile as context, not generic information.
 
---

## 🌟 Key Features
 
- **Multi-Modal Document Processing:** Upload scanned PDFs, digital PDFs, or photos (JPG/PNG). The system uses `PyMuPDF` for native text extraction and `EasyOCR` (with dynamic upscaling) to read tiny, sideways text on pill strips.
- **Indian Medicine Database:** Automatically maps regional Indian brand names (e.g., *Dolo 650*, *Telma 40*) to their active generic ingredients using a local CSV database — solving the biggest gap in every existing drug interaction tool for Indian users.
- **Automated Interaction Checking:** Checks your active ingredient list against a local DDI database (DrugBank v5.1), instantly flagging Safe, Moderate, or Severe interactions. Features a Groq AI fallback for drugs not found in the structured database, with all AI-estimated results clearly labelled.
- **Smart Sequential Uploads:** The React frontend automatically batches multi-file uploads into perfectly timed sequential requests, maximising OCR accuracy and preventing the AI from getting overwhelmed.
- **Persistent Medical Profile:** MaathirAI maintains a continuous conversation state (`chat_memory.json`) and a living medical profile (`medical_memory.json`) — acting like a dedicated assistant who remembers your exact blood sugar metrics from an earlier report and cross-references them with your latest prescription.
- **Designed for Indian Users:** Brand name resolution, support for Indian pharmaceutical naming conventions, and an interface built for users ranging from elderly patients to tech-savvy caregivers.

---

## 🛠️ Technology Stack

**Frontend:**
- React + Vite
- Tailwind CSS (v3)
- Lucide React (Icons)
- Axios & React-Markdown

**Backend:**
- Python 3 + FastAPI
- Groq Cloud API (`llama-3.3-70b-versatile` for lightning-fast entity extraction and conversational reasoning)
- EasyOCR & PyMuPDF (Document processing)
- TheFuzz (Fuzzy string matching for drug resolution)
- Pandas (Indian medicine CSV + DDI database lookups)

**Data Sources:**
- Indian Medicine Dataset — brand name to active ingredient mapping (~20,000 Indian medicines)
- Mendeley DDI Dataset — DrugBank v5.1 drug-drug interaction pairs (structured, peer-reviewed)

---

## ⚙️ Prerequisites

To run this project locally, you will need:
- **Node.js** (v18+)
- **Python** (v3.9+)
- A **Groq API Key** (Free tier works perfectly — get one at console.groq.com)

---

## 🚀 How to Run Locally

### 1. Backend Setup

Open a terminal and navigate to the `backend` folder:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

Set up your Environment Variables:
1. Create a file named `.env` inside the `backend` directory.
2. Add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```
*The backend API will be running at `http://localhost:8000`*

### 2. Frontend Setup

Open a **new** terminal and navigate to the `frontend` folder:
```bash
cd frontend
```

Install the Node modules:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The frontend UI will be running at `http://localhost:5173`*

---

## 💊 Example Use Cases
 
| Situation | What you upload | What MaathirAI does |
|-----------|----------------|---------------------|
| Just bought Dolo 650 and already take Warfarin | Photo of Dolo 650 strip | Resolves to Paracetamol, checks against Warfarin, flags interaction severity |
| Got a new prescription with 3 medicines | Prescription PDF | Extracts all 3 drugs, checks each pair, updates your profile |
| Want to know if your blood report affects your medicines | Blood test PDF | Extracts conditions (e.g. elevated creatinine), stores against your profile |
| Ask a question without uploading | Type: "Can I take Combiflam?" | AI checks your stored profile, resolves Combiflam to Ibuprofen + Paracetamol, answers with context |

---

## ⚠️ Disclaimer
**MaathirAI is a developmental project and not a substitute for professional medical advice.** Always consult a healthcare professional or pharmacist before making medical decisions or changing your medication regimen. AI-estimated interactions must always be clinically verified.
