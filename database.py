
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
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


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


def save_review_audit(
    issue,
    original_word,
    replacement,
    decision,
    original_content,
    corrected_content
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO review_audit (
            issue,
            original_word,
            replacement,
            decision,
            original_content,
            corrected_content
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        issue,
        original_word,
        replacement,
        decision,
        original_content,
        corrected_content
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
            reviewed_at
        FROM review_audit
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return rows


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
