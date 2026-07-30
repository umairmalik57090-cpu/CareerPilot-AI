from pathlib import Path

from resume_parser import parse_resume, read_resume_text


def test_parse_resume_extracts_common_sections(tmp_path: Path) -> None:
    sample_text = """
    Jane Doe
    jane@example.com
    +1 555 123 4567

    Skills
    Python, SQL, Streamlit

    Education
    B.S. Computer Science

    Experience
    Software Engineer at Acme Corp
    Built data pipelines.

    Projects
    CareerPilot AI

    Certifications
    AWS Cloud Practitioner
    """

    parsed = parse_resume(sample_text)

    assert parsed["name"] == "Jane Doe"
    assert parsed["email"] == "jane@example.com"
    assert parsed["phone"] == "+1 555 123 4567"
    assert "Python" in parsed["skills"]
    assert "B.S. Computer Science" in parsed["education"]
    assert parsed["experience"][0].startswith("Software Engineer")
    assert "CareerPilot AI" in parsed["projects"]
    assert "AWS Cloud Practitioner" in parsed["certifications"]


def test_read_resume_text_reads_plain_text(tmp_path: Path) -> None:
    file_path = tmp_path / "resume.txt"
    file_path.write_text("Hello world", encoding="utf-8")

    text = read_resume_text(file_path)

    assert text == "Hello world"
