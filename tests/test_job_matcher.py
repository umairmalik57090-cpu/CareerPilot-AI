from job_matcher import calculate_job_match


def test_calculate_job_match_returns_deterministic_values():
    resume = {
        "skills": ["Python", "SQL", "Machine Learning", "Git"],
        "experience": ["Worked as a software engineer for 2 years."]
    }
    job_description = """
    We are hiring a Python Developer with Python, SQL, Machine Learning, Git, Docker, AWS.
    2+ years of experience in software engineering.
    """

    result = calculate_job_match(resume, job_description, target_role="Python Developer")

    assert result["score"] >= 0
    assert result["score"] <= 100
    assert "Python" in result["matching_skills"]
    assert "Docker" in result["missing_skills"]
    assert result["experience_gap"]
    assert "score" in result


def test_calculate_job_match_filters_generic_words_and_matches_expected_skills():
    resume = {
        "skills": ["Python", "NumPy", "Pandas", "Scikit-learn", "Machine Learning", "Git/GitHub"],
        "experience": ["Built ML models and APIs using Python and Flask."]
    }
    job_description = """
    We are seeking an AI Engineer to build machine learning solutions.
    Required Skills: Python, NumPy, Pandas, Scikit-learn, Machine Learning, Deep Learning, SQL, Git/GitHub, REST APIs, NLP, Computer Vision, TensorFlow, PyTorch, Streamlit, Flask, Docker, AWS, Azure, GCP, Generative AI, LLMs.
    Responsibilities: Collaborate with team members, write code, design systems, deliver products.
    """

    result = calculate_job_match(resume, job_description, target_role="AI Engineer")

    assert "Python" in result["matching_skills"]
    assert "NumPy" in result["matching_skills"]
    assert "Pandas" in result["matching_skills"]
    assert "Scikit-learn" in result["matching_skills"]
    assert "Machine Learning" in result["matching_skills"]
    assert "Git/GitHub" in result["matching_skills"]
    assert "REST APIs" not in result["matching_skills"] or "REST APIs" in result["missing_skills"]
    assert "What" not in result["matching_skills"]
    assert "Are" not in result["matching_skills"]
    assert "They" not in result["matching_skills"]
    assert "Our" not in result["matching_skills"]
    assert "How" not in result["matching_skills"]
    assert "Key" not in result["matching_skills"]
    assert "Team" not in result["matching_skills"]
    assert "Professional" not in result["matching_skills"]
    assert "Development" not in result["matching_skills"]
    assert "Experience" not in result["matching_skills"]
    assert "Candidate" not in result["matching_skills"]
    assert "Responsibilities" not in result["matching_skills"]
