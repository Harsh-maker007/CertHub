#!/usr/bin/env python3
"""Quick test script for ATS improvements."""

import sys
sys.path.insert(0, '.')

from app import (
    get_keyword_synonyms,
    find_keyword_matches,
    score_section_quality,
    count_skill_variety,
    general_resume_score,
    ats_match,
    recommend_services,
    extract_keywords,
)

def test_helper_functions():
    """Test new helper functions."""
    print("Testing helper functions...")
    
    # Test keyword synonyms
    synonyms = get_keyword_synonyms()
    assert "machine learning" in synonyms
    assert "ml" in synonyms["machine learning"]
    print("✓ Keyword synonyms working")
    
    # Test keyword matching with synonyms
    text = "I have experience with ML and AI projects using tensorflow"
    matches = find_keyword_matches(text, ["machine learning", "deep learning"], use_synonyms=True)
    assert "machine learning" in matches
    print("✓ Fuzzy keyword matching with synonyms working")
    
    # Test section quality scoring
    summary = "Early-career engineer with 5 years experience in Python and cloud technologies."
    quality = score_section_quality(summary, "professional summary")
    assert quality["quality_score"] > 0
    assert quality["word_count"] > 10
    print("✓ Section quality scoring working")
    
    # Test skill variety counting
    skills = "Python, Java, JavaScript, SQL, AWS, Docker, React, Node.js, Communication, Leadership"
    variety = count_skill_variety(skills)
    assert variety["tech_count"] > 0
    assert variety["total_unique"] > 0
    print("✓ Skill variety counting working")

def test_general_score():
    """Test enhanced general resume scoring."""
    print("\nTesting general resume scoring...")
    
    sample_resume = """
Name & Contact
John Doe | (555) 123-4567 | john@example.com | linkedin.com/in/johndoe | github.com/johndoe

Professional Summary
Experienced software engineer with 3 years building scalable web applications using Python and JavaScript.

Skills
Python, JavaScript, React, Node.js, SQL, AWS, Docker, Git, Communication, Problem Solving

Experience
- Developed REST API handling 1M+ requests/day with 99.9% uptime.
- Led team of 3 engineers to deliver 5 features in Q3 2023.
- Optimized database queries reducing query time by 40%.

Projects
- Built e-commerce platform with React frontend and Node.js backend processing 10K daily transactions.
- Created ML model achieving 92% accuracy for user recommendation system.

Education
- B.S. Computer Science, State University, 2021

Certifications
- AWS Solutions Architect Associate
- Google Cloud Professional Data Engineer
"""
    
    score, strengths, gaps, edits = general_resume_score(sample_resume)
    print(f"  Score: {score}%")
    print(f"  Strengths ({len(strengths)}): {strengths[0]}")
    print(f"  Gaps ({len(gaps)}): {gaps[0] if gaps else 'None'}")
    print(f"  Edits ({len(edits)}): {edits[0]}")
    assert 0 <= score <= 100
    assert len(strengths) > 0
    print("✓ General resume scoring working correctly")

def test_ats_match():
    """Test enhanced ATS matching."""
    print("\nTesting ATS matching...")
    
    resume = "Experienced in ML, AI, and deep learning with Python and TensorFlow experience."
    jd_kw = {
        "essential": ["machine learning", "python", "tensorflow"],
        "preferred": ["deep learning", "pytorch"],
        "important": ["aws", "docker"],
    }
    
    score, matched, missing = ats_match(resume, jd_kw)
    print(f"  Match Score: {score}%")
    print(f"  Matched keywords: {matched}")
    print(f"  Missing keywords: {missing}")
    assert 0 <= score <= 100
    assert "machine learning" in matched
    print("✓ ATS matching with semantic recognition working")

def test_recommendations():
    """Test service recommendations."""
    print("\nTesting service recommendations...")
    
    resume_low = "Basic resume with limited content"
    recs_low = recommend_services(45, ["python", "aws", "communication"], resume_low)
    print(f"  Low score recommendations: {len(recs_low)} services")
    assert any("Resume Making" in r[0] for r in recs_low)
    print("✓ Service recommendations working")

if __name__ == "__main__":
    try:
        test_helper_functions()
        test_general_score()
        test_ats_match()
        test_recommendations()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
