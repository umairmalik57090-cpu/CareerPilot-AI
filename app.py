import os
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st

from ai_engine import analyze_resume
from ai_service import safe_ai_call
from analytics import build_dashboard_charts
from ats_checker import calculate_ats_score
from config import APP_CONFIG, SIDEBAR_ITEMS, HISTORY_DIR
from interview import evaluate_answer, generate_interview_questions
from job_matcher import calculate_job_match
from roadmap import (
    generate_career_tips,
    generate_linkedin_suggestions,
    generate_roadmap,
    generate_skill_gap_analysis,
    rewrite_resume_section,
)
from resume_parser import (
    build_analysis_history_entry,
    build_history_entry,
    extract_text_from_file,
    load_history_entries,
    parse_resume,
    save_history_entry,
    save_uploaded_resume,
)
from styles import get_custom_css
from utils import (
    build_dashboard_kpis,
    get_connection_status,
    get_current_datetime,
    initialize_session_state,
)


def get_groq_client_module():
    import importlib
    import groq_client
    importlib.reload(groq_client)
    return groq_client


def save_current_analysis_history(summary: str = "Analysis recorded", job_description: str = "") -> None:
    if not st.session_state.get("uploaded_resume"):
        return

    parsed_resume = st.session_state["uploaded_resume"]["parsed"]
    analysis_result = st.session_state.get("analysis_result") or {}
    ats_result = st.session_state.get("ats_result") or {}
    job_match_result = st.session_state.get("job_match_result") or {}

    resume_score = int(analysis_result.get("resume_score", analysis_result.get("overall_score", 0)) or 0)
    ats_score = int(ats_result.get("overall_score", 0) or 0)
    # job_match_result['score'] may be 'N/A' or None when insufficient data; coerce safely
    _raw_job_score = job_match_result.get("score", 0)
    try:
        job_match_score = int(_raw_job_score) if _raw_job_score is not None and _raw_job_score != "N/A" else 0
    except Exception:
        job_match_score = 0
    skill_coverage = int(job_match_result.get("skill_coverage", 0) or 0)
    interview_readiness = 100 if st.session_state.get("interview_questions") else 0

    history_record = build_analysis_history_entry(
        parsed_resume=parsed_resume,
        resume_score=resume_score,
        ats_score=ats_score,
        job_match_score=job_match_score,
        skill_coverage=skill_coverage,
        interview_readiness=interview_readiness,
        target_role=st.session_state.get("target_role", "General"),
        summary=summary,
        job_description=job_description,
        matching_skills=list(job_match_result.get("matching_skills", [])),
        missing_skills=list(job_match_result.get("missing_skills", [])),
        preferred_skills=list(job_match_result.get("preferred_skills", [])),
        partial_matches=list(job_match_result.get("partial_matches", [])),
    )
    save_history_entry(history_record)
    st.session_state["history_entries"] = load_history_entries()


def execute_single_call_resume_analysis(target_role: str = "General") -> None:
    if not st.session_state.get("uploaded_resume"):
        st.warning("Please upload a resume first.")
        return

    st.session_state["is_analyzing"] = True
    resume_data = st.session_state["uploaded_resume"]
    text = resume_data.get("text", "")
    parsed = resume_data.get("parsed", {})
    st.session_state["target_role"] = target_role

    try:
        from ai_engine import analyze_resume_comprehensive
        with st.spinner("Analyzing resume with Groq AI..."):
            result = analyze_resume_comprehensive(text, parsed, target_role=target_role)

            st.session_state["analysis_result"] = result

            local_ats = result.get("ats_details") or calculate_ats_score(parsed)
            if "ats_score" in result:
                local_ats["overall_score"] = result["ats_score"]
            st.session_state["ats_result"] = local_ats

            questions = result.get("interview_questions", [])
            st.session_state["interview_questions"] = questions
            st.session_state["interview_index"] = 0
            st.session_state["interview_feedbacks"] = [None] * len(questions)
            st.session_state["interview_answers"] = [""] * len(questions)

            st.session_state["roadmap"] = generate_roadmap(target_role, text, result)
            st.session_state["skill_gap"] = generate_skill_gap_analysis(target_role, text, result)
            st.session_state["linkedin"] = generate_linkedin_suggestions(text, result)
            st.session_state["career_tips"] = generate_career_tips()
            st.session_state["comprehensive_analysis"] = result
            st.session_state["analysis_done"] = True

            save_current_analysis_history(summary="Resume analysis completed.")

            if result.get("from_cache"):
                st.info("⚡ Loaded complete analysis from instant cache (0 API calls).")
            else:
                st.success("✨ Complete AI analysis ready! All UI sections populated using Groq AI.")
    except Exception as exc:
        print(f"[Resume Analysis] Groq exception: {repr(exc)}")
        st.error("Unable to generate AI response. Please try again.")
    finally:
        st.session_state["is_analyzing"] = False


st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

initialize_session_state()


import streamlit.components.v1 as components


def get_header_snapshot() -> tuple[str, str, str]:
    date_label, time_label = get_current_datetime()
    return date_label, time_label, get_connection_status()


