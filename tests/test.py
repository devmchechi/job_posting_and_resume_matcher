"""
Unit tests for agent workflow
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

# Set a fake API key for tests
os.environ['CEREBRAS_API_KEY'] = 'test-key-12345'

from aiagent.jobparser import JobPosting
from aiagent.requirementanalyzer import JobRequirements
from aiagent.resumematcher import MatchAnalysis
from utils.pdfreader import read_file


class TestPDFReader(unittest.TestCase):
    """Test PDF reading functionality"""
    
    @patch('utils.pdfreader.pypdf.PdfReader')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake pdf data")
    def test_read_pdf(self, mock_file, mock_exists, mock_pdf_reader):
        """Test reading PDF file"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Resume content from PDF"
        
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        from utils.pdfreader import read_pdf
        result = read_pdf("fake_resume.pdf")
        
        self.assertIn("Resume content", result)
    
    @patch('builtins.open', new_callable=mock_open, read_data="Text file content")
    def test_read_text_file(self, mock_file):
        """Test reading text file"""
        with patch('pathlib.Path.exists', return_value=True):
            result = read_file("fake_resume.txt")
            self.assertEqual(result, "Text file content")
    
    def test_unsupported_file_type(self):
        """Test error on unsupported file type"""
        with patch('pathlib.Path.exists', return_value=True):
            with self.assertRaises(ValueError) as context:
                read_file("resume.docx")
            self.assertIn("Unsupported file type", str(context.exception))


class TestPydanticModels(unittest.TestCase):
    """Test Pydantic model validation"""
    
    def test_job_posting_model(self):
        """Test JobPosting Pydantic model validation"""
        job = JobPosting(
            title="Senior Developer",
            company="StartupCo",
            location="Remote",
            description="Exciting role",
            raw_text="Full text here"
        )
        
        self.assertEqual(job.title, "Senior Developer")
        self.assertEqual(job.company, "StartupCo")
        
        # Test dict conversion
        job_dict = job.dict()
        self.assertIn("title", job_dict)
        self.assertEqual(job_dict["title"], "Senior Developer")
    
    def test_requirements_model(self):
        """Test JobRequirements model structure"""
        reqs = JobRequirements(
            technical_skills=["Java", "Spring"],
            soft_skills=["Leadership"],
            experience_years=5,
            education="MS in CS",
            nice_to_have=["GraphQL"]
        )
        
        self.assertEqual(len(reqs.technical_skills), 2)
        self.assertEqual(reqs.experience_years, 5)
        
        # Test dict conversion
        reqs_dict = reqs.dict()
        self.assertIn("technical_skills", reqs_dict)
        self.assertEqual(reqs_dict["experience_years"], 5)
    
    def test_match_analysis_model(self):
        """Test MatchAnalysis model validation"""
        analysis = MatchAnalysis(
            overall_score=75,
            matched_skills=["Python", "JavaScript"],
            missing_skills=["Go"],
            recommendations=["Add Go projects"],
            strengths=["Full-stack experience"]
        )
        
        self.assertEqual(analysis.overall_score, 75)
        self.assertEqual(len(analysis.matched_skills), 2)
        
        # Test dict conversion
        analysis_dict = analysis.dict()
        self.assertIn("overall_score", analysis_dict)
        self.assertEqual(analysis_dict["overall_score"], 75)
    
    def test_job_posting_validation(self):
        """Test that JobPosting validates required fields"""
        # All fields are required, missing raw_text should raise error
        with self.assertRaises(Exception):
            JobPosting(
                title="Test",
                company="TestCo",
                location="Remote"
                # Missing description and raw_text
            )
    
    def test_match_analysis_score_bounds(self):
        """Test match analysis score validation"""
        # Valid score
        analysis = MatchAnalysis(
            overall_score=85,
            matched_skills=["React"],
            missing_skills=[],
            recommendations=["Keep it up"],
            strengths=["Strong"]
        )
        self.assertEqual(analysis.overall_score, 85)


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""
    
    @patch('main.JobParserAgent')
    @patch('main.RequirementAnalyzerAgent')
    @patch('main.ResumeMatcherAgent')
    def test_complete_workflow(self, mock_matcher, mock_analyzer, mock_parser):
        """Test end-to-end workflow execution"""
        # Setup mocks
        mock_parser.return_value.parse.return_value = {
            "title": "Product Engineer",
            "company": "Levo",
            "location": "Boston, MA",
            "description": "Great role at healthcare startup",
            "raw_text": "Full text"
        }
        
        mock_analyzer.return_value.analyze.return_value = {
            "technical_skills": ["React", "TypeScript", "Go", "Python"],
            "soft_skills": ["Communication", "Customer-facing"],
            "experience_years": 0,
            "education": "Bachelor's in CS",
            "nice_to_have": ["AWS", "Docker"]
        }
        
        mock_matcher.return_value.match.return_value = {
            "overall_score": 85,
            "matched_skills": ["React", "TypeScript", "Python", "AWS"],
            "missing_skills": ["Go"],
            "recommendations": [
                "Add Go projects to your portfolio",
                "Emphasize your customer-facing TA experience"
            ],
            "strengths": [
                "Strong React and TypeScript experience from VaultDB.ai",
                "Leadership experience as Head TA"
            ]
        }
        
        # Import here to use mocked agents
        from main import JobMatcherOrchestrator
        
        orchestrator = JobMatcherOrchestrator()
        results = orchestrator.run_workflow("fake_job.txt", "fake_resume.txt")
        
        # Test results structure
        self.assertIn("job_posting", results)
        self.assertIn("requirements", results)
        self.assertIn("match_analysis", results)
        self.assertIn("workflow_traces", results)
        self.assertIn("generated_at", results)
        
        # Test job posting data
        self.assertEqual(results["job_posting"]["company"], "Levo")
        self.assertEqual(results["job_posting"]["title"], "Product Engineer")
        
        # Test requirements data
        self.assertIn("React", results["requirements"]["technical_skills"])
        self.assertEqual(results["requirements"]["experience_years"], 0)
        
        # Test match analysis
        self.assertEqual(results["match_analysis"]["overall_score"], 85)
        self.assertGreater(len(results["match_analysis"]["matched_skills"]), 0)
        self.assertGreater(len(results["match_analysis"]["recommendations"]), 0)
        
        # Test workflow traces
        self.assertGreater(len(results["workflow_traces"]), 0)
        
        # Verify all agents were called
        mock_parser.return_value.parse.assert_called_once()
        mock_analyzer.return_value.analyze.assert_called_once()
        mock_matcher.return_value.match.assert_called_once()


if __name__ == "__main__":
    unittest.main()