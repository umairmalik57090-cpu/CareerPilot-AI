# 🚀 CareerPilot AI

### **From CV to Career Success — An AI-Powered Career Intelligence Platform**

> **Analyze your CV. Match your dream job. Discover your skill gaps. Build your career roadmap. Prepare for success.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge\&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red?style=for-the-badge\&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge)
![Generative AI](https://img.shields.io/badge/Generative_AI-Powered-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Overview

**CareerPilot AI** is an upgraded AI-powered **Career Intelligence Platform** designed to help students, graduates, and job seekers move from simply having a CV to having a clear career strategy.

The improved version goes beyond traditional CV analysis by connecting **CV analysis, ATS optimization, job matching, skill-gap detection, career planning, and interview preparation** into one platform.

Powered by **Python, Streamlit, Groq, and LLM technology**, CareerPilot AI provides personalized insights based on the user's CV and target career.

---

## 🎯 The CareerPilot AI Journey

```text
             📄 Upload CV
                  │
                  ▼
          🔍 CV Analysis
                  │
                  ▼
          🎯 ATS Compatibility
                  │
                  ▼
         💼 Job Description Match
                  │
                  ▼
           🧠 Skill Gap Analysis
                  │
                  ▼
        🗺️ Personalized Roadmap
                  │
                  ▼
          🎤 Interview Practice
                  │
                  ▼
           📊 Career Analytics
```

---

# ✨ Key Features

## 📄 1. AI CV Analysis

Upload your CV and receive an intelligent analysis including:

* CV score
* Strengths
* Areas for improvement
* Detailed recommendations
* Professional feedback
* Extracted skills and information

Supports common CV formats such as **PDF and DOCX**.

---

## 🎯 2. ATS Compatibility Checker

Understand how your CV performs against Applicant Tracking Systems.

Features include:

* ATS score
* Keyword analysis
* Missing keywords
* Formatting issues
* Optimization suggestions
* ATS improvement recommendations

---

## 💼 3. Job Description Matcher

Compare your CV directly with a target job description.

The system identifies:

* Matching skills
* Missing skills
* Preferred skills
* Experience alignment
* Job Match Score
* Score breakdown
* Reasons behind the score

Instead of simply saying **"52/100"**, CareerPilot AI explains **why** you received that score.

---

## 🧠 4. Skill Gap Analysis

Discover what skills you need to develop for your target role.

The system can identify:

* Current skills
* Missing required skills
* Preferred skills
* Skill priorities
* Learning recommendations
* Areas requiring improvement

---

## 🗺️ 5. Personalized Career Roadmap

Turn your skill gaps into an actionable learning plan.

The roadmap can recommend:

* Skills to learn
* Learning priorities
* Technologies to explore
* Project ideas
* Career development steps
* Progress direction

---

## 🎤 6. AI Interview Coach

Prepare for real interviews with AI.

Features include:

* Role-specific interview questions
* Answer evaluation
* Technical feedback
* Communication feedback
* Improvement suggestions
* Interview readiness insights

---

## 💬 7. AI Career Assistant

Ask career-related questions and receive AI-powered guidance.

You can ask about:

* Career paths
* CV improvement
* Interview preparation
* Skill development
* Job applications
* AI/ML careers
* Learning strategies

---

## 📊 8. Career Analytics

Track your career readiness through a centralized dashboard.

Monitor:

* CV Score
* ATS Score
* Job Match Score
* Skill Coverage
* Interview Readiness
* Career progress

The analytics system is designed to use actual analysis results rather than displaying random or placeholder scores.

---

## 🕐 9. Analysis History

Keep track of previous career analyses.

Users can:

* Review previous results
* Compare progress
* Track improvements
* Maintain analysis history

---

## ⚡ 10. Optimized AI Integration

CareerPilot AI uses **Groq API** for fast LLM inference.

The application is designed to trigger AI requests **only when an AI-powered action is actually required**, helping reduce unnecessary API calls and improving efficiency.

---

# 🧠 Powered by Groq AI

CareerPilot AI uses the **Groq API** to power its AI features.

### Why Groq?

* ⚡ Fast AI inference
* 🧠 LLM-powered responses
* 🚀 Responsive application experience
* 🔑 API-based integration
* 💻 Suitable for AI-powered applications

---

# 🛠️ Tech Stack

| Technology             | Purpose                      |
| ---------------------- | ---------------------------- |
| **Python**             | Core application development |
| **Streamlit**          | Interactive web application  |
| **Groq API**           | LLM / AI processing          |
| **PyMuPDF**            | PDF CV processing            |
| **python-docx**        | DOCX CV processing           |
| **Pandas**             | Data processing              |
| **Plotly**             | Analytics & visualization    |
| **HTML/CSS**           | Custom interface             |
| **Prompt Engineering** | AI response optimization     |

The technical stack and project experience are based on the implementation described in the project material. 

---

# 📂 Project Structure

```text
CareerPilot-AI/
│
├── app.py
├── groq_client.py
├── ai_engine.py
├── ats_checker.py
├── interview.py
├── analytics.py
├── config.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── .env.example
│
├── assets/
├── uploads/
├── exports/
├── history/
└── screenshots/
```

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/umairmalik57090-cpu/CareerPilot-AI.git
```

## 2. Navigate to the Project

```bash
cd CareerPilot-AI
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Groq API

Create a `.env` file in the project root:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
MODEL_NAME=llama-3.3-70b-versatile
```

**Never commit your real API key to GitHub.**

## 5. Run CareerPilot AI

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile
```

Add `.env` to `.gitignore`:

```text
.env
__pycache__/
*.pyc
```

---

# 🌟 What Makes CareerPilot AI Different?

Traditional CV tools usually answer:

> **"How good is my CV?"**

CareerPilot AI goes further:

> **"Where am I now, what am I missing, what should I improve, and how can I prepare for my target career?"**

The platform connects the entire career preparation process into one workflow:

**Analyze → Match → Identify → Improve → Prepare → Grow**

---

# 🔮 Future Improvements

Potential future enhancements include:

* AI Cover Letter Generator
* LinkedIn Profile Analyzer
* Job Recommendation Engine
* Voice-Based Interview Practice
* Multi-language Support
* PDF Career Reports
* Cloud Database
* User Authentication
* Career Progress Tracking
* Personalized Job Recommendations

---

# 👨‍💻 Developer

### **Muhammad Umair**

**BS Computer Science Student | AI & Generative AI Enthusiast**

Passionate about building practical AI-powered applications that solve real-world problems using **Python, Streamlit, LLMs, Generative AI, and modern development tools**.

---

<div align="center">

### 🚀 **CareerPilot AI**

**Analyze Smarter • Match Better • Learn Faster • Build Your Career**

*From CV to Career Success — Powered by AI.*

</div>
