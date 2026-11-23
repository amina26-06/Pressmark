
import re
import json
from groq import Groq


def contains_whole_word(text, word):
    pattern = rf"\b{re.escape(word)}\b"

    return bool(
        re.search(pattern, text, flags=re.IGNORECASE)
    )


def check_brand_content(text, restricted_words, preferred_words):

    issues = []

    for word in restricted_words:

        if contains_whole_word(text, word):

            issues.append({
                "issue": f"Restricted word found: {word}",
                "matched_term": word.lower(),
                "suggestion": (
                    f"Remove or replace '{word}' "
                    "with an approved term."
                ),
                "severity": "High",
                "reason": (
                    "This word violates the brand's "
                    "restricted-word guideline."
                ),
                "source": "Rule-Based Analysis"
            })

    for old_word, new_word in preferred_words.items():

        if contains_whole_word(text, old_word):

            issues.append({
                "issue": f"Use of '{old_word}'",
                "matched_term": old_word.lower(),
                "suggestion": (
                    f"Consider using '{new_word}' instead."
                ),
                "severity": "Medium",
                "reason": (
                    "The brand prefers consistent use "
                    "of approved terminology."
                ),
                "source": "Rule-Based Analysis"
            })

    return issues


def analyze_with_groq(text, api_key, policies=None):

    if not text.strip():
        return []

    client = Groq(api_key=api_key, timeout=20.0)
    policy_text = "\n".join(policies or [])

    prompt = f"""
You are a professional brand compliance analyst.

Analyze the content for contextual brand violations.

Look for:
1. Tone-of-voice inconsistencies.
2. Semantic brand guideline violations.
3. Misleading or exaggerated claims.
4. Inappropriate wording in context.
5. Violations of the supplied brand policies.

IMPORTANT:
- Identify contextual problems, not just individual restricted words.
- Do not repeat a simple restricted-word finding if it is already
  covered by terminology rules.
- You may identify a broader contextual problem involving the same
  sentence if it adds a genuinely different insight.
- Do not invent violations.

Brand policies:
{policy_text if policy_text else "No additional policies supplied."}

Content:
{text[:12000]}

Return ONLY valid JSON in this exact structure:
{{
  "issues": [
    {{
      "issue": "Short description",
      "suggestion": "Recommended improvement",
      "severity": "High",
      "reason": "Explain the contextual violation"
    }}
  ]
}}

Severity must be High, Medium, or Low.
If no violations are found, return an empty issues list.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=1500
    )

    result = json.loads(
        completion.choices[0].message.content
    )

    ai_issues = result.get("issues", [])
    cleaned_issues = []

    for item in ai_issues:

        if not isinstance(item, dict):
            continue

        severity = str(
            item.get("severity", "Medium")
        ).capitalize()

        if severity not in ["High", "Medium", "Low"]:
            severity = "Medium"

        cleaned_issues.append({
            "issue": str(
                item.get("issue", "Brand guideline concern")
            ),
            "suggestion": str(
                item.get("suggestion", "Review this content.")
            ),
            "severity": severity,
            "reason": str(
                item.get("reason", "Contextual brand concern detected.")
            ),
            "source": "AI Context Analysis"
        })

    return cleaned_issues


def remove_duplicate_ai_issues(rule_issues, ai_issues):

    rule_terms = {
        str(issue.get("matched_term", "")).lower().strip()
        for issue in rule_issues
        if issue.get("matched_term")
    }

    filtered_issues = []

    for ai_issue in ai_issues:

        ai_text = (
            str(ai_issue.get("issue", "")) + " " +
            str(ai_issue.get("reason", ""))
        ).lower()

        duplicate = any(
            contains_whole_word(ai_text, term)
            for term in rule_terms
        )

        if not duplicate:
            filtered_issues.append(ai_issue)

    return filtered_issues
