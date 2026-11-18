
import re


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
                "suggestion": (
                    f"Remove or replace '{word}' "
                    "with an approved term."
                ),
                "severity": "High",
                "reason": (
                    "This word violates the brand's "
                    "restricted-word guideline."
                )
            })

    for old_word, new_word in preferred_words.items():

        if contains_whole_word(text, old_word):

            issues.append({
                "issue": f"Use of '{old_word}'",
                "suggestion": (
                    f"Consider using '{new_word}' instead."
                ),
                "severity": "Medium",
                "reason": (
                    "The brand prefers consistent use "
                    "of approved terminology."
                )
            })

    return issues
