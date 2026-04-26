# Scoring Logic

The scoring engine is intentionally simple and explainable.

## Inputs

- Resume text extracted from the PDF.
- Job description text.
- One free-text answer per required skill.

## Score components

Each skill score is a weighted combination of:

- Resume evidence: whether the skill or a close alias appears in the resume.
- Answer specificity: whether the candidate mentions concrete actions, tools, metrics, or tradeoffs.
- Answer length: a short answer gets less credit than a detailed one.
- Job relevance: if the skill is actually present in the JD, it gets a small priority bump.

## Interpretation bands

- 85 to 100: strong
- 70 to 84: working
- 50 to 69: developing
- below 50: early

## Learning plan rules

- Only skills below the working threshold are added to the plan.
- Each weak skill gets a realistic time estimate based on its score band.
- The plan prefers adjacent skills that the candidate already knows, so the next learning step stays feasible.
- Each plan item includes official or practical resources plus a first project idea.
