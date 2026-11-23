# ✳ Pressmark 2.0
### AI-Powered Brand Intelligence and Governance Platform

**Catching brand mistakes before they go live.**

Pressmark is an AI-powered brand-governance platform that helps teams review written content against their brand terminology, communication policies and content standards before publication.

It combines rule-based checks with contextual AI analysis and human review, helping organisations maintain consistent, responsible and brand-aligned communication.

**Live Application:** https://pressmark-d79vywstklhfseyoxcfgxw.streamlit.app/  
**Source Code:** https://github.com/amina26-06/Pressmark

---

## 1. The Problem

Organisations often have brand guidelines, but applying them consistently across content created by different writers and teams can be difficult.

Common challenges include:

- Inconsistent use of approved and restricted terminology.
- Exaggerated or potentially misleading claims.
- Difficulty managing brand communication policies.
- Limited visibility into review decisions and recurring content issues.
- Lack of a clear record of human review decisions.

Pressmark addresses these challenges through a centralised content-review and brand-governance workspace.

## 2. Key Features

### A. Context-Aware AI Content Validation

Pressmark combines configured terminology rules with contextual AI analysis.

- Identifies restricted and preferred terminology.
- Displays detected issues and suggested replacements.
- Uses severity levels to highlight important findings.
- Analyses content for exaggerated or potentially misleading claims.
- Considers saved brand policies during AI analysis.
- Supports PDF and DOCX document uploads, alongside pasted text.

The AI analysis uses Groq with the `openai/gpt-oss-120b` model.

### B. Advanced Brand Policy Management

Pressmark provides a dedicated workspace for managing brand communication policies.

- Create and save brand policies.
- Organise policies by category, such as Tone of Voice.
- View existing policies.
- Delete policies that are no longer required.
- Use saved policies as context during AI content analysis.

This helps teams maintain consistent communication standards beyond individual terminology rules.

### C. Analytics and Human Review Workflow

Pressmark provides visibility into content-review activity and human decisions.

- Accept or reject detected suggestions.
- Record reviewer names with review decisions.
- Maintain an audit history of reviewed content.
- View accepted and rejected decision counts.
- Analyse issue severity and frequently detected terms.
- View review and reviewer activity.
- Export audit records as CSV.
- Preview corrected content and export it as a text file.

Human reviewers retain control over final content decisions.

## 3. Application Modules

| Module | Purpose |
|---|---|
| Overview | Displays a summary of brand-governance activity |
| Review Studio | Reviews pasted or uploaded content |
| Analytics | Shows review trends and decision insights |
| Brand Rules | Manages restricted and preferred terminology |
| Brand Policies | Manages communication guidelines |
| Audit Logs | Records review history and decisions |

## 4. Technical Architecture

Pressmark follows a lightweight Python-based application architecture.

**Technology stack**

- Python – application logic.
- Streamlit – user interface.
- SQLite – persistent storage.
- Pandas – data processing and analytics.
- Regular Expressions – terminology detection.
- Groq API – contextual AI analysis.
- python-docx – DOCX document extraction.
- pdfplumber – PDF text extraction.

**Application structure**

```text
Pressmark/
│
├── app.py
├── brand_checker.py
├── database.py
├── requirements.txt
├── README.md
│
└── .streamlit/
    └── secrets.toml
```

**Architecture overview**

1. The user submits text or uploads a document through the Streamlit interface.
2. Text is extracted from supported document formats.
3. The brand-checking module identifies configured terminology issues.
4. Contextual AI analysis evaluates content against relevant brand policies.
5. Findings are presented for human review.
6. Review decisions and audit information are stored in SQLite.
7. Analytics displays insights from recorded review activity.

## 5. Installation and Setup

### Requirements

- Python 3.10 or later.
- pip.
- A Groq API key for contextual AI analysis.

### Step 1: Clone the repository

```bash
git clone https://github.com/amina26-06/Pressmark.git
cd Pressmark
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure the API key

Create a file named `secrets.toml` inside a `.streamlit` folder.

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Replace the placeholder with your own Groq API key.

**Important:** Never commit API keys or secret files to GitHub.

### Step 4: Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 6. Testing and Verification

The deployed application was manually checked for its principal workflows.

| Area | Verification |
|---|---|
| Application deployment | Live application opened successfully |
| Rule-based validation | Configured terminology detection checked |
| AI analysis | Groq contextual analysis checked on the deployed application |
| Brand policies | Policy creation and display checked |
| Human review | Accept/reject workflow checked |
| Audit history | Reviewer-attributed review record checked |
| Analytics | Review and decision summaries displayed |
| Document support | PDF and DOCX upload functionality included |
| Exports | Audit CSV and corrected text export functionality included |

Testing focused on the main user journeys and the integration of the three Round 2 improvements.

## 7. Limitations

- Contextual AI analysis requires a valid Groq API key and network access.
- AI output may require human verification.
- Analysis availability may depend on external API and model availability.
- The current application is a prototype and does not claim enterprise-grade authentication, role-based access control or real-time multi-user collaboration.
- Supported document extraction is focused on PDF and DOCX text.

## 8. Future Roadmap

Potential future developments include:

- Advanced visual brand checks, including logo spacing and colour contrast.
- Accessibility support and editable alt-text suggestions.
- Measured validation accuracy using a labelled evaluation dataset.
- More advanced guideline-health insights.
- Multilingual content validation.
- Integrations with document editors and team collaboration platforms.
- Enterprise deployment and enhanced access controls.

These are future development directions, not features currently claimed as complete.

## 9. Acknowledgements and Technology Disclosure

Pressmark was developed for the Inkloom AI Hackathon.

The project uses open-source Python libraries, Streamlit, SQLite and the Groq API for AI-powered analysis.

AI assistance was used during development for coding support, debugging and documentation. Final implementation, integration, testing and project decisions were carried out as part of the development process.

---

**Pressmark 2.0 — Human-reviewed brand governance.**

*Built to help teams catch brand mistakes before they go live.