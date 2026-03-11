#!/usr/bin/env python3
"""Test strict skill-based scoring."""

from app import general_resume_score

# SIMPLE RESUME (should score very low)
simple = """
Name: John Doe
Email: john@email.com
Phone: 555-1234

Summary
I am a developer with coding experience.

Skills
Python, JavaScript

Experience
Developer at Company
- Worked on projects
- Fixed bugs

Education
BS Computer Science

Certifications
None
"""

print("=" * 70)
print("TEST 1: SIMPLE RESUME (minimal skills, no target role)")
print("=" * 70)
score1, strengths1, gaps1, edits1 = general_resume_score(simple)
print(f"SCORE: {score1}%")
print(f"Expected: 5-10% (very strict)")
print(f"Strengths ({len(strengths1)}):")
for s in strengths1[:3]:
    print(f"  {s}")
print(f"Gaps ({len(gaps1)}):")
for g in gaps1[:4]:
    print(f"  {g}")
print()

# MEDIUM RESUME (decent but missing things)
medium = """
Target Job Role
Senior Software Developer

Name: Jane Smith
Email: jane@smith.com
Phone: (555) 987-6543
LinkedIn: linkedin.com/in/jane

Professional Summary
Software engineer with 3 years experience developing web applications. Skilled in Python, JavaScript, React, and databases. Strong problem-solving and team collaboration abilities. Seeking to grow in backend architecture and microservices.

Skills
Technical: Python, JavaScript, React, Node.js, SQL, MongoDB, Docker, Git, REST API, Agile, HTML, CSS
Soft: Communication, Problem Solving, Teamwork, Collaboration

Experience
Senior Developer at TechCo | Jan 2022 - Present
- Developed 5 new features using React and Node.js
- Improved database performance by 25%
- Led team of 3 junior developers
- Built REST API serving 10K users

Developer at StartupXYZ | Jun 2020 - Dec 2021
- Created 8 full-stack applications
- Increased code coverage to 80%
- Fixed 30 bugs in production

Projects
E-commerce Platform | 2022
- Built full-stack app with React and Node.js
- Processed 5K transactions monthly

Chat Application | 2021
- Developed real-time chat using Socket.io
- 100 concurrent users

Education
BS Computer Science, 2020
GPA: 3.5/4.0

Certifications
AWS Developer Associate, 2022
"""

print("=" * 70)
print("TEST 2: MEDIUM RESUME (decent structure, some skills, has target role)")
print("=" * 70)
score2, strengths2, gaps2, edits2 = general_resume_score(medium)
print(f"SCORE: {score2}%")
print(f"Expected: 25-35% (still needs major work)")
print(f"Strengths ({len(strengths2)}):")
for s in strengths2[:4]:
    print(f"  {s}")
print(f"Gaps ({len(gaps2)}):")
for g in gaps2[:5]:
    print(f"  {g}")
print()

