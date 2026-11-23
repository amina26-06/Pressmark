
import re
import html
import pandas as pd
import streamlit as st
import pdfplumber

from docx import Document

from database import (
    initialize_db,
    get_brand_rules,
    add_brand_rule,
    save_review_audit,
    get_audit_history,
    get_dashboard_stats,
    get_analytics_stats,
    get_severity_distribution,
    get_top_flagged_terms,
    get_review_activity,
    get_reviewer_stats,
    add_brand_policy,
    get_brand_policies,
    delete_brand_policy
)

from brand_checker import (
    check_brand_content,
    analyze_with_groq,
    remove_duplicate_ai_issues
)


# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Pressmark | Brand Intelligence",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_db()


# ==========================================================
# DESIGN SYSTEM
# ==========================================================

st.markdown("""
<style>
.stApp {
    background: #F5F5F0;
    color: #172B3A;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #102A3A;
    border-right: 1px solid #254354;
}

[data-testid="stSidebar"] * {
    color: #F4F7F6 !important;
}

[data-testid="stSidebar"] .stButton button {
    background: #18A999;
    color: white !important;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

h1, h2, h3 {
    color: #142D3D !important;
    letter-spacing: -0.5px;
}

p, label {
    color: #506575;
}

.brand-logo {
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #FFFFFF;
    margin-bottom: 2px;
}

.brand-caption {
    font-size: 12px;
    color: #A9C0CA;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.hero {
    background: linear-gradient(115deg, #102A3A, #194B58);
    padding: 32px 35px;
    border-radius: 18px;
    margin-bottom: 25px;
    color: white;
}

.hero h1 {
    color: white !important;
    font-size: 35px;
    margin-bottom: 7px;
}

.hero p {
    color: #D5E8E7;
    font-size: 15px;
    margin-bottom: 0;
}

.eyebrow {
    color: #159989;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E5E9E5;
    border-radius: 14px;
    padding: 20px;
    min-height: 115px;
}

.metric-label {
    font-size: 12px;
    color: #73818B;
    font-weight: 600;
    margin-bottom: 12px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #142D3D;
}

.pm-card {
    background: #FFFFFF;
    border: 1px solid #E5E9E5;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 14px;
}

.pm-card-title {
    font-size: 17px;
    font-weight: 750;
    color: #142D3D;
    margin-bottom: 7px;
}

.pm-muted {
    color: #74838B;
    font-size: 13px;
}

.rule-restricted {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #FCE9E6;
    color: #B54C3D;
    font-size: 11px;
    font-weight: 700;
}

.rule-preferred {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #DDF4EE;
    color: #167B68;
    font-size: 11px;
    font-weight: 700;
}

.rule-category {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #E9EFF5;
    color: #36566B;
    font-size: 11px;
    font-weight: 700;
    margin-right: 5px;
}

.rule-high {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #FCE9E6;
    color: #B54C3D;
    font-size: 11px;
    font-weight: 700;
    margin-right: 5px;
}

.rule-medium {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #FFF1D9;
    color: #946317;
    font-size: 11px;
    font-weight: 700;
    margin-right: 5px;
}

.example-box {
    background: #F5F7F5;
    border-left: 3px solid #18A999;
    border-radius: 6px;
    padding: 12px 15px;
    margin-top: 10px;
    font-size: 13px;
    color: #405663;
}

.section-line {
    border-top: 1px solid #E2E8E4;
    margin: 23px 0;
}

.stButton button,
.stDownloadButton button {
    border-radius: 9px;
    font-weight: 650;
    min-height: 42px;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

/* FIX: TEXT VISIBILITY IN INPUTS AND TEXT AREAS */

/* FIX: TEXT VISIBILITY IN INPUTS AND TEXT AREAS */

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    color: #172B3A !important;
    -webkit-text-fill-color: #172B3A !important;
    background-color: #FFFFFF !important;
    caret-color: #172B3A !important;
    opacity: 1 !important;
}

div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #74838B !important;
    -webkit-text-fill-color: #74838B !important;
    opacity: 1 !important;
}

div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
}

div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #74838B !important;
    -webkit-text-fill-color: #74838B !important;
    opacity: 1 !important;
}

div[role="radiogroup"] {
    gap: 7px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #E2E8E4;
    border-radius: 12px;
}

.footer {
    text-align: center;
    color: #84939A;
    font-size: 12px;
    padding: 25px 0 5px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {
    "review_issues": [],
    "review_has_run": False,
    "review_content": "",
    "review_id": 0,
    "audit_saved": set(),
    "corrected_content": "",
    "reviewer_name": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def load_rules():
    rules = get_brand_rules()

    restricted_words = []
    preferred_words = {}
    restricted_replacements = {}

    for rule_type, word, replacement in rules:
        if rule_type == "Restricted Word":
            restricted_words.append(word)

            if replacement:
                restricted_replacements[word] = replacement

        elif rule_type == "Preferred Word":
            preferred_words[word] = replacement or ""

    return (
        restricted_words,
        preferred_words,
        restricted_replacements
    )


def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def page_heading(eyebrow, title, description):
    st.markdown(f"""
    <div class="eyebrow">{eyebrow}</div>
    <h1>{title}</h1>
    <p style="color:#74838B; margin-top:-8px;">
        {description}
    </p>
    """, unsafe_allow_html=True)


def extract_document(uploaded_file):
    if uploaded_file.name.lower().endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(
                page.extract_text() or ""
                for page in pdf.pages
            )

    if uploaded_file.name.lower().endswith(".docx"):
        document = Document(uploaded_file)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    return ""


def get_issue_words(issue, preferred, restricted_replacements):
    original_word = ""
    replacement_word = ""

    if issue["issue"].startswith("Restricted word found: "):
        original_word = issue["issue"].replace(
            "Restricted word found: ", "", 1
        )

        replacement_word = next(
            (
                value for key, value
                in restricted_replacements.items()
                if key.lower() == original_word.lower()
            ),
            ""
        )

    elif issue["issue"].startswith("Use of '"):
        original_word = issue["issue"].split("'")[1]

        replacement_word = next(
            (
                value for key, value
                in preferred.items()
                if key.lower() == original_word.lower()
            ),
            ""
        )

    return original_word, replacement_word


def build_corrected_content(original_content, decisions):
    corrected = original_content

    for item in decisions:
        if item["decision"] != "Accept suggestion":
            continue

        word = item["original_word"]
        replacement = item["replacement"]

        if word and replacement:
            corrected = re.sub(
                rf"\b{re.escape(word)}\b",
                lambda match: replacement,
                corrected,
                flags=re.IGNORECASE
            )

    corrected = re.sub(
        r"\s+([.,!?;:])",
        r"\1",
        corrected
    )

    corrected = re.sub(r" {2,}", " ", corrected)

    return corrected.strip()


def get_rule_details(rule_type, word, replacement):
    if rule_type == "Restricted Word":
        return {
            "category": "Terminology",
            "severity": "High",
            "explanation": (
                "This term is restricted by the brand guidelines. "
                "Use approved terminology instead."
            ),
            "bad_example": f"Our products are {word}.",
            "good_example": (
                f"Our products are {replacement}."
                if replacement
                else "Use an approved alternative."
            )
        }

    return {
        "category": "Terminology",
        "severity": "Medium",
        "explanation": (
            "The brand prefers consistent use of this approved term."
        ),
        "bad_example": f"Get the best {word} today.",
        "good_example": (
            f"Get the best {replacement} today."
            if replacement
            else "Use the preferred brand terminology."
        )
    }


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 22px;">
        <div class="brand-logo">✳ PRESSMARK</div>
        <div class="brand-caption">
            Brand Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(
        "<p style='font-size:11px;letter-spacing:1.5px;"
        "color:#8FAAB5;'>WORKSPACE</p>",
        unsafe_allow_html=True
    )

    selected_page = st.radio(
        "Navigation",
        [
            "Overview",
            "Review Studio",
            "Analytics",
            "Brand Rules",
            "Brand Policies",
            "Audit Logs"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        "<p style='font-size:11px;letter-spacing:1.5px;"
        "color:#8FAAB5;'>QUICK SUMMARY</p>",
        unsafe_allow_html=True
    )

    all_rules = get_brand_rules()

    restricted_count = sum(
        1 for rule in all_rules
        if rule[0] == "Restricted Word"
    )

    preferred_count = sum(
        1 for rule in all_rules
        if rule[0] == "Preferred Word"
    )

    st.write(f"Restricted rules  ·  {restricted_count}")
    st.write(f"Preferred rules  ·  {preferred_count}")

    st.divider()

    st.caption("PRESSMARK 2.0")
    st.caption("Human-reviewed brand governance")


# ==========================================================
# OVERVIEW DASHBOARD
# ==========================================================

if selected_page == "Overview":

    st.markdown("""
    <div class="hero">
        <div style="font-size:12px;letter-spacing:2px;
                    color:#A7DAD3;font-weight:700;">
            BRAND GOVERNANCE WORKSPACE
        </div>
        <h1>Make every word count.</h1>
        <p>
            Review content, enforce terminology guidelines,
            and maintain consistency across your brand.
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_dashboard_stats()

    page_heading(
        "WORKSPACE OVERVIEW",
        "Your dashboard",
        "A snapshot of your brand content review activity."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("REVIEWED CONTENT", stats["reviewed_content"])

    with col2:
        metric_card("TOTAL DECISIONS", stats["total_decisions"])

    with col3:
        metric_card("ACCEPTED", stats["accepted"])

    with col4:
        metric_card("REJECTED", stats["rejected"])

    st.markdown("<div class='section-line'></div>",
                unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("Review activity")

        if stats["total_decisions"] > 0:
            chart_data = pd.DataFrame({
                "Decision": ["Accepted", "Rejected"],
                "Count": [
                    stats["accepted"],
                    stats["rejected"]
                ]
            })

            st.bar_chart(
                chart_data.set_index("Decision"),
                color="#18A999"
            )
        else:
            st.info(
                "Your review activity will appear here "
                "after your first review."
            )

    with right:
        st.subheader("Brand rule coverage")

        rules = get_brand_rules()

        restricted = sum(
            1 for rule in rules if rule[0] == "Restricted Word"
        )
        preferred = sum(
            1 for rule in rules if rule[0] == "Preferred Word"
        )

        st.markdown(f"""
        <div class="pm-card">
            <div class="pm-card-title">Configured guidelines</div>
            <h2 style="color:#159989 !important;">{len(rules)}</h2>
            <p class="pm-muted">Total active terminology rules</p>
            <div class="section-line"></div>
            <p>🔴 Restricted terms: <b>{restricted}</b></p>
            <p>🟢 Preferred terms: <b>{preferred}</b></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-line'></div>",
                unsafe_allow_html=True)

    st.subheader("Recent review decisions")

    history = get_audit_history(limit=5)

    if history:
        recent_df = pd.DataFrame(
            history,
            columns=[
                "ID", "Issue", "Original Word", "Replacement",
                "Decision", "Original Content", "Corrected Content",
                "Reviewed At", "Severity", "Reviewer"
            ]
        )

        st.dataframe(
            recent_df[
                ["ID", "Issue", "Decision", "Severity",
                 "Reviewer", "Reviewed At"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No review decisions yet. Start in the Review Studio.")


# ==========================================================
# REVIEW STUDIO
# ==========================================================

elif selected_page == "Review Studio":

    page_heading(
        "CONTENT INTELLIGENCE",
        "Review Studio",
        "Check your content against your brand's terminology guidelines."
    )

    st.markdown("""
    <div class="pm-card">
        <div class="pm-card-title">Your content, your brand standards.</div>
        <p class="pm-muted">
            Upload a document or paste your content.
            Pressmark identifies configured terminology issues
            and provides suggestions for human review.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["pdf", "docx"],
        key="document_upload"
    )

    extracted_text = ""

    if uploaded_file is not None:
        try:
            extracted_text = extract_document(uploaded_file)

            if extracted_text.strip():
                st.success(
                    f"Successfully extracted text from {uploaded_file.name}"
                )

                with st.expander("Preview extracted document"):
                    st.text(extracted_text)
            else:
                st.warning("No readable text was found in this document.")

        except Exception as error:
            st.error(f"Document extraction failed: {error}")

    content = st.text_area(
        "CONTENT EDITOR",
        value=extracted_text,
        height=220,
        placeholder="Start writing or paste your brand content here..."
    )

    check_button = st.button(
        "✳ Analyse brand content",
        type="primary",
        use_container_width=True
    )

    if check_button:
        if content.strip():
            st.session_state.review_id += 1
            st.session_state.review_content = content
            st.session_state.audit_saved = set()
            st.session_state.corrected_content = ""

            restricted, preferred, _ = load_rules()

            issues = check_brand_content(
                content,
                restricted,
                preferred
            )

            try:
                ai_issues = analyze_with_groq(
                    content,
                    st.secrets["GROQ_API_KEY"],
                    [
                        f"{p[1]} - {p[2]}: {p[3]}"
                        for p in get_brand_policies()
                    ]
                )

                filtered_ai_issues = remove_duplicate_ai_issues(
                    issues,
                    ai_issues
                )

                issues.extend(filtered_ai_issues)

                st.success("Context-aware AI analysis completed.")

            except Exception as e:
                st.error(f"Groq connection error: {e}")
                st.warning("Showing rule-based results instead.")

            st.session_state.review_issues = issues
            st.session_state.review_has_run = True

        else:
            st.warning("Please enter some content first.")

    if st.session_state.review_has_run:

        issues = st.session_state.review_issues
        original_content = st.session_state.review_content

        st.subheader("Analysis results")

        st.markdown("### Reviewer information")

        reviewer_name = st.text_input(
            "Reviewer name",
            value=st.session_state.reviewer_name,
            placeholder="Enter the name of the person reviewing this content",
            key="reviewer_name_input"
        )

        st.session_state.reviewer_name = reviewer_name.strip()

        if not issues:
            if get_brand_rules():
                st.success("No configured terminology violations found.")
                st.caption(
                    "This result reflects configured rules only. "
                    "It is not a guarantee of full brand compliance."
                )
            else:
                st.info(
                    "No brand rules are configured. "
                    "Add guidelines before evaluating content."
                )

        else:
            high_count = sum(
                1 for issue in issues
                if issue.get("severity") == "High"
            )

            medium_count = sum(
                1 for issue in issues
                if issue.get("severity") == "Medium"
            )

            compliance_score = max(
                0,
                100 - (high_count * 20) - (medium_count * 10)
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                metric_card("COMPLIANCE SCORE", f"{compliance_score}/100")

            with col2:
                metric_card("TOTAL FLAGS", len(issues))

            with col3:
                metric_card("HIGH SEVERITY", high_count)

            with col4:
                metric_card("MEDIUM SEVERITY", medium_count)

            st.progress(compliance_score / 100)

            st.caption(
                "Illustrative score based on configured terminology flags, "
                "not a measured percentage of overall brand compliance."
            )

            if compliance_score >= 80:
                st.success("Strong terminology compliance.")
            elif compliance_score >= 50:
                st.warning("Some brand terminology improvements are needed.")
            else:
                st.error("Several brand terminology issues need attention.")

            st.markdown("<div class='section-line'></div>",
                        unsafe_allow_html=True)

            restricted, preferred, restricted_replacements = load_rules()

            review_decisions = []

            st.subheader("Human review")

            st.caption(
                "Review each suggestion and decide whether to accept or reject it."
            )

            for index, issue in enumerate(issues):

                severity = issue.get("severity", "Unknown")

                if severity == "High":
                    st.error(f"🔴 HIGH SEVERITY · {issue['issue']}")
                elif severity == "Medium":
                    st.warning(f"🟠 MEDIUM SEVERITY · {issue['issue']}")
                else:
                    st.info(f"LOW SEVERITY · {issue['issue']}")

                st.markdown(f"""
                <div class="pm-card">
                    <div class="pm-card-title">Why this was flagged</div>
                    <p>{html.escape(str(issue.get('reason', '')))}</p>
                    <div class="pm-card-title">Recommended action</div>
                    <p>{html.escape(str(issue.get('suggestion', '')))}</p>
                </div>
                """, unsafe_allow_html=True)

                decision = st.radio(
                    "Your decision",
                    [
                        "Pending",
                        "Accept suggestion",
                        "Reject suggestion"
                    ],
                    horizontal=True,
                    key=f"decision_{st.session_state.review_id}_{index}"
                )

                original_word, replacement_word = get_issue_words(
                    issue,
                    preferred,
                    restricted_replacements
                )

                review_decisions.append({
                    "issue": issue["issue"],
                    "original_word": original_word,
                    "replacement": replacement_word,
                    "decision": decision,
                    "severity": severity
                })

                st.divider()

            corrected_content = build_corrected_content(
                original_content,
                review_decisions
            )

            st.session_state.corrected_content = corrected_content

            accepted_count = sum(
                1 for item in review_decisions
                if item["decision"] == "Accept suggestion"
            )

            rejected_count = sum(
                1 for item in review_decisions
                if item["decision"] == "Reject suggestion"
            )

            pending_count = sum(
                1 for item in review_decisions
                if item["decision"] == "Pending"
            )

            st.subheader("Review progress")

            st.write(
                f"Accepted: **{accepted_count}** · "
                f"Rejected: **{rejected_count}** · "
                f"Pending: **{pending_count}**"
            )

            for index, item in enumerate(review_decisions):

                decision = item["decision"]
                audit_key = (st.session_state.review_id, index)

                if (
                    decision != "Pending"
                    and audit_key not in st.session_state.audit_saved
                ):

                    if not st.session_state.reviewer_name:
                        st.warning(
                            "Enter a reviewer name before saving decisions."
                        )
                        continue

                    save_review_audit(
                        issue=item["issue"],
                        original_word=item["original_word"],
                        replacement=item["replacement"],
                        decision=(
                            "Accepted"
                            if decision == "Accept suggestion"
                            else "Rejected"
                        ),
                        original_content=original_content,
                        corrected_content=corrected_content,
                        severity=item["severity"],
                        reviewer=st.session_state.reviewer_name
                    )

                    st.session_state.audit_saved.add(audit_key)

            if corrected_content != original_content:

                st.markdown("<div class='section-line'></div>",
                            unsafe_allow_html=True)

                st.subheader("Content comparison")

                before, after = st.columns(2)

                with before:
                    st.markdown("**ORIGINAL CONTENT**")
                    st.text_area(
                        "Original",
                        value=original_content,
                        height=200,
                        disabled=True,
                        key=f"before_{st.session_state.review_id}"
                    )

                with after:
                    st.markdown("**CORRECTED CONTENT**")
                    st.text_area(
                        "Corrected",
                        value=corrected_content,
                        height=200,
                        key=f"after_{st.session_state.review_id}"
                    )

                st.download_button(
                    "⬇ Download corrected content",
                    data=corrected_content,
                    file_name="pressmark_corrected_content.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.caption(
                    "Review the corrected version for grammar, meaning "
                    "and context before publishing."
                )

            else:
                st.info(
                    "Accept at least one available suggestion "
                    "to generate corrected content."
                )


# ==========================================================
# ADVANCED ANALYTICS
# ==========================================================

elif selected_page == "Analytics":

    page_heading(
        "PERFORMANCE INTELLIGENCE",
        "Advanced analytics",
        "Understand review decisions, recurring issues and reviewer activity."
    )

    analytics = get_analytics_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("TOTAL DECISIONS", analytics["total"])

    with col2:
        metric_card("ACCEPTED", analytics["accepted"])

    with col3:
        metric_card("REJECTED", analytics["rejected"])

    with col4:
        metric_card("ACCEPTANCE RATE", f"{analytics['acceptance_rate']}%")

    st.markdown("<div class='section-line'></div>",
                unsafe_allow_html=True)

    if analytics["total"] == 0:
        st.info(
            "Analytics will appear here after reviewers make decisions "
            "in the Review Studio."
        )

    else:
        left, right = st.columns(2)

        with left:
            st.subheader("Decision distribution")

            decision_df = pd.DataFrame({
                "Decision": ["Accepted", "Rejected"],
                "Count": [
                    analytics["accepted"],
                    analytics["rejected"]
                ]
            })

            st.bar_chart(
                decision_df.set_index("Decision"),
                color="#18A999"
            )

        with right:
            st.subheader("Severity distribution")

            severity_rows = get_severity_distribution()

            if severity_rows:
                severity_df = pd.DataFrame(
                    severity_rows,
                    columns=["Severity", "Count"]
                )

                st.bar_chart(
                    severity_df.set_index("Severity")
                )
            else:
                st.info("No severity data is available yet.")

        st.markdown("<div class='section-line'></div>",
                    unsafe_allow_html=True)

        left, right = st.columns(2)

        with left:
            st.subheader("Frequently flagged terms")

            term_rows = get_top_flagged_terms()

            if term_rows:
                terms_df = pd.DataFrame(
                    term_rows,
                    columns=["Term", "Occurrences"]
                )

                st.bar_chart(
                    terms_df.set_index("Term"),
                    color="#18A999"
                )
            else:
                st.info("No flagged-term data is available.")

        with right:
            st.subheader("Review activity over time")

            activity_rows = get_review_activity()

            if activity_rows:
                activity_df = pd.DataFrame(
                    activity_rows,
                    columns=["Date", "Reviews"]
                )

                activity_df["Date"] = pd.to_datetime(
                    activity_df["Date"]
                )

                activity_df = activity_df.set_index("Date")

                st.line_chart(
                    activity_df,
                    color="#18A999"
                )
            else:
                st.info("No review activity is available.")

        st.markdown("<div class='section-line'></div>",
                    unsafe_allow_html=True)

        st.subheader("Reviewer activity")

        reviewer_rows = get_reviewer_stats()

        if reviewer_rows:
            reviewer_df = pd.DataFrame(
                reviewer_rows,
                columns=[
                    "Reviewer",
                    "Total Reviews",
                    "Accepted",
                    "Rejected"
                ]
            )

            st.dataframe(
                reviewer_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "Reviewer statistics will appear after decisions "
                "are saved with reviewer names."
            )

        st.caption(
            "Analytics are based on saved review decisions. "
            "Pending choices are not stored as audit decisions."
        )


# ==========================================================
# BRAND RULES
# ==========================================================

elif selected_page == "Brand Rules":

    page_heading(
        "BRAND CONFIGURATION",
        "Brand rules",
        "Manage the terminology your content should follow."
    )

    rules = get_brand_rules()

    restricted_count = sum(
        1 for rule in rules if rule[0] == "Restricted Word"
    )

    preferred_count = sum(
        1 for rule in rules if rule[0] == "Preferred Word"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("TOTAL RULES", len(rules))

    with col2:
        metric_card("RESTRICTED TERMS", restricted_count)

    with col3:
        metric_card("PREFERRED TERMS", preferred_count)

    st.markdown("<div class='section-line'></div>",
                unsafe_allow_html=True)

    left, right = st.columns([1, 1.3])

    with left:

        st.subheader("Create a new rule")

        with st.form("new_brand_rule_form"):

            rule_type = st.selectbox(
                "Rule category",
                ["Restricted Word", "Preferred Word"]
            )

            original_word = st.text_input(
                "Term to check",
                placeholder="Example: cheap"
            )

            replacement = st.text_input(
                "Approved replacement",
                placeholder="Example: affordable"
            )

            submitted = st.form_submit_button(
                "Save brand rule",
                use_container_width=True
            )

            if submitted:

                if original_word.strip():

                    add_brand_rule(
                        rule_type,
                        original_word.strip(),
                        replacement.strip()
                    )

                    st.success("Brand rule saved successfully.")
                    st.rerun()

                else:
                    st.warning("Please enter a term before saving.")

        st.caption(
            "Rule category and severity are automatically assigned "
            "based on the selected rule type."
        )

    with right:

        st.subheader("Configured guidelines")

        if rules:

            for index, (rule_type, word, replacement) in enumerate(rules, 1):

                details = get_rule_details(
                    rule_type,
                    word,
                    replacement
                )

                safe_word = html.escape(word)
                safe_replacement = html.escape(
                    replacement or "Not specified"
                )
                safe_explanation = html.escape(details["explanation"])
                safe_bad = html.escape(details["bad_example"])
                safe_good = html.escape(details["good_example"])

                if rule_type == "Restricted Word":
                    type_badge = (
                        "<span class='rule-restricted'>RESTRICTED</span>"
                    )
                    severity_badge = (
                        "<span class='rule-high'>HIGH SEVERITY</span>"
                    )
                else:
                    type_badge = (
                        "<span class='rule-preferred'>PREFERRED</span>"
                    )
                    severity_badge = (
                        "<span class='rule-medium'>MEDIUM SEVERITY</span>"
                    )

                st.html(f"""
                <div class="pm-card">

                    <div style="margin-bottom:12px;">
                        {type_badge}
                        <span class="rule-category">
                            {details['category'].upper()}
                        </span>
                        {severity_badge}
                    </div>

                    <div class="pm-card-title">
                        {index:02d}. {safe_word}
                    </div>

                    <p class="pm-muted">
                        Approved replacement: <b>{safe_replacement}</b>
                    </p>

                    <div class="section-line"></div>

                    <b>Why this rule exists</b>
                    <p>{safe_explanation}</p>

                    <div class="example-box">
                        <b>Example — Avoid</b><br>
                        {safe_bad}
                    </div>

                    <div class="example-box">
                        <b>Example — Preferred</b><br>
                        {safe_good}
                    </div>

                </div>
                """)

        else:
            st.info("No brand rules have been configured.")

    st.markdown("<div class='section-line'></div>",
                unsafe_allow_html=True)

    st.subheader("Understanding rule classifications")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="pm-card">
            <span class="rule-restricted">RESTRICTED</span>
            <span class="rule-high">HIGH</span>
            <div class="pm-card-title" style="margin-top:12px;">
                Restricted terminology
            </div>
            <p class="pm-muted">
                Words that violate the configured brand vocabulary.
                Pressmark flags these and suggests an approved replacement.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pm-card">
            <span class="rule-preferred">PREFERRED</span>
            <span class="rule-medium">MEDIUM</span>
            <div class="pm-card-title" style="margin-top:12px;">
                Preferred terminology
            </div>
            <p class="pm-muted">
                Words that can be replaced with terminology
                preferred by the brand for consistency.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        "These classifications are currently assigned by rule type. "
        "Custom severity levels and rule IDs can be added later."
    )


# ==========================================================
# BRAND POLICIES
# ==========================================================

elif selected_page == "Brand Policies":

    page_heading(
        "BRAND GOVERNANCE",
        "Brand Policies",
        "Create and manage guidelines for consistent brand communication."
    )

    st.subheader("Add a new policy")

    with st.form("add_brand_policy_form"):

        policy_category = st.selectbox(
            "Policy category",
            [
                "Tone of Voice",
                "Writing Style",
                "Disclaimers",
                "Organizational Policy"
            ]
        )

        policy_title = st.text_input(
            "Policy title",
            placeholder="Example: Professional communication"
        )

        policy_description = st.text_area(
            "Policy description",
            placeholder="Describe the brand guideline...",
            height=150,
            key="policy_description_input"
        )

        submitted = st.form_submit_button(
            "Save Policy",
            use_container_width=True
        )

        if submitted:

            if policy_title.strip() and policy_description.strip():

                add_brand_policy(
                    policy_category,
                    policy_title.strip(),
                    policy_description.strip()
                )

                st.success("Brand policy saved successfully!")
                st.rerun()

            else:
                st.warning(
                    "Please enter both a title and description."
                )

    st.markdown(
        "<div class='section-line'></div>",
        unsafe_allow_html=True
    )

    st.subheader("Saved brand policies")

    policies = get_brand_policies()

    if policies:

        for policy in policies:

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(f"**{policy[2]}**")
                st.caption(policy[1])
                st.write(policy[3])

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_policy_{policy[0]}"
                ):
                    delete_brand_policy(policy[0])
                    st.rerun()

            st.divider()

    else:

        st.info("No brand policies added yet.")


# ==========================================================
# AUDIT LOGS
# ==========================================================

elif selected_page == "Audit Logs":

    page_heading(
        "ACCOUNTABILITY",
        "Audit logs",
        "Track previous content reviews and human decisions."
    )

    history = get_audit_history()

    if history:

        columns = [
            "ID", "Issue", "Original Word", "Replacement",
            "Decision", "Original Content", "Corrected Content",
            "Reviewed At", "Severity", "Reviewer"
        ]

        history_df = pd.DataFrame(history, columns=columns)

        accepted = sum(
            1 for item in history if item[4] == "Accepted"
        )

        rejected = sum(
            1 for item in history if item[4] == "Rejected"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card("AUDIT RECORDS", len(history))

        with col2:
            metric_card("ACCEPTED", accepted)

        with col3:
            metric_card("REJECTED", rejected)

        st.markdown("<div class='section-line'></div>",
                    unsafe_allow_html=True)

        st.subheader("Decision history")

        display_df = history_df.drop(
            columns=["Original Content", "Corrected Content"]
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<div class='section-line'></div>",
                    unsafe_allow_html=True)

        st.subheader("Inspect a review")

        selected_id = st.selectbox(
            "Select audit record",
            history_df["ID"].tolist()
        )

        selected_record = history_df[
            history_df["ID"] == selected_id
        ].iloc[0]

        st.markdown(f"""
        <div class="pm-card">
            <div class="pm-card-title">
                Review #{selected_record['ID']}
            </div>
            <p><b>Issue:</b> {html.escape(str(selected_record['Issue']))}</p>
            <p><b>Decision:</b> {html.escape(str(selected_record['Decision']))}</p>
            <p><b>Replacement:</b> {html.escape(str(selected_record['Replacement']))}</p>
            <p><b>Severity:</b> {html.escape(str(selected_record['Severity']))}</p>
            <p><b>Reviewer:</b> {html.escape(str(selected_record['Reviewer']))}</p>
            <p class="pm-muted">
                Reviewed at: {html.escape(str(selected_record['Reviewed At']))}
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.text_area(
                "Original content",
                value=selected_record["Original Content"] or "",
                height=180,
                disabled=True,
                key=f"audit_original_{selected_id}"
            )

        with col2:
            st.text_area(
                "Corrected content",
                value=selected_record["Corrected Content"] or "",
                height=180,
                disabled=True,
                key=f"audit_corrected_{selected_id}"
            )

        csv_data = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Export complete audit history",
            data=csv_data,
            file_name="pressmark_audit_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        st.info(
            "No audit records are available yet. "
            "Complete a content review to create your first record."
        )


# ==========================================================
# FOOTER
# ==========================================================

st.markdown("""
<div class="footer">
    ✳ PRESSMARK 2.0 · Brand Intelligence & Governance
    <br>
    Built for more consistent, accountable content reviews.
</div>
""", unsafe_allow_html=True)
