

import re
import pandas as pd
import streamlit as st
import pdfplumber

from docx import Document

from database import (
    initialize_db,
    get_brand_rules,
    add_brand_rule,
    delete_brand_rule,
    save_review_audit,
    get_audit_history,
    get_dashboard_stats
)

from brand_checker import check_brand_content


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Pressmark | Brand Governance",
    page_icon="📝",
    layout="wide"
)

initialize_db()


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 25px;
        border-radius: 14px;
        background: linear-gradient(120deg, #142d4e, #247b83);
        color: white;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 5px;
    }

    .hero p {
        color: #e5f5f5;
        margin-bottom: 0;
    }

    .small-note {
        color: #64748b;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>📝 Pressmark</h1>
    <p>Catching brand mistakes before they go live.</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD BRAND RULES
# --------------------------------------------------

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


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "review_issues" not in st.session_state:
    st.session_state.review_issues = []

if "review_has_run" not in st.session_state:
    st.session_state.review_has_run = False

if "review_content" not in st.session_state:
    st.session_state.review_content = ""

if "review_id" not in st.session_state:
    st.session_state.review_id = 0

if "audit_saved" not in st.session_state:
    st.session_state.audit_saved = set()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("⚙️ Pressmark")

    st.caption("Brand Governance Workspace")

    st.divider()

    st.subheader("Add Brand Rule")

    rule_type = st.selectbox(
        "Rule category",
        ["Restricted Word", "Preferred Word"]
    )

    original_word = st.text_input(
        "Word to check"
    )

    replacement = st.text_input(
        "Approved replacement",
        help="Leave empty if the word should simply be removed."
    )

    if st.button("Save Brand Rule", use_container_width=True):

        if original_word.strip():

            add_brand_rule(
                rule_type,
                original_word.strip(),
                replacement.strip()
            )

            st.success("Brand rule saved!")

            st.rerun()

        else:

            st.warning("Please enter a word.")

    st.divider()

    st.subheader("Current Brand Rules")

    current_rules = get_brand_rules()

    if current_rules:

        for rule, word, new_word in current_rules:

            if new_word:
                st.write(f"**{word}** → {new_word}")
            else:
                st.write(f"**{word}** · {rule}")

    else:

        st.caption("No brand rules added yet.")


# --------------------------------------------------
# NAVIGATION TABS
# --------------------------------------------------

dashboard_tab, review_tab, history_tab = st.tabs([
    "📊 Dashboard",
    "📝 Content Review",
    "📚 Audit History"
])


# ==================================================
# DASHBOARD
# ==================================================

with dashboard_tab:

    st.subheader("Dashboard")

    st.write(
        "Monitor brand reviews and human review decisions."
    )

    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Reviewed Content",
        stats["reviewed_content"]
    )

    col2.metric(
        "Total Decisions",
        stats["total_decisions"]
    )

    col3.metric(
        "Accepted",
        stats["accepted"]
    )

    col4.metric(
        "Rejected",
        stats["rejected"]
    )

    st.divider()

    st.subheader("Brand Governance Overview")

    if stats["total_decisions"] > 0:

        chart_data = pd.DataFrame({
            "Decision": ["Accepted", "Rejected"],
            "Count": [
                stats["accepted"],
                stats["rejected"]
            ]
        })

        st.bar_chart(
            chart_data.set_index("Decision")
        )

    else:

        st.info(
            "Your review statistics will appear here "
            "after the first completed review."
        )

    st.caption(
        "Statistics are calculated from saved human review decisions."
    )


# ==================================================
# CONTENT REVIEW
# ==================================================

