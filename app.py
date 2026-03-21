import datetime
import hashlib
import os
import re
import sqlite3
import smtplib
from collections import Counter
from email.message import EmailMessage
from io import BytesIO

import docx
import pdfplumber
import streamlit as st
from streamlit.components.v1 import html as st_html


APP_NAME = "CertHub"
DB_PATH = "certhub_users.db"
RAZORPAY_LINK = "https://razorpay.me/@harshshandilya"
CONTACT_EMAIL = "itscerthub@gmail.com"
CONTACT_PHONE = "+918603234533"
CONTACT_TEXT = f"Contact: {CONTACT_EMAIL} | {CONTACT_PHONE}"
INDIA_QR_PATH = os.path.join("assets", "india_qr.png")
MALAYSIA_QR_PATH = os.path.join("assets", "malaysia_qr.png")
NOTIFY_EMAIL = "harshshandilya01@gmail.com"

HEADINGS = [
    "name & contact",
    "professional summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]

SECTION_ALIASES = {
    "name & contact": ["name", "contact", "phone", "email", "linkedin", "github"],
    "professional summary": ["professional summary", "summary", "objective", "profile"],
    "skills": ["skills", "technical skills", "core skills", "competencies"],
    "experience": ["experience", "work experience", "employment", "internship"],
    "projects": ["projects", "academic projects", "personal projects"],
    "education": ["education", "academic background", "academics"],
    "certifications": ["certifications", "licenses"],
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "with", "at", "by",
    "as", "is", "are", "be", "from", "that", "this", "will", "you", "your", "our",
    "we", "it", "can", "should", "must", "into", "across", "using", "used", "role",
    "job", "work", "team", "teams", "ability", "experience", "years", "year",
}

TECH_PATTERNS = [
    "python", "java", "javascript", "typescript", "sql", "excel", "power bi", "tableau",
    "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git", "github", "flask",
    "fastapi", "django", "react", "node", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "nlp", "machine learning", "deep learning", "data analysis",
    "data visualization", "rest api", "agile", "scrum", "jira", "mongodb", "c++",
    "dsa", "algorithm", "oop", "html", "css",
]

SOFT_PATTERNS = [
    "communication", "problem solving", "analytical", "leadership",
    "collaboration", "stakeholder management", "time management",
]

ACTION_VERBS = {
    "built", "developed", "implemented", "designed", "optimized", "automated",
    "led", "created", "delivered", "analyzed", "improved", "reduced", "increased",
    "managed", "deployed", "integrated", "collaborated",
}

SERVICES = [
    {
        "name": "Certificate Assistance",
        "description": "Help obtaining certificates from HackerRank, Infosys Springboard, Google, Udemy and platform guidance.",
        "best_for": "Students needing verified certifications quickly.",
        "original_price": 599,
        "offer_price": 299,
        "delivery_time": "Up to 12 hrs",
    },
    {
        "name": "Portfolio Making",
        "description": "Custom portfolio website, mobile responsive, SEO optimized, professional layout, domain and hosting setup.",
        "best_for": "Missing project visibility and personal branding.",
        "original_price": 499,
        "offer_price": 199,
        "delivery_time": "24 hrs",
    },
    {
        "name": "LinkedIn Manager",
        "description": "Profile optimization, content strategy, network building, personal branding, post scheduling.",
        "best_for": "Better discoverability and personal brand.",
        "original_price": 399,
        "offer_price": 199,
        "delivery_time": "6 hrs",
    },
    {
        "name": "Presentation Making",
        "description": "Custom slides, data visualization, brand consistency, interactive elements, templates.",
        "best_for": "Interview rounds requiring project walkthroughs.",
        "original_price": 200,
        "offer_price": 100,
        "delivery_time": "30 min",
    },
    {
        "name": "Resume Making",
        "description": "ATS optimized resume, professional formatting, keyword optimization, cover letter included.",
        "best_for": "Low ATS score, weak structure, missing role keywords.",
        "original_price": 500,
        "offer_price": 200,
        "delivery_time": "6 hours",
    },
    {
        "name": "UI/UX Designer",
        "description": "User research, wireframes, prototyping, responsive design, usability testing.",
        "best_for": "Website/app projects needing stronger usability and visual quality.",
        "original_price": 599,
        "offer_price": 299,
        "delivery_time": "24 hrs",
    },
    {
        "name": "Basic Website Project",
        "description": "Custom design, mobile responsive, up to 5 pages, contact form, basic SEO.",
        "best_for": "Beginners building first portfolio-ready projects.",
        "original_price": 699,
        "offer_price": 369,
        "delivery_time": "48 hrs",
    },
    {
        "name": "Full Functional Website",
        "description": "Custom UI/UX, backend integration, database setup, hosting deployment.",
        "best_for": "Intermediate profile with deployment-ready project requirement.",
        "original_price": 2999,
        "offer_price": 999,
        "delivery_time": "1-2 days",
    },
    {
        "name": "Advanced Project (ML/AI)",
        "description": "ML model development, data preprocessing, training/testing, deployment ready.",
        "best_for": "Students targeting data or AI roles.",
        "original_price": 5499,
        "offer_price": 2999,
        "delivery_time": "5-7 days",
    },
    {
        "name": "Report Making",
        "description": "Technical reports for internships, projects, and case studies.",
        "best_for": "Academic and project submissions requiring formal documentation.",
        "original_price": 299,
        "offer_price": 149,
        "delivery_time": "6 hrs",
    },
]

NOTES = [
    {"title": "Python Notes (Up to Advanced)", "price_inr": 199, "topics": ["Python Fundamentals", "Data Structures", "OOP Concepts", "Advanced Python", "Libraries & Frameworks"]},
    {"title": "Java with DSA", "price_inr": 299, "topics": ["Java Fundamentals", "Data Structures", "Algorithms", "Problem Solving", "Interview Preparation"]},
    {"title": "HTML + CSS", "price_inr": 199, "topics": ["HTML5 Elements", "CSS3 Styling", "Responsive Design", "Flexbox & Grid", "Modern CSS"]},
    {"title": "SQL", "price_inr": 99, "topics": ["SQL Basics", "Database Design", "Query Optimization", "Joins & Subqueries", "Advanced SQL"]},
    {"title": "C++", "price_inr": 199, "topics": ["C++ Fundamentals", "OOP Concepts", "Data Structures", "Memory Management", "STL Library"]},
    {"title": "DAA (Design & Analysis of Algorithms)", "price_inr": 199, "topics": ["Algorithm Fundamentals", "Time & Space Complexity", "Sorting & Searching", "Dynamic Programming", "Graph Algorithms"]},
    {"title": "JavaScript", "price_inr": 99, "topics": ["JavaScript Fundamentals", "DOM Manipulation", "ES6+ Features", "Async Programming", "Modern JavaScript"]},
    {"title": "MongoDB", "price_inr": 99, "topics": ["MongoDB Fundamentals", "Database Design", "CRUD Operations", "Aggregation Framework", "Indexing & Performance"]},
    {"title": "Machine Learning", "price_inr": 369, "topics": ["ML Fundamentals", "Supervised Learning", "Unsupervised Learning", "Neural Networks", "Model Optimization"]},
]
MALAYSIA_RATE = 0.057  # Rough INR -> MYR display conversion


def inject_theme():
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at 20% 10%, #0f3d2b 0%, #071f17 40%, #03110d 100%);
            }
            .certhub-hero {
                border: 1px solid rgba(46, 204, 113, 0.25);
                border-radius: 20px;
                padding: 28px 24px;
                margin-bottom: 16px;
                background: linear-gradient(135deg, rgba(8,41,30,0.95), rgba(5,23,17,0.95));
            }
            .certhub-title {
                font-size: 2.2rem;
                line-height: 1.15;
                font-weight: 800;
                color: #2ee06f;
                margin: 0;
            }
            .certhub-subtitle {
                color: #b6c4bc;
                margin-top: 10px;
                font-size: 1.05rem;
            }
            .recommend-card {
                border: 2px solid #2ee06f;
                border-radius: 16px;
                padding: 18px;
                margin: 8px 0 16px 0;
                background: rgba(10, 44, 31, 0.95);
                box-shadow: 0 0 0 1px rgba(46, 224, 111, 0.2), 0 8px 24px rgba(0, 0, 0, 0.35);
            }
            .service-spotlight {
                border: 2px solid #2ee06f;
                border-radius: 18px;
                padding: 20px;
                margin-bottom: 18px;
                background: linear-gradient(135deg, rgba(18, 66, 46, 0.95), rgba(8, 33, 24, 0.95));
                box-shadow: 0 0 0 1px rgba(46, 224, 111, 0.25), 0 12px 28px rgba(0, 0, 0, 0.35);
            }
            .recommend-label {
                color: #9ff0bf;
                font-weight: 700;
                letter-spacing: 0.2px;
                font-size: 0.92rem;
                text-transform: uppercase;
            }
            .recommend-main {
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 900;
                margin: 6px 0;
            }
            .recommend-reason {
                color: #d2ddd7;
                font-size: 1rem;
            }
            .note-title {
                font-size: 1.3rem;
                font-weight: 900;
                color: #58f7a0;
                margin-bottom: 4px;
                letter-spacing: 0.1px;
            }
            .note-price {
                color: #e9fff3;
                font-weight: 700;
            }
            .service-title {
                font-size: 1.25rem;
                font-weight: 900;
                color: #58f7a0;
                margin-bottom: 4px;
                letter-spacing: 0.1px;
            }
            .service-price-row {
                margin: 2px 0 8px 0;
                color: #d9ffe9;
                font-size: 0.96rem;
            }
            .service-old-price {
                text-decoration: line-through;
                opacity: 0.75;
                margin-right: 10px;
            }
            .service-offer-price {
                color: #7dffb2;
                font-weight: 900;
                margin-right: 12px;
            }
            .service-delivery {
                color: #bde7cc;
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="certhub-hero">
            <p class="certhub-title">Certification Excellence Hub</p>
            <p class="certhub-subtitle">
                Resume review, project services, and premium handwritten notes in one place.
                Upload resume and get instant ATS guidance with clear service recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_primary_recommendation(recommended):
    if not recommended:
        return
    top_name, top_reason = recommended[0]
    top_service = next((s for s in SERVICES if s["name"] == top_name), None)
    top_offer_price = top_service["offer_price"] if top_service else None
    user = st.session_state.get("auth_user") or {}
    currency = "MYR" if user.get("country") == "Malaysia" else "INR"
    rate = MALAYSIA_RATE if currency == "MYR" else 1.0
    display_offer = round(top_offer_price * rate, 2) if top_offer_price else None
    st.markdown(
        f"""
        <div class="recommend-card">
            <div class="recommend-label">Recommended Service For You</div>
            <div class="recommend-main">{top_name}</div>
            <div class="recommend-reason">{top_reason}</div>
            <div class="recommend-reason"><b>Offer Price:</b> {currency} {display_offer if display_offer is not None else 'NA'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        if top_offer_price:
            render_payment_action(top_name, top_offer_price, f"recommend_{top_name}")
        else:
            st.link_button("Pay Now", RAZORPAY_LINK, use_container_width=True)
    with c2:
        if st.button("Open This Service", use_container_width=True, key=f"open_reco_{top_name}"):
            st.session_state["selected_service"] = top_name
            st.session_state["page"] = "Services"
            st.rerun()


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def build_pay_link(amount_inr: int, item_name: str):
    # Fallback to base Razorpay profile link because dynamic amount URLs differ by account setup.
    # This avoids BAD_REQUEST_ERROR from invalid path patterns.
    return RAZORPAY_LINK


def send_payment_email(item_name: str, amount_inr: int, user: dict, note: str, attachment_file=None):
    smtp_host = st.secrets.get("SMTP_HOST", "")
    smtp_port = int(st.secrets.get("SMTP_PORT", 0) or 0)
    smtp_user = st.secrets.get("SMTP_USER", "")
    smtp_password = st.secrets.get("SMTP_PASSWORD", "")
    smtp_from = st.secrets.get("SMTP_FROM", smtp_user or CONTACT_EMAIL)
    if not smtp_host or not smtp_port or not smtp_user or not smtp_password:
        return False, "Email is not configured. Add SMTP settings in Streamlit secrets."

    msg = EmailMessage()
    msg["Subject"] = f"CertHub payment proof: {item_name}"
    msg["From"] = smtp_from
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(
        "\n".join(
            [
                note,
                f"Service/Note: {item_name}",
                f"Amount (INR): {amount_inr}",
                f"Name: {user.get('name', 'Unknown')}",
                f"Email: {user.get('email', 'Unknown')}",
                f"Country: {user.get('country', 'Other')}",
                f"Time (UTC): {datetime.datetime.utcnow().isoformat()}",
            ]
        )
    )
    if attachment_file is not None:
        data = attachment_file.getvalue()
        content_type = attachment_file.type or "application/octet-stream"
        if "/" in content_type:
            maintype, subtype = content_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=attachment_file.name)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        return True, None
    except Exception as exc:
        return False, f"Email send failed: {exc}"


def show_browser_notification(title: str, body: str):
    st_html(
        f"""
        <script>
        (function() {{
            if (!("Notification" in window)) {{
                return;
            }}
            function show() {{
                try {{
                    new Notification({title!r}, {{ body: {body!r} }});
                }} catch (e) {{}}
            }}
            if (Notification.permission === "granted") {{
                show();
            }} else if (Notification.permission !== "denied") {{
                Notification.requestPermission().then(function (permission) {{
                    if (permission === "granted") {{
                        show();
                    }}
                }});
            }}
        }})();
        </script>
        """,
        height=0,
    )

def render_payment_action(item_name: str, amount_inr: int, button_key: str):
    user = st.session_state.get("auth_user") or {}
    payment_country = user.get("country", "Other")
    if payment_country in {"India", "Malaysia"}:
        st.markdown("**Scan to Pay**")
        if payment_country == "India":
            st.image(INDIA_QR_PATH, use_container_width=True, caption="UPI QR (India)")
        else:
            st.image(MALAYSIA_QR_PATH, use_container_width=True, caption="Malaysia National QR")
        st.caption("Upload your payment screenshot to notify the team.")
        proof = st.file_uploader(
            "Payment Screenshot",
            type=["png", "jpg", "jpeg", "pdf"],
            key=f"proof_{button_key}",
        )
        txn_id = st.text_input("Transaction ID (optional)", key=f"txn_{button_key}")
        if st.button("Submit Payment Proof", use_container_width=True, key=f"paid_btn_{button_key}"):
            if not proof:
                st.warning("Please upload a payment screenshot.")
            else:
                note = "Payment proof uploaded."
                if txn_id.strip():
                    note += f" Transaction ID: {txn_id.strip()}."
                ok, err = send_payment_email(item_name, amount_inr, user, note, proof)
                if ok:
                    st.success("Thanks! We have notified the team.")
                else:
                    st.warning(err or "Could not send notification email.")
        return

    st.info("If you are in India or Malaysia, update your country in Profile to see the QR option.")
    st.link_button(
        f"Pay Now - INR {amount_inr}",
        build_pay_link(amount_inr, item_name),
        use_container_width=True,
    )


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'Other'
        )
        """
    )
    columns = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "country" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN country TEXT NOT NULL DEFAULT 'Other'")
    conn.commit()
    conn.close()


def hash_password(password: str, salt_hex: str | None = None):
    if salt_hex is None:
        salt = os.urandom(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000).hex()
    return salt_hex, pw_hash


def create_user(full_name: str, email: str, password: str, country: str):
    email = email.strip().lower()
    country = (country or "Other").strip()
    salt, pw_hash = hash_password(password)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, salt, created_at, country) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name.strip(), email, pw_hash, salt, datetime.datetime.utcnow().isoformat(), country),
        )
        conn.commit()
        return True, "Account created successfully. Please sign in."
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()