def render_header():
    date_label, time_label, status_label = get_header_snapshot()
    st.markdown(
        f"""
        <div class="topbar-card">
            <div>
                <div class="eyebrow">{APP_CONFIG['tagline']}</div>
                <h1 class="hero-title">{APP_CONFIG['title']}</h1>
                <p class="hero-subtitle">{APP_CONFIG['subtitle']}</p>
            </div>
            <div class="topbar-meta">
                <div class="meta-pill" id="live-date-pill">📅 {date_label}</div>
                <div class="meta-pill" id="live-time-pill">🕒 {time_label}</div>
                <div class="meta-pill">✨ {status_label}</div>
            </div>
        </div>
        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" style="display:none;" onerror="
        (function(){{
            function updateClock(){{
                var dateEl = document.getElementById('live-date-pill');
                var timeEl = document.getElementById('live-time-pill');
                if(!dateEl || !timeEl) return;
                var now = new Date();
                var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
                var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                var dayName = days[now.getDay()];
                var monthName = months[now.getMonth()];
                var dayNum = String(now.getDate()).padStart(2, '0');
                var year = now.getFullYear();
                var hours = now.getHours();
                var minutes = String(now.getMinutes()).padStart(2, '0');
                var ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12 || 12;
                var formattedHours = String(hours).padStart(2, '0');
                var dateStr = '📅 ' + dayName + ', ' + monthName + ' ' + dayNum + ', ' + year;
                var timeStr = '🕒 ' + formattedHours + ':' + minutes + ' ' + ampm;
                if(dateEl.textContent !== dateStr) dateEl.textContent = dateStr;
                if(timeEl.textContent !== timeStr) timeEl.textContent = timeStr;
            }}
            updateClock();
            if(!window.__careerpilot_clock_timer){{
                window.__careerpilot_clock_timer = setInterval(updateClock, 1000);
            }}
        }})();
        ">
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <script>
        (function() {
            function updateClock() {
                try {
                    const doc = window.parent.document;
                    const dateEl = doc.getElementById("live-date-pill");
                    const timeEl = doc.getElementById("live-time-pill");
                    if (!dateEl || !timeEl) return;
                    const now = new Date();
                    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
                    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    const dayName = days[now.getDay()];
                    const monthName = months[now.getMonth()];
                    const dayNum = String(now.getDate()).padStart(2, '0');
                    const year = now.getFullYear();
                    let hours = now.getHours();
                    const minutes = String(now.getMinutes()).padStart(2, '0');
                    const ampm = hours >= 12 ? 'PM' : 'AM';
                    hours = hours % 12 || 12;
                    const formattedHours = String(hours).padStart(2, '0');
                    const dateStr = "📅 " + dayName + ", " + monthName + " " + dayNum + ", " + year;
                    const timeStr = "🕒 " + formattedHours + ":" + minutes + " " + ampm;
                    if (dateEl.textContent !== dateStr) dateEl.textContent = dateStr;
                    if (timeEl.textContent !== timeStr) timeEl.textContent = timeStr;
                } catch(e) {}
            }
            updateClock();
            setInterval(updateClock, 1000);
        })();
        </script>
        """,
        height=0,
    )


def render_sidebar():
    with st.sidebar:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown(
                "<div class='sidebar-title'>CareerPilot AI</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='sidebar-title'>Navigation</div>", unsafe_allow_html=True)
        sidebar_labels = list(SIDEBAR_ITEMS.keys())
        current_page = st.session_state.get("active_page", "Dashboard")
        last_active_page = st.session_state.get("_last_active_page", current_page)
        selected_index = 0
        if current_page in SIDEBAR_ITEMS.values():
            for index, label in enumerate(sidebar_labels):
                if SIDEBAR_ITEMS[label] == current_page:
                    selected_index = index
                    break

        sidebar_label_for_current_page = sidebar_labels[selected_index]
        if (
            "sidebar_radio" not in st.session_state
            or current_page != last_active_page
        ):
            st.session_state["sidebar_radio"] = sidebar_label_for_current_page

        selected_label = st.radio(
            "",
            sidebar_labels,
            key="sidebar_radio",
            label_visibility="collapsed",
        )
        page = SIDEBAR_ITEMS.get(selected_label, "Dashboard")
        st.session_state["active_page"] = page
        st.session_state["_last_active_page"] = page

        st.markdown("---")
        st.markdown(
            "<div class='sidebar-footer'>"
            "<strong>Phase 1 Ready</strong><br/>"
            "Premium UI scaffold and navigation live."
            "</div>",
            unsafe_allow_html=True,
        )
        return page


