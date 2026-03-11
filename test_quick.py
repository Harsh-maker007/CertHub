#!/usr/bin/env python3
"""Quick test to verify strict scoring works."""

from app import general_resume_score

# Simple resume - should score LOW now
simple_resume = """
John Doe
john@email.com

Summary
I am a software developer with experience in coding.

Skills
Python, JavaScript

Experience
Software Developer at Company
- Worked on projects
- Fixed bugs

Education
BS Computer Science
"""

score_simple = general_resume_score(simple_resume)
print(f"Simple resume score: {score_simple}")
print("(Should be LOW - around 10-25%)")

# Good resume - should score HIGH
good_resume = """
Target Job Role
Full Stack Software Engineer

John Doe
john@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

Professional Summary
Experienced Full Stack Engineer with 5+ years building scalable web applications. Proficient in Python, JavaScript, AWS, and Kubernetes. Delivered 15+ production features impacting 100K+ users. Passionate about optimizing system performance and mentoring junior developers.

Skills
Technical: Python, JavaScript, React, Node.js, AWS, Kubernetes, Docker, PostgreSQL, Redis, CI/CD, Linux
Leadership: Team Leadership, Code Review, Mentoring, Agile, Technical Documentation
Business: Product Strategy, Stakeholder Communication, Project Management

Experience
Senior Software Engineer at TechCorp | Jan 2021 - Present
- Architected microservices platform using Kubernetes, reducing deployment time by 60%
- Led team of 4 developers to deliver 12 major features, increasing user base to 150K
- Optimized database queries, improving response time by 40%
- Implemented CI/CD pipeline using GitHub Actions, reducing deployment errors by 80%
- Mentored 3 junior engineers, promoting 2 to mid-level roles

Software Engineer at WebCo | Jun 2018 - Dec 2020
- Built 20 full-stack features using React and Node.js
- Increased application performance by 35% through code optimization
- Managed PostgreSQL database with 5M+ records
- Developed 50+ unit tests, achieving 85% code coverage

Projects
E-commerce Platform | Lead Developer | 2022
- Developed full-stack e-commerce platform handling 10K concurrent users
- Implemented payment integration processing $500K+ annually
- Built real-time inventory system using Redis, reducing latency by 45%
- Scaled to handle 1M+ transactions monthly

Data Pipeline Application | Developer | 2021
- Created Python data pipeline processing 100GB+ daily
- Implemented automated testing reducing bugs by 70%
- Deployed using Docker/Kubernetes, achieving 99.9% uptime

Education
BS Computer Science - State University | 2018
GPA: 3.8/4.0

Certifications
AWS Certified Solutions Architect - Associate | 2022
Kubernetes Application Developer | 2021
"""

score_good = general_resume_score(good_resume)
print(f"\nGood resume score: {score_good}")
print("(Should be HIGH - around 80-95%)")

# Medium resume - should score MEDIUM
medium_resume = """
Target Job Role
Software Developer

Jane Smith
jane@email.com | (555) 987-6543

Professional Summary
Software developer with 3 years experience in web development. Skilled in JavaScript and Python. Looking to grow in cloud technologies.

Skills
Python, JavaScript, React, Node.js, SQL, Git, Docker
Leadership, Teamwork, Problem-solving

Experience
Developer at StartupXYZ | Mar 2021 - Present
- Developed 8 React components for dashboard
- Built 3 API endpoints using Node.js
- Fixed 15 bugs in production
- Improved page load time by 25%

Junior Developer at WebAgency | Jun 2020 - Feb 2021
- Created 5 web pages using HTML, CSS, JavaScript
- Fixed frontend bugs
- Helped with database design

Projects
Todo Application | 2022
- Built simple todo app with React
- Used Firebase for data storage
- 5K+ downloads

Education
Diploma in Web Development | TechCollege | 2020

Certifications
JavaScript Fundamentals | 2020
"""

score_medium = general_resume_score(medium_resume)
print(f"\nMedium resume score: {score_medium}")
print("(Should be MEDIUM - around 40-60%)")

print("\n" + "="*60)
print("SUMMARY:")
print(f"Simple:  {score_simple}% (Expected: 10-25%)")
print(f"Medium:  {score_medium}% (Expected: 40-60%)")
print(f"Good:    {score_good}% (Expected: 80-95%)")
print("\n✓ If scores follow expected ranges, multiplier strictness is working!")