def authenticate_user(email: str, password: str):
    email = email.strip().lower()
    conn = get_conn()
    row = conn.execute(
        "SELECT id, full_name, email, password_hash, salt, country FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    _, full_name, user_email, stored_hash, salt, country = row
    _, candidate_hash = hash_password(password, salt)
    if candidate_hash == stored_hash:
        return {"name": full_name, "email": user_email, "country": country or "Other"}
    return None


def update_user_country(user_email: str, country: str):
    conn = get_conn()
    try:
        conn.execute("UPDATE users SET country = ? WHERE email = ?", (country, user_email))
        conn.commit()
        return True
    finally:
        conn.close()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_resume_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    name = (uploaded_file.name or "").lower()
    file_bytes = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    if name.endswith(".pdf"):
        text_chunks = []
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text_chunks.append(page.extract_text() or "")
        except Exception:
            return ""
        return "\n".join(text_chunks).strip()
    if name.endswith(".docx"):
        try:
            document = docx.Document(BytesIO(file_bytes))
            return "\n".join(p.text for p in document.paragraphs).strip()
        except Exception:
            return ""
    return ""


def tokenize(text: str):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-/]*", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def split_sections(raw_resume: str):
    lines = [line.strip() for line in (raw_resume or "").splitlines()]
    sections = {h: "" for h in HEADINGS}
    current = "name & contact"
    bucket = []

    def flush(section_key):
        if bucket:
            existing = sections.get(section_key, "")
            joined = "\n".join(bucket).strip()
            sections[section_key] = (existing + "\n" + joined).strip() if existing else joined

    for line in lines:
        lowered = line.lower()
        matched_section = None
        for canonical, aliases in SECTION_ALIASES.items():
            if any(lowered == alias or lowered.startswith(alias + ":") for alias in aliases):
                matched_section = canonical
                break
        if matched_section:
            flush(current)
            bucket.clear()
            current = matched_section
        else:
            bucket.append(line)
    flush(current)
    return sections