# GOOD RESUME (strong, comprehensive)
good = """
Target Job Role
Full Stack Software Engineer

Name: Alex Johnson
Email: alex@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/alexjohnson
GitHub: github.com/alexjohnson

Professional Summary
Experienced Full Stack Engineer with 6+ years building scalable web applications and microservices. Proficient in Python, JavaScript, TypeScript, React, Node.js, AWS, Docker, Kubernetes, and PostgreSQL. Led teams of 5+ developers. Delivered 20+ production features impacting 100K+ users. Passionate about clean code, system design, and mentoring junior engineers. Proven track record of 40% performance improvements through optimization.

Skills
Languages: Python, JavaScript, TypeScript, Java, SQL, Bash, Go, Rust
Frontend: React, Vue.js, Angular, Next.js, Tailwind CSS, Webpack, Vite, Redux, GraphQL
Backend: Node.js, Express, FastAPI, Django, Spring Boot, NestJS, GraphQL, REST API
Databases: PostgreSQL, MongoDB, Redis, Elasticsearch, Firebase, DynamoDB
DevOps & Cloud: AWS (EC2, S3, Lambda, RDS), Azure, Docker, Kubernetes, Terraform, Jenkins, GitHub Actions
Tools & Platforms: Git, GitHub, GitLab, Jira, Figma, VS Code, Linux, Postman, Datadog, Prometheus
Soft Skills: Leadership, Team Management, Strategic Planning, Problem Solving, Communication, Mentoring, Stakeholder Management, Project Management

Experience
Lead Software Engineer at BigTech | Jun 2021 - Present
- Architected microservices platform using Kubernetes, reducing deployment time from 2 hours to 15 minutes (92% improvement)
- Led team of 6 engineers to deliver 15 major features, increasing user base from 50K to 150K
- Optimized database queries, improving API response time from 800ms to 120ms (85% reduction)
- Implemented automated CI/CD pipeline using GitHub Actions, reducing deployment errors by 95%
- Mentored 4 junior engineers, promoting 2 to mid-level senior roles
- Designed and built payment microservice processing $2M+ annually with 99.99% uptime
- Reduced cloud infrastructure costs by 35% through optimization and rightsizing

Senior Software Engineer at MidCorp | Jan 2019 - May 2021
- Developed 25 full-stack features using React, Node.js, and PostgreSQL
- Increased application performance by 45% through code optimization and caching
- Managed PostgreSQL database with 500M+ records and 1000+ QPS queries
- Implemented comprehensive testing suite with 85% code coverage using Jest and Mocha
- Deployed microservices to AWS using Docker and Kubernetes, serving 50K daily users
- Built real-time notification system using WebSockets, reducing latency by 60%

Software Engineer at StartupABC | Jul 2017 - Dec 2018
- Created 12 REST API endpoints serving mobile and web clients
- Built React dashboard displaying real-time analytics for 10K+ users
- Optimized SQL queries, reducing database load by 40%

Projects
Advanced E-Commerce Platform | Lead Developer | 2023
- Developed full-stack e-commerce platform using Next.js, Node.js, PostgreSQL
- Implemented real-time inventory system using Redis, achieving 99.9% uptime
- Processed 100K+ orders monthly, generating $5M+ in GMV
- Scaled to handle 10K concurrent users with sub-200ms response times
- Integrated Stripe payment processing, supporting 15+ payment methods
- Implemented ML-based recommendation engine, increasing conversion by 28%

Real-Time Data Pipeline | Developer | 2022
- Created Python data pipeline processing 100GB+ of data daily
- Built ETL system with Apache Kafka for streaming data ingestion
- Implemented automated testing, reducing data quality issues by 90%
- Deployed using Docker/Kubernetes on AWS, achieving 99.95% uptime

Machine Learning Model Deployment | Developer | 2021
- Built Python service to deploy TensorFlow models to production
- Served 1M+ predictions monthly with <50ms latency
- Implemented monitoring and alerting using Prometheus and Grafana
- A/B tested model improvements, increasing accuracy by 12%

Education
Bachelor of Science in Computer Science, State University | 2017
GPA: 3.9/4.0
Relevant Coursework: Data Structures, Algorithms, Database Systems, Computer Networks, Machine Learning

Certifications
AWS Certified Solutions Architect - Professional | 2023 (Valid until 2026)
Kubernetes Application Developer (CKAD) | 2022
AWS Certified Developer - Associate | 2021
Google Cloud Certified - Associate Cloud Engineer | 2021
"""

print("=" * 70)
print("TEST 3: STRONG RESUME (comprehensive, many skills, excellent structure)")
print("=" * 70)
score3, strengths3, gaps3, edits3 = general_resume_score(good)
print(f"SCORE: {score3}%")
print(f"Expected: 65-75% (good candidate)")
print(f"Strengths ({len(strengths3)}):")
for s in strengths3[:6]:
    print(f"  {s}")
print(f"Gaps ({len(gaps3)}):")
for g in gaps3[:4]:
    print(f"  {g}")
print()

