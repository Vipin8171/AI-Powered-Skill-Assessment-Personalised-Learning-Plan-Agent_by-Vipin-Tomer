# AI-Powered Skill Assessment & Personalised Learning Plan Agent

This prototype reads a job description and a resume, interviews the candidate one required skill at a time, scores the real proficiency signal, highlights gaps, and generates a personalized learning plan focused on adjacent skills the candidate can realistically learn next.

## What it does

- Extracts text from a resume PDF.
- Detects the most relevant skills in a job description.
- Asks a conversational prompt for each skill.
- Scores the answer using resume evidence, specificity, and practical detail.
- Produces a gap analysis and a learning plan with curated resources and time estimates.

## Local setup

1. Create and activate the existing virtual environment at `c:\Users\tvipi\project\.venv` if it is not already active.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

4. Open the browser URL printed by Streamlit, usually `http://localhost:8501`.

## Sample input and output

- Sample resume: `Vipin Tomer Resume.pdf`
- Sample job description: `sample_inputs/sample_job_description.txt`
- Sample output report: `sample_outputs/sample_assessment.md`
- Sample output JSON: `sample_outputs/sample_assessment.json`

## Files to review

- `ARCHITECTURE_README.md` for the architecture diagram and system breakdown.
- `SCORING_LOGIC.md` for a short explanation of the scoring rules.
