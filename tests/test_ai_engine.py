import unittest
from unittest.mock import MagicMock, patch

from ai_engine import (
    _ANALYSIS_CACHE,
    analyze_resume,
    analyze_resume_comprehensive,
    clear_analysis_cache,
    get_cache_key,
)
from groq_client import check_groq_connection


class TestAIEngine(unittest.TestCase):
    def setUp(self):
        clear_analysis_cache()

    def tearDown(self):
        clear_analysis_cache()

    def test_cache_key_generation(self):
        key1 = get_cache_key("Sample Resume Text", "Python Developer")
        key2 = get_cache_key("Sample Resume Text", "Python Developer")
        key3 = get_cache_key("Sample Resume Text", "AI Engineer")

        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)

    @patch("ai_engine.generate_chat_completion")
    def test_analyze_resume_comprehensive_single_call_and_caching(self, mock_generate):
        mock_generate.return_value = """
        {
          "resume_score": 88,
          "ats_score": 82,
          "executive_summary": "Solid candidate with strong backend Python experience.",
          "strengths": ["Python expertise", "Clean code focus"],
          "weaknesses": ["Needs more metrics"],
          "missing_skills": ["Docker", "Kubernetes"],
          "interview_questions": [
            "Explain Python GIL.",
            "How do you optimize SQL queries?",
            "Describe a complex system you built."
          ],
          "career_roadmap": {
            "thirty_day_plan": ["Learn Docker"],
            "sixty_day_plan": ["Build K8s demo"],
            "ninety_day_plan": ["Apply to senior roles"]
          },
          "improvement_suggestions": ["Quantify results with percentages"]
        }
        """

        resume_text = "John Doe Software Engineer Python SQL"
        parsed_resume = {"name": "John Doe", "skills": ["Python", "SQL"]}

        # First call - hits API (1 call)
        result1 = analyze_resume_comprehensive(resume_text, parsed_resume, target_role="Python Developer")
        self.assertEqual(mock_generate.call_count, 1)
        self.assertEqual(result1["resume_score"], 88)
        self.assertEqual(result1["ats_score"], 82)
        self.assertIn("Solid candidate", result1["executive_summary"])
        self.assertIn("Python expertise", result1["strengths"])
        self.assertIn("Docker", result1["missing_skills"])
        self.assertEqual(len(result1["interview_questions"]), 3)
        self.assertFalse(result1["from_cache"])

        # Second call - hits cache (0 API calls)
        result2 = analyze_resume_comprehensive(resume_text, parsed_resume, target_role="Python Developer")
        self.assertEqual(mock_generate.call_count, 1)
        self.assertTrue(result2["from_cache"])
        self.assertEqual(result2["resume_score"], 88)

    @patch("ai_engine.generate_chat_completion")
    def test_analyze_resume_error_fallback(self, mock_generate):
        mock_generate.side_effect = Exception("API connection error")

        resume_text = "Jane Smith Developer"
        parsed_resume = {"name": "Jane Smith", "skills": ["Python"]}

        result = analyze_resume(resume_text, parsed_resume)
        self.assertIn("Unable to generate AI response. Please try again.", result["error_message"])
        self.assertIn("resume_score", result)
        self.assertIn("ats_score", result)
        self.assertIn("executive_summary", result)


if __name__ == "__main__":
    unittest.main()
