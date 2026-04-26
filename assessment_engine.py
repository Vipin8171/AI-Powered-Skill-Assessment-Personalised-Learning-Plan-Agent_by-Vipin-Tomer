from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
from typing import Any

from pypdf import PdfReader


@dataclass(frozen=True)
class Resource:
    title: str
    url: str
    reason: str


@dataclass(frozen=True)
class SkillProfile:
    name: str
    aliases: tuple[str, ...]
    question: str
    adjacent: tuple[str, ...]
    resources: tuple[Resource, ...]
    bridge_hint: str


def _resource(title: str, url: str, reason: str) -> Resource:
    return Resource(title=title, url=url, reason=reason)


SKILL_LIBRARY: dict[str, SkillProfile] = {
    "Python": SkillProfile(
        name="Python",
        aliases=("python",),
        question="Walk me through a Python solution you built end to end. What was the problem, what libraries did you choose, and how did you measure success?",
        adjacent=("SQL", "Git", "Data Analysis", "FastAPI"),
        resources=(
            _resource("Python Tutorial", "https://docs.python.org/3/tutorial/", "Official refresher for core language patterns."),
            _resource("Real Python", "https://realpython.com/", "Practical exercises for production Python habits."),
            _resource("Build a small API", "https://fastapi.tiangolo.com/tutorial/", "Pairs Python with deployable backend practice."),
        ),
        bridge_hint="You already show Python-heavy work, so the best next step is turning scripts into reusable modules and APIs.",
    ),
    "SQL": SkillProfile(
        name="SQL",
        aliases=("sql", "database", "dbms", "postgres", "mysql"),
        question="Describe a query or data pipeline where SQL changed the outcome. How did you validate correctness and performance?",
        adjacent=("Data Analysis", "Python", "Analytics", "Data Modeling"),
        resources=(
            _resource("SQLBolt", "https://sqlbolt.com/", "Quick drill on joins, filters, and aggregations."),
            _resource("Mode SQL Tutorial", "https://mode.com/sql-tutorial/", "Analytics-focused practice with realistic examples."),
            _resource("PostgreSQL Docs", "https://www.postgresql.org/docs/", "Reference for production SQL behavior."),
        ),
        bridge_hint="Your Python and analytics background can carry SQL quickly if you focus on joins, aggregation, and query plans.",
    ),
    "Machine Learning": SkillProfile(
        name="Machine Learning",
        aliases=("machine learning", "ml", "regression", "classification", "model evaluation"),
        question="Pick one ML model you trust. Which features mattered, how did you validate it, and what failure mode did you have to fix?",
        adjacent=("Statistics", "Python", "Deep Learning", "Experiment Tracking"),
        resources=(
            _resource("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course", "Short conceptual refresh with exercises."),
            _resource("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html", "Practical baseline modeling reference."),
            _resource("Kaggle Learn", "https://www.kaggle.com/learn", "Fast applied practice on datasets."),
        ),
        bridge_hint="You already understand the theory, so the gap is less about concepts and more about tightening evaluation and error analysis.",
    ),
    "Deep Learning": SkillProfile(
        name="Deep Learning",
        aliases=("deep learning", "cnn", "lstm", "transformer", "neural network", "pytorch", "tensorflow"),
        question="Tell me about a deep learning model you trained. Which architecture choices mattered most, and how did you debug unstable training?",
        adjacent=("PyTorch", "TensorFlow", "Computer Vision", "LLMs"),
        resources=(
            _resource("Deep Learning Book Notes", "https://www.deeplearningbook.org/", "Conceptual reference for optimization and generalization."),
            _resource("PyTorch Tutorials", "https://pytorch.org/tutorials/", "Hands-on model building and debugging."),
            _resource("TensorFlow Guides", "https://www.tensorflow.org/learn", "Alternative framework practice if the role uses TensorFlow."),
        ),
        bridge_hint="Your resume already shows deep learning projects, so this is a strength to leverage for adjacent deployment skills.",
    ),
    "Computer Vision": SkillProfile(
        name="Computer Vision",
        aliases=("computer vision", "opencv", "image processing", "yolov8", "deep sort", "feature extraction"),
        question="Explain a computer vision pipeline you built. What preprocessing, model selection, and postprocessing choices affected accuracy?",
        adjacent=("OpenCV", "Deep Learning", "MLOps", "Data Annotation"),
        resources=(
            _resource("OpenCV Docs", "https://docs.opencv.org/", "Core image processing and pipeline reference."),
            _resource("Ultralytics YOLO Docs", "https://docs.ultralytics.com/", "Useful for detection workflows and deployment."),
            _resource("Computer Vision Specialization", "https://www.coursera.org/specializations/computer-vision", "Structured refresher for classical + deep CV."),
        ),
        bridge_hint="This is already a strong area; the realistic next step is turning CV experiments into production services.",
    ),
    "LLMs": SkillProfile(
        name="LLMs",
        aliases=("llm", "llms", "large language model", "prompt engineering", "agents", "rag"),
        question="Describe an LLM workflow you built. How did you reduce hallucinations and verify the system stayed grounded in source data?",
        adjacent=("RAG", "LangChain", "FAISS", "NLP"),
        resources=(
            _resource("OpenAI Cookbook", "https://cookbook.openai.com/", "Patterns for grounding, retrieval, and evals."),
            _resource("Hugging Face LLM Course", "https://huggingface.co/learn", "Practical transformer and deployment material."),
            _resource("Prompt Engineering Guide", "https://www.promptingguide.ai/", "Quick reference for prompt design and evaluation."),
        ),
        bridge_hint="You already have concrete LLM and RAG experience, so focus on evaluation, cost control, and observability.",
    ),
    "RAG": SkillProfile(
        name="RAG",
        aliases=("rag", "retrieval augmented generation", "retrieval", "semantic chunking", "embeddings", "faiss", "langchain"),
        question="Walk through your retrieval pipeline. How did you chunk content, retrieve context, and decide whether the answer was grounded enough to return?",
        adjacent=("FAISS", "LangChain", "Embeddings", "NLP"),
        resources=(
            _resource("LangChain Docs", "https://python.langchain.com/docs/", "Common orchestration layer for retrieval workflows."),
            _resource("FAISS Docs", "https://faiss.ai/", "Vector search and retrieval basics."),
            _resource("Vector Database Guide", "https://www.pinecone.io/learn/", "Practical retrieval design and tradeoffs."),
        ),
        bridge_hint="Your resume already shows RAG work; the adjacent leap is stronger retrieval evaluation and caching strategies.",
    ),
    "LangChain": SkillProfile(
        name="LangChain",
        aliases=("langchain",),
        question="What abstraction did LangChain give you in your last project, and where did you intentionally avoid over-abstracting?",
        adjacent=("RAG", "LLMs", "Python", "Agents"),
        resources=(
            _resource("LangChain Docs", "https://python.langchain.com/docs/", "Core framework documentation."),
            _resource("LangChain Academy", "https://academy.langchain.com/", "Short project-based learning path."),
            _resource("LangSmith Docs", "https://docs.smith.langchain.com/", "Useful for tracing and evaluation."),
        ),
        bridge_hint="LangChain is already in your resume, so this should stay a confidence area rather than a gap.",
    ),
    "FAISS": SkillProfile(
        name="FAISS",
        aliases=("faiss",),
        question="How would you choose an index in FAISS for a large embedding corpus, and how would you evaluate recall versus latency?",
        adjacent=("Embeddings", "RAG", "Python", "Vector Search"),
        resources=(
            _resource("FAISS Docs", "https://faiss.ai/", "Vector indexing and search fundamentals."),
            _resource("Embedding Retrieval Primer", "https://www.pinecone.io/learn/vector-database/", "Good starting point for retrieval tradeoffs."),
            _resource("ANN Concepts", "https://www.ann-benchmarks.com/", "Benchmark intuition for approximate nearest neighbor search."),
        ),
        bridge_hint="You can transfer your retrieval work directly into FAISS tuning and ANN tradeoffs.",
    ),
    "FastAPI": SkillProfile(
        name="FastAPI",
        aliases=("fastapi", "flask", "api", "backend"),
        question="If you had to ship your model as an API, what would the request schema, error handling, and latency budget look like?",
        adjacent=("Python", "Git", "Docker", "MLOps"),
        resources=(
            _resource("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/", "Official guide to request/response design."),
            _resource("FastAPI Deployment", "https://fastapi.tiangolo.com/deployment/", "Deployment and scaling reference."),
            _resource("API Design Guide", "https://stripe.com/docs/api", "Useful for understanding clean interface design."),
        ),
        bridge_hint="This is a realistic adjacent skill for a Python-heavy candidate because it turns models into usable services.",
    ),
    "Docker": SkillProfile(
        name="Docker",
        aliases=("docker", "container", "containerization"),
        question="How would you package one of your AI projects into a container, and what would you inspect first when startup fails?",
        adjacent=("FastAPI", "Python", "Linux", "MLOps"),
        resources=(
            _resource("Docker Get Started", "https://docs.docker.com/get-started/", "Fast path to container basics."),
            _resource("Docker Best Practices", "https://docs.docker.com/develop/dev-best-practices/", "Production packaging habits."),
            _resource("Play with Docker", "https://labs.play-with-docker.com/", "Interactive practice without local setup pain."),
        ),
        bridge_hint="Your Python and project experience make Docker an efficient bridge skill for deployment readiness.",
    ),
    "AWS": SkillProfile(
        name="AWS",
        aliases=("aws", "s3", "ec2", "lambda", "cloud"),
        question="What would you deploy to AWS first if your model had to handle real traffic, and how would you keep cost under control?",
        adjacent=("Docker", "FastAPI", "MLOps", "Linux"),
        resources=(
            _resource("AWS Skill Builder", "https://skillbuilder.aws/", "Official cloud learning paths."),
            _resource("AWS Lambda Docs", "https://docs.aws.amazon.com/lambda/", "Serverless reference for simple workloads."),
            _resource("AWS Architecture Center", "https://aws.amazon.com/architecture/", "Patterns for production deployment."),
        ),
        bridge_hint="This is usually a downstream bridge after Docker and API serving, not a first skill to learn in isolation.",
    ),
    "PyTorch": SkillProfile(
        name="PyTorch",
        aliases=("pytorch",),
        question="Show me how you would debug a PyTorch training loop. Which tensors, gradients, or metrics would you inspect first?",
        adjacent=("Deep Learning", "Computer Vision", "LLMs", "MLOps"),
        resources=(
            _resource("PyTorch Tutorials", "https://pytorch.org/tutorials/", "Core framework docs and examples."),
            _resource("PyTorch Recipes", "https://pytorch.org/tutorials/recipes/recipes_index.html", "Debugging and training patterns."),
            _resource("Lightning Guide", "https://lightning.ai/docs/pytorch/stable/", "Useful if the role values training structure."),
        ),
        bridge_hint="PyTorch is already one of your strongest adjacent skills and should anchor your learning plan.",
    ),
    "Statistics": SkillProfile(
        name="Statistics",
        aliases=("statistics", "probability", "hypothesis", "variance", "confidence interval"),
        question="Which statistical check would you use to decide whether a model improvement is real rather than noise?",
        adjacent=("Machine Learning", "Experiment Tracking", "Optimization", "A/B Testing"),
        resources=(
            _resource("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "Quick structured review of statistical basics."),
            _resource("StatQuest", "https://www.youtube.com/@statquest", "Accessible intuition for model evaluation concepts."),
            _resource("A/B Testing Guide", "https://www.optimizely.com/optimization-glossary/ab-testing/", "Useful for inference in product settings."),
        ),
        bridge_hint="Your math background makes statistics a strong bridging asset for better evaluation and experiment design.",
    ),
    "Git": SkillProfile(
        name="Git",
        aliases=("git", "github", "version control"),
        question="How do you structure branches, reviews, and releases so that model changes stay reproducible?",
        adjacent=("Docker", "Python", "MLOps", "Linux"),
        resources=(
            _resource("Pro Git", "https://git-scm.com/book/en/v2", "Practical version-control reference."),
            _resource("GitHub Docs", "https://docs.github.com/", "Branching and collaboration workflows."),
            _resource("Learn Git Branching", "https://learngitbranching.js.org/", "Interactive Git practice."),
        ),
        bridge_hint="Git is usually a support skill, but it is critical for making your AI work reviewable and deployable.",
    ),
    "Linux": SkillProfile(
        name="Linux",
        aliases=("linux", "shell", "bash"),
        question="When a deployment is slow or failing, what Linux-level checks would you use before touching the model code?",
        adjacent=("Docker", "Git", "FastAPI", "AWS"),
        resources=(
            _resource("Linux Journey", "https://linuxjourney.com/", "Fast structured tour of shell and systems basics."),
            _resource("The Linux Command Line", "https://linuxcommand.org/tlcl.php", "Classic practical command-line reference."),
            _resource("Bash Guide", "https://mywiki.wooledge.org/BashGuide", "Good for shell scripting habits."),
        ),
        bridge_hint="Linux is a natural adjacent skill for a Python and Git-heavy candidate preparing for production work.",
    ),
}


SECTION_MARKERS = (
    "summary",
    "education",
    "projects",
    "technical skills",
    "achievements",
    "profile links",
)


def extract_text_from_pdf(pdf_path: Path | str) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _match_aliases(text: str, aliases: tuple[str, ...]) -> list[str]:
    normalized = normalize_text(text)
    matches: list[str] = []
    for alias in aliases:
        pattern = rf"(?<!\w){re.escape(alias.lower())}(?!\w)"
        if re.search(pattern, normalized):
            matches.append(alias)
    return matches


def extract_skills(text: str, limit: int | None = None) -> list[str]:
    findings: list[tuple[str, int]] = []
    for skill_name, profile in SKILL_LIBRARY.items():
        hits = _match_aliases(text, profile.aliases)
        if hits:
            score = len(hits)
            if skill_name in {"Python", "Machine Learning", "Deep Learning", "Computer Vision", "LLMs", "RAG"}:
                score += 1
            findings.append((skill_name, score))
    findings.sort(key=lambda item: (-item[1], list(SKILL_LIBRARY).index(item[0])))
    ordered = [name for name, _ in findings]
    return ordered[:limit] if limit else ordered


def _section_bonus(text: str, aliases: tuple[str, ...]) -> int:
    normalized = normalize_text(text)
    bonus = 0
    for alias in aliases:
        if f"technical skills {alias.lower()}" in normalized:
            bonus += 2
        if f"projects {alias.lower()}" in normalized:
            bonus += 1
    return bonus


def score_answer(skill_name: str, answer: str, resume_text: str, jd_text: str) -> dict[str, Any]:
    profile = SKILL_LIBRARY[skill_name]
    answer_text = answer.strip()
    answer_normalized = normalize_text(answer_text)
    resume_hits = _match_aliases(resume_text, profile.aliases)
    jd_hits = _match_aliases(jd_text, profile.aliases)

    resume_score = min(38, len(resume_hits) * 14 + _section_bonus(resume_text, profile.aliases))
    if answer_text:
        length_words = len(answer_text.split())
        length_score = min(14, length_words // 8)
        evidence_score = 0
        for token in ("built", "implemented", "trained", "deployed", "optimized", "evaluated", "debugged", "measured", "tradeoff", "metric", "latency", "accuracy", "recall", "precision"):
            if token in answer_normalized:
                evidence_score += 3
        number_score = 4 if re.search(r"\d", answer_text) else 0
        specificity_score = 0
        for token in profile.aliases:
            if token in answer_normalized:
                specificity_score += 2
        for token in ("project", "pipeline", "dataset", "model", "production", "failure", "tradeoff", "grounded", "retrieval"):
            if token in answer_normalized:
                specificity_score += 1
        answer_score = min(50, length_score + evidence_score + number_score + specificity_score)
    else:
        answer_score = 0

    jd_priority = 6 if jd_hits else 0
    total = min(100, resume_score + answer_score + jd_priority)

    if total >= 85:
        level = "strong"
    elif total >= 70:
        level = "working"
    elif total >= 50:
        level = "developing"
    else:
        level = "early"

    if answer_text:
        if total >= 75:
            rationale = "The answer shows concrete experience, explicit tradeoffs, and enough context to trust the skill."
        elif total >= 50:
            rationale = "The answer is directionally good, but it needs more precise examples, metrics, or debugging detail."
        else:
            rationale = "The answer stays too high-level to verify production-level understanding."
    else:
        rationale = "No direct answer was provided, so the score relies mostly on resume evidence."

    gap = max(0, 100 - total)
    next_focus = profile.bridge_hint
    return {
        "skill": skill_name,
        "resume_hits": resume_hits,
        "jd_hits": jd_hits,
        "score": total,
        "level": level,
        "gap": gap,
        "rationale": rationale,
        "next_focus": next_focus,
        "answer": answer_text,
    }


def build_question(skill_name: str, resume_text: str) -> str:
    profile = SKILL_LIBRARY[skill_name]
    resume_hits = _match_aliases(resume_text, profile.aliases)
    if resume_hits:
        evidence = ", ".join(sorted(set(resume_hits)))
        return f"I found {evidence} in your resume. {profile.question}"
    return profile.question


def pick_bridge_skills(target_skill: str, candidate_strengths: list[str]) -> list[str]:
    profile = SKILL_LIBRARY[target_skill]
    bridges = [skill for skill in profile.adjacent if skill in candidate_strengths]
    if bridges:
        return bridges[:3]
    return list(profile.adjacent[:3])


def learning_plan(assessments: list[dict[str, Any]], candidate_strengths: list[str]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    sorted_items = sorted(assessments, key=lambda item: (-item["gap"], item["score"]))
    for item in sorted_items:
        if item["score"] >= 75:
            continue
        profile = SKILL_LIBRARY[item["skill"]]
        hours = 6 if item["score"] >= 60 else 10 if item["score"] >= 45 else 14 if item["score"] >= 30 else 18
        bridges = pick_bridge_skills(item["skill"], candidate_strengths)
        plan.append(
            {
                "skill": item["skill"],
                "target": f"Reach working proficiency in {item['skill']}",
                "time_hours": hours,
                "why_now": profile.bridge_hint,
                "bridge_skills": bridges,
                "resources": [asdict(resource) for resource in profile.resources[:3]],
                "first_step": f"Build a tiny project that combines {bridges[0]} with {item['skill']} and write a short evaluation note.",
            }
        )
    return plan


def summarize_results(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    if not assessments:
        return {"overall_score": 0, "strengths": [], "gaps": [], "readiness": "not started"}
    scores = [item["score"] for item in assessments]
    strengths = [item["skill"] for item in assessments if item["score"] >= 75]
    gaps = [item["skill"] for item in assessments if item["score"] < 60]
    average = round(sum(scores) / len(scores), 1)
    if average >= 80:
        readiness = "job-ready"
    elif average >= 65:
        readiness = "promising"
    elif average >= 50:
        readiness = "mixed"
    else:
        readiness = "early"
    return {"overall_score": average, "strengths": strengths, "gaps": gaps, "readiness": readiness}


def build_report_payload(candidate_name: str, jd_text: str, resume_text: str, assessments: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_results(assessments)
    candidate_strengths = [item["skill"] for item in assessments if item["score"] >= 75]
    plan = learning_plan(assessments, candidate_strengths)
    return {
        "candidate_name": candidate_name,
        "job_description_skills": extract_skills(jd_text),
        "resume_skills": extract_skills(resume_text),
        "summary": summary,
        "assessments": assessments,
        "learning_plan": plan,
    }


def render_report_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"# Skill Assessment Report for {payload['candidate_name']}",
        "",
        f"Overall score: {summary['overall_score']}",
        f"Readiness: {summary['readiness']}",
        "",
        "## Assessed Skills",
    ]
    for item in payload["assessments"]:
        lines.append(f"- {item['skill']}: {item['score']} ({item['level']})")
    lines.extend([
        "",
        "## Learning Plan",
    ])
    for step in payload["learning_plan"]:
        lines.append(f"- {step['skill']}: {step['time_hours']}h | bridge: {', '.join(step['bridge_skills'])}")
        lines.append(f"  - First step: {step['first_step']}")
    return "\n".join(lines)


def payload_to_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2)
