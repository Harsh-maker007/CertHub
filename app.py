import datetime
import hashlib
import os
import re
import sqlite3
from collections import Counter
from io import BytesIO
import secrets

import docx
import pdfplumber
import requests
import streamlit as st


APP_NAME = "CertHub"
DB_PATH = "certhub_users.db"
RAZORPAY_LINK = "https://razorpay.me/@harshshandilya"
RAZORPAY_KEY_ID = "rzp_live_RJNwYg2Jx647o8"
CONTACT_EMAIL = "itscerthub@gmail.com"
CONTACT_PHONE = "+918603234533"
CONTACT_TEXT = f"Contact: {CONTACT_EMAIL} | {CONTACT_PHONE}"

HEADINGS = [
    "target job role",
    "name & contact",
    "professional summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]

SECTION_ALIASES = {
    "target job role": ["target", "role", "position", "target role", "job role", "target position"],
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
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "php", "ruby", "swift", "kotlin",
    "r programming", "matlab", "scala", "perl", "bash", "shell", "sql", "plsql", "tsql",
    # Frontend
    "react", "vue", "angular", "svelte", "nextjs", "nuxtjs", "html", "css", "sass", "tailwind", "bootstrap",
    "jquery", "three.js", "d3", "webpack", "vite", "parcel",
    # Backend
    "node", "nodejs", "express", "fastapi", "flask", "django", "spring", "springboot", "asp.net", "dotnet",
    "rails", "laravel", "symfony", "nestjs", "gin", "gorilla", "actix",
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "firestore",
    "oracle", "sqlite", "mariadb", "couchdb", "neo4j", "graphdb",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "digitalocean",
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "gitlab", "github actions", "circleci",
    "datadog", "prometheus", "grafana", "elk stack", "splunk",
    # Data & ML
    "pandas", "numpy", "scikit-learn", "scipy", "matplotlib", "seaborn", "plotly", "tableau", "power bi",
    "tensorflow", "pytorch", "keras", "xgboost", "lightgbm", "catboost", "nlp", "spacy", "nltk",
    "machine learning", "deep learning", "neural networks", "cnn", "rnn", "lstm", "transformer",
    "computer vision", "opencv", "pillow", "data analysis", "data visualization", "data engineering",
    # Tools & Frameworks
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack", "figma", "sketch", "adobe xd",
    "postman", "swagger", "rest api", "graphql", "websockets", "rpc",
    # Soft Skills (Tech)
    "agile", "scrum", "kanban", "dsa", "algorithm", "oop", "functional programming", "design patterns",
    "microservices", "monolithic", "serverless", "rest", "grpc", "message queue", "rabbitmq", "kafka",
    "cicd", "devops", "site reliability", "sre", "testing", "unit test", "integration test",
    "tdd", "bdd", "automation", "performance", "optimization", "scalability", "security", "encryption",
    "oauth", "jwt", "authentication", "authorization", "api design", "system design",
]

SOFT_PATTERNS = [
    # Leadership & Management
    "communication", "leadership", "team lead", "management", "decision making", "strategic thinking",
    "delegation", "mentoring", "coaching", "stakeholder management", "project management",
    # Problem Solving & Analysis
    "problem solving", "analytical", "critical thinking", "creative thinking", "innovation",
    "root cause analysis", "troubleshooting", "debugging", "research",
    # Collaboration & Teamwork
    "collaboration", "teamwork", "cooperation", "interpersonal", "networking", "relationship building",
    "conflict resolution", "negotiation", "empathy",
    # Time & Organization
    "time management", "organization", "planning", "prioritization", "multitasking", "deadline driven",
    # Communication Skills
    "presentation", "public speaking", "documentation", "technical writing", "storytelling",
    "active listening", "written communication", "verbal communication",
    # Business Skills
    "business acumen", "customer focus", "user empathy", "market awareness", "sales", "marketing",
    "cost analysis", "budget", "financial", "roi", "kpi", "metrics",
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
        "original_price": 999,
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
    st.markdown(
        f"""
        <div class="recommend-card">
            <div class="recommend-label">Recommended Service For You</div>
            <div class="recommend-main">{top_name}</div>
            <div class="recommend-reason">{top_reason}</div>
            <div class="recommend-reason"><b>Offer Price:</b> INR {top_offer_price if top_offer_price else 'NA'}</div>
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


def get_razorpay_credentials():
    key_id = st.secrets.get("RAZORPAY_KEY_ID", RAZORPAY_KEY_ID)
    key_secret = st.secrets.get("RAZORPAY_KEY_SECRET", "")
    return key_id, key_secret


def create_razorpay_payment_link(amount_inr: int, item_name: str, user_name: str, user_email: str):
    key_id, key_secret = get_razorpay_credentials()
    if not key_id or not key_secret:
        return None, "Razorpay secret is not configured."

    payload = {
        "amount": int(amount_inr) * 100,
        "currency": "INR",
        "accept_partial": False,
        "description": f"{APP_NAME} - {item_name}",
        "reference_id": f"certhub_{secrets.token_hex(6)}",
        "customer": {
            "name": user_name or "CertHub User",
            "email": user_email or CONTACT_EMAIL,
            "contact": CONTACT_PHONE.replace("+", ""),
        },
        "notify": {"sms": True, "email": True},
        "reminder_enable": True,
        "notes": {"item": item_name, "amount_inr": str(amount_inr)},
    }

    try:
        resp = requests.post(
            "https://api.razorpay.com/v1/payment_links",
            auth=(key_id, key_secret),
            json=payload,
            timeout=20,
        )
        if resp.status_code >= 300:
            return None, f"Razorpay error: {resp.status_code} - {resp.text[:200]}"
        data = resp.json()
        return data.get("short_url"), None
    except Exception as exc:
        return None, f"Payment link request failed: {exc}"


def render_payment_action(item_name: str, amount_inr: int, button_key: str):
    if "payment_links" not in st.session_state:
        st.session_state["payment_links"] = {}

    user = st.session_state.get("auth_user") or {}
    cached = st.session_state["payment_links"].get(button_key)

    if st.button(f"Pay Now - INR {amount_inr}", use_container_width=True, key=f"pay_btn_{button_key}"):
        payment_url, error = create_razorpay_payment_link(
            amount_inr=amount_inr,
            item_name=item_name,
            user_name=user.get("name", ""),
            user_email=user.get("email", ""),
        )
        if payment_url:
            st.session_state["payment_links"][button_key] = payment_url
            cached = payment_url
            st.success("Secure payment link created.")
        else:
            st.warning(error or "Could not create payment link. Using direct Razorpay profile link.")
            st.session_state["payment_links"][button_key] = RAZORPAY_LINK
            cached = RAZORPAY_LINK

    if cached:
        st.link_button("Open Secure Checkout", cached, use_container_width=True)


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
            created_at TEXT NOT NULL
        )
        """
    )
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


def create_user(full_name: str, email: str, password: str):
    email = email.strip().lower()
    salt, pw_hash = hash_password(password)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
            (full_name.strip(), email, pw_hash, salt, datetime.datetime.utcnow().isoformat()),
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
        "SELECT id, full_name, email, password_hash, salt FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    _, full_name, user_email, stored_hash, salt = row
    _, candidate_hash = hash_password(password, salt)
    if candidate_hash == stored_hash:
        return {"name": full_name, "email": user_email}
    return None


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


def get_keyword_synonyms() -> dict:
    """Map keywords to their common variations and synonyms."""
    return {
        "machine learning": ["ml", "machine learning", "ai", "artificial intelligence"],
        "deep learning": ["deep learning", "neural network", "dl"],
        "data science": ["data science", "data scientist", "analytics"],
        "rest api": ["rest api", "api", "rest"],
        "node": ["node", "nodejs", "node.js"],
        "power bi": ["power bi", "powerbi"],
        "scikit-learn": ["scikit-learn", "sklearn"],
        "c++": ["c++", "cpp"],
        "javascript": ["javascript", "js"],
        "typescript": ["typescript", "ts"],
    }


def find_keyword_matches(text: str, keywords: list[str], use_synonyms: bool = True) -> list[str]:
    """Find keyword matches with optional synonym handling."""
    text_lower = (text or "").lower()
    matched = []
    synonyms = get_keyword_synonyms() if use_synonyms else {}
    
    for kw in keywords:
        if kw in text_lower:
            matched.append(kw)
        elif use_synonyms and kw in synonyms:
            for syn in synonyms[kw]:
                if syn in text_lower and kw not in matched:
                    matched.append(kw)
                    break
    return matched


def score_section_quality(section_text: str, section_name: str) -> dict:
    """Score the quality of a resume section."""
    text = normalize_space(section_text)
    if not text:
        return {"quality_score": 0, "word_count": 0, "has_bullets": False, "has_verbs": False, "has_metrics": False}
    
    words = tokenize(text)
    lines = [l.strip() for l in (section_text or "").splitlines() if l.strip()]
    bullets = [l for l in lines if l.startswith(("-", "•", "*"))]
    
    has_verbs = any(w in ACTION_VERBS for w in words)
    has_metrics = bool(re.findall(r"\b\d+%?|\$\d+[kKmM]?\b", section_text))
    
    quality = 0
    quality += min(len(words) / 50, 1) * 30 if words else 0
    quality += 20 if bullets else 0
    quality += 25 if has_verbs else 0
    quality += 25 if has_metrics else 0
    
    return {
        "quality_score": round(min(quality, 100), 2),
        "word_count": len(words),
        "has_bullets": len(bullets) > 0,
        "has_verbs": has_verbs,
        "has_metrics": has_metrics,
    }


def count_skill_variety(skills_text: str) -> dict:
    """Analyze skill section variety and depth."""
    if not skills_text:
        return {"tech_count": 0, "soft_count": 0, "total_unique": 0}
    
    text_lower = skills_text.lower()
    tech_count = sum(1 for tech in TECH_PATTERNS if tech in text_lower)
    soft_count = sum(1 for soft in SOFT_PATTERNS if soft in text_lower)
    unique_skills = len(set(tokenize(skills_text)))
    
    return {
        "tech_count": tech_count,
        "soft_count": soft_count,
        "total_unique": unique_skills,
    }


def ats_match(resume_text: str, jd_kw: dict):
    """ULTRA-STRICT ATS matching with severe keyword penalties."""
    resume_lower = (resume_text or "").lower()
    essential = jd_kw["essential"]
    preferred = jd_kw["preferred"]
    important = jd_kw["important"][:20]

    matched_essential = find_keyword_matches(resume_text, essential, use_synonyms=True)
    matched_preferred = find_keyword_matches(resume_text, preferred, use_synonyms=True)
    matched_important = find_keyword_matches(resume_text, important, use_synonyms=True)

    total = len(essential) * 5 + len(preferred) * 2 + len(important)
    score = (len(matched_essential) * 5) + (len(matched_preferred) * 2) + len(matched_important)
    
    essential_match_ratio = len(matched_essential) / len(essential) if essential else 1.0
    preferred_match_ratio = len(matched_preferred) / len(preferred) if preferred else 1.0
    
    penalty = 0.0
    if essential_match_ratio < 0.4:
        penalty += 35
    elif essential_match_ratio < 0.6:
        penalty += 25
    elif essential_match_ratio < 0.8:
        penalty += 15
    
    if preferred_match_ratio < 0.25:
        penalty += 20
    elif preferred_match_ratio < 0.5:
        penalty += 10
    
    score_adjusted = max(0, score - penalty)
    pct = round((score_adjusted / total) * 100, 2) if total else 0.0
    pct = min(pct, 95)
    
    missing = [k for k in essential if k not in find_keyword_matches(resume_text, [k], use_synonyms=True)]
    matched = sorted(set(matched_essential + matched_preferred + matched_important))
    return pct, matched, missing


def general_resume_score(resume_text: str):
    """Strict general resume ATS scoring with rigorous quality checks."""
    sections = split_sections(resume_text)
    present_sections = [h for h in HEADINGS if sections.get(h, "").strip()]
    missing_sections = [h for h in HEADINGS if not sections.get(h, "").strip()]

    words = tokenize(resume_text)
    verb_hits = [w for w in words if w in ACTION_VERBS]
    number_hits = re.findall(r"\b\d+%?|\$\d+[kKmM]?\b", resume_text)

    contact_info = sections.get("name & contact", "").strip()
    has_contact = bool(contact_info and len(contact_info) > 15)
    has_email = any(x in contact_info.lower() for x in ["@", "email"])
    has_phone = any(x in contact_info for x in ["(", "+", "-"] if len(contact_info) > 5)
    has_links = any(x in contact_info.lower() for x in ["linkedin", "github", "portfolio"])
    
    target_role = sections.get("target job role", "").strip()
    has_target_role = bool(target_role and len(target_role) > 5)
    
    summary_info = sections.get("professional summary", "").strip()
    summary_quality = score_section_quality(summary_info, "professional summary")
    
    skills_text = sections.get("skills", "").strip()
    skills_quality = count_skill_variety(skills_text)
    skills_count = len(set(tokenize(skills_text)))
    
    exp_text = sections.get("experience", "").strip()
    exp_quality = score_section_quality(exp_text, "experience")
    exp_bullets = [l.strip() for l in exp_text.splitlines() if l.strip().startswith(("-", "•", "*"))]
    
    proj_text = sections.get("projects", "").strip()
    proj_quality = score_section_quality(proj_text, "projects")
    proj_bullets = [l.strip() for l in proj_text.splitlines() if l.strip().startswith(("-", "•", "*"))]

    score = 0.0
    penalties = 0.0

    exp_verbs = sum(1 for line in exp_bullets if any(v in line.lower() for v in ACTION_VERBS))
    exp_metrics = sum(1 for line in exp_bullets if re.search(r"\b\d+%?|\$\d+[kKmM]?\b", line))
    
    proj_verbs = sum(1 for line in proj_bullets if any(v in line.lower() for v in ACTION_VERBS))
    proj_metrics = sum(1 for line in proj_bullets if re.search(r"\b\d+%?|\$\d+[kKmM]?\b", line))
    
    edu_text = sections.get("education", "").strip()
    edu_bullets = [l.strip() for l in edu_text.splitlines() if l.strip()]
    
    cert_text = sections.get("certifications", "").strip()
    
    contact_quality = sum([has_email, has_phone, has_links])

    section_ratio = len(present_sections) / len(HEADINGS)
    if section_ratio == 1.0:
        score += 25
    elif section_ratio >= 0.85:
        score += 16
    elif section_ratio >= 0.71:
        score += 8
    elif section_ratio >= 0.57:
        score += 2
    else:
        penalties += 25
    
    if len(verb_hits) >= 30:
        score += 20
    elif len(verb_hits) >= 25:
        score += 16
    elif len(verb_hits) >= 20:
        score += 12
    elif len(verb_hits) >= 15:
        score += 8
    elif len(verb_hits) >= 10:
        score += 4
    else:
        penalties += 18
    
    if len(number_hits) >= 22:
        score += 20
    elif len(number_hits) >= 18:
        score += 16
    elif len(number_hits) >= 14:
        score += 12
    elif len(number_hits) >= 10:
        score += 8
    elif len(number_hits) >= 6:
        score += 4
    else:
        penalties += 18
    
    if contact_quality == 3 and has_contact:
        score += 10
    elif contact_quality == 2 and has_contact:
        score += 5
    elif contact_quality >= 1:
        score += 1
    else:
        penalties += 15
    
    if summary_quality["word_count"] >= 80 and summary_quality["has_verbs"]:
        score += 10
    elif summary_quality["word_count"] >= 60:
        score += 7
    elif summary_quality["word_count"] >= 45:
        score += 4
    elif summary_quality["word_count"] >= 25:
        score += 1
    else:
        penalties += 8
    
    if skills_quality["tech_count"] >= 20 and skills_count >= 30:
        score += 12
    elif skills_quality["tech_count"] >= 16 and skills_count >= 24:
        score += 10
    elif skills_quality["tech_count"] >= 12 and skills_count >= 18:
        score += 7
    elif skills_quality["tech_count"] >= 8 and skills_count >= 12:
        score += 3
    else:
        penalties += 15
    
    if len(exp_bullets) >= 5 and exp_quality["quality_score"] >= 85 and exp_verbs >= 4 and exp_metrics >= 3:
        score += 14
    elif len(exp_bullets) >= 4 and exp_quality["quality_score"] >= 75 and exp_verbs >= 3 and exp_metrics >= 2:
        score += 10
    elif len(exp_bullets) >= 3 and exp_quality["quality_score"] >= 60 and exp_verbs >= 2 and exp_metrics >= 1:
        score += 6
    elif len(exp_bullets) >= 2 and exp_quality["quality_score"] >= 40:
        score += 2
    else:
        penalties += 18
    
    if len(proj_bullets) >= 4 and proj_quality["quality_score"] >= 85 and proj_verbs >= 3 and proj_metrics >= 2:
        score += 12
    elif len(proj_bullets) >= 3 and proj_quality["quality_score"] >= 75 and proj_verbs >= 2 and proj_metrics >= 2:
        score += 8
    elif len(proj_bullets) >= 2 and proj_quality["quality_score"] >= 60 and proj_verbs >= 2 and proj_metrics >= 1:
        score += 5
    elif len(proj_bullets) >= 2 and proj_quality["quality_score"] >= 40:
        score += 1
    else:
        penalties += 15
    
    if len(edu_bullets) >= 1:
        score += 4
    else:
        penalties += 8
    
    if cert_text and len(cert_text.strip()) > 10:
        score += 2
    
    if has_target_role:
        score += 4
    else:
        penalties += 12
    
    score = max(0, score - penalties)
    base_percent = round((score / 130) * 100, 2)
    
    strictness_multiplier = 1.0
    if len(present_sections) < 8:
        strictness_multiplier -= 0.08 * (8 - len(present_sections))
    if len(verb_hits) < 25:
        strictness_multiplier -= 0.10
    if len(number_hits) < 18:
        strictness_multiplier -= 0.10
    if contact_quality < 3:
        strictness_multiplier -= 0.08
    if len(exp_bullets) < 4 or exp_quality["quality_score"] < 70:
        strictness_multiplier -= 0.10
    if skills_quality["tech_count"] < 12 or skills_count < 18:
        strictness_multiplier -= 0.12
    if len(proj_bullets) < 2 or proj_quality["quality_score"] < 60:
        strictness_multiplier -= 0.08
    if not has_target_role:
        strictness_multiplier -= 0.10
    
    strictness_multiplier = max(0.15, strictness_multiplier)
    score = round(base_percent * strictness_multiplier, 2)
    score = min(score, 95)

    strengths = []
    gaps = []
    edits = []

    if len(present_sections) == 8:
        strengths.append("✓ All 8 sections present.")
    elif len(present_sections) >= 7:
        strengths.append(f"✓ {len(present_sections)}/8 sections present.")
    
    if contact_quality == 3:
        strengths.append("✓ Complete contact: email, phone, and LinkedIn/GitHub.")
    
    if len(verb_hits) >= 20:
        strengths.append(f"✓ Excellent action verbs: {len(verb_hits)} detected.")
    elif len(verb_hits) >= 15:
        strengths.append(f"✓ Good action verbs: {len(verb_hits)} detected.")
    
    if len(number_hits) >= 14:
        strengths.append(f"✓ Strong metrics: {len(number_hits)} quantified.")
    elif len(number_hits) >= 10:
        strengths.append(f"✓ Good metrics: {len(number_hits)} quantified.")
    
    if skills_quality["tech_count"] >= 10:
        strengths.append(f"✓ Excellent skills: {skills_quality['tech_count']} tech.")
    elif skills_quality["tech_count"] >= 7:
        strengths.append(f"✓ Good skills: {skills_quality['tech_count']} tech.")
    
    if summary_quality["word_count"] >= 70:
        strengths.append("✓ Detailed summary.")
    
    if has_target_role:
        strengths.append("✓ Target role clearly identified.")
    
    if len(missing_sections) > 0:
        missing = [s.title() for s in missing_sections]
        gaps.append(f"✗ CRITICAL: Missing {len(missing_sections)} sections: {', '.join(missing)}.")
        edits.append(f"Add ALL missing sections: {', '.join(missing)}.")
    
    if contact_quality < 3:
        gaps.append(f"✗ Incomplete contact: missing {3 - contact_quality} elements.")
        edits.append("REQUIRED: Email, Phone, LinkedIn URL, GitHub URL.")
    
    if len(verb_hits) < 15:
        gaps.append(f"✗ CRITICAL: Only {len(verb_hits)} verbs (need 25+).")
        edits.append("Rewrite EVERY bullet: Developed, Built, Architected, Optimized, Led, Increased, Delivered, Achieved, Scaled.")
    
    if len(number_hits) < 10:
        gaps.append(f"✗ CRITICAL: Only {len(number_hits)} metrics (need 18+).")
        edits.append("Add metrics to EVERY achievement: percentages, dollars, users, features, uptime, speed improvements.")
    
    if summary_quality["word_count"] < 60:
        gaps.append(f"✗ Summary too brief: {summary_quality['word_count']} words (need 80+).")
        edits.append("Write 80+ word summary: role, 5+ skills, experience level, proven impact.")
    
    if not has_target_role:
        gaps.append("✗ CRITICAL: Target job role missing (reduces precision scoring).")
        edits.append("Add 'Target Job Role' section at top with specific role (e.g., 'Senior Software Engineer').")
    
    if skills_quality["tech_count"] < 8 or skills_count < 12:
        gaps.append(f"✗ Limited skills: {skills_quality['tech_count']} tech, {skills_count} total (need 12+ tech, 18+ total).")
        edits.append("List 12+ technical skills, 5+ soft skills: frameworks, tools, languages, platforms.")
    
    if len(exp_bullets) < 3 or exp_quality["quality_score"] < 60 or exp_verbs < 2 or exp_metrics < 1:
        gaps.append(f"✗ Experience weak: {len(exp_bullets)} bullets, {exp_verbs} verbs, {exp_metrics} metrics.")
        edits.append("Strengthen: 4+ bullets per role, each with verb + metric + impact.")
    
    if len(proj_bullets) < 2 or proj_quality["quality_score"] < 60 or proj_verbs < 2:
        gaps.append(f"✗ Projects underdeveloped: {len(proj_bullets)} bullets.")
        edits.append("Enhance: 3+ projects with tech stack, role, outcomes, and metrics.")
    
    if len(edu_bullets) < 1:
        gaps.append("✗ Education missing or incomplete.")
        edits.append("Add: Degree, Institution, Year, GPA (if 3.5+), coursework.")
    
    if not edits:
        edits.extend([
            "Single-column format only—no tables, icons, graphics.",
            "Consistent formatting: dates, bullets, spacing, font.",
            "Test ATS compatibility, avoid image-heavy PDFs.",
        ])

    if not strengths:
        strengths.append("Resume needs major improvements across all areas.")
    if not gaps:
        gaps.append("No gaps detected.")

    return score, strengths[:6], gaps[:6], edits[:7]


def recommend_services(score: float, missing_keywords: list[str], resume_text: str):
    """ULTRA-STRICT service recommendations with aggressive push for Resume Making."""
    recommended = []
    resume_lower = resume_text.lower()
    sections = split_sections(resume_text)
    
    words = tokenize(resume_text)
    verb_hits = len([w for w in words if w in ACTION_VERBS])
    number_hits = len(re.findall(r"\b\d+%?|\$\d+[kKmM]?\b", resume_text))
    
    skills_quality = count_skill_variety(sections.get("skills", ""))
    exp_text = sections.get("experience", "").strip()
    proj_text = sections.get("projects", "").strip()
    
    has_portfolio = "portfolio" in resume_lower or ("github" in resume_lower and len(sections.get("projects", "").strip()) > 100)
    has_good_projects = "projects" in resume_lower and len(proj_text) > 150
    
    if score < 30:
        recommended.append(("Resume Making", "🔴 CRITICAL: Complete overhaul required. Resume fails ATS standards across all areas."))
    elif score < 45:
        recommended.append(("Resume Making", "🔴 SEVERE: Major structural issues. Resume needs comprehensive rewrite for ATS compatibility."))
    elif score < 60:
        recommended.append(("Resume Making", "🟠 MAJOR: Add all missing sections, increase metrics to 10+, expand skills to 12+ technical."))
    elif score < 75:
        recommended.append(("Resume Making", "🟡 IMPROVEMENT: Strengthen verbs to 20+, metrics to 15+, details to all bullets."))
    elif score < 85:
        recommended.append(("Resume Making", "🟢 FINAL POLISH: Fine-tune formatting, add more metrics, strengthen technical depth."))
    
    if verb_hits < 15:
        recommended.append(("Resume Making", "CRITICAL: Only {0} action verbs (need 25+). Every bullet must start with: Developed, Built, Optimized, Led, Increased.".format(verb_hits)))
    
    if number_hits < 10:
        recommended.append(("Resume Making", "CRITICAL: Only {0} metrics (need 18+). Add quantification: percentages, dollars, users, speed, team size.".format(number_hits)))
    
    if skills_quality["tech_count"] < 10 or len(set(tokenize(sections.get("skills", "")))) < 14:
        recommended.append(("Resume Making", "URGENT: Technical skills insufficient. List 12+ tech skills, 5+ soft skills—this significantly impacts ATS."))
    
    if not has_good_projects:
        recommended.append(("Portfolio Making", "Portfolio projects critical—resumes with projects score 40% higher. Build 3+ strong projects NOW."))
    
    if not has_portfolio:
        recommended.append(("Portfolio Making", "REQUIRED: Online portfolio is non-negotiable. Showcase projects, increases recruiter visibility by 10x."))
    
    if len(missing_keywords) >= 7:
        recommended.append(("LinkedIn Manager", "CRITICAL: 7+ skill gaps detected. LinkedIn optimization essential—immediate action recommended."))
    elif len(missing_keywords) >= 5:
        recommended.append(("LinkedIn Manager", "LinkedIn alignment urgent: {0} key skills missing from profile. Update immediately.".format(len(missing_keywords))))
    
    if any(k in missing_keywords for k in ["communication", "presentation", "public speaking", "leadership"]):
        recommended.append(("Presentation Making", "URGENT: Soft skills gap detected. Project walkthroughs and presentations are deal-breakers in interviews."))
    
    if any(k in missing_keywords for k in ["machine learning", "tensorflow", "pytorch", "deep learning", "nlp", "data science"]):
        recommended.append(("Advanced Project (ML/AI)", "HIGH-VALUE: AI/ML skills missing. Building 1 strong ML project increases competitiveness exponentially."))
    
    if score >= 85 and len(recommended) == 0:
        recommended.append(("Full Functional Website", "Excellent foundation. Build advanced full-stack project to demonstrate production-ready expertise."))
    elif score >= 75 and len(recommended) <= 2:
        recommended.append(("Full Functional Website", "Good progress. Full-stack project is critical next step—shows complete development lifecycle."))
    
    if not recommended or len(recommended) == 0:
        if score < 50:
            recommended.append(("Resume Making", "Resume Making is PRIORITY ONE—all other improvements secondary to fixing resume quality first."))
        else:
            recommended.append(("Portfolio Making", "Portfolio projects essential—are your biggest differentiator after resume optimization."))
    
    return recommended[:5]





def render_service_cards():
    st.subheader("Services")
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
            render_payment_action(focus_service["name"], focus_service["offer_price"], f"spotlight_{focus_service['name']}")
        with c2:
            st.link_button("Contact Us (Spotlight)", f"mailto:{CONTACT_EMAIL}", use_container_width=True)

    for service in SERVICES:
        with st.container(border=True):
            st.markdown(f"<div class='service-title'>{service['name']}</div>", unsafe_allow_html=True)
            st.markdown(
                (
                    f"<div class='service-price-row'>"
                    f"<span class='service-old-price'>INR {service['original_price']}</span>"
                    f"<span class='service-offer-price'>Offer INR {service['offer_price']}</span>"
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
                    st.rerun()


def render_notes_store():
    st.subheader("Handwritten Notes")
    st.caption("Premium handwritten notes to help master programming concepts.")
    for note in NOTES:
        with st.container(border=True):
            st.markdown(f"<div class='note-title'>{note['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='note-price'>Price: INR {note['price_inr']}</div>", unsafe_allow_html=True)
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
    st.markdown("""
    <style>
        .auth-container {
            background: linear-gradient(135deg, rgba(46,204,113,0.08), rgba(46,204,113,0.02));
            border: 2px solid rgba(46,204,113,0.2);
            border-radius: 16px;
            padding: 32px;
            margin-top: 20px;
        }
        .auth-title {
            font-size: 2.5rem;
            font-weight: 900;
            color: #2ee06f;
            text-align: center;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            text-align: center;
            color: #a0b0a8;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-title">🎯 CertHub</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Your Career Growth Platform</div>', unsafe_allow_html=True)
    
    render_hero()
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 🔐 Sign In")
        with st.form("signin_form"):
            email = st.text_input("📧 Email", placeholder="your@email.com", label_visibility="collapsed")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
            st.markdown("")
            submit = st.form_submit_button("➜ Sign In", use_container_width=True, type="primary")
        
        if submit:
            user = authenticate_user(email, password)
            if user:
                st.session_state["auth_user"] = user
                st.success("✅ Signed in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
    
    with col_right:
        st.markdown("### ✨ Create Account")
        with st.form("signup_form"):
            full_name = st.text_input("👤 Full Name", placeholder="Your full name", label_visibility="collapsed")
            email = st.text_input("📧 Email", key="signup_email", placeholder="your@email.com", label_visibility="collapsed")
            password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters", label_visibility="collapsed")
            st.markdown("")
            submit = st.form_submit_button("➜ Create Account", use_container_width=True, type="primary")
        
        if submit:
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters.")
            elif not full_name.strip() or not email.strip():
                st.error("❌ Name and email are required.")
            else:
                ok, msg = create_user(full_name, email, password)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")


def render_resume_checker():
    st.markdown("""
    <style>
        .score-container {
            background: linear-gradient(135deg, rgba(46,204,113,0.1), rgba(46,204,113,0.05));
            border: 2px solid rgba(46,204,113,0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        .score-number {
            font-size: 3rem;
            font-weight: 800;
            color: #2ee06f;
        }
        .score-label {
            font-size: 0.9rem;
            color: #a0b0a8;
            margin-top: 8px;
        }
        .insight-box {
            background: rgba(15, 61, 43, 0.8);
            border-left: 4px solid #2ee06f;
            padding: 14px;
            margin: 10px 0;
            border-radius: 6px;
        }
        .insight-title {
            font-weight: 700;
            color: #2ee06f;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }
        .insight-item {
            color: #c0d0c8;
            font-size: 0.9rem;
            margin: 6px 0;
            padding-left: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📄 Resume Analyzer")
    st.markdown("*Upload your resume to get AI-powered ATS scoring and actionable feedback*")

    col1, col2 = st.columns([2, 1])
    with col1:
        resume_file = st.file_uploader("📤 Upload Resume", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    with col2:
        job_role = st.text_input("🎯 Target Role (optional)", label_visibility="collapsed", placeholder="e.g., Senior Developer")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_analysis = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    if not run_analysis:
        return

    resume_text = extract_resume_text(resume_file)
    has_role = bool(job_role.strip())
    job_description = ""
    has_jd = False

    if not resume_file:
        st.error("❌ Please upload a resume file.")
        return
    if not resume_text:
        st.error("❌ Could not extract text. Try a different file format.")
        return

    if not has_role:
        score, strengths, gaps, edits = general_resume_score(resume_text)
        default_kw = {"essential": [], "preferred": [], "important": TECH_PATTERNS[:8] + SOFT_PATTERNS[:3]}
        rewritten = format_resume("Entry-Level Professional", resume_text, default_kw)
        recs = recommend_services(score, [], resume_text)

        render_primary_recommendation(recs)
        
        # Score Display
        st.markdown(f"""
        <div class="score-container">
            <div class="score-number">{score}%</div>
            <div class="score-label">ATS Compatibility Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Results in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Strengths")
            for item in strengths:
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-item">✓ {item}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### ⚠️ Gaps")
            for item in gaps:
                st.markdown(f"""
                <div class="insight-box" style="border-left-color: #ff9800;">
                    <div class="insight-item">✗ {item}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 💡 What to Improve")
            for item in edits:
                st.markdown(f"""
                <div class="insight-box" style="border-left-color: #ffc107;">
                    <div class="insight-item">→ {item}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if recs:
                st.markdown("### 🎯 Recommended Services")
                for name, reason in recs:
                    st.markdown(f"""
                    <div class="insight-box" style="border-left-color: #2ee06f;">
                        <div class="insight-title">{name}</div>
                        <div class="insight-item">{reason}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📝 ATS-Optimized Resume")
        st.markdown("*Below is your resume rewritten for maximum ATS compatibility*")
        st.text_area("", rewritten, height=300, disabled=True, label_visibility="collapsed")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                "⬇️ Download (.txt)",
                rewritten,
                file_name="certhub_optimized_resume.txt",
                use_container_width=True
            )


def render_dashboard(user):
    render_hero()
    st.markdown(f"## 👋 Welcome back, {user['name']}!")
    st.markdown("Your complete career growth platform in one place")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(46,204,113,0.15), rgba(46,204,113,0.05)); 
                    border: 2px solid rgba(46,204,113,0.3); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #2ee06f;">""" + str(len(SERVICES)) + """</div>
            <div style="color: #a0b0a8; margin-top: 8px;">Professional Services</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(52,152,219,0.15), rgba(52,152,219,0.05)); 
                    border: 2px solid rgba(52,152,219,0.3); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #3498db;">""" + str(len(NOTES)) + """</div>
            <div style="color: #a0b0a8; margin-top: 8px;">Study Notes</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(155,89,182,0.15), rgba(155,89,182,0.05)); 
                    border: 2px solid rgba(155,89,182,0.3); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #9b59b6;">🚀</div>
            <div style="color: #a0b0a8; margin-top: 8px;">Payment Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Check Your Resume", use_container_width=True, key="dash_resume"):
            st.session_state["page"] = "Resume Checker"
            st.rerun()
    with col2:
        if st.button("🛍️ Browse Services", use_container_width=True, key="dash_services"):
            st.session_state["page"] = "Services"
            st.rerun()
    
    st.markdown("---")
    st.markdown(f"📞 **{CONTACT_TEXT}**")


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
        key_id, key_secret = get_razorpay_credentials()
        st.write("Payment Settings")
        st.code(f"Razorpay Key ID: {key_id}")
        if key_secret:
            st.success("Razorpay secret is configured. Fixed-amount payment links are enabled.")
        else:
            st.warning("Razorpay secret is missing. Configure `RAZORPAY_KEY_SECRET` in Streamlit secrets for fixed checkout.")
            st.code(
                "[secrets]\n"
                "RAZORPAY_KEY_ID = \"rzp_live_RJNwYg2Jx647o8\"\n"
                "RAZORPAY_KEY_SECRET = \"your_live_secret_here\""
            )
        st.write("Fallback Payment Link:")
        st.code(RAZORPAY_LINK)
        st.write(CONTACT_TEXT)


if __name__ == "__main__":
    main()
