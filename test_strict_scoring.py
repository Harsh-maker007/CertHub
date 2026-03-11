#!/usr/bin/env python3
"""Test stricter ATS scoring with examples."""

from app import general_resume_score, ats_match, recommend_services, extract_keywords

print("=" * 70)
print("STRICT ATS SCORING EXAMPLES")
print("=" * 70)

# Test 1: Simple Resume (should score LOW)
simple_resume = """
Name & Contact
John Doe | john@example.com

Skills
Python, JavaScript

Experience
Software Engineer at TechCorp
"""

score1, str1, gaps1, edits1 = general_resume_score(simple_resume)
print(f"\n❌ Test 1: Simple Resume")
print(f"   Score: {score1}%")
print(f"   Strengths: {len(str1)} found")
print(f"   Gaps: {gaps1[0]}")
print(f"   Expected: Should be LOW (< 40%)")

# Test 2: Complete Resume with Rich Content
complete_resume = """
Name & Contact
John Doe | (555) 123-4567 | john@example.com | linkedin.com/in/johndoe | github.com/johndoe

Professional Summary
Experienced software engineer with 5+ years building scalable web applications using Python, JavaScript, and AWS. Proven track record of delivering high-impact solutions that improved performance by 40% and reduced costs by $200K annually. Strong leadership and mentoring skills demonstrated through leading teams of 5+ engineers.

Skills
Python, JavaScript, React, Node.js, SQL, PostgreSQL, MongoDB, AWS (EC2, S3, Lambda), Docker, Kubernetes, Git, REST APIs, GraphQL, Redis, Elasticsearch, Apache Kafka, Jenkins, Agile/Scrum, Problem Solving, Leadership, Communication, Mentoring

Experience
- Led team of 5 engineers to architect microservices platform handling 1M+ daily transactions with 99.99% uptime, reducing latency by 60%.
- Developed REST API serving 10K concurrent users, improved query response time by 45% through database optimization and caching.
- Automated CI/CD pipeline using Jenkins, reducing deployment time from 2 hours to 10 minutes, enabling 50+ deployments weekly.
- Mentored 3 junior engineers, with 2 promoted within 18 months; conducted 30+ code reviews monthly maintaining quality standards.
- Implemented real-time monitoring dashboard using ELK stack, reducing incident detection time from 30 min to 2 min.

Projects
- Built e-commerce platform: React frontend, Node.js backend, MongoDB, handling 50K daily users with 98% uptime. Implemented personalization engine improving conversion by 35%.
- Created ML-powered recommendation system achieving 92% accuracy, processing 5M+ events daily, deployed on AWS Lambda.
- Developed data pipeline processing 100GB+ daily logs using Kafka and Apache Spark, enabling real-time analytics.

Education
- B.S. Computer Science, State University, 2018
- AWS Solutions Architect Associate Certification, 2023

Certifications
- AWS Certified Solutions Architect - Professional
- Certified Kubernetes Administrator (CKA)
"""

score2, str2, gaps2, edits2 = general_resume_score(complete_resume)
print(f"\n✅ Test 2: Complete, Rich Resume")
print(f"   Score: {score2}%")
print(f"   Strengths: {len(str2)}")
for s in str2[:3]:
    print(f"     • {s}")
print(f"   Gaps: {len(gaps2)}")
print(f"   Expected: Should be HIGH (> 85%)")

# Test 3: Medium Resume
medium_resume = """
Name & Contact
Jane Smith | jane@email.com | (555) 987-6543

Professional Summary
Software developer with 3 years experience in web development. Experienced with Python and JavaScript.

Skills
Python, JavaScript, HTML, CSS, SQL, Git

Experience
- Developed web application using React
- Fixed bugs in production code
- Worked on team projects with other developers

Projects
- Personal portfolio website using HTML, CSS, JavaScript
- Todo app in React

Education
- B.S. Computer Science, University, 2021
"""

score3, str3, gaps3, edits3 = general_resume_score(medium_resume)
print(f"\n⚠️  Test 3: Medium Resume (needs work)")
print(f"   Score: {score3}%")
print(f"   Gaps: {gaps3[0]}")
print(f"   Expected: Should be MEDIUM (50-65%)")

# Test 4: Targeted JD Matching - High Match
print(f"\n" + "=" * 70)
print("TARGETED ATS MATCH SCORING")
print("=" * 70)

jd_keywords = extract_keywords("""
We are looking for a Senior Software Engineer with:
- Required: Python, AWS, microservices architecture, leadership
- Preferred: Kubernetes, CI/CD pipelines, mentoring
- Important: System design, scalability, performance optimization
""")

resume_high_match = """
I am a Senior Software Engineer with 5+ years building microservices on AWS.
I have led teams, mentored junior developers, and architected Kubernetes deployments.
My CI/CD expertise and system design skills have been crucial in scaling platforms to handle millions of requests.
"""

score_jd_high, matched_high, missing_high = ats_match(resume_high_match, jd_keywords)
print(f"\n✅ High Match Resume vs JD")
print(f"   Match Score: {score_jd_high}%")
print(f"   Matched ({len(matched_high)}): {', '.join(matched_high[:5])}")
print(f"   Missing ({len(missing_high)}): {missing_high}")
print(f"   Expected: Should be HIGH (> 75%)")

# Test 5: Targeted JD Matching - Low Match
resume_low_match = """
I know Python and some JavaScript.
I did internship at a tech company.
I am interested in backend work.
"""

score_jd_low, matched_low, missing_low = ats_match(resume_low_match, jd_keywords)
print(f"\n❌ Low Match Resume vs JD")
print(f"   Match Score: {score_jd_low}%")
print(f"   Matched ({len(matched_low)}): {matched_low}")
print(f"   Missing ({len(missing_low)}): {missing_low[:4]}")
print(f"   Expected: Should be LOW (< 40%)")

# Test 6: Service Recommendations
print(f"\n" + "=" * 70)
print("SERVICE RECOMMENDATIONS")
print("=" * 70)

print(f"\nLow Score Resume (30%): Recommendations:")
recs_low = recommend_services(30, ["python", "aws", "leadership"], simple_resume)
for svc, reason in recs_low[:2]:
    print(f"  • {svc}: {reason[:60]}...")

print(f"\nHigh Score Resume (90%): Recommendations:")
recs_high = recommend_services(90, [], complete_resume)
for svc, reason in recs_high[:2]:
    print(f"  • {svc}: {reason[:60]}...")

print(f"\n" + "=" * 70)
print("SCORING SUMMARY")
print("=" * 70)
print(f"""
Scoring Thresholds:
  🔴 < 40%  : Critical - Needs comprehensive overhaul
  🟠 40-60%  : Poor - Multiple significant gaps
  🟡 60-75%  : Fair - Good structure, needs depth
  🟢 75-85%  : Good - Strong candidate
  🟢 85%+    : Excellent - ATS-optimized resume

Key Strictness Features:
  ✓ Requires 15+ action verbs for full points (was 8)
  ✓ Requires 12+ metrics/numbers (was 6)
  ✓ Requires 10+ tech + soft skills (was 5)
  ✓ Requires 3+ bullets per experience section
  ✓ Requires complete contact (email + phone + links)
  ✓ Penalizes missing essential keywords (-20 points)
  ✓ Penalizes missing preferred keywords (-10 points)
""")

print("=" * 70)