with review_tab:

    st.subheader("📄 Upload and Review Content")

    st.write(
        "Upload a document or paste content to check it "
        "against your brand guidelines."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF or Word document",
        type=["pdf", "docx"],
        key="document_upload"
    )

    extracted_text = ""

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".pdf"):

                with pdfplumber.open(uploaded_file) as pdf:

                    extracted_text = "\n".join(
                        page.extract_text() or ""
                        for page in pdf.pages
                    )

            elif uploaded_file.name.lower().endswith(".docx"):

                document = Document(uploaded_file)

                extracted_text = "\n".join(
                    paragraph.text
                    for paragraph in document.paragraphs
                )

            if extracted_text.strip():

                st.success("Document extracted successfully!")

                with st.expander("View extracted content"):

                    st.text(extracted_text)

            else:

                st.warning(
                    "No readable text was found in this document."
                )

        except Exception as error:

            st.error(
                f"Could not read the document: {error}"
            )

    content = st.text_area(
        "Your brand content",
        value=extracted_text,
        height=200,
        placeholder="Example: Our products are cheap. Get the best deals today!"
    )

    if st.button(
        "🔍 Check My Content",
        type="primary",
        use_container_width=True
    ):

        if content.strip():

            # Clear previous review decisions
            for index in range(
                len(st.session_state.review_issues)
            ):

                st.session_state.pop(
                    f"review_decision_{index}",
                    None
                )

            st.session_state.review_id += 1
            st.session_state.audit_saved = set()

            st.session_state.review_content = content

            restricted, preferred, _ = load_rules()

            st.session_state.review_issues = check_brand_content(
                content,
                restricted,
                preferred
            )

            st.session_state.review_has_run = True

        else:

            st.warning("Please enter some content first.")

    # ----------------------------------------------
    # DISPLAY REVIEW RESULTS
    # ----------------------------------------------

    if st.session_state.review_has_run:

        issues = st.session_state.review_issues

        original_content = st.session_state.review_content

        st.divider()

        st.subheader("Review Results")

        if issues:

            high_count = sum(
                1 for issue in issues
                if issue["severity"] == "High"
            )

            medium_count = sum(
                1 for issue in issues
                if issue["severity"] == "Medium"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Issues", len(issues))
            col2.metric("High Severity", high_count)
            col3.metric("Medium Severity", medium_count)

            st.divider()

            restricted, preferred, restricted_replacements = (
                load_rules()
            )

            review_decisions = []

            # --------------------------------------
            # HUMAN REVIEW
            # --------------------------------------

            for index, issue in enumerate(issues):

                if issue["severity"] == "High":

                    st.error(
                        f"🔴 HIGH SEVERITY — {issue['issue']}"
                    )

                elif issue["severity"] == "Medium":

                    st.warning(
                        f"🟠 MEDIUM SEVERITY — {issue['issue']}"
                    )

                else:

                    st.info(
                        f"LOW SEVERITY — {issue['issue']}"
                    )

                st.write(
                    f"**Why flagged:** {issue['reason']}"
                )

                st.write(
                    f"**Suggestion:** {issue['suggestion']}"
                )

                decision = st.radio(
                    "Human Review Decision",
                    [
                        "Pending",
                        "Accept suggestion",
                        "Reject suggestion"
                    ],
                    horizontal=True,
                    key=f"review_decision_{index}"
                )

                original_word = ""
                replacement_word = ""

                if issue["issue"].startswith(
                    "Restricted word found: "
                ):

                    original_word = issue["issue"].replace(
                        "Restricted word found: ",
                        "",
                        1
                    )

                    replacement_word = next(
                        (
                            value
                            for key, value in restricted_replacements.items()
                            if key.lower() == original_word.lower()
                        ),
                        ""
                    )

                elif issue["issue"].startswith("Use of '"):

                    original_word = issue["issue"].split("'")[1]

                    replacement_word = next(
                        (
                            value
                            for key, value in preferred.items()
                            if key.lower() == original_word.lower()
                        ),
                        ""
                    )

                review_decisions.append({
                    "issue": issue["issue"],
                    "original_word": original_word,
                    "replacement": replacement_word,
                    "decision": decision
                })

                if decision == "Accept suggestion":

                    st.success("Suggestion accepted.")

                elif decision == "Reject suggestion":

                    st.info("Suggestion rejected.")

                else:

                    st.caption("Awaiting your decision.")

                st.divider()

            # --------------------------------------
            # APPLY ACCEPTED SUGGESTIONS
            # --------------------------------------

            corrected_content = original_content

            for item in review_decisions:

                if item["decision"] != "Accept suggestion":
                    continue

                word = item["original_word"]
                replacement_word = item["replacement"]

                if word:

                    corrected_content = re.sub(
                        rf"\b{re.escape(word)}\b",
                        lambda match: replacement_word,
                        corrected_content,
                        flags=re.IGNORECASE
                    )

            corrected_content = re.sub(
                r"\s+([.,!?;:])",
                r"\1",
                corrected_content
            )

            corrected_content = re.sub(
                r" {2,}",
                " ",
                corrected_content
            ).strip()

            # --------------------------------------
            # SAVE AUDIT DECISIONS
            # --------------------------------------

            for index, item in enumerate(review_decisions):

                decision = item["decision"]

                audit_key = (
                    st.session_state.review_id,
                    index
                )

                if (
                    decision != "Pending"
                    and audit_key not in st.session_state.audit_saved
                ):

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
                        corrected_content=corrected_content
                    )

                    st.session_state.audit_saved.add(audit_key)

            # --------------------------------------
            # CORRECTED PREVIEW
            # --------------------------------------

            if corrected_content != original_content:

                st.subheader("✨ Corrected Content")

                preview_key = (
                    f"corrected_preview_"
                    f"{st.session_state.review_id}"
                )

                st.session_state[preview_key] = corrected_content

                st.text_area(
                    "Review your corrected version",
                    height=150,
                    key=preview_key
                )

                st.download_button(
                    "⬇️ Download Corrected Content",
                    data=corrected_content,
                    file_name="pressmark_corrected_content.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.caption(
                    "Please review the grammar and meaning "
                    "before using the corrected content."
                )

            else:

                st.info(
                    "Accept a suggestion to generate corrected content."
                )

        else:
            configured_rules = get_brand_rules()

            if not configured_rules:
                st.info(
                    "No rules configured yet. Add brand rules in the sidebar "
                    "before checking whether content follows your guidelines."
                )
            else:
                st.success(
                    "🎉 No brand guideline violations found!"
                )

                st.write(
                    "Your content passed the current brand rule checks."
                )


