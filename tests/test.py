"""
Unit tests for agent workflow
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock

from aiagent.jobparser import JobParserAgent, JobPosting
from aiagent.requirementanalyzer import RequirementAnalyzerAgent, JobRequirements
from aiagent.resumematcher import ResumeMatcherAgent, MatchAnalysis
from utils.pdfreader import read_file


class TestPDFReader(unittest.TestCase):
    """Test PDF reading functionality"""
    
    @patch('utils.pdf_reader.pypdf.PdfReader')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake pdf data")
    def test_read_pdf(self, mock_file, mock_pdf_reader):
        """Test reading PDF file"""
        # Mock PDF page
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Resume content from PDF"
        
        # Mock PDF reader
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        from utils.pdfreader import read_pdf
        result = read_pdf("fake_resume.pdf")
        
        self.assertIn("Resume content", result)
    
    @patch('builtins.open', new_callable=mock_open, read_data="Text file content")
    def test_read_text_file(self, mock_file):
        """Test reading text file"""
        # Create a Path object mock
        with patch('pathlib.Path.exists', return_value=True):
            result = read_file("fake_resume.txt")
            self.assertEqual(result, "Text file content")
    
    def test_unsupported_file_type(self):
        """Test error on unsupported file type"""
        with patch('pathlib.Path.exists', return_value=True):
            with self.assertRaises(ValueError) as context:
                read_file("resume.docx")
            self.assertIn("Unsupported file type", str(context.exception))


class TestJobParserAgent(unittest.TestCase):
    """Test JobParserAgent"""
    
    @patch('agents.job_parser.ChatOpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data="Software Engineer at TechCorp\nLocation: Boston\nGreat opportunity!")
    def test_parse_job_posting(self, mock_file, mock_llm):
        """Test parsing a job posting file"""
        # Mock LLM response
        mock_result = JobPosting(
            title="Software Engineer",
            company="TechCorp",
            location="Boston, MA",
            description="Great opportunity for a software engineer",
            raw_text="Software Engineer at TechCorp\nLocation: Boston\nGreat opportunity!"
        )
        mock_llm.return_value.invoke.return_value = mock_result
        
        agent = JobParserAgent()
        result = agent.parse("fake_path.txt")
        
        self.assertEqual(result["title"], "Software Engineer")
        self.assertEqual(result["company"], "TechCorp")
        self.assertIn("location", result)
    
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


class TestRequirementAnalyzerAgent(unittest.TestCase):
    """Test RequirementAnalyzerAgent"""
    
    @patch('agents.requirement_analyzer.ChatOpenAI')
    def test_analyze_requirements(self, mock_llm):
        """Test requirement extraction from job posting"""
        # Mock LLM response
        mock_result = JobRequirements(
            technical_skills=["Python", "React", "AWS"],
            soft_skills=["Communication", "Teamwork"],
            experience_years=3,
            education="Bachelor's in Computer Science",
            nice_to_have=["Docker", "Kubernetes"]
        )
        mock_llm.return_value.invoke.return_value = mock_result
        
        agent = RequirementAnalyzerAgent()
        job_posting = {
            "title": "Software Engineer",
            "company": "TechCorp",
            "description": "We need someone with Python and React experience"
        }
        
        result = agent.analyze(job_posting)
        
        self.assertIn("Python", result["technical_skills"])
        self.assertGreater(len(result["technical_skills"]), 0)
        self.assertIsInstance(result["experience_years"], int)
    
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


class TestResumeMatcherAgent(unittest.TestCase):
    """Test ResumeMatcherAgent"""
    
    @patch('agents.resume_matcher.ChatOpenAI')
    @patch('utils.pdf_reader.read_file', return_value="Experienced Python developer with 4 years...")
    def test_match_resume(self, mock_read_file, mock_llm):
        """Test resume matching against requirements (supports PDF)"""
        # Mock LLM response
        mock_result = MatchAnalysis(
            overall_score=85,
            matched_skills=["Python", "AWS"],
            missing_skills=["React"],
            recommendations=[
                "Add specific React projects to experience section",
                "Highlight AWS certifications more prominently"
            ],
            strengths=["Strong Python background", "4 years experience"]
        )
        mock_llm.return_value.invoke.return_value = mock_result
        
        agent = ResumeMatcherAgent()
        requirements = {
            "technical_skills": ["Python", "React", "AWS"],
            "soft_skills": ["Communication"],
            "experience_years": 3,
            "education": "Bachelor's",
            "nice_to_have": ["Docker"]
        }
        
        result = agent.match(requirements, "fake_resume.txt")
        
        self.assertGreater(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 100)
        self.assertIsInstance(result["matched_skills"], list)
        self.assertIsInstance(result["recommendations"], list)
    
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


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""
    
    @patch('main.JobParserAgent')
    @patch('main.RequirementAnalyzerAgent')
    @patch('main.ResumeMatcherAgent')
    def test_complete_workflow(self, mock_matcher, mock_analyzer, mock_parser):
        """Test end-to-end workflow execution"""
        # Setup mocks
        mock_parser.return_value.parse.return_value = {
            "title": "Software Engineer",
            "company": "TechCorp",
            "location": "Boston",
            "description": "Great role"
        }
        
        mock_analyzer.return_value.analyze.return_value = {
            "technical_skills": ["Python"],
            "soft_skills": ["Teamwork"],
            "experience_years": 2,
            "education": "Bachelor's",
            "nice_to_have": []
        }
        
        mock_matcher.return_value.match.return_value = {
            "overall_score": 80,
            "matched_skills": ["Python"],
            "missing_skills": [],
            "recommendations": ["Good match"],
            "strengths": ["Strong background"]
        }
        
        # Import here to use mocked agents
        from main import JobMatcherOrchestrator
        
        orchestrator = JobMatcherOrchestrator()
        results = orchestrator.run_workflow("fake_job.txt", "fake_resume.txt")
        
        self.assertIn("job_posting", results)
        self.assertIn("requirements", results)
        self.assertIn("match_analysis", results)
        self.assertIn("workflow_traces", results)
        self.assertGreater(len(results["workflow_traces"]), 0)


if __name__ == "__main__":
    unittest.main()