def render_home_page():
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-copy">
                <div class="eyebrow">Launch your job search with intelligence</div>
                <h2>Turn your resume into a confident career story.</h2>
                <p>Upload a resume, analyze your strengths, and prepare for interviews with a polished AI experience designed for modern professionals.</p>
            </div>
            <div class="hero-actions">
                <a class="btn-primary" href="#resume-upload">Upload Resume</a>
                <a class="btn-secondary" href="#insights">Explore Insights</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>Core Experience</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    cards = [
        ("Resume Analysis", "Get a clear snapshot of your current profile, strengths, and improvement areas.", "📄"),
        ("ATS Checker", "Measure how well your resume aligns with applicant tracking systems.", "✅"),
        ("Interview Coach", "Practice tailored questions and receive actionable feedback.", "🎤"),
    ]
    for col, (title, body, icon) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class='dashboard-card'>
                    <div class='card-icon'>{icon}</div>
                    <h4>{title}</h4>
                    <p>{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div id='resume-upload' class='section-title'>Upload Workspace</div>", unsafe_allow_html=True)
    upload_col, info_col = st.columns([1.2, 0.8])
    with upload_col:
        st.markdown(
            """
            <div class='upload-zone'>
                <div class='upload-icon'>⬆️</div>
                <h4>Drop your resume here</h4>
                <p>PDF, DOCX, and TXT files are supported.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                saved_path, safe_name = save_uploaded_resume(uploaded_file)
                extracted_text = extract_text_from_file(saved_path)
                parsed_resume = parse_resume(extracted_text)
                st.session_state["uploaded_resume"] = {
                    "name": uploaded_file.name,
                    "saved_path": saved_path,
                    "parsed": parsed_resume,
                    "text": extracted_text,
                }
                history_entry = build_history_entry(uploaded_file, parsed_resume, saved_path)
                save_history_entry(history_entry)
                st.session_state["history_entries"] = load_history_entries()
                st.session_state["analysis_done"] = True
                st.session_state["analysis_result"] = None
                st.success(f"Resume parsed successfully: {uploaded_file.name}")
            except Exception as exc:
                st.error(f"Unable to parse the selected file. {exc}")

    with info_col:
        st.markdown(
            """
            <div class='dashboard-card'>
                <h4>What happens next</h4>
                <p>Once uploaded, the platform will parse your details, score your resume, and prepare interview guidance.</p>
                <ul>
                    <li>Resume extraction</li>
                    <li>ATS compatibility review</li>
                    <li>Interview preparation</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.get("uploaded_resume"):
        parsed_resume = st.session_state["uploaded_resume"]["parsed"]
        st.markdown("<div class='section-title'>Parsed Resume Snapshot</div>", unsafe_allow_html=True)
        profile_col, details_col = st.columns([0.9, 1.1])
        with profile_col:
            st.markdown(
                f"""
                <div class='dashboard-card'>
                    <h4>{parsed_resume.get('name') or 'Resume Profile'}</h4>
                    <p><strong>Email:</strong> {parsed_resume.get('email') or 'Not detected'}</p>
                    <p><strong>Phone:</strong> {parsed_resume.get('phone') or 'Not detected'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with details_col:
            st.markdown(
                """
                <div class='dashboard-card'>
                    <h4>Structured Resume Highlights</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )
            tabs = st.tabs(["Skills", "Education", "Experience", "Projects", "Certifications"])
            tab_values = [
                parsed_resume.get("skills") or ["No skills detected"],
                parsed_resume.get("education") or ["No education detected"],
                parsed_resume.get("experience") or ["No experience detected"],
                parsed_resume.get("projects") or ["No projects detected"],
                parsed_resume.get("certifications") or ["No certifications detected"],
            ]
            for tab, values in zip(tabs, tab_values):
                with tab:
                    if isinstance(values, list):
                        for item in values:
                            st.write(f"- {item}")
                    else:
                        st.write(values)

        with st.expander("Preview extracted text", expanded=False):
            st.text_area(
                "Extracted content",
                value=st.session_state["uploaded_resume"].get("text", ""),
                height=220,
                label_visibility="collapsed",
            )

        is_disabled = st.session_state.get("is_analyzing", False)
        if st.button("Run AI Resume Analysis", use_container_width=True, disabled=is_disabled):
            execute_single_call_resume_analysis()

    if st.session_state.get("analysis_result"):
        analysis = st.session_state["analysis_result"]
        score = analysis.get("resume_score", analysis.get("overall_score", 0))
        exec_summary = analysis.get("executive_summary") or "The AI coach highlights strengths, weak points, and next-step recommendations for quick improvement."

        st.markdown("<div class='section-title'>AI Resume Analysis</div>", unsafe_allow_html=True)
        score_col, info_col = st.columns([0.5, 1.5])
        with score_col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Overall Resume Score</div>
                    <div class='metric-value'>{score}/100</div>
                    <div class='metric-foot'>AI-powered review</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with info_col:
            st.markdown(
                f"""
                <div class='dashboard-card'>
                    <h4>Executive Summary</h4>
                    <p>{exec_summary}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        sections = [
            ("Strengths", analysis.get("strengths", [])),
            ("Weaknesses", analysis.get("weaknesses", [])),
            ("Missing Sections", analysis.get("missing_sections", [])),
            ("Grammar Issues", analysis.get("grammar_issues", [])),
            ("Formatting Suggestions", analysis.get("formatting_suggestions", [])),
            ("Keyword Suggestions", analysis.get("keyword_suggestions", [])),
            ("Recommendations", analysis.get("recommendations", [])),
        ]
        for title, values in sections:
            if values:
                st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
                for item in values:
                    st.write(f"- {item}")

        st.markdown("<div class='section-title'>Narrative Review</div>", unsafe_allow_html=True)
        review_cols = st.columns(3)
        review_items = [
            ("Professional Summary Review", analysis.get("professional_summary_review", "")),
            ("Technical Skills Review", analysis.get("technical_skills_review", "")),
            ("Soft Skills Review", analysis.get("soft_skills_review", "")),
        ]
        for col, (title, text) in zip(review_cols, review_items):
            with col:
                st.markdown(
                    f"""
                    <div class='dashboard-card'>
                        <h4>{title}</h4>
                        <p>{text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if st.session_state.get("uploaded_resume"):
        st.markdown("<div class='section-title'>ATS Compatibility Checker</div>", unsafe_allow_html=True)
        with st.form("ats_form"):
            job_description = st.text_area("Paste a job description to compare your resume against", height=140)
            submitted = st.form_submit_button("Evaluate ATS Match")
        if submitted:
            ats_result = calculate_ats_score(st.session_state["uploaded_resume"]["parsed"], job_description)
            st.session_state["ats_result"] = ats_result
            # Persist the last-used job description so skill coverage can be calculated consistently
            st.session_state["job_description"] = job_description

        if st.session_state.get("ats_result"):
            ats_result = st.session_state["ats_result"]
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>ATS Compatibility Score</div>
                    <div class='metric-value'>{ats_result['overall_score']}/100</div>
                    <div class='metric-foot'>Keyword alignment and structure review</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            metrics = [
                ("Formatting", ats_result["formatting_score"]),
                ("Keywords", ats_result["keywords_score"]),
                ("Experience", ats_result["experience_score"]),
                ("Skills", ats_result["skills_score"]),
                ("Education", ats_result["education_score"]),
                ("Projects", ats_result["projects_score"]),
            ]
            for label, value in metrics:
                st.progress(value / 100, text=f"{label}: {value}/100")
            st.markdown("<div class='section-title'>ATS Suggestions</div>", unsafe_allow_html=True)
            for item in ats_result.get("suggestions", []):
                st.write(f"- {item}")
            if ats_result.get("keywords"):
                st.write("Matched keywords: " + ", ".join(ats_result["keywords"]))

    st.markdown("<div id='insights' class='section-title'>Performance Snapshot</div>", unsafe_allow_html=True)
    kpis = build_dashboard_kpis()
    metric_cols = st.columns(4)
    for col, metric in zip(metric_cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{metric['label']}</div>
                    <div class='metric-value'>{metric['value']}</div>
                    <div class='metric-foot'>{metric['foot']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_interview_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Interview Coach</h3>
            <p>Generate role-based questions, practice one at a time, and receive AI feedback on your response.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    role = st.selectbox(
        "Choose a job role",
        ["Python Developer", "AI Engineer", "Data Analyst", "Web Developer", "Digital Marketing", "Prompt Engineer"],
    )
    count = st.slider("How many questions?", 3, 10, 5)
    if st.button("Generate Interview Questions"):
        with st.spinner("Creating questions..."):
            questions = generate_interview_questions(role, count)
        st.session_state["interview_questions"] = questions
        st.session_state["interview_index"] = 0
        st.session_state["interview_feedbacks"] = [None] * len(questions)
        st.session_state["interview_answers"] = ["" for _ in questions]

    if st.session_state.get("interview_questions"):
        index = st.session_state.get("interview_index", 0)
        if index >= len(st.session_state["interview_questions"]):
            index = 0
            st.session_state["interview_index"] = 0

        current_question = st.session_state["interview_questions"][index]
        st.markdown(
            f"<div class='section-title'>Question {index + 1}/{len(st.session_state['interview_questions'])}</div>",
            unsafe_allow_html=True,
        )
        st.info(current_question)

        answer_key = f"interview_answer_{index}"
        default_answer = st.session_state["interview_answers"][index] if index < len(st.session_state["interview_answers"]) else ""
        answer = st.text_area("Your answer", value=default_answer, height=180, key=answer_key)
        if index < len(st.session_state["interview_answers"]):
            st.session_state["interview_answers"][index] = answer

        if st.button("Evaluate Answer") and answer.strip():
            with st.spinner("Evaluating response..."):
                feedback = evaluate_answer(role, current_question, answer)
            st.session_state["interview_feedbacks"][index] = feedback
            st.success("Feedback generated.")

        feedback = st.session_state["interview_feedbacks"][index]
        if feedback:
            st.markdown("<div class='section-title'>Feedback</div>", unsafe_allow_html=True)
            metric_cols = st.columns(3)
            metrics = [
                ("Confidence", feedback.get("confidence_score", 0)),
                ("Technical Accuracy", feedback.get("technical_accuracy", 0)),
                ("Communication", feedback.get("communication", 0)),
            ]
            for col, (label, value) in zip(metric_cols, metrics):
                with col:
                    st.metric(label, f"{value}/100")
            st.markdown("<div class='section-title'>Strengths</div>", unsafe_allow_html=True)
            for item in feedback.get("strengths", []):
                st.write(f"- {item}")
            st.markdown("<div class='section-title'>Weaknesses</div>", unsafe_allow_html=True)
            for item in feedback.get("weaknesses", []):
                st.write(f"- {item}")
            st.markdown("<div class='section-title'>Improved Answer</div>", unsafe_allow_html=True)
            st.text_area("Suggested answer", value=feedback.get("improved_answer", ""), height=140, label_visibility="collapsed")

        if index < len(st.session_state["interview_questions"]) - 1:
            if st.button("Next Question"):
                st.session_state["interview_index"] = index + 1
                st.rerun()


def render_career_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Career Development Suite</h3>
            <p>Identify missing skills, generate a plan, rewrite resume sections, and get coaching guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("uploaded_resume"):
        st.warning("Upload a resume first to personalize the career recommendations.")
        return

    role = st.selectbox("Target role", ["Python Developer", "AI Engineer", "Data Analyst", "Web Developer", "Digital Marketing", "Prompt Engineer"])
    if st.button("Generate Career Insights"):
        comp_data = st.session_state.get("comprehensive_analysis")
        if not comp_data:
            execute_single_call_resume_analysis(target_role=role)
        else:
            text = st.session_state["uploaded_resume"].get("text", "")
            st.session_state["skill_gap"] = generate_skill_gap_analysis(role, text, comp_data)
            st.session_state["roadmap"] = generate_roadmap(role, text, comp_data)
            st.session_state["linkedin"] = generate_linkedin_suggestions(text, comp_data)
            st.session_state["career_tips"] = generate_career_tips()
            # Update canonical skill coverage if a job description is present in session
            try:
                from utils import calculate_skill_coverage_from_session

                st.session_state["skill_coverage"] = calculate_skill_coverage_from_session()
            except Exception:
                st.session_state["skill_coverage"] = None
            st.success("Career guidance is ready.")

    if st.session_state.get("skill_gap"):
        gap = st.session_state["skill_gap"]
        st.markdown("<div class='section-title'>Skill Gap Analysis</div>", unsafe_allow_html=True)
        for title, values in [
            ("Missing Skills", gap.get("missing_skills", [])),
            ("Recommended Certifications", gap.get("recommended_certifications", [])),
            ("Recommended Projects", gap.get("recommended_projects", [])),
            ("Learning Priorities", gap.get("learning_priorities", [])),
        ]:
            st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
            for item in values:
                st.write(f"- {item}")

    if st.session_state.get("roadmap"):
        roadmap = st.session_state["roadmap"]
        st.markdown("<div class='section-title'>Career Roadmap</div>", unsafe_allow_html=True)
        tab_keys = ["30-Day Plan", "60-Day Plan", "90-Day Plan", "Weekly Goals", "Resources", "Projects"]
        tabs = st.tabs(tab_keys)
        values = [
            roadmap.get("thirty_day_plan", []),
            roadmap.get("sixty_day_plan", []),
            roadmap.get("ninety_day_plan", []),
            roadmap.get("weekly_goals", []),
            roadmap.get("resources", []),
            roadmap.get("projects", []),
        ]
        for tab, items in zip(tabs, values):
            with tab:
                for item in items:
                    st.write(f"- {item}")

    st.markdown("<div class='section-title'>Resume Rewriter</div>", unsafe_allow_html=True)
    section_name = st.selectbox("Select section", ["Professional Summary", "Experience", "Projects", "Skills"])
    section_content = st.text_area("Section content", height=140)
    if st.button("Rewrite Section") and section_content.strip():
        with st.spinner("Rewriting section..."):
            rewritten = rewrite_resume_section(section_name, section_content)
        st.session_state["rewritten_section"] = rewritten
    if st.session_state.get("rewritten_section"):
        st.text_area("Professional rewrite", value=st.session_state["rewritten_section"], height=160, label_visibility="collapsed")

    if st.session_state.get("linkedin"):
        linkedin = st.session_state["linkedin"]
        st.markdown("<div class='section-title'>LinkedIn Profile Suggestions</div>", unsafe_allow_html=True)
        st.write("Headline:", linkedin.get("headline", ""))
        st.write("About section:", linkedin.get("about_section", ""))
        st.write("Skills:", ", ".join(linkedin.get("skills", [])))
        for item in linkedin.get("suggestions", []):
            st.write(f"- {item}")

    if st.session_state.get("career_tips"):
        tips = st.session_state["career_tips"]
        st.markdown("<div class='section-title'>Career Coaching Tips</div>", unsafe_allow_html=True)
        for title, values in [
            ("Resume Tips", tips.get("resume_tips", [])),
            ("Interview Tips", tips.get("interview_tips", [])),
            ("Career Advice", tips.get("career_advice", [])),
            ("Salary Negotiation Tips", tips.get("salary_negotiation_tips", [])),
            ("LinkedIn Tips", tips.get("linkedin_tips", [])),
            ("Portfolio Suggestions", tips.get("portfolio_suggestions", [])),
        ]:
            st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
            for item in values:
                st.write(f"- {item}")


def render_resume_analysis_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Resume Analysis</h3>
            <p>Upload a resume to parse your profile and get AI-powered feedback.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("uploaded_resume"):
        st.warning("Upload a resume first to start analysis.")
        uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                saved_path, safe_name = save_uploaded_resume(uploaded_file)
                extracted_text = extract_text_from_file(saved_path)
                parsed_resume = parse_resume(extracted_text)
                st.session_state["uploaded_resume"] = {
                    "name": uploaded_file.name,
                    "saved_path": saved_path,
                    "parsed": parsed_resume,
                    "text": extracted_text,
                }
                history_entry = build_history_entry(uploaded_file, parsed_resume, saved_path)
                save_history_entry(history_entry)
                st.session_state["history_entries"] = load_history_entries()
                st.session_state["analysis_done"] = True
                st.session_state["analysis_result"] = None
                st.success(f"Resume parsed successfully: {uploaded_file.name}")
            except Exception as exc:
                st.error(f"Unable to parse the selected file. {exc}")
        return

    uploaded = st.session_state["uploaded_resume"]
    parsed_resume = uploaded["parsed"]

    st.markdown("<div class='section-title'>Parsed Resume Snapshot</div>", unsafe_allow_html=True)
    profile_col, details_col = st.columns([0.9, 1.1])
    with profile_col:
        st.markdown(
            f"""
            <div class='dashboard-card'>
                <h4>{parsed_resume.get('name') or 'Resume Profile'}</h4>
                <p><strong>Email:</strong> {parsed_resume.get('email') or 'Not detected'}</p>
                <p><strong>Phone:</strong> {parsed_resume.get('phone') or 'Not detected'}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with details_col:
        st.markdown(
            """
            <div class='dashboard-card'>
                <h4>Structured Resume Highlights</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tabs = st.tabs(["Skills", "Education", "Experience", "Projects", "Certifications"])
        tab_values = [
            parsed_resume.get("skills") or ["No skills detected"],
            parsed_resume.get("education") or ["No education detected"],
            parsed_resume.get("experience") or ["No experience detected"],
            parsed_resume.get("projects") or ["No projects detected"],
            parsed_resume.get("certifications") or ["No certifications detected"],
        ]
        for tab, values in zip(tabs, tab_values):
            with tab:
                if isinstance(values, list):
                    for item in values:
                        st.write(f"- {item}")
                else:
                    st.write(values)

    with st.expander("Preview extracted text", expanded=False):
        st.text_area("Extracted content", value=uploaded.get("text", ""), height=220, label_visibility="collapsed")

    is_disabled = st.session_state.get("is_analyzing", False)
    if st.button("Run AI Resume Analysis", use_container_width=True, disabled=is_disabled, key="btn_run_analysis_page"):
        execute_single_call_resume_analysis()

    if st.session_state.get("analysis_result"):
        analysis = st.session_state["analysis_result"]
        score = analysis.get("resume_score", analysis.get("overall_score", 0))
        exec_summary = analysis.get("executive_summary") or "The AI coach highlights strengths, weak points, and next-step recommendations for quick improvement."

        st.markdown("<div class='section-title'>AI Resume Analysis</div>", unsafe_allow_html=True)
        score_col, info_col = st.columns([0.5, 1.5])
        with score_col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>Overall Resume Score</div>
                    <div class='metric-value'>{score}/100</div>
                    <div class='metric-foot'>AI-powered review</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with info_col:
            st.markdown(
                f"""
                <div class='dashboard-card'>
                    <h4>Executive Summary</h4>
                    <p>{exec_summary}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        sections = [
            ("Strengths", analysis.get("strengths", [])),
            ("Weaknesses", analysis.get("weaknesses", [])),
            ("Missing Sections", analysis.get("missing_sections", [])),
            ("Grammar Issues", analysis.get("grammar_issues", [])),
            ("Formatting Suggestions", analysis.get("formatting_suggestions", [])),
            ("Keyword Suggestions", analysis.get("keyword_suggestions", [])),
            ("Recommendations", analysis.get("recommendations", [])),
        ]
        for title, values in sections:
            if values:
                st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
                for item in values:
                    st.write(f"- {item}")

        st.markdown("<div class='section-title'>Narrative Review</div>", unsafe_allow_html=True)
        review_cols = st.columns(3)
        review_items = [
            ("Professional Summary Review", analysis.get("professional_summary_review", "")),
            ("Technical Skills Review", analysis.get("technical_skills_review", "")),
            ("Soft Skills Review", analysis.get("soft_skills_review", "")),
        ]
        for col, (title, text) in zip(review_cols, review_items):
            with col:
                st.markdown(
                    f"""
                    <div class='dashboard-card'>
                        <h4>{title}</h4>
                        <p>{text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_ats_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>ATS Checker</h3>
            <p>Compare your resume against a job description and measure ATS compatibility.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("uploaded_resume"):
        st.warning("Upload a resume first to use the ATS Checker.")
        uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                saved_path, safe_name = save_uploaded_resume(uploaded_file)
                extracted_text = extract_text_from_file(saved_path)
                parsed_resume = parse_resume(extracted_text)
                st.session_state["uploaded_resume"] = {
                    "name": uploaded_file.name,
                    "saved_path": saved_path,
                    "parsed": parsed_resume,
                    "text": extracted_text,
                }
                history_entry = build_history_entry(uploaded_file, parsed_resume, saved_path)
                save_history_entry(history_entry)
                st.session_state["history_entries"] = load_history_entries()
                st.success(f"Resume parsed successfully: {uploaded_file.name}")
            except Exception as exc:
                st.error(f"Unable to parse the selected file. {exc}")
        return

    parsed_resume = st.session_state["uploaded_resume"]["parsed"]
    job_description = st.text_area("Paste a job description to compare your resume against", height=180)
    if st.button("Evaluate ATS Match"):
        st.session_state["ats_result"] = calculate_ats_score(parsed_resume, job_description)
        save_current_analysis_history(summary="ATS analysis completed.", job_description=job_description)

    if st.session_state.get("ats_result"):
        ats_result = st.session_state["ats_result"]
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>ATS Compatibility Score</div>
                <div class='metric-value'>{ats_result['overall_score']}/100</div>
                <div class='metric-foot'>Keyword alignment and structure review</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        metrics = [
            ("Formatting", ats_result["formatting_score"]),
            ("Keywords", ats_result["keywords_score"]),
            ("Experience", ats_result["experience_score"]),
            ("Skills", ats_result["skills_score"]),
            ("Education", ats_result["education_score"]),
            ("Projects", ats_result["projects_score"]),
        ]
        for label, value in metrics:
            st.progress(value / 100, text=f"{label}: {value}/100")
        st.markdown("<div class='section-title'>ATS Suggestions</div>", unsafe_allow_html=True)
        for item in ats_result.get("suggestions", []):
            st.write(f"- {item}")
        if ats_result.get("keywords"):
            st.write("Matched keywords: " + ", ".join(ats_result["keywords"]))


def render_job_matcher_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Job Matcher</h3>
            <p>See how well your resume matches a job description and where the gaps are.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("uploaded_resume"):
        st.warning("Upload a resume first to use the Job Matcher.")
        uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                saved_path, safe_name = save_uploaded_resume(uploaded_file)
                extracted_text = extract_text_from_file(saved_path)
                parsed_resume = parse_resume(extracted_text)
                st.session_state["uploaded_resume"] = {
                    "name": uploaded_file.name,
                    "saved_path": saved_path,
                    "parsed": parsed_resume,
                    "text": extracted_text,
                }
                history_entry = build_history_entry(uploaded_file, parsed_resume, saved_path)
                save_history_entry(history_entry)
                st.session_state["history_entries"] = load_history_entries()
                st.success(f"Resume parsed successfully: {uploaded_file.name}")
            except Exception as exc:
                st.error(f"Unable to parse the selected file. {exc}")
        return

    parsed_resume = st.session_state["uploaded_resume"]["parsed"]
    role = st.selectbox(
        "Target role",
        ["Python Developer", "AI Engineer", "Data Analyst", "Web Developer", "Digital Marketing", "Prompt Engineer"],
        key="job_match_role",
    )
    job_description = st.text_area("Paste a job description to compare against", height=180, key="job_match_description")
    if st.button("Evaluate Job Match", key="btn_job_match"):
        if not job_description.strip():
            st.warning("Please paste a job description before evaluating.")
        else:
            result = calculate_job_match(parsed_resume, job_description, target_role=role)
            st.session_state["job_match_result"] = result
            # Persist job description and canonical skill coverage for other pages
            st.session_state["job_description"] = job_description
            try:
                st.session_state["skill_coverage"] = int(result.get("skill_coverage") if result.get("skill_coverage") is not None else None)
            except Exception:
                st.session_state["skill_coverage"] = None
            save_current_analysis_history(summary="Job match evaluation completed.", job_description=job_description)

    job_description_text = st.session_state.get("job_description", "") or job_description
    if not job_description_text.strip() and not st.session_state.get("job_match_result"):
        st.info("Add a job description to compare your resume with the target role.")

    if st.session_state.get("job_match_result"):
        result = st.session_state["job_match_result"]
        st.markdown("<div class='section-title'>Job Match Score</div>", unsafe_allow_html=True)
        top_score = result.get('score')
        if isinstance(top_score, int):
            st.metric("Score", f"{top_score}/100")
        else:
            st.metric("Score", "N/A")

        # Score breakdown card
        breakdown = result.get("score_breakdown", {})
        st.markdown("<div class='section-title'>Score Breakdown</div>", unsafe_allow_html=True)
        bcols = st.columns([1, 1, 1, 0.8])
        with bcols[0]:
            val = breakdown.get("required_match")
            st.write("**Required Skills Match**")
            st.write(f"{val if val is not None else 'N/A'}%")
        with bcols[1]:
            val = breakdown.get("preferred_match")
            st.write("**Preferred Skills Match**")
            st.write(f"{val if val is not None else 'N/A'}%")
        with bcols[2]:
            val = breakdown.get("experience_alignment")
            st.write("**Experience Alignment**")
            st.write(f"{val if val is not None else 'N/A'}%")
        with bcols[3]:
            st.write("**Overall**")
            overall_val = breakdown.get('overall')
            if isinstance(overall_val, int):
                st.write(f"{overall_val}/100")
            else:
                st.write("N/A")

        # Main sections: Matching / Missing / Preferred
        st.markdown("<div class='section-title'>Skills Overview</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        with cols[0]:
            st.write("**Matching Skills**")
            for item in result.get("matching_skills", []):
                st.write(f"- {item}")
        with cols[1]:
            st.write("**Missing Skills (prioritized)**")
            ms = result.get("missing_skills_detailed") or []
            if ms:
                for item in ms:
                    st.markdown(f"- **{item['skill']}** — Priority: {item['priority']}\n  - {item['reason']}")
            else:
                st.write("No missing required skills detected.")
        with cols[2]:
            st.write("**Preferred Skills**")
            if result.get("preferred_skills"):
                for item in result.get("preferred_skills", []):
                    st.write(f"- {item}")
            else:
                st.write("None")

        # Partial matches
        if result.get("partial_matches"):
            st.markdown("<div class='section-title'>Partial Matches</div>", unsafe_allow_html=True)
            for item in result.get("partial_matches", []):
                st.write(f"- {item}")

        # Experience Gap human readable
        st.markdown("<div class='section-title'>Experience Gap</div>", unsafe_allow_html=True)
        exp = result.get("experience_gap")
        if isinstance(exp, dict):
            if exp.get("job_required_years") and exp.get("resume_years") is not None:
                st.write(f"Job requires ~{exp['job_required_years']} years; resume shows ~{exp['resume_years']} years ({exp.get('alignment_pct', 'N/A')}% alignment).")
            elif exp.get("job_required_years") and not exp.get("resume_years"):
                st.write("Job includes a years-of-experience requirement but your resume does not list explicit years. Cannot calculate alignment.")
            else:
                st.write("No explicit years-of-experience requirement found in the job description.")
        else:
            st.write(exp or "No experience data available.")

        # Why this score
        st.markdown("<div class='section-title'>Why This Score?</div>", unsafe_allow_html=True)
        st.write(result.get("why_score", ""))

        # Recommended learning path
        st.markdown("<div class='section-title'>Recommended Skill Path</div>", unsafe_allow_html=True)
        path = result.get("recommended_path", [])
        if path:
            for idx, step in enumerate(path, start=1):
                st.markdown(f"**{idx}. {step['skill']}**")
                st.write(f"- Why: {step['why']}")
                st.write(f"- Suggested focus: {step['focus']}")
                st.write(f"- Estimated difficulty: {step['difficulty']}")
        else:
            st.write("No recommended path available.")

        # Action buttons to connect to Skill Gap and Roadmap
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("View My Skill Gap →", key="btn_view_skill_gap"):
                # populate skill gap using current analysis and navigate
                try:
                    st.session_state["skill_gap"] = generate_skill_gap_analysis(role, st.session_state["uploaded_resume"]["text"], result)
                except Exception:
                    st.session_state["skill_gap"] = generate_skill_gap_analysis(role, st.session_state["uploaded_resume"]["text"], None)
                st.session_state["active_page"] = "Skill Gap"
                st.rerun()
        with action_cols[1]:
            if st.button("Build My Career Roadmap →", key="btn_build_roadmap"):
                try:
                    st.session_state["roadmap"] = generate_roadmap(role, st.session_state["uploaded_resume"]["text"], result)
                except Exception:
                    st.session_state["roadmap"] = generate_roadmap(role, st.session_state["uploaded_resume"]["text"], None)
                st.session_state["active_page"] = "Career Roadmap"
                st.rerun()


def submit_ai_assistant():
    prompt = st.session_state.get("assistant_prompt", "").strip()
    if not prompt:
        st.session_state["assistant_error"] = "Enter a question before sending it to the AI assistant."
        return

    response = safe_ai_call(
        "AI Assistant",
        prompt,
        system_prompt="You are a helpful career assistant who provides resume tips, interview guidance, and job search advice.",
    )
    messages = st.session_state.get("assistant_messages", [])
    messages.append({"role": "user", "text": prompt})
    messages.append({"role": "assistant", "text": response})
    st.session_state["assistant_messages"] = messages
    st.session_state["assistant_prompt"] = ""
    st.session_state["assistant_error"] = ""


def render_ai_assistant_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>AI Career Assistant</h3>
            <p>Ask an AI assistant for help with resume wording, career advice, interview preparation, and job strategy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("groq_online"):
        st.warning("Groq AI is not connected. Please check your API key in Settings.")

    st.text_area("Ask a question", value=st.session_state.get("assistant_prompt", ""), height=160, key="assistant_prompt")
    st.button("Send to AI", key="btn_ai_assistant", on_click=submit_ai_assistant)

    if st.session_state.get("assistant_error"):
        st.warning(st.session_state.get("assistant_error"))

    if st.session_state.get("assistant_messages"):
        st.markdown("<div class='section-title'>Conversation</div>", unsafe_allow_html=True)
        for message in st.session_state["assistant_messages"]:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['text']}")
            else:
                st.markdown(f"**Assistant:** {message['text']}")


def render_career_analytics_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Career Analytics</h3>
            <p>Track your resume, ATS, job match, and interview readiness with analytics dashboards.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history_entries = st.session_state.get("history_entries") or load_history_entries()
    if not history_entries:
        st.info("Complete more analyses to see your progress.")
        return

    latest = history_entries[0]
    resume_score = latest.get("resume_score")
    ats_score = latest.get("ats_score")
    job_match_score = latest.get("job_match_score")
    job_description = latest.get("job_description", "")
    skill_coverage = latest.get("skill_coverage", 0) or 0
    interview_readiness = latest.get("interview_readiness", 0) or 0

    kpis = [
        {"label": "Resume Score", "value": f"{resume_score}/100" if resume_score is not None else "N/A", "foot": "Latest resume analysis"},
        {"label": "ATS Score", "value": f"{ats_score}/100" if ats_score is not None else "N/A", "foot": "Latest ATS analysis"},
        {"label": "Job Match Score", "value": f"{job_match_score}/100" if job_description and job_match_score is not None else "N/A", "foot": "Latest job match evaluation"},
        {"label": "Skill Coverage", "value": f"{skill_coverage}%" if job_description else "N/A", "foot": "Required skills matched"},
    ]

    cols = st.columns(4)
    for col, metric in zip(cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{metric['label']}</div>
                    <div class='metric-value'>{metric['value']}</div>
                    <div class='metric-foot'>{metric['foot']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    records = [
        {
            "analysis": f"Analysis {idx + 1}",
            "resume_score": entry.get("resume_score", 0) if entry.get("resume_score") is not None else 0,
            "ats_score": entry.get("ats_score", 0) if entry.get("ats_score") is not None else 0,
            "job_match_score": entry.get("job_match_score", 0) if entry.get("job_description") else None,
            "skill_coverage": entry.get("skill_coverage", 0) if entry.get("job_description") else None,
            "interview_readiness": entry.get("interview_readiness", 0),
        }
        for idx, entry in enumerate(reversed(history_entries))
    ]

    df = pd.DataFrame(records)
    if df.empty:
        st.info("Complete more analyses to see your progress.")
        return

    if "job_match_score" in df.columns:
        df["job_match_score"] = df["job_match_score"].fillna(0).astype(int)
    df["resume_score"] = df["resume_score"].fillna(0).astype(int)
    df["ats_score"] = df["ats_score"].fillna(0).astype(int)
    df["skill_coverage"] = df["skill_coverage"].fillna(0).astype(int)
    df["interview_readiness"] = df["interview_readiness"].fillna(0).astype(int)

    st.markdown("<div class='section-title'>Resume vs ATS Score Trend</div>", unsafe_allow_html=True)
    st.line_chart(df.set_index("analysis")[ ["resume_score", "ats_score", "job_match_score"] ])

    st.markdown("<div class='section-title'>Readiness Snapshot</div>", unsafe_allow_html=True)
    snapshot_df = df.tail(1).set_index("analysis")[ ["resume_score", "ats_score", "job_match_score", "skill_coverage", "interview_readiness"] ]
    st.bar_chart(snapshot_df.T)


def render_skill_gap_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Skill Gap</h3>
            <p>Identify missing skills and receive personalized learning recommendations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("uploaded_resume"):
        st.warning("Upload a resume first to run Skill Gap analysis.")
        uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                saved_path, safe_name = save_uploaded_resume(uploaded_file)
                extracted_text = extract_text_from_file(saved_path)
                parsed_resume = parse_resume(extracted_text)
                st.session_state["uploaded_resume"] = {
                    "name": uploaded_file.name,
                    "saved_path": saved_path,
                    "parsed": parsed_resume,
                    "text": extracted_text,
                }
                history_entry = build_history_entry(uploaded_file, parsed_resume, saved_path)
                save_history_entry(history_entry)
                st.session_state["history_entries"] = load_history_entries()
                st.success(f"Resume parsed successfully: {uploaded_file.name}")
            except Exception as exc:
                st.error(f"Unable to parse the selected file. {exc}")
        return

    role = st.selectbox("Target role", ["Python Developer", "AI Engineer", "Data Analyst", "Web Developer", "Digital Marketing", "Prompt Engineer"])
    if st.button("Generate Skill Gap Analysis"):
        comp_data = st.session_state.get("comprehensive_analysis")
        if not comp_data:
            execute_single_call_resume_analysis(target_role=role)
        else:
            text = st.session_state["uploaded_resume"]["text"]
            st.session_state["skill_gap"] = generate_skill_gap_analysis(role, text, comp_data)
            st.session_state["roadmap"] = generate_roadmap(role, text, comp_data)
            st.session_state["linkedin"] = generate_linkedin_suggestions(text, comp_data)
            st.success("Skill Gap analysis complete.")

    if st.session_state.get("skill_gap"):
        gap = st.session_state["skill_gap"]
        st.markdown("<div class='section-title'>Skill Gap Analysis</div>", unsafe_allow_html=True)
        for title, values in [
            ("Missing Skills", gap.get("missing_skills", [])),
            ("Recommended Certifications", gap.get("recommended_certifications", [])),
            ("Recommended Projects", gap.get("recommended_projects", [])),
            ("Learning Priorities", gap.get("learning_priorities", [])),
        ]:
            st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
            for item in values:
                st.write(f"- {item}")

    if st.session_state.get("roadmap"):
        roadmap = st.session_state["roadmap"]
        st.markdown("<div class='section-title'>Career Roadmap</div>", unsafe_allow_html=True)
        tab_keys = ["30-Day Plan", "60-Day Plan", "90-Day Plan", "Weekly Goals", "Resources", "Projects"]
        tabs = st.tabs(tab_keys)
        values = [
            roadmap.get("thirty_day_plan", []),
            roadmap.get("sixty_day_plan", []),
            roadmap.get("ninety_day_plan", []),
            roadmap.get("weekly_goals", []),
            roadmap.get("resources", []),
            roadmap.get("projects", []),
        ]
        for tab, items in zip(tabs, values):
            with tab:
                for item in items:
                    st.write(f"- {item}")

    if st.session_state.get("linkedin"):
        linkedin = st.session_state["linkedin"]
        st.markdown("<div class='section-title'>LinkedIn Suggestions</div>", unsafe_allow_html=True)
        st.write("Headline:", linkedin.get("headline", ""))
        st.write("About section:", linkedin.get("about_section", ""))
        st.write("Skills:", ", ".join(linkedin.get("skills", [])))
        for item in linkedin.get("suggestions", []):
            st.write(f"- {item}")


def render_history_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>History</h3>
            <p>Review your past resume uploads and AI session history.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history_entries = st.session_state.get("history_entries") or load_history_entries()
    if not history_entries:
        st.info("No history found. Upload and analyze a resume to build your history.")
        return

    for entry in history_entries:
        st.markdown(f"### {entry.get('file_name', 'Resume')}")
        st.write(f"Uploaded: {entry.get('uploaded_at', 'Unknown')}")
        st.write(f"Target role: {entry.get('target_role', 'Not specified')}")
        st.write(f"Resume score: {entry.get('resume_score', 'N/A')}")
        st.markdown("---")


def render_settings_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>Settings</h3>
            <p>Manage your AI model and Groq connection status.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='section-title'>Configuration</div>", unsafe_allow_html=True)
    st.write("Current AI model:", os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"))
    connection_status = get_connection_status()
    st.write("Groq connection:", connection_status)
    st.write("Status details:", st.session_state.get("groq_status_message", "No status available."))
    if st.session_state.get("groq_online", False):
        st.success("Groq API key is configured and the connection is healthy.")
    else:
        st.warning("Groq connection is offline or requires attention.")
        st.code("GROQ_API_KEY=your_groq_api_key_here\nMODEL_NAME=llama-3.3-70b-versatile")
        st.info("Ensure GROQ_API_KEY is present in your .env file and restart the app.")


def render_about_page():
    st.markdown(
        """
        <div class='dashboard-card'>
            <h3>About CareerPilot AI</h3>
            <p>CareerPilot AI helps you build a better resume, prepare for interviews, and understand your career gaps using Groq AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='section-title'>What it does</div>", unsafe_allow_html=True)
    st.write("- Parse resumes from PDF, DOCX, or TXT files")
    st.write("- Analyze resume quality and provide AI feedback")
    st.write("- Check ATS compatibility against job descriptions")
    st.write("- Identify skill gaps and career roadmap suggestions")
    st.write("- Practice interview questions and get answer feedback")
    st.write("- Save history and export analysis reports")
    st.markdown("<div class='section-title'>How to use</div>", unsafe_allow_html=True)
    st.write("1. Upload your resume.")
    st.write("2. Run resume analysis and ATS checks.")
    st.write("3. Generate skill gap and career recommendations.")
    st.write("4. Use Settings to verify Groq connection.")


def initialize_groq_status() -> None:
    groq_client = get_groq_client_module()
    online, status = groq_client.check_groq_connection()
    st.session_state["groq_status_checked"] = True
    st.session_state["groq_online"] = online
    st.session_state["groq_status_label"] = status
    st.session_state["groq_status_message"] = status


def main():
    initialize_groq_status()
    render_header()
    page = render_sidebar()

    if page == "Dashboard":
        render_home_page()
    elif page == "Resume Analysis":
        render_resume_analysis_page()
    elif page == "ATS Checker":
        render_ats_page()
    elif page == "Job Matcher":
        render_job_matcher_page()
    elif page == "Interview Coach":
        render_interview_page()
    elif page == "AI Assistant":
        render_ai_assistant_page()
    elif page == "Skill Gap":
        render_skill_gap_page()
    elif page == "Career Analytics":
        render_career_analytics_page()
    elif page == "Career Roadmap":
        render_career_page()
    elif page == "History":
        render_history_page()
    elif page == "Settings":
        render_settings_page()
    elif page == "About":
        render_about_page()
    else:
        st.warning(f"The page '{page}' is not implemented yet. Please select a different tab.")


if __name__ == "__main__":
    main()
