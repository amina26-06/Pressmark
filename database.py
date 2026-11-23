
import os
import sqlite3

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "pressmark.db"
)


def get_connection():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    return sqlite3.connect(DB_NAME)


def initialize_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_type TEXT NOT NULL,
            original_word TEXT NOT NULL,
            replacement TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue TEXT NOT NULL,
            original_word TEXT,
            replacement TEXT,
            decision TEXT NOT NULL,
            original_content TEXT,
            corrected_content TEXT,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT DEFAULT 'Unknown',
            reviewer TEXT DEFAULT 'Unassigned'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_category TEXT NOT NULL,
            policy_title TEXT NOT NULL,
            policy_description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safely upgrade existing databases without deleting records.
    existing_columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(review_audit)").fetchall()
    ]

    if "severity" not in existing_columns:
        conn.execute("""
            ALTER TABLE review_audit
            ADD COLUMN severity TEXT DEFAULT 'Unknown'
        """)

    if "reviewer" not in existing_columns:
        conn.execute("""
            ALTER TABLE review_audit
            ADD COLUMN reviewer TEXT DEFAULT 'Unassigned'
        """)

    default_rules = [
        ("Restricted Word", "cheap", "affordable"),
        ("Restricted Word", "guaranteed", "reliable"),
        ("Restricted Word", "best in the world", "high-quality"),
        ("Preferred Word", "deals", "offers")
    ]

    for rule_type, word, replacement in default_rules:
        existing = conn.execute("""
            SELECT id FROM brand_rules
            WHERE LOWER(rule_type) = LOWER(?)
            AND LOWER(original_word) = LOWER(?)
        """, (rule_type, word)).fetchone()

        if not existing:
            conn.execute("""
                INSERT INTO brand_rules
                (rule_type, original_word, replacement)
                VALUES (?, ?, ?)
            """, (rule_type, word, replacement))

    conn.commit()
    conn.close()


# --------------------------------------------------
# BRAND RULES
# --------------------------------------------------

def get_brand_rules():
    conn = get_connection()

    rows = conn.execute("""
        SELECT rule_type, original_word, replacement
        FROM brand_rules
        ORDER BY id
    """).fetchall()

    conn.close()
    return rows


def add_brand_rule(rule_type, original_word, replacement=""):
    conn = get_connection()

    existing = conn.execute("""
        SELECT id FROM brand_rules
        WHERE LOWER(rule_type) = LOWER(?)
        AND LOWER(original_word) = LOWER(?)
    """, (rule_type, original_word)).fetchone()

    if existing:
        conn.execute("""
            UPDATE brand_rules
            SET replacement = ?
            WHERE id = ?
        """, (replacement, existing[0]))
    else:
        conn.execute("""
            INSERT INTO brand_rules
            (rule_type, original_word, replacement)
            VALUES (?, ?, ?)
        """, (rule_type, original_word, replacement))

    conn.commit()
    conn.close()


def delete_brand_rule(rule_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM brand_rules WHERE id = ?",
        (rule_id,)
    )

    conn.commit()
    conn.close()


# --------------------------------------------------
# REVIEW AUDIT
# --------------------------------------------------

def save_review_audit(
    issue,
    original_word,
    replacement,
    decision,
    original_content,
    corrected_content,
    severity="Unknown",
    reviewer="Unassigned"
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO review_audit (
            issue,
            original_word,
            replacement,
            decision,
            original_content,
            corrected_content,
            severity,
            reviewer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        issue,
        original_word,
        replacement,
        decision,
        original_content,
        corrected_content,
        severity,
        reviewer
    ))

    conn.commit()
    conn.close()


def get_audit_history(limit=500):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            issue,
            original_word,
            replacement,
            decision,
            original_content,
            corrected_content,
            reviewed_at,
            severity,
            reviewer
        FROM review_audit
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return rows


# --------------------------------------------------
# DASHBOARD STATISTICS
# --------------------------------------------------

def get_dashboard_stats():
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM review_audit"
    ).fetchone()[0]

    accepted = conn.execute("""
        SELECT COUNT(*) FROM review_audit
        WHERE decision = 'Accepted'
    """).fetchone()[0]

    rejected = conn.execute("""
        SELECT COUNT(*) FROM review_audit
        WHERE decision = 'Rejected'
    """).fetchone()[0]

    unique_content = conn.execute("""
        SELECT COUNT(DISTINCT original_content)
        FROM review_audit
    """).fetchone()[0]

    conn.close()

    return {
        "total_decisions": total,
        "accepted": accepted,
        "rejected": rejected,
        "reviewed_content": unique_content
    }


# --------------------------------------------------
# ADVANCED ANALYTICS
# --------------------------------------------------

def get_analytics_stats():
    conn = get_connection()

    total = conn.execute("""
        SELECT COUNT(*) FROM review_audit
    """).fetchone()[0]

    accepted = conn.execute("""
        SELECT COUNT(*) FROM review_audit
        WHERE decision = 'Accepted'
    """).fetchone()[0]

    rejected = conn.execute("""
        SELECT COUNT(*) FROM review_audit
        WHERE decision = 'Rejected'
    """).fetchone()[0]

    pending = conn.execute("""
        SELECT COUNT(*) FROM review_audit
        WHERE decision = 'Pending'
    """).fetchone()[0]

    acceptance_rate = (
        round((accepted / (accepted + rejected)) * 100, 1)
        if accepted + rejected > 0
        else 0
    )

    conn.close()

    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "acceptance_rate": acceptance_rate
    }


def get_severity_distribution():
    conn = get_connection()

    rows = conn.execute("""
        SELECT severity, COUNT(*)
        FROM review_audit
        GROUP BY severity
        ORDER BY COUNT(*) DESC
    """).fetchall()

    conn.close()
    return rows


def get_top_flagged_terms(limit=10):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            COALESCE(NULLIF(original_word, ''), 'Other'),
            COUNT(*)
        FROM review_audit
        GROUP BY LOWER(original_word)
        ORDER BY COUNT(*) DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return rows


def get_review_activity():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            DATE(reviewed_at),
            COUNT(*)
        FROM review_audit
        GROUP BY DATE(reviewed_at)
        ORDER BY DATE(reviewed_at)
    """).fetchall()

    conn.close()
    return rows


def get_reviewer_stats():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            reviewer,
            COUNT(*) AS total_reviews,
            SUM(CASE WHEN decision = 'Accepted' THEN 1 ELSE 0 END),
            SUM(CASE WHEN decision = 'Rejected' THEN 1 ELSE 0 END)
        FROM review_audit
        GROUP BY reviewer
        ORDER BY total_reviews DESC
    """).fetchall()

    conn.close()
    return rows


# --------------------------------------------------
# BRAND POLICIES
# --------------------------------------------------

def add_brand_policy(
    policy_category,
    policy_title,
    policy_description
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO brand_policies (
            policy_category,
            policy_title,
            policy_description
        )
        VALUES (?, ?, ?)
    """, (
        policy_category,
        policy_title,
        policy_description
    ))

    conn.commit()
    conn.close()


def get_brand_policies():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            policy_category,
            policy_title,
            policy_description
        FROM brand_policies
        ORDER BY id DESC
    """).fetchall()

    conn.close()
    return rows


def delete_brand_policy(policy_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM brand_policies WHERE id = ?",
        (policy_id,)
    )

    conn.commit()
    conn.close()