def extract_keywords(jd_text: str):
    text = (jd_text or "").lower()
    essential = []
    preferred = []
    for kw in TECH_PATTERNS + SOFT_PATTERNS:
        if kw in text:
            if re.search(rf"(preferred|nice to have|plus|bonus).{{0,30}}{re.escape(kw)}", text):
                preferred.append(kw)
            else:
                essential.append(kw)
    counts = Counter(tokenize(text))
    frequent = [w for w, c in counts.items() if c >= 2 and w not in essential and w not in preferred]
    return {
        "essential": sorted(set(essential)),
        "preferred": sorted(set(preferred)),
        "important": sorted(set(essential + preferred + frequent[:20])),
    }


def bullets_from_text(block: str, max_items: int = 4):
    lines = [l.strip(" -\u2022\t") for l in (block or "").splitlines() if l.strip()]
    out = []
    for line in lines:
        if len(line) < 8:
            continue
        if not line.endswith("."):
            line += "."
        out.append(line[:1].upper() + line[1:])
        if len(out) >= max_items:
            break
    return out


def build_summary(role: str, section_data: dict, jd_kw: dict):
    existing = normalize_space(section_data.get("professional summary", ""))
    picked = jd_kw["essential"][:3] if jd_kw["essential"] else jd_kw["important"][:3]
    kw_phrase = ", ".join(picked) if picked else "core technical and communication skills"
    if existing:
        return f"Early-career candidate targeting {role} roles with strengths in {kw_phrase}. {existing}"
    return f"Early-career candidate targeting {role} roles with strengths in {kw_phrase}, project execution, and collaborative problem solving."


