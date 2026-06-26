import json
import logging
from typing import List, Dict, Optional, Any
import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.schemas.analysis import AIAnalysisResult
from app.schemas.resume import (
    CoverLetterResponse,
    InterviewQuestionsResponse,
    LinkedInSummaryResponse,
    RewriteSectionResponse,
    RoadmapResponse
)

logger = logging.getLogger(__name__)

# Initialize clients if keys are present
def get_ai_client(user_api_key: Optional[str] = None):
    # Determine which key to use (User preferred vs system default)
    gemini_key = user_api_key or settings.GEMINI_API_KEY
    openai_key = user_api_key or settings.OPENAI_API_KEY

    is_gemini_active = bool(gemini_key and "your_gemini_api_key" not in gemini_key)
    is_openai_active = bool(openai_key and "your_openai_api_key" not in openai_key)

    return is_gemini_active, gemini_key, is_openai_active, openai_key

class AIService:
    @staticmethod
    def analyze_resume(
        resume_text: str,
        job_desc_text: Optional[str] = None,
        user_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the resume text against the job description.
        Returns a dict conforming to AIAnalysisResult.
        """
        is_gemini_active, gemini_key, is_openai_active, openai_key = get_ai_client(user_api_key)

        prompt = f"""
        You are an expert ATS (Applicant Tracking System) optimizer and professional recruiter.
        Analyze the following resume text and compare it with the provided job description (if any).
        
        RESUME CONTENT:
        ---
        {resume_text}
        ---

        JOB DESCRIPTION (Optional):
        ---
        {job_desc_text or "No specific job description provided. Analyze resume generally for a professional career profile."}
        ---

        Please extract information, perform keyword analysis, check spelling/grammar, format issues, and assess overall matching.
        """

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": AIAnalysisResult
                    }
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"Gemini API analysis failed: {str(e)}. Falling back.")

        if is_openai_active:
            try:
                client = OpenAI(api_key=openai_key)
                response = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional ATS recruiter assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=AIAnalysisResult
                )
                # Parse structured output from OpenAI
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"OpenAI API analysis failed: {str(e)}. Falling back.")

        # Fallback Mock Mode (Runs when no API keys are present)
        logger.warning("Running AI Analysis in MOCK mode. Please configure GEMINI_API_KEY in environment variables.")
        return AIService._get_mock_analysis(resume_text, job_desc_text)

    @staticmethod
    def generate_cover_letter(
        resume_text: str,
        job_desc_text: str,
        user_api_key: Optional[str] = None
    ) -> CoverLetterResponse:
        is_gemini_active, gemini_key, is_openai_active, openai_key = get_ai_client(user_api_key)

        prompt = f"""
        Write a professional, highly-engaging cover letter based on this resume and job description.
        Incorporate matching skills and express enthusiasm. Keep it to one page (300-400 words).
        
        RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {job_desc_text}

        Format the output in clean text with spacing.
        """

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return CoverLetterResponse(cover_letter=response.text)
            except Exception as e:
                logger.error(f"Gemini Cover Letter failed: {e}")

        # Mock / Fallback
        mock_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the open position, as advertised. With a strong background highlighted in my resume, I am confident in my ability to add immediate value to your engineering organization.

Throughout my career, I have focused on solving complex technical challenges, collaborating with cross-functional teams, and implementing scalable solutions. The responsibilities described in your job posting align perfectly with my skillset. Specifically, my experience in development matches the core requirements of your team.

I am eager to discuss how my qualification fits your needs in detail during an interview. Thank you for your time and consideration.

Sincerely,
Job Applicant"""
        return CoverLetterResponse(cover_letter=mock_letter)

    @staticmethod
    def generate_interview_questions(
        resume_text: str,
        job_desc_text: Optional[str] = None,
        user_api_key: Optional[str] = None
    ) -> InterviewQuestionsResponse:
        is_gemini_active, gemini_key, _, _ = get_ai_client(user_api_key)

        prompt = f"""
        Generate a list of 5 interview questions tailored to this resume and the job description.
        Include a mix of technical and behavioral questions.
        For each question, provide an 'ideal_answer' summary highlighting what the recruiter is looking for.
        
        RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {job_desc_text or "General Industry role"}
        """

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": InterviewQuestionsResponse
                    }
                )
                return InterviewQuestionsResponse(**json.loads(response.text))
            except Exception as e:
                logger.error(f"Gemini interview questions failed: {e}")

        # Mock Interview Questions
        mock_questions = [
            {
                "question": "Can you describe a challenging project from your resume and how you overcame technical hurdles?",
                "type": "Behavioral",
                "ideal_answer": "The candidate should discuss a project mentioned in their resume, explaining the problem, their specific actions (technologies used, leadership, design choices), and the measurable result (performance boost, delivery on-time)."
            },
            {
                "question": "How do you keep your skills updated in such a fast-evolving technical landscape?",
                "type": "General",
                "ideal_answer": "Look for a structured approach to learning: online courses, reading documentation, pet projects, or contributing to open source."
            },
            {
                "question": "Based on the job requirements, how do you handle state management or scalability in your code?",
                "type": "Technical",
                "ideal_answer": "Candidate should mention standard design patterns, API integrations, caching mechanisms, or system design principles relevant to their field."
            }
        ]
        return InterviewQuestionsResponse(questions=mock_questions)

    @staticmethod
    def generate_linkedin_summary(
        resume_text: str,
        user_api_key: Optional[str] = None
    ) -> LinkedInSummaryResponse:
        is_gemini_active, gemini_key, _, _ = get_ai_client(user_api_key)
        prompt = f"Based on this resume, generate a modern LinkedIn profile summary, 3 catchy headlines, and a website portfolio summary:\n\n{resume_text}"

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": LinkedInSummaryResponse
                    }
                )
                return LinkedInSummaryResponse(**json.loads(response.text))
            except Exception as e:
                logger.error(f"Gemini LinkedIn Summary failed: {e}")

        mock_data = {
            "linkedin_summary": "Passionate Software Engineer | Specializing in building high-performance web applications using modern web technologies. Experience driving business value and automating developer workflows.",
            "headline_suggestions": [
                "Software Engineer | React & FastAPI Developer | SaaS Builder",
                "Full Stack Developer | Turning Complex Problems into Elegant Code",
                "Technical Analyst | Specialist in Software Engineering & Scale"
            ],
            "portfolio_summary": "Hello! I am a full-stack engineer focused on creating efficient, beautiful interfaces and robust backend microservices. Welcome to my portfolio!"
        }
        return LinkedInSummaryResponse(**mock_data)

    @staticmethod
    def generate_rewrite(
        resume_text: str,
        user_api_key: Optional[str] = None
    ) -> RewriteSectionResponse:
        is_gemini_active, gemini_key, _, _ = get_ai_client(user_api_key)
        prompt = f"Analyze the resume and rewrite the professional summary, suggest a optimized list of skills, improve existing bullet points to use strong action verbs, and write an ATS friendly markdown version of the resume:\n\n{resume_text}"

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": RewriteSectionResponse
                    }
                )
                return RewriteSectionResponse(**json.loads(response.text))
            except Exception as e:
                logger.error(f"Gemini Rewrite failed: {e}")

        mock_data = {
            "original_summary": "Motivated developer looking for software engineering roles.",
            "suggested_summary": "Results-oriented Software Engineer with experience designing and developing scalable web applications. Proficient in React, Python, FastAPI, and PostgreSQL. Proven track record of improving application performance by 25% and automating backend integrations.",
            "original_skills": ["Coding", "Python", "Websites"],
            "suggested_skills": ["Python (Advanced)", "FastAPI", "React", "SQLAlchemy", "PostgreSQL", "RESTful APIs", "System Design", "Agile Methodologies"],
            "suggested_bullets": [
                {
                    "original": "Worked on the backend of the main application.",
                    "improved": "Architected and optimized RESTful endpoints using FastAPI, reducing database response times by 30% through index optimization.",
                    "reason": "Uses active verbs ('Architected', 'optimized') and includes measurable impact (30% latency reduction)."
                }
            ],
            "ats_friendly_markdown": "# Job Applicant\n\n- Email: applicant@email.com\n- Portfolio: portfolio.com\n\n## Professional Summary\nResults-oriented Software Engineer with experience..."
        }
        return RewriteSectionResponse(**mock_data)

    @staticmethod
    def generate_career_roadmap(
        resume_text: str,
        user_api_key: Optional[str] = None
    ) -> RoadmapResponse:
        is_gemini_active, gemini_key, _, _ = get_ai_client(user_api_key)
        prompt = f"Perform deep career analysis on this resume. Identify career path, level, readability score, estimated salary, industry and layout a 4-step roadmap with learning resources:\n\n{resume_text}"

        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": RoadmapResponse
                    }
                )
                return RoadmapResponse(**json.loads(response.text))
            except Exception as e:
                logger.error(f"Gemini Career Roadmap failed: {e}")

        mock_data = {
            "career_path": "Full-Stack Software Engineering / Tech Lead",
            "timeline_steps": [
                {
                    "step": "Master Advanced System Architecture & Microservices",
                    "timeline": "3 - 6 Months",
                    "skills_to_acquire": "Docker, Kubernetes, gRPC, Message Queues (RabbitMQ/Kafka)",
                    "resources": "System Design Primer (GitHub), Designing Data-Intensive Applications (Book)"
                },
                {
                    "step": "Develop Cloud Computing Proficiency",
                    "timeline": "6 - 12 Months",
                    "skills_to_acquire": "AWS/GCP infrastructure, Terraform (IAC), CI/CD workflows",
                    "resources": "AWS Certified Solutions Architect Course, HashiCorp Learn"
                },
                {
                    "step": "Enhance Team Leadership & Mentorship Skills",
                    "timeline": "12 - 18 Months",
                    "skills_to_acquire": "Agile Scrum Master, Code review best practices, Tech design docs creation",
                    "resources": "Pragmatic Programmer, Scrum.org certifications"
                }
            ],
            "industry": "Information Technology / SaaS",
            "career_level": "Mid-Level Engineer",
            "readability_score": 72,
            "salary_estimate": "$95,000 - $125,000"
        }
        return RoadmapResponse(**mock_data)

    @staticmethod
    def chat_assistant(
        resume_text: str,
        chat_history: List[Dict[str, str]],
        new_message: str,
        job_desc_text: Optional[str] = None,
        user_api_key: Optional[str] = None
    ) -> str:
        """
        Chat assistant scoped to the resume and optional job description.
        """
        is_gemini_active, gemini_key, is_openai_active, openai_key = get_ai_client(user_api_key)

        # Build context prompt
        system_instruction = f"""
        You are a career chat assistant named "Resume Bot".
        You have direct access to the user's resume and an optional job description.
        Answer all questions professionally, providing guidance, mock interview preparation, or layout improvements.
        Do not make up facts not mentioned in the resume. Be encouraging and concise.

        USER RESUME:
        {resume_text}

        JOB DESCRIPTION (If any):
        {job_desc_text or "None provided."}
        """

        # Format conversation
        messages = []
        # Add system context
        if is_gemini_active:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                # Create history structure
                contents = []
                for msg in chat_history:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [msg["content"]]})
                contents.append({"role": "user", "parts": [new_message]})
                
                response = model.generate_content(contents)
                return response.text
            except Exception as e:
                logger.error(f"Gemini chat failed: {e}")

        if is_openai_active:
            try:
                client = OpenAI(api_key=openai_key)
                openai_msgs = [{"role": "system", "content": system_instruction}]
                for msg in chat_history:
                    role = "user" if msg["role"] == "user" else "assistant"
                    openai_msgs.append({"role": role, "content": msg["content"]})
                openai_msgs.append({"role": "user", "content": new_message})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=openai_msgs
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI chat failed: {e}")

        # Mock Response
        return f"Hello! (Running in Mock Mode) I see you asked about: '{new_message}'. Based on your resume skills in development, this is a great area to focus on. What specific experience would you like to highlight?"

    @staticmethod
    def _get_mock_analysis(resume_text: str, job_desc: Optional[str]) -> Dict[str, Any]:
        """
        Helper to return high quality mock analysis data.
        """
        # Search for some programming languages in resume to customize mock list
        detected = []
        all_checks = ["python", "javascript", "react", "fastapi", "sql", "java", "c++", "docker", "aws", "node", "typescript"]
        for tech in all_checks:
            if tech in resume_text.lower():
                detected.append(tech.title())

        if not detected:
            detected = ["JavaScript", "React", "Python", "SQL"]

        missing = ["Docker", "Kubernetes", "AWS Cloud", "GraphQL"]
        if job_desc:
            # Add some missing words if job description is present
            for tech in ["typescript", "tailwind", "redis", "mongodb"]:
                if tech in job_desc.lower() and tech not in resume_text.lower():
                    missing.append(tech.title())

        # Simple score generation
        ats = 78
        match = 65 if job_desc else 0
        if len(detected) > 6:
            ats += 8
        if job_desc and len(missing) < 3:
            match += 20

        return {
            "ats_score": min(ats, 100),
            "match_percentage": min(match, 100) if job_desc else 80,
            "skills_detected": detected,
            "missing_skills": missing,
            "technical_skills": detected,
            "soft_skills": ["Problem Solving", "Team Collaboration", "Effective Communication", "Adaptability"],
            "keyword_analysis": [
                {"word": detected[0], "count": 5, "density": 1.2, "status": "Good"},
                {"word": "Developer", "count": 8, "density": 2.0, "status": "Good"},
                {"word": "Responsible", "count": 10, "density": 2.5, "status": "Overused"}
            ],
            "experience_summary": "Extracted professional background demonstrating progressive engineering responsibilities.",
            "education_summary": "Found degree in relevant technical discipline (e.g. Computer Science or Engineering).",
            "certifications": ["AWS Certified Cloud Practitioner (Mock)"],
            "projects": ["Personal SaaS Portfolio Project (Mock)"],
            "contact_validation": {
                "email": "@" in resume_text,
                "phone": any(c.isdigit() for c in resume_text),
                "linkedin": "linkedin.com" in resume_text.lower(),
                "portfolio": "github.com" in resume_text.lower() or "portfolio" in resume_text.lower(),
                "suggestions": ["Include professional LinkedIn link if missing", "Ensure phone number includes country code"]
            },
            "grammar_check": [
                {"issue": "Passive voice detected", "suggestion": "Use active verbs like 'Architected' or 'Led'", "snippet": "Responsible for maintaining code..."}
            ],
            "formatting_suggestions": ["Ensure 1-inch margins on all sides", "Use bullet points rather than paragraphs"],
            "resume_length_analysis": {
                "length_type": "Ideal",
                "word_count": len(resume_text.split()),
                "page_count": 1,
                "advice": "Your resume fits perfectly on 1 page."
            },
            "action_verb_analysis": {
                "count": 12,
                "verbs": ["Developed", "Managed", "Implemented", "Designed"],
                "rating": "Strong",
                "advice": "Good usage of impact verbs."
            },
            "strengths": ["Clear structure", "Good technical stack alignment", "Highlights projects"],
            "weaknesses": ["Lacks quantifiable achievements (e.g. % improvement metrics)", "Lacks Docker/cloud infrastructure indicators"],
            "improvement_suggestions": [
                "Quantify results: e.g. instead of 'wrote backend', use 'Designed backend endpoints that reduced page load by 20%'.",
                "Include certifications section to make it ATS friendly."
            ],
            "recruiter_tips": [
                "Recruiters scan resumes in 6 seconds. Place technical skills at the top.",
                "Tailor bullet points to emphasize requirements listed in the job description."
            ]
        }
