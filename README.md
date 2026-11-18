
# Pressmark

### Catching brand mistakes before they go live.

Pressmark is a brand content review tool that helps identify restricted words and preferred terminology before content is published.

## Live Application

**Live App:** https://pressmark-d79vywstklhfseyoxcfgxw.streamlit.app/

**GitHub:** https://github.com/amina26-06/Pressmark

## Features

- Brand rule management
- Default restricted and preferred word rules
- PDF and DOCX text extraction
- Automatic terminology checking
- High and medium severity classification
- Accept or reject suggested changes
- Corrected content preview
- TXT download
- Audit history
- Dashboard metrics
- CSV export

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Regular Expressions
- PyPDF
- Python-docx

## What Works

- PDF and DOCX uploads
- Restricted and preferred word detection
- Severity classification
- Human review with accept/reject decisions
- Corrected content preview and TXT download
- Audit history and CSV export
- Dashboard and live deployment

## Current Limitations

- Detection is currently rule-based, not contextual AI.
- The tool may not understand the meaning or context of a sentence.
- Current rule categories are Restricted Word and Preferred Word.
- Human review is required before publishing corrected content.

## Run Locally

1. Clone the repository:

   `git clone https://github.com/amina26-06/Pressmark.git`

2. Install dependencies:

   `pip install -r requirements.txt`

3. Run the application:

   `python -m streamlit run app.py`

## Future Improvements

1. Context-aware language detection using NLP.
2. Additional brand guidelines for tone, disclaimers, and writing style.
3. Enhanced analytics and reporting.

---

**Pressmark — Catching brand mistakes before they go live.**