def merge_skills(section_data: dict, jd_kw: dict):
    resume_skills = set(tokenize(section_data.get("skills", "")))
    boosted = list(resume_skills)
    source = (section_data.get("skills", "") + " " + section_data.get("projects", "") + " " + section_data.get("experience", "")).lower()
    for kw in jd_kw["essential"] + jd_kw["preferred"]:
        if kw in source:
            boosted.append(kw)
    cleaned = sorted(set(boosted), key=lambda x: (len(x.split()), x))
    return cleaned[:24]


def format_resume(role: str, raw_resume: str, jd_kw: dict):
    sections = split_sections(raw_resume)
    summary = build_summary(role, sections, jd_kw)
    skills = merge_skills(sections, jd_kw)
    experience_bullets = bullets_from_text(sections.get("experience", ""))
    project_bullets = bullets_from_text(sections.get("projects", ""))
    education_bullets = bullets_from_text(sections.get("education", ""), max_items=3)
    cert_bullets = bullets_from_text(sections.get("certifications", ""), max_items=3)

    if not experience_bullets:
        experience_bullets = ["Academic or internship experience with measurable outcomes can be added here."]
    if not project_bullets:
        project_bullets = ["Project details can be added with tech stack, role, and impact metrics."]
    if not education_bullets:
        education_bullets = ["Degree details, institution, graduation timeline, and relevant coursework."]

    name_contact = sections.get("name & contact", "").strip() or "Candidate Name | Phone | Email | LinkedIn | GitHub"
    lines = [
        "Name & Contact",
        name_contact,
        "",
        "Professional Summary",
        summary,
        "",
        "Skills",
        ", ".join(skills) if skills else "Python, SQL, Communication, Problem Solving",
        "",
        "Experience",
    ]
    lines.extend([f"- {b}" for b in experience_bullets])
    lines.extend(["", "Projects"])
    lines.extend([f"- {b}" for b in project_bullets])
    lines.extend(["", "Education"])
    lines.extend([f"- {b}" for b in education_bullets])
    if cert_bullets:
        lines.extend(["", "Certifications"])
        lines.extend([f"- {b}" for b in cert_bullets])
    return "\n".join(lines).strip()


