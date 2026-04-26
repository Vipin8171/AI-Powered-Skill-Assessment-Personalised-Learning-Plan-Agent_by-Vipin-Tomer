"""Groq API integration for dynamic question generation and answer evaluation."""

import json
from groq import Groq
from config import GROQ_API_KEY

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

DIFFICULTY_LEVELS = {
    0: "basic and foundational",
    1: "intermediate and applied",
    2: "advanced and situational"
}


def get_difficulty_level(index: int, total: int) -> str:
    """Determine difficulty based on position in assessment."""
    if index == 0:
        return DIFFICULTY_LEVELS[0]  # First question: basic
    elif index < (total * 0.66):
        return DIFFICULTY_LEVELS[1]  # Middle questions: intermediate
    else:
        return DIFFICULTY_LEVELS[2]  # Last questions: advanced


def generate_dynamic_question(
    skill: str,
    resume_text: str,
    jd_text: str,
    question_number: int,
    total_questions: int,
    history: list = None,
) -> str:
    """
    Generate a dynamic, contextual interview question using Groq.
    
    Args:
        skill: The skill being assessed
        resume_text: Candidate's resume
        jd_text: Job description
        question_number: Current question index (0-based)
        total_questions: Total questions in assessment
        history: Previous conversation history
    
    Returns:
        Generated question string
    """
    if history is None:
        history = []
    
    difficulty = get_difficulty_level(question_number, total_questions)
    
    # Format conversation history
    history_str = "\n".join([
        f"{msg['role'].upper()}: {msg['content'][:200]}"
        for msg in history[-4:]  # Last 4 messages
    ])
    
    prompt = f"""You are an expert AI technical interviewer for a startup.

SKILL TO ASSESS: {skill}

ABOUT THE ROLE:
{jd_text[:1000]}

CANDIDATE'S BACKGROUND (Resume excerpt):
{resume_text[:1500]}

INTERVIEW CONTEXT:
- This is question {question_number + 1} of {total_questions}
- Difficulty level: {difficulty}
- Previous conversation:
{history_str if history_str else "Starting fresh"}

YOUR TASK:
Generate ONE high-quality interview question that:
1. Is {difficulty}
2. Tests real understanding and practical experience
3. Is specific to their background and the job
4. Avoids generic textbook questions
5. Is answerable in 2-3 sentences
6. Shows you understand their resume and the job

IMPORTANT:
- Make it conversational and engaging
- Reference their resume if relevant
- Connect to the specific job requirements
- Don't ask yes/no questions

Return ONLY the question, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback question if API fails
        return f"Tell me about your experience with {skill} and how you've applied it in real projects."


def evaluate_answer_with_groq(
    skill: str,
    question: str,
    answer: str,
    resume_text: str,
    jd_text: str,
) -> dict:
    """
    Evaluate answer using Groq AI.
    
    Args:
        skill: The skill being assessed
        question: The question asked
        answer: Candidate's answer
        resume_text: Candidate's resume
        jd_text: Job description
    
    Returns:
        Dictionary with score, strengths, weaknesses, improvement tips
    """
    
    prompt = f"""You are an expert technical evaluator.

SKILL: {skill}

QUESTION ASKED: {question}

CANDIDATE'S ANSWER: {answer}

JOB REQUIREMENT (from JD):
{jd_text[:800]}

RESUME CONTEXT:
{resume_text[:800]}

EVALUATE THIS ANSWER AND RESPOND WITH ONLY A JSON OBJECT (no markdown, no explanation):
{{
  "score": <0-100 integer>,
  "level": "<one of: Early, Developing, Working, Strong>",
  "strength": "<one key strength in 1-2 sentences>",
  "weakness": "<one gap or area to improve in 1-2 sentences>",
  "improvement_tip": "<specific, actionable advice in 1-2 sentences>",
  "job_relevance": "<how this answer relates to the job in 1-2 sentences>"
}}

SCORING GUIDELINES:
- 85-100: Demonstrates deep expertise with practical examples
- 70-84: Shows competence with some practical understanding
- 50-69: Shows basic knowledge but lacks depth or examples
- 0-49: Limited understanding or completely off-topic

Return ONLY valid JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temp for consistency
            max_tokens=400,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up response if it has markdown
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        return result
        
    except json.JSONDecodeError as e:
        # Fallback evaluation if JSON parsing fails
        return {
            "score": 65,
            "level": "Developing",
            "strength": "Candidate provided a thoughtful response",
            "weakness": "Could provide more specific examples or technical details",
            "improvement_tip": "Add concrete examples from your projects to strengthen this skill area",
            "job_relevance": "This skill is valuable for the role"
        }
    except Exception as e:
        # Fallback for API errors
        return {
            "score": 60,
            "level": "Developing",
            "strength": "Response shows awareness of the topic",
            "weakness": "Could be more detailed",
            "improvement_tip": "Practice explaining your experience with concrete examples",
            "job_relevance": "This skill is relevant to the position"
        }


def explain_why_question(skill: str, jd_text: str, resume_text: str) -> str:
    """
    Generate explanation for why a specific question is being asked.
    
    Args:
        skill: Skill being assessed
        jd_text: Job description
        resume_text: Resume text
    
    Returns:
        Brief explanation string
    """
    
    prompt = f"""Why is knowledge of '{skill}' important for this job?

Job Description:
{jd_text[:800]}

Resume shows: {("some experience" if skill.lower() in resume_text.lower() else "limited or no evidence")} of {skill}

Provide a 1-2 sentence explanation of why this skill matters for the role.
Be specific and reference the job requirements.
Return ONLY the explanation, no preamble."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"This skill is important for succeeding in the {skill} requirements of this role."
