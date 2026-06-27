AI Resume Analyzer 🚀

An AI-powered Resume Analyzer built with React, FastAPI, and Google Gemini AI. Upload your resume, analyze ATS compatibility, identify missing skills, and receive actionable suggestions to improve your chances of landing interviews.

🌐 Live Demo

Frontend:
https://ai-resume-analyzer-frontend-9fyi.onrender.com

Backend API Docs:
https://ai-resume-analyzer-lc35.onrender.com/docs

---

✨ Features

- User Authentication
- Resume PDF Upload
- Resume Text Extraction
- ATS Score Analysis
- Skills Detection
- Missing Skills Identification
- Experience Summary
- Education Summary
- Resume Improvement Suggestions
- Job Description Matching
- Responsive Modern UI
- FastAPI REST API
- Google Gemini AI Integration
- Cloud Deployment on Render

---

🛠️ Tech Stack

Frontend

- React (Vite)
- Tailwind CSS
- React Router
- Axios

Backend

- FastAPI
- Python
- SQLAlchemy
- SQLite
- Pydantic

AI

- Google Gemini API

Deployment

- Render

---

📂 Project Structure

AI-Resume-Analyzer/
│
├── backend/
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│
├── .env.example
├── .gitignore
└── README.md

🚀 Installation

Clone Repository

git clone https://github.com/thanigai1612/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer

Backend Setup

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload

Backend runs at:

http://localhost:8000

Frontend Setup

cd frontend

npm install

npm run dev

Frontend runs at:

http://localhost:5173

---

🔑 Environment Variables

Create a ".env" file inside the backend folder:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
SECRET_KEY=YOUR_SECRET_KEY
DATABASE_URL=sqlite:///./resume_analyzer.db

---

📊 Future Enhancements

- AI Resume Rewrite
- AI Cover Letter Generator
- AI Interview Preparation
- Resume Comparison
- Resume History Tracking
- PostgreSQL Support
- Analytics Dashboard
- PDF Report Export

---

👨‍💻 Author

Thanigai Velan

GitHub:
https://github.com/thanigai1612

---
44564564
⭐ Support

If you found this project useful, consider giving it a star on GitHub.