# PERFECT RESUME (has everything)
perfect = """
Target Job Role
Distinguished Engineer - Full Stack Architecture

Name: Expert Developer
Email: expert@email.com
Phone: (555) 111-2222
LinkedIn: linkedin.com/in/expertdev
GitHub: github.com/expertdev
Portfolio: expertdev.com

Professional Summary
Distinguished Full Stack Engineer with 10+ years architecting and leading development of enterprise-scale systems. Expert in Python, JavaScript, TypeScript, Java, Go, Rust, React, Vue, Angular, Node.js, Express, FastAPI, Django, Spring Boot, NestJS, AWS, Azure, GCP, Docker, Kubernetes, PostgreSQL, MongoDB, Redis, Elasticsearch, Kafka, and advanced system design. Led teams of 15+ engineers delivering 100+ production features impacting 1M+ users globally. Consistently delivered 50%+ performance improvements. Passionate about mentoring, open-source contributions, technical speaking, and driving engineering excellence. Published 20+ technical articles and spoken at 30+ conferences.

Skills
Languages: Python, JavaScript, TypeScript, Java, C++, Go, Rust, C#, SQL, Bash, Scala, R
Frontend: React, Vue.js, Angular, Svelte, Next.js, Nuxt.js, Gatsby, Tailwind CSS, Material-UI, Bootstrap, Webpack, Vite, Parcel, Three.js, D3.js, Storybook
Backend: Node.js, Express, Fastapi, Flask, Django, Spring, Spring Boot, ASP.NET, NestJS, Rails, Laravel, Gin, Gorilla, Actix, GraphQL, gRPC, REST, WebSockets
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra, DynamoDB, Firestore, Oracle, Neo4j, Memcached, RabbitMQ, Kafka, Spark
Cloud & DevOps: AWS (15+ services), Azure (10+ services), GCP (8+ services), Docker, Kubernetes (CKAD certified), Terraform, Ansible, Jenkins, GitLab CI, GitHub Actions, ArgoCD
Data & ML: Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, Keras, XGBoost, LightGBM, Spark, Hadoop, Airflow, Jupyter, MLflow
Tools: Git, GitHub, GitLab, Jira, Confluence, Figma, Sketch, Postman, Swagger, DataDog, Prometheus, Grafana, ELK Stack, New Relic
Soft Skills: Leadership, Team Management, Strategic Planning, System Design, Architecture, Technical Mentoring, Public Speaking, Communication, Negotiation, Change Management, Stakeholder Engagement

Experience
Distinguished Engineer | BigGlobalTech | Jan 2022 - Present
- Architected microservices ecosystem serving 1M+ daily active users across 15 countries
- Designed and implemented event-driven architecture using Kafka, reducing latency by 70%
- Led platform engineering team of 12 engineers, improving deployment frequency by 300%
- Drove API versioning strategy, supporting 500+ integration partners with zero downtime
- Mentored 8 senior engineers, 5 promoted to staff/principal levels
- Reduced infrastructure costs by 50% through optimization and resource planning ($5M annually)
- Designed disaster recovery and multi-region failover system with 99.999% uptime
- Implemented advanced monitoring and observability stack processing 10B+ events/day
- Delivered keynote presentations at 5 major tech conferences on microservices and system design
- Published 15 technical blog posts reaching 500K+ engineering readers
- Open source contributor: Maintained popular project with 50K+ GitHub stars

VP of Engineering | MegaCorp | Jun 2019 - Dec 2021
- Scaled engineering org from 8 to 50+ engineers, establishing technical excellence culture
- Architected and led migration of monolithic system to microservices on Kubernetes (6 month project)
- Implemented comprehensive CI/CD pipeline reducing deployment time from 4 hours to 8 minutes
- Drove technical strategy resulting in 45% performance improvement and 60% cost reduction
- Established code review, testing, and documentation standards improving quality by 80%
- Built and mentored leadership team of 5 engineering managers
- Negotiated and integrated 3 acquisitions, consolidating engineering teams successfully

Senior Architect | TechInnovate | Feb 2017 - May 2019
- Architected distributed system processing 500M+ transactions daily on AWS
- Led team of 20 engineers building real-time analytics platform
- Designed and implemented sharding strategy handling 10B+ records
- Built data warehouse on Snowflake analyzing 1TB+ historical data
- Achieved 99.99% system uptime through chaos engineering and resilience practices
- Conducted technical interviews and hiring, building high-performing teams

Projects
Global Scale E-Commerce Platform | Lead Architect | 2023
- Architected and built e-commerce platform serving 10M+ users in 50 countries
- Implemented multi-region active-active deployment on AWS, Kubernetes, PostgreSQL sharding
- Processed 1M+ orders daily, generating $100M+ in GMV annually
- Built ML recommendation engine increasing conversion by 35%
- Implemented real-time fraud detection reducing chargebacks by 90%
- Achieved 99.95% uptime with <100ms median latency globally

Advanced Analytics Platform | Technical Lead | 2022
- Built real-time analytics platform processing 1B+ events daily using Kafka and Spark
- Implemented complex data pipelines with Apache Airflow for 500+ transformations
- Designed dimensional data warehouse supporting 10K+ concurrent queries
- Created self-service BI dashboards for 1000+ business users
- Reduced data processing latency from 2 hours to 5 minutes

Real-Time Collaboration System | Principal Architect | 2021
- Architected WebSocket-based collaboration platform supporting 100K+ concurrent users
- Implemented operational transformation algorithm for conflict-free document merging
- Built distributed state machine using Redis and event sourcing patterns
- Achieved sub-100ms latency for real-time updates across continents

Education
Master of Science in Computer Science, Top Tier University | 2015
GPA: 4.0/4.0, Honors: Summa Cum Laude
Relevant Coursework: Distributed Systems, Advanced Algorithms, Machine Learning, Computational Complexity, Cryptography, Advanced Database Systems

Bachelor of Science in Computer Science, Premier University | 2013
GPA: 3.95/4.0, Honors: Summa Cum Laude, Valedictorian

Certifications
AWS Certified Solutions Architect - Professional | 2024 (Active)
Kubernetes Application Developer (CKAD) | 2023 (Active)
AWS Certified DevOps Engineer - Professional | 2023 (Active)
Google Cloud Certified - Professional Cloud Architect | 2023 (Active)
Certified Kubernetes Administrator (CKA) | 2022 (Active)
AWS Certified Database - Specialty | 2022 (Active)

Awards & Recognition
Keynote Speaker, KubeCon North America | 2023
Innovation Award, Global Tech Summit | 2022
Engineering Excellence Award, TechInnovate | 2019
"""

print("=" * 70)
print("TEST 4: PERFECT RESUME (everything optimized, all skills)")
print("=" * 70)
score4, strengths4, gaps4, edits4 = general_resume_score(perfect)
print(f"SCORE: {score4}%")
print(f"Expected: 80-95% (excellent, near maximum)")
print(f"Strengths ({len(strengths4)}):")
for s in strengths4[:8]:
    print(f"  {s}")
print(f"Gaps ({len(gaps4)}):")
for g in gaps4[:3]:
    print(f"  {g}")
print()

print("=" * 70)
print("SUMMARY OF STRICTNESS")
print("=" * 70)
print(f"Simple:   {score1}% (Expected: 5-15%)")
print(f"Medium:   {score2}% (Expected: 25-35%)")
print(f"Good:     {score3}% (Expected: 65-75%)")
print(f"Perfect:  {score4}% (Expected: 80-95%, capped at 95%)")
print()
print("✓ Scoring is STRICT when:")
print("  - Missing skills (checks all 100+ skills now)")
print("  - Few action verbs (needs 30+)")
print("  - Few metrics (needs 22+)")
print("  - Multiplier penalizes gaps aggressively")
print("  - Minimum score is 15%")
print("  - Maximum score is 95%")
