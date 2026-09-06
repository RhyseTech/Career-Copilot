# ResumeIQ - AI ATS Optimizer

An AI-powered resume intelligence platform that provides transparent ATS scoring, job description alignment, and semantic AI matching.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (Optional, for running PostgreSQL/Redis locally)

## 1. Setup the Backend

The backend is built with FastAPI, PyMuPDF, Sentence-BERT, and RapidFuzz.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configuration (Required):
   To use the AI Optimization features, create a `.env` file in the `backend/` directory with the following variables:
   ```env
   LLM_PROVIDER=gemini  # or groq
   GEMINI_API_KEY=your-gemini-api-key-here
   GROQ_API_KEY=your-groq-api-key-here
   GEMINI_MODEL=gemini-3.8-flash
   GROQ_MODEL=openai/gpt-oss-120b
   DATABASE_URL=postgresql://resumeiq:password@localhost:5432/resumeiq_db
   SECRET_KEY=your-super-secret-key
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Note: On the first run, the Sentence-BERT model (`all-MiniLM-L6-v2`) will be downloaded automatically (approx 80MB).*

The backend API will be available at [http://localhost:8000](http://localhost:8000). You can view the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## 2. Setup the Frontend

The frontend is built with Next.js (App Router), React, and Tailwind CSS.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

## 3. Setup the Database (Optional)

If you wish to use the Postgres + pgvector database for storing users and resume versions:

1. In the root directory, run:
   ```bash
   docker-compose up -d
   ```
   This will spin up PostgreSQL (port 5432) and Redis (port 6379).

## API Endpoints Overview

- `POST /resumes/upload`: Upload a PDF or DOCX file. Extracts text and basic sections.
- `POST /ats/analyze`: Calculates the Resume-Only ATS score based on heuristic rules (Structure, Skills, Experience, Content, Keywords, Impact).
- `POST /ats/match`: Calculates the Hybrid Job Match Score comparing a resume against a specific Job Description using fuzzy matching and Semantic Sentence-BERT.
- `POST /optimization/suggest`: Uses an LLM (Groq or Google Gemini) to generate targeted, actionable resume improvements without fabrication.
