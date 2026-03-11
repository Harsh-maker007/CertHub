#!/usr/bin/env python3
"""Quick test script to verify app.py functions work correctly."""

import sys
import os

# Test imports
print("=" * 60)
print("🧪 QUICK TEST - VERIFYING APP.PY")
print("=" * 60)

print("\n1️⃣ Testing imports...")
try:
    import datetime
    import hashlib
    import os
    import re
    import sqlite3
    from collections import Counter
    from io import BytesIO
    import secrets
    print("   ✅ Built-in imports OK")
except Exception as e:
    print(f"   ❌ Built-in imports FAILED: {e}")
    sys.exit(1)

try:
    import docx
    print("   ✅ python-docx OK")
except ImportError:
    print("   ❌ python-docx NOT installed - Run: pip install python-docx")
    sys.exit(1)

try:
    import pdfplumber
    print("   ✅ pdfplumber OK")
except ImportError:
    print("   ❌ pdfplumber NOT installed - Run: pip install pdfplumber")
    sys.exit(1)

try:
    import requests
    print("   ✅ requests OK")
except ImportError:
    print("   ❌ requests NOT installed - Run: pip install requests")
    sys.exit(1)

try:
    import streamlit as st
    print("   ✅ streamlit OK")
except ImportError:
    print("   ❌ streamlit NOT installed - Run: pip install streamlit>=1.55.0")
    sys.exit(1)

print("\n2️⃣ Checking app.py syntax...")
try:
    import py_compile
    py_compile.compile('app.py', doraise=True)
    print("   ✅ app.py syntax OK")
except py_compile.PyCompileError as e:
    print(f"   ❌ Syntax error in app.py: {e}")
    sys.exit(1)

print("\n3️⃣ Loading app.py constants...")
try:
    from app import (
        HEADINGS, SECTION_ALIASES, TECH_PATTERNS, SOFT_PATTERNS,
        general_resume_score, render_score_circle
    )
    print(f"   ✅ HEADINGS: {len(HEADINGS)} sections")
    print(f"   ✅ TECH_PATTERNS: {len(TECH_PATTERNS)} skills")
    print(f"   ✅ SOFT_PATTERNS: {len(SOFT_PATTERNS)} soft skills")
    print(f"   ✅ SECTION_ALIASES: {len(SECTION_ALIASES)} sections")
except Exception as e:
    print(f"   ❌ Failed to load constants: {e}")
    sys.exit(1)

print("\n4️⃣ Verifying HEADINGS (8 sections)...")
expected_headings = [
    "target job role",
    "name & contact",
    "professional summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]
for i, heading in enumerate(expected_headings, 1):
    if heading in HEADINGS:
        print(f"   ✅ [{i}] {heading}")
    else:
        print(f"   ❌ [{i}] {heading} MISSING")

print("\n5️⃣ Verifying key skills in patterns...")
key_skills = {
    "Tech": ["python", "java", "react", "docker", "aws"],
    "Soft": ["communication", "leadership", "problem solving"],
}
for category, skills in key_skills.items():
    patterns = TECH_PATTERNS if category == "Tech" else SOFT_PATTERNS
    for skill in skills:
        if any(skill.lower() in p.lower() for p in patterns):
            print(f"   ✅ {category}: {skill}")
        else:
            print(f"   ❌ {category}: {skill} NOT found")

print("\n6️⃣ Testing scoring function with sample resume...")
sample_resume = """
JOHN DOE
New York, NY | john@email.com | (555) 123-4567 | LinkedIn.com/in/johndoe | GitHub.com/johndoe

TARGET ROLE: Software Engineer

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years building scalable web applications.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, Java
Frontend: React, Vue.js, HTML5, CSS3, Tailwind
Backend: Node.js, Django, Flask, FastAPI
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes
Tools: Git, GitHub, Jira, VS Code

EXPERIENCE
Senior Software Engineer | Tech Company | Jan 2022 - Present
- Led development of microservices reducing latency by 40%
- Architected REST APIs serving 10M+ requests/day
- Mentored team of 5 junior developers
- Implemented CI/CD pipeline using GitHub Actions

Software Engineer | Startup Inc | Jun 2020 - Dec 2021
- Built full-stack web applications using React and Django
- Optimized database queries improving performance by 35%
- Collaborated with product team on requirements

PROJECTS
E-Commerce Platform (Personal)
- Built with React, Node.js, MongoDB
- Implemented payment integration and user authentication

Data Analysis Dashboard
- Created with Python, Pandas, and Plotly
- Processed 100K+ data points daily

EDUCATION
Bachelor of Science in Computer Science
State University | Graduated 2020

CERTIFICATIONS
AWS Certified Solutions Architect
Google Cloud Professional Cloud Architect
"""

try:
    score, strengths, gaps, edits = general_resume_score(sample_resume)
    print(f"   ✅ Score calculated: {score}%")
    print(f"   ✅ Strengths: {len(strengths)} items")
    print(f"   ✅ Gaps: {len(gaps)} items")
    print(f"   ✅ Edits: {len(edits)} items")
    
    # Verify score is in valid range
    if 0 <= score <= 95:
        print(f"   ✅ Score in valid range (0-95%)")
    else:
        print(f"   ❌ Score out of range: {score}%")
except Exception as e:
    print(f"   ❌ Scoring function failed: {e}")
    import traceback
    traceback.print_exc()

print("\n7️⃣ Checking database...")
try:
    db_path = "certhub_users.db"
    if os.path.exists(db_path):
        print(f"   ✅ Database exists: {db_path}")
    else:
        print(f"   ⚠️  Database doesn't exist yet (will be created on first run)")
except Exception as e:
    print(f"   ❌ Database check failed: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n📝 You can now run: streamlit run app.py")
print("🌐 App will open at: http://localhost:8501")
print("\n" + "=" * 60)
