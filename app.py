from __future__ import annotations

from io import BytesIO
from pathlib import Path
import json

import streamlit as st

from assessment_engine import (
    build_question,
    build_report_payload,
    extract_skills,
    extract_text_from_pdf,
    payload_to_json,
    render_report_markdown,
    score_answer,
)

# Groq integration - will handle API key loading
try:
    from groq_integration import (
        generate_dynamic_question,
        evaluate_answer_with_groq,
        explain_why_question,
    )
    GROQ_AVAILABLE = True
except ValueError as e:
    # API key not configured yet
    GROQ_AVAILABLE = False
    GROQ_ERROR = str(e)


APP_DIR = Path(__file__).parent
DEFAULT_RESUME = APP_DIR / "Vipin Tomer Resume.pdf"
DEFAULT_JD = APP_DIR / "sample_inputs" / "sample_job_description.txt"


st.set_page_config(
    page_title="AI Skill Assessment Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_resume(uploaded_file) -> tuple[str, str]:
    if uploaded_file is not None:
        data = BytesIO(uploaded_file.getvalue())
        temp_path = APP_DIR / ".uploaded_resume.pdf"
        temp_path.write_bytes(data.getvalue())
        text = extract_text_from_pdf(temp_path)
        temp_path.unlink(missing_ok=True)
        return uploaded_file.name, text
    if DEFAULT_RESUME.exists():
        return DEFAULT_RESUME.name, extract_text_from_pdf(DEFAULT_RESUME)
    return "No resume loaded", ""


def initialize_session(jd_text: str, resume_name: str, resume_text: str) -> None:
    required_skills = extract_skills(jd_text, limit=8)
    if not required_skills:
        required_skills = ["Python", "Machine Learning", "Deep Learning"]
    st.session_state.assessment = {
        "job_description": jd_text,
        "resume_name": resume_name,
        "resume_text": resume_text,
        "required_skills": required_skills,
        "current_index": 0,
        "answers": [],
        "history": [],
        "started": True,
    }


def current_state():
    return st.session_state.get("assessment", {})


def reset_assessment_state() -> None:
    st.session_state.assessment = {
        "job_description": "",
        "resume_name": "",
        "resume_text": "",
        "required_skills": [],
        "current_index": 0,
        "answers": [],
        "history": [],
        "started": False,
    }


def inject_modern_css() -> None:
    """Inject modern glassmorphism CSS with animations and styling."""
    st.markdown(
        """
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* === MAIN APP BACKGROUND === */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        }
        
        /* === GLASSMORPHISM CARDS === */
        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }
        
        /* === HERO SECTION === */
        .hero-section {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 24px;
            padding: 48px 32px;
            margin-bottom: 32px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.1);
        }
        
        .hero-section h1 {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
            animation: fadeInDown 0.8s ease;
        }
        
        .hero-section p {
            font-size: 1.1rem;
            color: #cbd5e1;
            max-width: 600px;
            margin: 0 auto;
            animation: fadeInUp 0.8s ease 0.2s both;
        }
        
        /* === SKILL TAGS/BADGES === */
        .skill-badge {
            display: inline-block;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
            border: 1px solid rgba(168, 85, 247, 0.5);
            color: #a78bfa;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 4px;
            transition: all 0.2s ease;
        }
        
        .skill-badge:hover {
            transform: scale(1.05);
            border-color: rgba(168, 85, 247, 1);
        }
        
        /* === METRIC CARDS === */
        .metric-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            background: rgba(99, 102, 241, 0.15);
            border-color: rgba(99, 102, 241, 0.5);
            transform: translateY(-4px);
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* === CHAT INTERFACE === */
        .chat-message {
            margin-bottom: 16px;
            animation: slideIn 0.3s ease;
        }
        
        .chat-message.ai {
            background: rgba(99, 102, 241, 0.12);
            border-left: 3px solid #6366f1;
        }
        
        .chat-message.user {
            background: rgba(168, 85, 247, 0.12);
            border-left: 3px solid #a855f7;
        }
        
        .chat-message {
            padding: 16px;
            border-radius: 12px;
            color: #e2e8f0;
        }
        
        .chat-skill-badge {
            display: inline-block;
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.3), rgba(59, 130, 246, 0.3));
            color: #86efac;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 8px;
        }
        
        /* === PROGRESS TRACKER === */
        .progress-tracker {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        
        .progress-step {
            flex: 1;
            min-width: 80px;
            text-align: center;
        }
        
        .progress-circle {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin: 0 auto 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            border: 2px solid rgba(99, 102, 241, 0.3);
        }
        
        .progress-circle.active {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            border-color: #a855f7;
            box-shadow: 0 0 20px rgba(166, 85, 247, 0.4);
        }
        
        .progress-circle.completed {
            background: linear-gradient(135deg, #34d399, #10b981);
            border-color: #10b981;
        }
        
        .progress-circle.pending {
            background: rgba(255, 255, 255, 0.05);
            color: #64748b;
        }
        
        .progress-label {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 6px;
        }
        
        /* === CIRCULAR PROGRESS === */
        .circular-progress {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            position: relative;
            width: 140px;
            height: 140px;
            margin: 20px auto;
        }
        
        .circle-background {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(
                from 0deg,
                #6366f1 0deg,
                #a855f7 180deg,
                rgba(99, 102, 241, 0.2) 180deg
            );
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.3);
        }
        
        .circle-inner {
            width: 90%;
            height: 90%;
            border-radius: 50%;
            background: #1e293b;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .circle-score {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .circle-label {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* === LEARNING PLAN TIMELINE === */
        .timeline-item {
            position: relative;
            padding-left: 40px;
            margin-bottom: 24px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            border: 2px solid rgba(99, 102, 241, 0.5);
        }
        
        .timeline-item::after {
            content: '';
            position: absolute;
            left: 9px;
            top: 20px;
            width: 2px;
            height: calc(100% + 4px);
            background: rgba(99, 102, 241, 0.2);
        }
        
        .timeline-item:last-child::after {
            display: none;
        }
        
        .timeline-content {
            background: rgba(99, 102, 241, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 16px;
            transition: all 0.3s ease;
        }
        
        .timeline-content:hover {
            border-color: rgba(168, 85, 247, 0.5);
            background: rgba(168, 85, 247, 0.12);
        }
        
        /* === BUTTONS === */
        .stButton button {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        }
        
        /* === ANIMATIONS === */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
        
        .typing-indicator {
            display: flex;
            gap: 4px;
            align-items: center;
            margin-top: 8px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #a78bfa;
            animation: pulse 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        /* === SIDEBAR STYLING === */
        .sidebar-title {
            font-size: 1.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 16px;
        }
        
        .upload-area {
            border: 2px dashed rgba(99, 102, 241, 0.4);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            background: rgba(99, 102, 241, 0.05);
        }
        
        .upload-area:hover {
            border-color: rgba(168, 85, 247, 0.6);
            background: rgba(168, 85, 247, 0.1);
        }
        
        /* === TEXT STYLES === */
        h1, h2, h3 {
            color: #e2e8f0;
        }
        
        p, span, label, div {
            color: #cbd5e1;
        }
        
        .stTextArea textarea {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #e2e8f0;
            border-radius: 12px;
        }
        
        .stTextArea textarea:focus {
            border-color: rgba(168, 85, 247, 0.6);
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.1);
        }
        
        .stFileUploader {
            color: #cbd5e1;
        }
        
        /* === TABS === */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
            border-color: rgba(168, 85, 247, 0.6);
        }
        
        /* === EXPANDER === */
        .stExpander {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
        }

        .tracker-header {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(168, 85, 247, 0.12));
            border: 1px solid rgba(99, 102, 241, 0.22);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.22);
            margin-bottom: 1rem;
        }

        .tracker-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f8fafc;
        }

        .tracker-subtitle {
            color: #cbd5e1;
            font-size: 0.92rem;
            margin-top: 0.25rem;
        }

        .status-chip {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .status-chip.completed {
            background: rgba(34, 197, 94, 0.18);
            color: #86efac;
            border: 1px solid rgba(34, 197, 94, 0.32);
        }

        .status-chip.progress {
            background: rgba(251, 191, 36, 0.18);
            color: #fde68a;
            border: 1px solid rgba(251, 191, 36, 0.34);
        }

        .status-chip.pending {
            background: rgba(148, 163, 184, 0.12);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.22);
        }
        
        .streamlit-expanderHeader {
            color: #e2e8f0;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, str, str]:
    """Render modern sidebar with resume upload and JD input."""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">📋 Assessment Setup</div>', unsafe_allow_html=True)
        st.caption("Configure your assessment by uploading a resume and pasting a job description.")
        
        st.markdown("---")
        
        # Resume Upload Section
        st.markdown("### 📄 Resume Upload")
        st.markdown(
            '<div class="upload-area">Drag & drop your PDF or click to browse</div>',
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader("Resume PDF", type=["pdf"], label_visibility="collapsed")
        
        st.markdown("---")
        
        # Job Description Section
        st.markdown("### 💼 Job Description")
        jd_placeholder = load_text_file(DEFAULT_JD) or "Paste the role description here. Include required skills, responsibilities, and qualifications."
        jd_text = st.text_area(
            "JD Input",
            value=jd_placeholder,
            height=220,
            label_visibility="collapsed",
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Load Sample", use_container_width=True):
                jd_text = load_text_file(DEFAULT_JD)
                st.session_state.sample_jd = jd_text
                st.rerun()
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                reset_assessment_state()
                st.rerun()
        
        st.markdown("---")
        
        # Detected Skills
        if jd_text:
            detected = extract_skills(jd_text, limit=8)
            if detected:
                st.markdown("### 🎯 Detected Skills")
                st.markdown(" ".join([f'<span class="skill-badge">{s}</span>' for s in detected]), unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("💡 Tip: Use the sample data to test the assessment before adding your own resume.")
    
    resume_name, resume_text = load_resume(uploaded)
    if st.session_state.get("sample_jd"):
        jd_text = st.session_state.sample_jd
    return jd_text, resume_name, resume_text


def render_skill_progress(skills: list[str], current_index: int, answers: list) -> None:
    """Render a native Streamlit skill tracker with cards and progress bars."""
    total_skills = max(len(skills), 1)
    completed_count = min(current_index, len(skills))
    current_step = min(current_index + 1, total_skills)
    overall_progress = completed_count / total_skills

    st.markdown('<div class="tracker-header">', unsafe_allow_html=True)
    top_left, top_right = st.columns([3, 1])

    with top_left:
        st.markdown('<div class="tracker-title">📊 Assessment Progress</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="tracker-subtitle">Current step: Skill {current_step} of {total_skills}</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        st.metric("Progress", f"{int(overall_progress * 100)}%")

    st.progress(overall_progress)
    st.markdown('</div>', unsafe_allow_html=True)

    legend_left, legend_middle, legend_right = st.columns(3)
    with legend_left:
        st.markdown('<span class="status-chip completed">✅ Completed</span>', unsafe_allow_html=True)
    with legend_middle:
        st.markdown('<span class="status-chip progress">⏳ In Progress</span>', unsafe_allow_html=True)
    with legend_right:
        st.markdown('<span class="status-chip pending">🔒 Pending</span>', unsafe_allow_html=True)

    st.markdown("")

    left_col, right_col = st.columns(2)
    for i, skill in enumerate(skills):
        is_completed = i < current_index
        is_current = i == current_index and current_index < len(skills)
        status_text = "✅ Completed" if is_completed else "⏳ In Progress" if is_current else "🔒 Pending"
        status_class = "completed" if is_completed else "progress" if is_current else "pending"
        progress_value = 1.0 if is_completed else 0.6 if is_current else 0.08
        target_col = left_col if i % 2 == 0 else right_col

        with target_col:
            with st.container(border=True):
                if is_current:
                    st.markdown(f"**▶ Current skill: {skill}**")
                else:
                    st.markdown(f"**{skill}**")
                st.markdown(
                    f'<span class="status-chip {status_class}">{status_text}</span>',
                    unsafe_allow_html=True,
                )
                st.progress(progress_value)
                if is_current:
                    st.caption("Highlighting the skill currently being assessed.")
                elif is_completed:
                    st.caption("Assessment complete for this skill.")
                else:
                    st.caption("Coming up next in the assessment flow.")


def render_history(history: list[dict[str, str]]) -> None:
    """Render chat history with modern styling."""
    for message in history:
        role = message["role"]
        content = message["content"]
        
        if role == "assistant":
            st.markdown(
                f'<div class="chat-message ai"><strong>🤖 Assessment:</strong> {content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-message user"><strong>📝 Your Answer:</strong> {content}</div>',
                unsafe_allow_html=True,
            )


def render_typing_indicator() -> None:
    """Render typing indicator animation."""
    st.markdown(
        '''
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def render_circular_progress(score: float, level: str) -> None:
    """Render circular progress indicator for score."""
    progress_color = {
        "Strong": "#22c55e",
        "Working": "#eab308",
        "Developing": "#f97316",
        "Early": "#ef4444"
    }.get(level, "#6366f1")
    
    html = f'''
    <div class="circular-progress">
        <div class="circle-background" style="background: conic-gradient(from 0deg, {progress_color} 0deg, {progress_color} {score}%, rgba(99, 102, 241, 0.2) {score}%);">
            <div class="circle-inner">
                <div class="circle-score">{int(score)}</div>
                <div class="circle-label">points</div>
            </div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def get_score_level(score: float) -> tuple[str, str]:
    """Get score level and emoji."""
    if score >= 85:
        return "Strong", "🟢"
    elif score >= 70:
        return "Working", "🟡"
    elif score >= 50:
        return "Developing", "🟠"
    else:
        return "Early", "🔴"


def render_score_feedback(skill: str, result: dict) -> None:
    """Render score feedback with circular progress."""
    score = result["score"]
    level, emoji = get_score_level(score)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Circular progress
        progress_color = {
            "Strong": "#22c55e",
            "Working": "#eab308",
            "Developing": "#f97316",
            "Early": "#ef4444"
        }[level]
        
        html = f'''
        <div class="circular-progress">
            <div class="circle-background" style="background: conic-gradient(from 0deg, {progress_color} 0deg, {progress_color} {score}%, rgba(99, 102, 241, 0.2) {score}%);">
                <div class="circle-inner">
                    <div class="circle-score">{int(score)}</div>
                    <div class="circle-label">points</div>
                </div>
            </div>
        </div>
        '''
        st.markdown(html, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {emoji} {level}")
        st.markdown(f"**Skill:** {skill}")
        st.markdown(f"**Score:** {int(score)}/100")
        st.markdown(f"**Feedback:** {result['rationale']}")
        
        if result.get('resume_hits'):
            st.markdown(f"**Resume Evidence:** {', '.join(result['resume_hits'])}")


def render_summary_panel(payload: dict[str, object]) -> None:
    """Render final summary dashboard with enhanced styling."""
    summary = payload["summary"]
    assessments = payload["assessments"]
    learning_plan = payload["learning_plan"]

    # Summary Metrics
    st.markdown('<div class="hero-section"><h1>🎉 Assessment Complete</h1><p>Here\'s your personalized skill report</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f'''<div class="metric-card">
            <div class="metric-label">Overall Score</div>
            <div class="metric-value">{summary["overall_score"]}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f'''<div class="metric-card">
            <div class="metric-label">Readiness Level</div>
            <div class="metric-value">{summary["readiness"]}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    
    with col3:
        st.markdown(
            f'''<div class="metric-card">
            <div class="metric-label">Skills Assessed</div>
            <div class="metric-value">{len(assessments)}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    
    st.markdown("---")
    
    # Skill Breakdown
    st.markdown("### 🎯 Skill Breakdown")
    
    for item in assessments:
        with st.expander(f"{item['skill']} — Score: {int(item['score'])}/100"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                score = item["score"]
                level, emoji = get_score_level(score)
                st.markdown(f"<h3 style='color:#a78bfa;'>{emoji} {level}</h3>", unsafe_allow_html=True)
            
            with col2:
                st.progress(min(100, int(score)) / 100)
            
            st.markdown(f"**Why this score:** {item['rationale']}")
            if item.get('resume_hits'):
                st.markdown(f"**Resume Evidence:** {', '.join(item['resume_hits'])}")
    
    st.markdown("---")
    
    # Learning Plan
    st.markdown("### 🚀 Personalized Learning Plan")
    st.caption(f"We identified {len(learning_plan)} priority areas based on the job description and your resume.")
    
    plan_html = ""
    for i, step in enumerate(learning_plan, 1):
        plan_html += f'''
        <div class="timeline-item">
            <div class="timeline-content">
                <h4 style="color:#a78bfa;">📚 {i}. {step['skill']}</h4>
                <p><strong>Time Investment:</strong> {step['time_hours']} hours</p>
                <p><strong>Why focus here:</strong> {step['why_now']}</p>
                <p><strong>Bridge from:</strong> {', '.join(step['bridge_skills']) or 'Foundation building'}</p>
                <p><strong>First Step:</strong> {step['first_step']}</p>
                <div style="margin-top:12px;">
                    <strong>Resources:</strong>
                    <ul>
        '''
        for resource in step["resources"]:
            plan_html += f'<li><a href="{resource["url"]}" target="_blank">{resource["title"]}</a> - {resource["reason"]}</li>'
        
        plan_html += '</ul></div></div></div>'
    
    st.markdown(plan_html, unsafe_allow_html=True)


def render_hero_section() -> None:
    """Render hero section."""
    st.markdown(
        '''
        <div class="hero-section">
            <h1>✨ AI Skill Assessment Agent</h1>
            <p>Turn your resume and job description into a conversational skill audit, gap analysis, and realistic learning plan.</p>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def main() -> None:
    """Main app logic with modern UI."""
    inject_modern_css()
    
    # Check Groq API availability
    if not GROQ_AVAILABLE:
        st.error("⚠️ Groq API not configured")
        st.markdown(GROQ_ERROR)
        return
    
    if "assessment" not in st.session_state:
        reset_assessment_state()

    jd_text, resume_name, resume_text = render_sidebar()

    # Hero Section
    render_hero_section()

    state = current_state()
    
    # Pre-Assessment Review Screen
    if not state.get("started"):
        st.markdown("### 📋 Review Before Starting")
        
        tab1, tab2, tab3 = st.tabs(["Resume", "Job Description", "Skills"])
        
        with tab1:
            st.markdown("#### Extracted Resume")
            st.caption(f"📄 {resume_name}")
            st.markdown(
                f'<div class="glass-card">{resume_text[:3000]}</div>',
                unsafe_allow_html=True,
            )
        
        with tab2:
            st.markdown("#### Job Description")
            st.markdown(
                f'<div class="glass-card">{jd_text[:2000]}</div>',
                unsafe_allow_html=True,
            )
        
        with tab3:
            st.markdown("#### Detected Required Skills")
            detected_skills = extract_skills(jd_text, limit=10) or ["Python", "Machine Learning", "Deep Learning"]
            skill_html = " ".join([f'<span class="skill-badge">{s}</span>' for s in detected_skills])
            st.markdown(skill_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Assessment", use_container_width=True, key="start_btn"):
                initialize_session(jd_text, resume_name, resume_text)
                st.rerun()
        return

    # Update session if inputs changed
    if state["job_description"] != jd_text or state["resume_text"] != resume_text:
        initialize_session(jd_text, resume_name, resume_text)
        state = current_state()

    skills = state["required_skills"]
    current_index = state["current_index"]

    # Assessment Screen
    st.markdown(f"**Resume:** {resume_name}")
    
    # Show progress
    render_skill_progress(skills, current_index, state["answers"])
    
    # Chat history
    render_history(state["history"])

    # Current Question
    if current_index < len(skills):
        skill = skills[current_index]
        
        # Generate dynamic question using Groq
        with st.spinner(f"🤖 Generating personalized question for {skill}..."):
            question = generate_dynamic_question(
                skill=skill,
                resume_text=state["resume_text"],
                jd_text=state["job_description"],
                question_number=current_index,
                total_questions=len(skills),
                history=state["history"][-6:] if state["history"] else []
            )
        
        # Display question with styling
        st.markdown(
            f'<div class="chat-message ai"><strong><span class="chat-skill-badge">{skill}</span>Question {current_index + 1} of {len(skills)}</strong><br>{question}</div>',
            unsafe_allow_html=True,
        )
        
        # Show why this question is being asked
        with st.spinner("Generating context..."):
            why = explain_why_question(skill, state["job_description"], state["resume_text"])
        st.caption(f"💡 Why this question: {why}")
        
        answer = st.chat_input(f"Share your experience with {skill}...")
        
        if answer:
            # Score the answer using Groq
            with st.spinner("🤔 Evaluating your answer..."):
                result = evaluate_answer_with_groq(
                    skill=skill,
                    question=question,
                    answer=answer,
                    resume_text=state["resume_text"],
                    jd_text=state["job_description"]
                )
            
            # Update history
            state["history"].append({"role": "user", "content": answer})
            state["history"].append({
                "role": "assistant",
                "content": f"{skill} scored {result['score']}/100. {result['strength']}"
            })
            
            state["answers"].append(result)
            state["current_index"] += 1
            st.session_state.assessment = state
            
            # Show feedback
            col1, col2 = st.columns([1, 2])
            with col1:
                render_circular_progress(result['score'], result['level'])
            with col2:
                st.success(f"✅ Answer evaluated! ({result['level']})")
                st.markdown(f"**Strength:** {result['strength']}")
                st.markdown(f"**Area to improve:** {result['weakness']}")
                st.markdown(f"**Tip:** {result['improvement_tip']}")
            
            st.info("Moving to next skill...")
            st.rerun()
    
    # Final Report
    else:
        payload = build_report_payload("Skill Assessment", state["job_description"], state["resume_text"], state["answers"])
        render_summary_panel(payload)
        
        st.markdown("---")
        st.markdown("### 📥 Export Your Report")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📊 Download JSON Report",
                data=payload_to_json(payload),
                file_name="skill_assessment_report.json",
                mime="application/json",
                use_container_width=True,
            )
        
        with col2:
            st.download_button(
                "📄 Download Markdown Report",
                data=render_report_markdown(payload),
                file_name="skill_assessment_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        
        st.markdown("---")
        if st.button("🔄 Start New Assessment", use_container_width=True):
            reset_assessment_state()
            st.rerun()


if __name__ == "__main__":
    main()
