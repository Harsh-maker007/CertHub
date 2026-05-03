import csv
import datetime
import hashlib
import io
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
ADMIN_EMAIL = "harshshandilya01@gmail.com"
DB_PATH = "certhub_users.db"
RAZORPAY_LINK = "https://razorpay.me/@harshshandilya"
RAZORPAY_KEY_ID = "rzp_live_RJNwYg2Jx647o8"
CONTACT_EMAIL = "itscerthub@gmail.com"
CONTACT_PHONE = "+918603234533"
CONTACT_TEXT = f"Contact: {CONTACT_EMAIL} | {CONTACT_PHONE}"
INDIA_QR_PATH = os.path.join("assets", "india_qr.png")
MALAYSIA_QR_PATH = os.path.join("assets", "malaysia_qr.png")

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
    {"name": "Certificate Assistance", "description": "Help obtaining certificates from HackerRank, Infosys Springboard, Google, Udemy and platform guidance.", "best_for": "Students needing verified certifications quickly.", "original_price": 599, "offer_price": 299, "delivery_time": "Up to 12 hrs", "category": "Career"},
    {"name": "Portfolio Making", "description": "Custom portfolio website, mobile responsive, SEO optimized, professional layout, domain and hosting setup.", "best_for": "Missing project visibility and personal branding.", "original_price": 999, "offer_price": 199, "delivery_time": "24 hrs", "category": "Web"},
    {"name": "LinkedIn Manager", "description": "Profile optimization, content strategy, network building, personal branding, post scheduling.", "best_for": "Better discoverability and personal brand.", "original_price": 399, "offer_price": 199, "delivery_time": "6 hrs", "category": "Career"},
    {"name": "Presentation Making", "description": "Custom slides, data visualization, brand consistency, interactive elements, templates.", "best_for": "Interview rounds requiring project walkthroughs.", "original_price": 200, "offer_price": 100, "delivery_time": "30 min", "category": "Career"},
    {"name": "Resume Making", "description": "ATS optimized resume, professional formatting, keyword optimization, cover letter included.", "best_for": "Low ATS score, weak structure, missing role keywords.", "original_price": 500, "offer_price": 200, "delivery_time": "6 hours", "category": "Career"},
    {"name": "UI/UX Designer", "description": "User research, wireframes, prototyping, responsive design, usability testing.", "best_for": "Website/app projects needing stronger usability and visual quality.", "original_price": 599, "offer_price": 299, "delivery_time": "24 hrs", "category": "Web"},
    {"name": "Basic Website Project", "description": "Custom design, mobile responsive, up to 5 pages, contact form, basic SEO.", "best_for": "Beginners building first portfolio-ready projects.", "original_price": 699, "offer_price": 369, "delivery_time": "48 hrs", "category": "Web"},
    {"name": "Full Functional Website", "description": "Custom UI/UX, backend integration, database setup, hosting deployment.", "best_for": "Intermediate profile with deployment-ready project requirement.", "original_price": 2999, "offer_price": 999, "delivery_time": "1-2 days", "category": "Web"},
    {"name": "Advanced Project (ML/AI)", "description": "ML model development, data preprocessing, training/testing, deployment ready.", "best_for": "Students targeting data or AI roles.", "original_price": 5499, "offer_price": 2999, "delivery_time": "5-7 days", "category": "AI"},
    {"name": "Report Making", "description": "Technical reports for internships, projects, and case studies.", "best_for": "Academic and project submissions requiring formal documentation.", "original_price": 299, "offer_price": 149, "delivery_time": "6 hrs", "category": "Career"},
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
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
            html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
            .stApp{background:linear-gradient(135deg,#020810 0%,#060f1e 50%,#020810 100%);min-height:100vh}
            @keyframes pulse-glow{0%,100%{box-shadow:0 0 20px rgba(108,99,255,.15)}50%{box-shadow:0 0 40px rgba(108,99,255,.35)}}
            @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
            @keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
            @keyframes fade-in{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
            section[data-testid="stSidebar"]{background:linear-gradient(180deg,#030b18 0%,#071224 100%)!important;border-right:1px solid rgba(108,99,255,.2)!important}
            .stButton>button{border-radius:12px!important;font-weight:700!important;transition:all .25s ease!important;letter-spacing:.3px!important}
            .stButton>button:hover{transform:translateY(-3px)!important;box-shadow:0 8px 24px rgba(108,99,255,.4)!important}
            .hero-section{background:linear-gradient(135deg,rgba(108,99,255,.14) 0%,rgba(0,212,255,.08) 100%);border:1px solid rgba(108,99,255,.3);border-radius:24px;padding:48px 36px;margin-bottom:28px;position:relative;overflow:hidden;animation:fade-in .6s ease}
            .hero-section::before{content:'';position:absolute;top:-60px;right:-60px;width:260px;height:260px;background:radial-gradient(circle,rgba(108,99,255,.18) 0%,transparent 70%);pointer-events:none}
            .hero-title{font-size:3rem;font-weight:900;background:linear-gradient(135deg,#a78bfa,#6C63FF,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;margin:0 0 14px 0}
            .hero-sub{color:#94a3b8;font-size:1.1rem;margin:0 0 22px 0;line-height:1.7}
            .feature-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
            .feature-chip{background:rgba(108,99,255,.13);border:1px solid rgba(108,99,255,.3);border-radius:30px;padding:7px 18px;color:#c4b5fd;font-size:.83rem;font-weight:600}
            .trust-bar{display:flex;gap:28px;flex-wrap:wrap;align-items:center;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:14px 24px;margin:16px 0 20px 0}
            .trust-item{display:flex;align-items:center;gap:8px;color:#94a3b8;font-size:.85rem;font-weight:500}
            .trust-item b{color:#e2e8f0}
            .urgency-bar{background:linear-gradient(90deg,rgba(239,68,68,.12),rgba(245,158,11,.12));border:1px solid rgba(239,68,68,.25);border-radius:12px;padding:10px 20px;text-align:center;color:#fca5a5;font-size:.88rem;font-weight:600;margin-bottom:18px;animation:pulse-glow 2s infinite}
            .step-card{background:rgba(108,99,255,.06);border:1px solid rgba(108,99,255,.18);border-radius:16px;padding:24px 20px;text-align:center;transition:all .25s}
            .step-card:hover{transform:translateY(-4px);box-shadow:0 14px 40px rgba(108,99,255,.2);border-color:rgba(108,99,255,.35)}
            .step-num{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#6C63FF,#00D4FF);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1.1rem;color:#fff;margin:0 auto 14px auto}
            .step-title{font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:6px}
            .step-desc{color:#64748b;font-size:.85rem;line-height:1.6}
            .testimonial-card{background:rgba(255,255,255,.04);border:1px solid rgba(108,99,255,.15);border-radius:16px;padding:22px 22px 16px 22px;margin-bottom:10px}
            .testimonial-text{color:#cbd5e1;font-size:.9rem;line-height:1.7;margin-bottom:12px}
            .testimonial-author{font-weight:700;color:#a78bfa;font-size:.82rem}
            .testimonial-role{color:#475569;font-size:.78rem}
            .stars{color:#f59e0b;letter-spacing:2px;margin-bottom:8px;font-size:.9rem}
            .premium-card{background:rgba(255,255,255,.04);backdrop-filter:blur(14px);border:1px solid rgba(108,99,255,.18);border-radius:18px;padding:26px;margin-bottom:14px;transition:transform .25s,box-shadow .25s}
            .premium-card:hover{transform:translateY(-4px);box-shadow:0 16px 48px rgba(108,99,255,.2)}
            .stat-card{background:rgba(255,255,255,.04);border:1px solid rgba(108,99,255,.18);border-radius:16px;padding:24px;text-align:center;transition:all .25s}
            .stat-card:hover{border-color:rgba(108,99,255,.4);transform:translateY(-4px)}
            .stat-number{font-size:2.6rem;font-weight:900;background:linear-gradient(135deg,#6C63FF,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
            .stat-label{font-size:.8rem;color:#64748b;margin-top:6px;letter-spacing:.8px;text-transform:uppercase}
            .score-ring-wrap{display:flex;justify-content:center;align-items:center;margin:20px 0}
            .insight-success{background:rgba(16,185,129,.08);border-left:3px solid #10b981;border-radius:10px;padding:12px 16px;margin:6px 0;color:#d1fae5;font-size:.88rem}
            .insight-warn{background:rgba(245,158,11,.08);border-left:3px solid #f59e0b;border-radius:10px;padding:12px 16px;margin:6px 0;color:#fef3c7;font-size:.88rem}
            .insight-danger{background:rgba(239,68,68,.08);border-left:3px solid #ef4444;border-radius:10px;padding:12px 16px;margin:6px 0;color:#fee2e2;font-size:.88rem}
            .insight-info{background:rgba(108,99,255,.08);border-left:3px solid #6C63FF;border-radius:10px;padding:12px 16px;margin:6px 0;color:#e0e7ff;font-size:.88rem}
            .service-card{background:rgba(255,255,255,.04);border:1px solid rgba(108,99,255,.15);border-top:3px solid #6C63FF;border-radius:18px;padding:22px;margin-bottom:12px;transition:all .25s}
            .service-card:hover{border-color:rgba(108,99,255,.45);transform:translateY(-3px);box-shadow:0 10px 32px rgba(108,99,255,.18)}
            .service-name{font-size:1.05rem;font-weight:700;color:#f1f5f9;margin-bottom:6px}
            .offer-price{font-size:1.3rem;font-weight:900;color:#818cf8}
            .orig-price{font-size:.85rem;color:#475569;text-decoration:line-through;margin-right:8px}
            .delivery-badge{display:inline-block;background:rgba(16,185,129,.12);color:#34d399;border:1px solid rgba(16,185,129,.25);border-radius:20px;padding:3px 11px;font-size:.73rem;font-weight:600;margin-left:8px}
            .best-for-pill{display:inline-block;background:rgba(108,99,255,.1);color:#a78bfa;border:1px solid rgba(108,99,255,.2);border-radius:20px;padding:3px 11px;font-size:.73rem;margin-top:8px}
            .hot-badge{display:inline-block;background:linear-gradient(90deg,#ef4444,#f97316);color:#fff;border-radius:20px;padding:2px 10px;font-size:.7rem;font-weight:700;margin-left:6px;letter-spacing:.5px}
            .note-card{background:rgba(255,255,255,.04);border:1px solid rgba(0,212,255,.15);border-top:3px solid #00D4FF;border-radius:18px;padding:22px;margin-bottom:12px;transition:all .25s}
            .note-card:hover{transform:translateY(-3px);box-shadow:0 10px 32px rgba(0,212,255,.14)}
            .note-name{font-size:1.05rem;font-weight:700;color:#f1f5f9;margin-bottom:6px}
            .note-price{font-size:1.2rem;font-weight:900;color:#22d3ee}
            .topic-pill{display:inline-block;background:rgba(0,212,255,.08);color:#67e8f9;border:1px solid rgba(0,212,255,.18);border-radius:20px;padding:2px 9px;font-size:.72rem;margin:2px 2px 4px 0}
            .page-title{font-size:1.8rem;font-weight:900;background:linear-gradient(135deg,#6C63FF,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
            .page-sub{color:#475569;font-size:.92rem;margin-bottom:22px}
            .admin-badge{display:inline-block;background:linear-gradient(135deg,#6C63FF,#00D4FF);color:#fff;border-radius:20px;padding:3px 14px;font-size:.72rem;font-weight:700;letter-spacing:.5px}
            .admin-stat{background:rgba(108,99,255,.07);border:1px solid rgba(108,99,255,.18);border-radius:14px;padding:20px;text-align:center}
            .reco-card{border:2px solid rgba(108,99,255,.5);border-radius:18px;padding:20px;margin:8px 0 16px 0;background:linear-gradient(135deg,rgba(108,99,255,.1),rgba(0,212,255,.05));box-shadow:0 0 0 1px rgba(108,99,255,.15),0 10px 30px rgba(0,0,0,.35);animation:pulse-glow 3s infinite}
            .reco-label{color:#a78bfa;font-weight:700;font-size:.8rem;text-transform:uppercase;letter-spacing:.8px}
            .reco-main{color:#f1f5f9;font-size:1.4rem;font-weight:900;margin:6px 0}
            .reco-reason{color:#94a3b8;font-size:.92rem}
            .auth-card{background:rgba(255,255,255,.03);border:1px solid rgba(108,99,255,.2);border-radius:18px;padding:30px 24px}
            .footer-bar{background:rgba(108,99,255,.06);border:1px solid rgba(108,99,255,.12);border-radius:14px;padding:16px 24px;text-align:center;margin-top:28px;color:#475569;font-size:.85rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="urgency-bar">🔥 Limited Offer — Save up to 66% on all services this week only!</div>
        <div class="hero-section">
            <p class="hero-title">🚀 CertHub — Your Career Launchpad</p>
            <p class="hero-sub">India's #1 platform for ATS-optimized resumes, expert career services &amp; premium study notes.<br>Join <b>2,000+</b> students who landed their dream jobs with CertHub.</p>
            <div class="trust-bar">
                <div class="trust-item">✅ <b>2,000+</b> Students Served</div>
                <div class="trust-item">⚡ <b>30-min</b> Fastest Delivery</div>
                <div class="trust-item">🏆 <b>4.9★</b> Avg Rating</div>
                <div class="trust-item">💯 <b>100%</b> Satisfaction Guarantee</div>
                <div class="trust-item">🔒 Secure Payments</div>
            </div>
            <div class="feature-row">
                <span class="feature-chip">📄 ATS Resume Scorer</span>
                <span class="feature-chip">🛍️ 10+ Expert Services</span>
                <span class="feature-chip">📚 Premium Study Notes</span>
                <span class="feature-chip">⚡ Fast Delivery</span>
                <span class="feature-chip">🎯 Job-Specific Advice</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_it_works():
    st.markdown('<p class="page-title">⚡ How It Works</p><p class="page-sub">Get your career on track in 3 simple steps</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    steps = [
        ("1", "Upload or Analyze", "Upload your resume or browse our services. Our AI scores your resume instantly."),
        ("2", "Get Expert Help", "Choose a service. Our experts deliver high-quality work within your timeline."),
        ("3", "Land Your Dream Job", "Apply with a stronger profile, pass ATS filters, and ace your interviews."),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(f'<div class="step-card"><div class="step-num">{num}</div><div class="step-title">{title}</div><div class="step-desc">{desc}</div></div>', unsafe_allow_html=True)


def render_testimonials():
    st.markdown('<p class="page-title" style="margin-top:8px">💬 What Students Say</p>', unsafe_allow_html=True)
    testimonials = [
        ("Got placed at Infosys within 2 weeks of using CertHub's resume service. My ATS score jumped from 34% to 87%!", "Priya S.", "Software Engineer @ Infosys", "★★★★★"),
        ("The LinkedIn Manager service got me 3x more profile views in a week. Highly recommend!", "Rahul M.", "Data Analyst @ TCS", "★★★★★"),
        ("Best investment for my career. Got my Python notes + resume done together. Super affordable!", "Aisha K.", "ML Engineer @ Wipro", "★★★★★"),
    ]
    cols = st.columns(3)
    for col, (text, author, role, stars) in zip(cols, testimonials):
        with col:
            st.markdown(f'<div class="testimonial-card"><div class="stars">{stars}</div><div class="testimonial-text">"{text}"</div><div class="testimonial-author">{author}</div><div class="testimonial-role">{role}</div></div>', unsafe_allow_html=True)

def render_primary_recommendation(recommended):
    if not recommended:
        return
    top_name, top_reason = recommended[0]
    top_service = next((s for s in SERVICES if s["name"] == top_name), None)
    top_offer_price = top_service["offer_price"] if top_service else None
    st.markdown(
        f"""
        <div class="reco-card">
            <div class="reco-label">⭐ Recommended For You</div>
            <div class="reco-main">{top_name}</div>
            <div class="reco-reason">{top_reason}</div>
            <div class="reco-reason" style="margin-top:8px"><span style="color:#6C63FF;font-weight:700">Offer Price: INR {top_offer_price if top_offer_price else 'NA'}</span></div>
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
        if st.button("🔍 Open This Service", use_container_width=True, key=f"open_reco_{top_name}"):
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
    user = st.session_state.get("auth_user") or {}
    payment_country = user.get("country", "Other")
    if payment_country in {"India", "Malaysia"}:
        st.markdown("**Scan to Pay**")
        if payment_country == "India":
            st.image(INDIA_QR_PATH, use_container_width=True, caption="UPI QR (India)")
        else:
            st.image(MALAYSIA_QR_PATH, use_container_width=True, caption="Malaysia National QR")
        st.caption("After payment, share the transaction ID with support for confirmation.")
        return

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


def get_all_users():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, full_name, email, country, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows


def get_user_count():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count


def delete_user(email: str):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE email = ?", (email.strip().lower(),))
    conn.commit()
    conn.close()


def update_user(email: str, new_name: str, new_country: str):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET full_name = ?, country = ? WHERE email = ?",
        (new_name.strip(), new_country.strip(), email.strip().lower()),
    )
    conn.commit()
    conn.close()


def reset_password_db(email: str, full_name: str, new_password: str):
    """Reset password after verifying email + full_name match."""
    email = email.strip().lower()
    conn = get_conn()
    row = conn.execute(
        "SELECT full_name FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    if not row:
        return False, "No account found with that email."
    if row[0].strip().lower() != full_name.strip().lower():
        return False, "Full name does not match our records."
    salt, pw_hash = hash_password(new_password)
    conn = get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ?, salt = ? WHERE email = ?",
        (pw_hash, salt, email),
    )
    conn.commit()
    conn.close()
    return True, "Password reset successfully. Please sign in."


def change_password(email: str, old_password: str, new_password: str):
    user = authenticate_user(email, old_password)
    if not user:
        return False, "Current password is incorrect."
    salt, pw_hash = hash_password(new_password)
    conn = get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ?, salt = ? WHERE email = ?",
        (pw_hash, salt, email.strip().lower()),
    )
    conn.commit()
    conn.close()
    return True, "Password changed successfully."


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
    st.markdown('<p class="page-title">🛍️ Services</p><p class="page-sub">Expert services to accelerate your career growth</p>', unsafe_allow_html=True)
    cats = ["All"] + sorted(set(s.get("category","Other") for s in SERVICES))
    sel_cat = st.radio("Filter", cats, horizontal=True, label_visibility="collapsed")
    filtered = SERVICES if sel_cat == "All" else [s for s in SERVICES if s.get("category") == sel_cat]
    focus_name = st.session_state.get("selected_service")
    focus_service = next((s for s in SERVICES if s["name"] == focus_name), None)
    if focus_service:
        st.markdown(f"""
        <div class="reco-card">
            <div class="reco-label">✨ Service Spotlight</div>
            <div class="reco-main">{focus_service['name']}</div>
            <div class="reco-reason">{focus_service['description']}</div>
            <div class="reco-reason"><b>Best for:</b> {focus_service['best_for']}</div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            render_payment_action(focus_service["name"], focus_service["offer_price"], f"spotlight_{focus_service['name']}")
        with c2:
            st.link_button("📧 Contact Us", f"mailto:{CONTACT_EMAIL}?subject=Inquiry%20for%20{focus_service['name'].replace(' ','%20')}", use_container_width=True)
        st.markdown("---")
    cols = st.columns(3)
    for i, service in enumerate(filtered):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="service-card">
                <div class="service-name">{service['name']}</div>
                <div style="margin:4px 0 8px 0">
                    <span class="orig-price">₹{service['original_price']}</span>
                    <span class="offer-price">₹{service['offer_price']}</span>
                    <span class="delivery-badge">⚡ {service['delivery_time']}</span>
                </div>
                <div style="color:#94a3b8;font-size:.88rem;margin-bottom:8px">{service['description']}</div>
                <div class="best-for-pill">🎯 {service['best_for']}</div>
            </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                render_payment_action(service["name"], service["offer_price"], f"svc_{service['name']}")
            with c2:
                st.link_button("Contact", f"mailto:{CONTACT_EMAIL}?subject={service['name'].replace(' ','%20')}", use_container_width=True)

    focus_name = st.session_state.get("selected_service")
    focus_service = next((s for s in SERVICES if s["name"] == focus_name), None)



def render_notes_store():
    st.markdown('<p class="page-title">📚 Study Notes</p><p class="page-sub">Premium handwritten notes to master programming concepts</p>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, note in enumerate(NOTES):
        with cols[i % 3]:
            topics_html = "".join(f'<span class="topic-pill">{t}</span>' for t in note["topics"])
            st.markdown(f"""
            <div class="note-card">
                <div class="note-name">{note['title']}</div>
                <div class="note-price">₹{note['price_inr']}</div>
                <div style="margin-top:10px">{topics_html}</div>
            </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                render_payment_action(note["title"], note["price_inr"], f"note_{note['title']}")
            with c2:
                st.link_button("Contact", f"mailto:{CONTACT_EMAIL}?subject={note['title'].replace(' ','%20')}", use_container_width=True)


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
    st.caption("Build: country-select enabled")
    
    render_hero()
    st.markdown('<p style="text-align:center;color:#64748b;font-size:.85rem;margin-top:-10px">Forgot password? Use the tab below ↓</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔐 Sign In", "✨ Create Account", "🔑 Reset Password"])
    with tab1:
        with st.form("signin_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
        if submit:
            user = authenticate_user(email, password)
            if user:
                st.session_state["auth_user"] = user
                st.success("✅ Signed in!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
    with tab2:
        with st.form("signup_form"):
            full_name = st.text_input("Full Name", placeholder="Your full name")
            email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Min 8 characters")
            country = st.selectbox("Country", ["India", "Malaysia", "Other"], index=2)
            submit = st.form_submit_button("Create Account →", use_container_width=True, type="primary")
        if submit:
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters.")
            elif not full_name.strip() or not email.strip():
                st.error("❌ Name and email are required.")
            else:
                ok, msg = create_user(full_name, email, password, country)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
    with tab3:
        st.caption("Verify your identity with your registered name to reset password.")
        with st.form("reset_form"):
            r_email = st.text_input("Registered Email", placeholder="your@email.com")
            r_name = st.text_input("Full Name (as registered)", placeholder="Your full name")
            r_new = st.text_input("New Password", type="password", placeholder="Min 8 characters")
            r_submit = st.form_submit_button("Reset Password →", use_container_width=True, type="primary")
        if r_submit:
            if len(r_new) < 8:
                st.error("❌ New password must be at least 8 characters.")
            else:
                ok, msg = reset_password_db(r_email, r_name, r_new)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")


def _score_color(score):
    if score >= 75: return "#10b981", "#d1fae5"
    if score >= 50: return "#f59e0b", "#fef3c7"
    return "#ef4444", "#fee2e2"


def _build_resume_text(role, resume_text, jd_kw):
    sections = split_sections(resume_text)
    summary = build_summary(role, sections, jd_kw)
    skills = merge_skills(sections, jd_kw)
    exp_bullets = bullets_from_text(sections.get("experience", ""))
    proj_bullets = bullets_from_text(sections.get("projects", ""))
    edu_bullets = bullets_from_text(sections.get("education", ""), max_items=3)
    cert_bullets = bullets_from_text(sections.get("certifications", ""), max_items=3)
    if not exp_bullets:
        exp_bullets = ["Academic or internship experience with measurable outcomes."]
    if not proj_bullets:
        proj_bullets = ["Project details with tech stack, role, and impact metrics."]
    if not edu_bullets:
        edu_bullets = ["Degree, Institution, Graduation Year, Relevant Coursework."]
    name_contact = sections.get("name & contact", "").strip() or "Candidate Name | Phone | Email | LinkedIn | GitHub"
    sep = "=" * 60
    lines = [
        sep,
        f"  TARGET ROLE: {role.upper()}",
        sep, "",
        "CONTACT",
        "-" * 40,
        name_contact, "",
        "PROFESSIONAL SUMMARY",
        "-" * 40,
        summary, "",
        "SKILLS",
        "-" * 40,
        ", ".join(skills) if skills else "Python, SQL, Communication, Problem Solving", "",
        "EXPERIENCE",
        "-" * 40,
    ]
    lines += [f"  • {b}" for b in exp_bullets]
    lines += ["", "PROJECTS", "-" * 40]
    lines += [f"  • {b}" for b in proj_bullets]
    lines += ["", "EDUCATION", "-" * 40]
    lines += [f"  • {b}" for b in edu_bullets]
    if cert_bullets:
        lines += ["", "CERTIFICATIONS", "-" * 40]
        lines += [f"  • {b}" for b in cert_bullets]
    lines += ["", sep]
    return "\n".join(lines)


def render_resume_checker():
    st.markdown('<p class="page-title">📄 Resume Analyzer</p><p class="page-sub">AI-powered ATS scoring with actionable improvement insights</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        resume_file = st.file_uploader("Upload Resume (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
    with col2:
        job_role = st.text_input("Target Role (optional)", placeholder="e.g. Data Scientist")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        run_analysis = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    if not run_analysis:
        return
    if not resume_file:
        st.error("❌ Please upload a resume file.")
        return
    resume_text = extract_resume_text(resume_file)
    if not resume_text:
        st.error("❌ Could not extract text. Try a different file format.")
        return
    has_role = bool(job_role.strip())
    if has_role:
        jd_kw = extract_keywords(job_role)
        ats_score, matched_kw, missing_kw = ats_match(resume_text, jd_kw)
        score = ats_score
        score_label = "Job-Specific ATS Match"
        recs = recommend_services(score, missing_kw, resume_text)
        rewritten = _build_resume_text(job_role, resume_text, jd_kw)
        strengths_list = [f"Matched keyword: {k}" for k in matched_kw[:5]]
        gaps_list = [f"Missing keyword: {k}" for k in missing_kw[:5]]
        edits_list = [f"Add '{k}' to your resume skills/experience" for k in missing_kw[:4]]
    else:
        score, strengths_list, gaps_list, edits_list = general_resume_score(resume_text)
        score_label = "General ATS Score"
        jd_kw = {"essential": [], "preferred": [], "important": TECH_PATTERNS[:8] + SOFT_PATTERNS[:3]}
        recs = recommend_services(score, [], resume_text)
        rewritten = _build_resume_text("Entry-Level Professional", resume_text, jd_kw)
        matched_kw, missing_kw = [], []
    ring_color, _ = _score_color(score)
    ring_bg = f"conic-gradient({ring_color} {score * 3.6}deg, rgba(255,255,255,0.06) 0deg)"
    st.markdown(f"""
    <div class="score-ring-wrap">
        <div style="width:160px;height:160px;border-radius:50%;background:{ring_bg};display:flex;align-items:center;justify-content:center;">
            <div style="width:120px;height:120px;border-radius:50%;background:#080f1f;display:flex;flex-direction:column;align-items:center;justify-content:center;">
                <div style="font-size:2rem;font-weight:900;color:#f1f5f9">{score}%</div>
                <div style="font-size:.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px">{score_label}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    render_primary_recommendation(recs)
    t1, t2, t3, t4 = st.tabs(["✅ Strengths", "⚠️ Gaps", "💡 Improvements", "📝 Optimized Resume"])
    with t1:
        if strengths_list:
            for item in strengths_list:
                st.markdown(f'<div class="insight-success">✓ {item}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a more detailed resume for strength analysis.")
    with t2:
        for item in gaps_list:
            cls = "insight-danger" if "CRITICAL" in item else "insight-warn"
            st.markdown(f'<div class="{cls}">✗ {item}</div>', unsafe_allow_html=True)
    with t3:
        for item in edits_list:
            st.markdown(f'<div class="insight-info">→ {item}</div>', unsafe_allow_html=True)
    with t4:
        st.markdown("**ATS-Optimized Resume** — structured for maximum compatibility:")
        st.text_area("Optimized Resume", rewritten, height=420, key="resume_out")
        st.download_button("⬇️ Download (.txt)", rewritten, file_name="certhub_ats_resume.txt", use_container_width=False)


def render_dashboard(user):
    render_hero()
    avatar = user["name"][0].upper()
    st.markdown(f"""
    <div class="premium-card" style="display:flex;align-items:center;gap:16px;padding:20px 24px">
        <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#6C63FF,#00D4FF);display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:900;color:#fff;flex-shrink:0">{avatar}</div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#f1f5f9">Welcome back, {user['name']}! 👋</div>
            <div style="font-size:.85rem;color:#64748b">{user['email']} · {user.get('country','Other')}</div>
        </div>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    stats = [(str(len(SERVICES)), "Expert Services"), (str(len(NOTES)), "Study Notes"), ("2,000+", "Students Helped"), ("4.9★", "Avg Rating")]
    for col, (num, lbl) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("📄 Analyze Resume", use_container_width=True, key="dash_resume"):
            st.session_state["page"] = "Resume Checker"; st.rerun()
    with qa2:
        if st.button("🛍️ Browse Services", use_container_width=True, key="dash_services"):
            st.session_state["page"] = "Services"; st.rerun()
    with qa3:
        if st.button("📚 Study Notes", use_container_width=True, key="dash_notes"):
            st.session_state["page"] = "Notes Store"; st.rerun()
    with qa4:
        st.link_button("📧 Contact Support", f"mailto:{CONTACT_EMAIL}", use_container_width=True)
    st.markdown("---")
    render_how_it_works()
    st.markdown("---")
    st.markdown("### 🌟 Featured Service")
    import random
    feat = random.choice(SERVICES)
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        st.markdown(f"""
        <div class="service-card">
            <div class="service-name">{feat['name']} <span class="hot-badge">🔥 HOT</span></div>
            <div style="margin:6px 0"><span class="orig-price">₹{feat['original_price']}</span><span class="offer-price">₹{feat['offer_price']}</span><span class="delivery-badge">⚡ {feat['delivery_time']}</span></div>
            <div style="color:#94a3b8;font-size:.88rem">{feat['description']}</div>
            <div class="best-for-pill">🎯 {feat['best_for']}</div>
        </div>""", unsafe_allow_html=True)
    with fc2:
        if st.button("🛍️ Get This Service", use_container_width=True, key="feat_svc"):
            st.session_state["selected_service"] = feat["name"]
            st.session_state["page"] = "Services"
            st.rerun()
        st.link_button("📧 Contact Us", f"mailto:{CONTACT_EMAIL}", use_container_width=True)
    st.markdown("---")
    render_testimonials()
    st.markdown(f'<div class="footer-bar">📞 {CONTACT_TEXT} &nbsp;|&nbsp; 🌐 <a href="mailto:{CONTACT_EMAIL}" style="color:#818cf8">itscerthub@gmail.com</a> &nbsp;|&nbsp; Built with ❤️ for career growth</div>', unsafe_allow_html=True)


def render_profile(user):
    st.markdown('<p class="page-title">👤 Profile</p><p class="page-sub">Manage your account details</p>', unsafe_allow_html=True)
    avatar = user["name"][0].upper()
    st.markdown(f"""
    <div class="premium-card" style="display:flex;align-items:center;gap:16px">
        <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#6C63FF,#00D4FF);display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:900;color:#fff">{avatar}</div>
        <div><div style="font-size:1.2rem;font-weight:700;color:#f1f5f9">{user['name']}</div>
        <div style="color:#64748b">{user['email']}</div></div>
    </div>""", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["✏️ Edit Profile", "🔒 Change Password", "💳 Payment Info"])
    with t1:
        with st.form("edit_profile"):
            new_name = st.text_input("Full Name", value=user["name"])
            new_country = st.selectbox("Country", ["India", "Malaysia", "Other"], index=["India","Malaysia","Other"].index(user.get("country","Other")))
            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                update_user(user["email"], new_name, new_country)
                st.session_state["auth_user"]["name"] = new_name
                st.session_state["auth_user"]["country"] = new_country
                st.success("✅ Profile updated!")
                st.rerun()
    with t2:
        with st.form("change_pw"):
            old_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password", placeholder="Min 8 characters")
            if st.form_submit_button("Change Password", type="primary", use_container_width=True):
                if len(new_pw) < 8:
                    st.error("❌ New password must be at least 8 characters.")
                else:
                    ok, msg = change_password(user["email"], old_pw, new_pw)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
    with t3:
        key_id, key_secret = get_razorpay_credentials()
        st.code(f"Razorpay Key ID: {key_id}")
        if key_secret:
            st.success("✅ Razorpay configured. Dynamic payment links enabled.")
        else:
            st.warning("⚠️ Razorpay secret missing. Add RAZORPAY_KEY_SECRET to Streamlit secrets.")
        st.write(CONTACT_TEXT)


def render_admin_dashboard():
    st.markdown('<p class="page-title">🛡️ Admin Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<span class="admin-badge">ADMIN</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    total_users = get_user_count()
    all_users = get_all_users()
    countries = set(r[3] for r in all_users if r[3])
    c1, c2, c3 = st.columns(3)
    for col, (num, lbl) in zip([c1, c2, c3], [(total_users,"Total Users"),(len(countries),"Countries"),(len(SERVICES),"Services Listed")]):
        with col:
            st.markdown(f'<div class="admin-stat"><div class="stat-number">{num}</div><div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("### 🕐 Recent Sign-Ups")
    for row in all_users[:10]:
        _, name, email, country, created = row
        st.markdown(f'<div class="insight-info">👤 <b>{name}</b> · {email} · {country} · <span style="color:#475569">{created[:10]}</span></div>', unsafe_allow_html=True)


def render_admin_users():
    st.markdown('<p class="page-title">👥 User Management</p><p class="page-sub">View, edit and delete user accounts</p>', unsafe_allow_html=True)
    all_users = get_all_users()
    search = st.text_input("🔍 Search by name or email", placeholder="Type to filter...")
    filtered = [r for r in all_users if not search or search.lower() in r[1].lower() or search.lower() in r[2].lower()]
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["ID","Name","Email","Country","Joined"])
    writer.writerows(filtered)
    st.download_button("⬇️ Export CSV", csv_data.getvalue(), "certhub_users.csv", "text/csv")
    st.markdown(f"**{len(filtered)} users**")
    for row in filtered:
        uid, name, email, country, created = row
        if email.lower() == ADMIN_EMAIL.lower():
            continue
        with st.expander(f"👤 {name} — {email} ({country})"):
            st.caption(f"Joined: {created[:10]}")
            ecol1, ecol2, ecol3 = st.columns([2, 1, 1])
            with ecol1:
                new_name = st.text_input("Name", value=name, key=f"name_{uid}")
                new_country = st.selectbox("Country", ["India","Malaysia","Other"], index=["India","Malaysia","Other"].index(country) if country in ["India","Malaysia","Other"] else 2, key=f"country_{uid}")
            with ecol2:
                if st.button("💾 Save", key=f"save_{uid}", use_container_width=True):
                    update_user(email, new_name, new_country)
                    st.success("✅ Updated")
                    st.rerun()
            with ecol3:
                if st.button("🗑️ Delete", key=f"del_{uid}", use_container_width=True, type="secondary"):
                    if st.session_state.get(f"confirm_del_{uid}"):
                        delete_user(email)
                        st.success(f"Deleted {email}")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{uid}"] = True
                        st.warning("Click Delete again to confirm.")


def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🚀", layout="wide")
    inject_theme()
    init_db()
    for k, v in [("auth_user", None), ("page", "Dashboard"), ("selected_service", None)]:
        if k not in st.session_state:
            st.session_state[k] = v
    user = st.session_state["auth_user"]
    if not user:
        render_auth()
        return
    is_admin = user.get("email","").lower() == ADMIN_EMAIL.lower()
    user_pages = ["Dashboard", "Resume Checker", "Services", "Notes Store", "Profile"]
    admin_pages = ["Admin Dashboard", "User Management"]
    pages = user_pages + (admin_pages if is_admin else [])
    with st.sidebar:
        st.markdown(f'<div style="font-size:1.3rem;font-weight:900;background:linear-gradient(135deg,#6C63FF,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px">🚀 {APP_NAME}</div>', unsafe_allow_html=True)
        if is_admin:
            st.markdown('<span class="admin-badge">ADMIN</span>', unsafe_allow_html=True)
        st.caption(user["email"])
        st.markdown("---")
        current_page = st.session_state.get("page", "Dashboard")
        if current_page not in pages:
            current_page = "Dashboard"
        page = st.radio("Navigation", pages, index=pages.index(current_page), label_visibility="collapsed")
        st.session_state["page"] = page
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in ["auth_user", "selected_service"]:
                st.session_state[k] = None
            st.session_state["page"] = "Dashboard"
            st.rerun()
        st.markdown(f'<p style="color:#475569;font-size:.75rem;text-align:center;margin-top:8px">{CONTACT_TEXT}</p>', unsafe_allow_html=True)
    if page == "Dashboard":
        render_dashboard(user)
    elif page == "Resume Checker":
        render_resume_checker()
    elif page == "Services":
        render_service_cards()
    elif page == "Notes Store":
        render_notes_store()
    elif page == "Profile":
        render_profile(user)
    elif page == "Admin Dashboard":
        render_admin_dashboard()
    elif page == "User Management":
        render_admin_users()


if __name__ == "__main__":
    main()