def ats_match(resume_text: str, jd_kw: dict):
    resume_lower = (resume_text or "").lower()
    essential = jd_kw["essential"]
    preferred = jd_kw["preferred"]
    important = jd_kw["important"][:20]

    matched_essential = [k for k in essential if k in resume_lower]
    matched_preferred = [k for k in preferred if k in resume_lower]
    matched_important = [k for k in important if k in resume_lower]

    total = len(essential) * 5 + len(preferred) * 2 + len(important)
    score = (len(matched_essential) * 5) + (len(matched_preferred) * 2) + len(matched_important)
    pct = round((score / total) * 100, 2) if total else 0.0
    missing = [k for k in essential if k not in resume_lower]
    matched = sorted(set(matched_essential + matched_preferred + matched_important))
    return pct, matched, missing


def general_resume_score(resume_text: str):
    sections = split_sections(resume_text)
    present_sections = [h for h in HEADINGS if sections.get(h, "").strip()]
    missing_sections = [h for h in HEADINGS if not sections.get(h, "").strip()]

    words = tokenize(resume_text)
    verb_hits = [w for w in words if w in ACTION_VERBS]
    number_hits = re.findall(r"\b\d+%?|\$\d+[kKmM]?\b", resume_text)

    score = 0.0
    score += (len(present_sections) / len(HEADINGS)) * 60
    score += min(len(verb_hits), 8) / 8 * 20
    score += min(len(number_hits), 6) / 6 * 20
    score = round(min(score, 100), 2)

    strengths = []
    gaps = []
    edits = []

    if present_sections:
        strengths.append(f"Detected ATS sections: {', '.join(present_sections[:6])}.")
    if verb_hits:
        strengths.append("Uses action-oriented language in project/experience content.")
    if number_hits:
        strengths.append("Includes measurable indicators (numbers/percentages).")

    if missing_sections:
        gaps.append(f"Missing or weak sections: {', '.join(missing_sections)}.")
        edits.append(f"Add explicit headings for: {', '.join(missing_sections)}.")
    if not verb_hits:
        gaps.append("Limited action verbs in bullets.")
        edits.append("Start bullets with verbs like Developed, Built, Optimized, Led.")
    if not number_hits:
        gaps.append("Impact is not quantified in clear metrics.")
        edits.append("Add numbers: % improvement, users, response time, or delivery outcomes.")

    edits.extend(
        [
            "Keep one-column format and avoid tables, icons, and headers/footers.",
            "Repeat core tools in both Skills and Experience/Projects sections.",
            "Keep one page for fresher profile unless experience clearly requires more.",
        ]
    )

    if not strengths:
        strengths.append("Resume content exists and can be optimized with ATS structure.")
    if not gaps:
        gaps.append("No major structural gaps detected in general mode.")

    return score, strengths[:6], gaps[:6], edits[:7]