# ==================================================
# AUDIT HISTORY
# ==================================================

with history_tab:

    st.subheader("📚 Review Audit History")

    st.write(
        "View the decisions made during previous content reviews."
    )

    history = get_audit_history()

    if history:

        columns = [
            "ID",
            "Issue",
            "Original Word",
            "Replacement",
            "Decision",
            "Original Content",
            "Corrected Content",
            "Reviewed At"
        ]

        history_df = pd.DataFrame(
            history,
            columns=columns
        )

        display_df = history_df.drop(
            columns=["Original Content", "Corrected Content"]
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Review Details")

        selected_id = st.selectbox(
            "Choose an audit record",
            history_df["ID"].tolist()
        )

        selected_record = history_df[
            history_df["ID"] == selected_id
        ].iloc[0]

        st.write(
            f"**Issue:** {selected_record['Issue']}"
        )

        st.write(
            f"**Decision:** {selected_record['Decision']}"
        )

        st.write(
            f"**Replacement:** {selected_record['Replacement']}"
        )

        st.text_area(
            "Original Content",
            value=selected_record["Original Content"] or "",
            height=120,
            disabled=True
        )

        st.text_area(
            "Corrected Content",
            value=selected_record["Corrected Content"] or "",
            height=120,
            disabled=True
        )

        csv_data = history_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Export Audit History (CSV)",
            data=csv_data,
            file_name="pressmark_audit_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:

        st.info(
            "No audit records found yet. "
            "Complete a content review to create your first record."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    "<p class='small-note' style='text-align:center;'>"
    "Pressmark | AI Brand Governance Assistant"
    "</p>",
    unsafe_allow_html=True
)