def recommend_services(score: float, missing_keywords: list[str], resume_text: str):
    recommended = []
    resume_lower = resume_text.lower()

    if score < 60:
        recommended.append(("Resume Making", "ATS score indicates structure and keyword optimization needs."))
    if "portfolio" not in resume_lower and ("projects" not in resume_lower or "github" not in resume_lower):
        recommended.append(("Portfolio Making", "Project visibility and profile branding can be improved."))
    if len(missing_keywords) >= 4:
        recommended.append(("LinkedIn Manager", "Profile positioning can be aligned with target role keywords."))
    if "presentation" in missing_keywords or "communication" in missing_keywords:
        recommended.append(("Presentation Making", "Project communication support can strengthen interview rounds."))
    if any(k in missing_keywords for k in ["machine learning", "tensorflow", "pytorch"]):
        recommended.append(("Advanced Project (ML/AI)", "Advanced project proof can bridge skill gaps."))
    if not recommended:
        recommended.append(("Full Functional Website", "Strong portfolio project can increase recruiter confidence."))
    return recommended[:4]


def render_service_cards():
    st.subheader("Services")
    if not st.session_state.get("notified_services"):
        show_browser_notification(
            "CertHub Services",
            "Limited-time offers are active. Explore premium services to boost your profile today.",
        )
        st.session_state["notified_services"] = True
    if st.session_state.get("show_service_notification"):
        service_name = st.session_state.pop("show_service_notification")
        show_browser_notification(
            "Service Opened",
            f"{service_name} is ready. Add another service for faster results.",
        )
    focus_name = st.session_state.get("selected_service")
    focus_service = next((s for s in SERVICES if s["name"] == focus_name), None)

    if focus_service:
        st.markdown(
            f"""
            <div class="service-spotlight">
                <div class="recommend-label">Service Spotlight</div>
                <div class="recommend-main">{focus_service['name']}</div>
                <div class="recommend-reason">{focus_service['description']}</div>
                <div class="recommend-reason"><b>Best for:</b> {focus_service['best_for']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            render_payment_action(
                focus_service["name"],
                focus_service["offer_price"],
                f"spotlight_{focus_service['name']}",
            )
        with c2:
            st.link_button("Contact Us (Spotlight)", f"mailto:{CONTACT_EMAIL}", use_container_width=True)

    user = st.session_state.get("auth_user") or {}
    currency = "MYR" if user.get("country") == "Malaysia" else "INR"
    rate = MALAYSIA_RATE if currency == "MYR" else 1.0
    for service in SERVICES:
        original_display = round(service["original_price"] * rate, 2)
        offer_display = round(service["offer_price"] * rate, 2)
        with st.container(border=True):
            st.markdown(f"<div class='service-title'>{service['name']}</div>", unsafe_allow_html=True)
            st.markdown(
                (
                    f"<div class='service-price-row'>"
                    f"<span class='service-old-price'>{currency} {original_display}</span>"
                    f"<span class='service-offer-price'>Offer {currency} {offer_display}</span>"
                    f"<span class='service-delivery'>Delivery: {service['delivery_time']}</span>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )
            st.write(service["description"])
            st.caption(f"Best for: {service['best_for']}")
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                render_payment_action(service["name"], service["offer_price"], f"service_{service['name']}")
            with c2:
                st.link_button(
                    f"Contact Us - {service['name']}",
                    f"mailto:{CONTACT_EMAIL}?subject=Inquiry%20for%20{service['name'].replace(' ', '%20')}",
                    use_container_width=True,
                )
            with c3:
                if st.button("Open Service", use_container_width=True, key=f"open_{service['name']}"):
                    st.session_state["selected_service"] = service["name"]
                    st.session_state["page"] = "Services"
                    st.session_state["show_service_notification"] = service["name"]
                    st.rerun()


def render_notes_store():
    st.subheader("Handwritten Notes")
    st.caption("Premium handwritten notes to help master programming concepts.")
    user = st.session_state.get("auth_user") or {}
    currency = "MYR" if user.get("country") == "Malaysia" else "INR"
    rate = MALAYSIA_RATE if currency == "MYR" else 1.0
    if not st.session_state.get("notified_notes"):
        show_browser_notification(
            "CertHub Notes",
            "Grab premium notes now and pair them with services for maximum impact.",
        )
        st.session_state["notified_notes"] = True
    for note in NOTES:
        price_display = round(note["price_inr"] * rate, 2)
        with st.container(border=True):
            st.markdown(f"<div class='note-title'>{note['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='note-price'>Price: {currency} {price_display}</div>", unsafe_allow_html=True)
            st.write("Includes:")
            for topic in note["topics"]:
                st.write(f"- {topic}")
            c1, c2 = st.columns([1, 1])
            with c1:
                render_payment_action(note["title"], note["price_inr"], f"note_{note['title']}")
            with c2:
                st.link_button(
                    f"Contact Us - {note['title']}",
                    f"mailto:{CONTACT_EMAIL}?subject=Inquiry%20for%20{note['title'].replace(' ', '%20')}",
                    use_container_width=True,
                )


def render_auth():
    st.title(APP_NAME)
    st.caption("Sign in to access resume checker, services, and notes marketplace.")
    render_hero()
    tabs = st.tabs(["Sign In", "Create Account"])

    with tabs[0]:
        with st.form("signin_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
        if submit:
            user = authenticate_user(email, password)
            if user:
                st.session_state["auth_user"] = user
                st.success("Signed in successfully.")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tabs[1]:
        with st.form("signup_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password (min 8 chars)", type="password")
            country = st.selectbox("Country", ["India", "Malaysia", "Other"], index=2)
            submit = st.form_submit_button("Create Account")
        if submit:
            if len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif not full_name.strip() or not email.strip():
                st.error("Name and email are required.")
            else:
                ok, msg = create_user(full_name, email, password, country)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


def render_resume_checker():
    st.subheader("Resume Checker")
    st.caption("Upload resume only for general ATS review, or add target role + JD for tailored scoring.")

    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    with st.expander("Optional targeted mode fields"):
        job_role = st.text_input("Target Job Role")
        job_description = st.text_area("Target Job Description", height=180)

    run_analysis = st.button("Analyze Resume", type="primary", use_container_width=True)
    if not run_analysis:
        return

    resume_text = extract_resume_text(resume_file)
    has_role = bool(job_role.strip())
    has_jd = bool(job_description.strip())

    if not resume_file:
        st.error("Please upload a resume file.")
        return
    if not resume_text:
        st.error("Text extraction failed. Upload a clear PDF, DOCX, or TXT file.")
        return
    if has_role != has_jd:
        st.warning("For targeted scoring, provide both role and job description. Otherwise keep both blank.")
        return

    if not has_role and not has_jd:
        score, strengths, gaps, edits = general_resume_score(resume_text)
        default_kw = {"essential": [], "preferred": [], "important": TECH_PATTERNS[:8] + SOFT_PATTERNS[:3]}
        rewritten = format_resume("Entry-Level Professional", resume_text, default_kw)
        recs = recommend_services(score, [], resume_text)

        render_primary_recommendation(recs)
        st.metric("General ATS Score", f"{score}%")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Strengths")
            for item in strengths:
                st.write(f"- {item}")
            st.write("Gaps")
            for item in gaps:
                st.write(f"- {item}")
        with c2:
            st.write("What to improve")
            for item in edits:
                st.write(f"- {item}")
            st.write("Recommended services")
            for name, reason in recs:
                st.write(f"- {name}: {reason}")

        st.subheader("ATS-friendly rewritten resume")
        st.text_area("Output", rewritten, height=420)
        st.download_button("Download Rewrite (.txt)", rewritten, file_name="certhub_rewritten_resume.txt")
        return

    jd_keywords = extract_keywords(job_description)
    score, matched, missing = ats_match(resume_text, jd_keywords)
    rewritten = format_resume(job_role.strip(), resume_text, jd_keywords)
    recs = recommend_services(score, missing, resume_text)

    render_primary_recommendation(recs)
    st.metric("Targeted ATS Match", f"{score}%")
    c1, c2 = st.columns(2)
    with c1:
        st.write("Essential skills:", ", ".join(jd_keywords["essential"]) if jd_keywords["essential"] else "Not detected clearly.")
        st.write("Preferred skills:", ", ".join(jd_keywords["preferred"]) if jd_keywords["preferred"] else "Not detected clearly.")
        st.write("Important keywords/tools:", ", ".join(jd_keywords["important"][:25]) if jd_keywords["important"] else "Not detected clearly.")
    with c2:
        st.write("Matched keywords:", ", ".join(matched) if matched else "None")
        st.write("Missing essential keywords:", ", ".join(missing) if missing else "None")

    st.write("Recommended services")
    for name, reason in recs:
        st.write(f"- {name}: {reason}")

    st.subheader("ATS-friendly tailored resume")
    st.text_area("Output", rewritten, height=420)
    st.download_button("Download Rewrite (.txt)", rewritten, file_name="certhub_targeted_resume.txt")


def render_dashboard(user):
    render_hero()
    st.subheader(f"Welcome, {user['name']}")
    st.write("CertHub provides profile services, notes, and ATS resume optimization in one place.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Services", len(SERVICES))
    with c2:
        st.metric("Notes", len(NOTES))
    with c3:
        st.metric("Payment Gateway", "Razorpay")
    st.info("Use sidebar to access Resume Checker, Services, and Notes Store.")
    st.write(CONTACT_TEXT)


def main():
    st.set_page_config(page_title=APP_NAME, page_icon=":briefcase:", layout="wide")
    inject_theme()
    init_db()

    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "Dashboard"
    if "selected_service" not in st.session_state:
        st.session_state["selected_service"] = None

    user = st.session_state["auth_user"]
    if not user:
        render_auth()
        return

    with st.sidebar:
        st.markdown(f"**{APP_NAME}**")
        st.caption(user["email"])
        pages = ["Dashboard", "Resume Checker", "Services", "Notes Store", "Profile"]
        current_page = st.session_state.get("page", "Dashboard")
        if current_page not in pages:
            current_page = "Dashboard"
        page = st.radio("Navigate", pages, index=pages.index(current_page))
        st.session_state["page"] = page
        if st.button("Sign Out", use_container_width=True):
            st.session_state["auth_user"] = None
            st.session_state["page"] = "Dashboard"
            st.session_state["selected_service"] = None
            st.rerun()

    if page == "Dashboard":
        render_dashboard(user)
    elif page == "Resume Checker":
        render_resume_checker()
    elif page == "Services":
        render_service_cards()
    elif page == "Notes Store":
        render_notes_store()
    else:
        st.subheader("Profile")
        st.write(f"Name: {user['name']}")
        st.write(f"Email: {user['email']}")
        st.write("Country")
        current_country = user.get("country", "Other")
        country_options = ["India", "Malaysia", "Other"]
        if current_country not in country_options:
            current_country = "Other"
        country = st.selectbox("Country", country_options, index=country_options.index(current_country))
        if st.button("Save Country", use_container_width=True):
            if update_user_country(user["email"], country):
                st.session_state["auth_user"]["country"] = country
                st.success("Country updated.")
        st.write("Payment Link:")
        st.code(RAZORPAY_LINK)
        st.write(CONTACT_TEXT)


if __name__ == "__main__":
    main()
