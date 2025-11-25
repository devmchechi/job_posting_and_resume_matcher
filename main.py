"""
Job Posting Analyzer & Resume Matcher
Main orchestration file for LLM agent workflow
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

from aiagent.jobparser import JobParserAgent
from aiagent.requirementanalyzer import RequirementAnalyzerAgent
from aiagent.resumematcher import ResumeMatcherAgent
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()


class JobMatcherOrchestrator:
    """Orchestrates the multi-agent workflow for job matching"""
    
    def __init__(self):
        self.parser = JobParserAgent()
        self.analyzer = RequirementAnalyzerAgent()
        self.matcher = ResumeMatcherAgent()
        self.traces = []
    
    def log_trace(self, agent: str, action: str, data: Any):
        """Log reasoning traces for transparency"""
        trace = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "data": data
        }
        self.traces.append(trace)
        logger.info(f"[{agent}] {action}")
    
    def run_workflow(self, job_posting_path: str, resume_path: str) -> Dict[str, Any]:
        """
        Execute the complete workflow:
        1. Parse job posting
        2. Analyze requirements
        3. Match with resume
        """
        logger.info("="*60)
        logger.info("Starting Job Matcher Workflow")
        logger.info("="*60)
        
        # Step 1: Parse job posting
        self.log_trace("JobParser", "Reading job posting", {"path": job_posting_path})
        parsed_job = self.parser.parse(job_posting_path)
        self.log_trace("JobParser", "Completed parsing", {
            "title": parsed_job.get("title"),
            "company": parsed_job.get("company")
        })
        
        # Step 2: Analyze requirements
        self.log_trace("RequirementAnalyzer", "Analyzing requirements", {})
        requirements = self.analyzer.analyze(parsed_job)
        self.log_trace("RequirementAnalyzer", "Extracted requirements", {
            "technical_skills_count": len(requirements.get("technical_skills", [])),
            "soft_skills_count": len(requirements.get("soft_skills", [])),
            "experience_years": requirements.get("experience_years")
        })
        
        # Step 3: Match with resume
        self.log_trace("ResumeMatcher", "Reading resume", {"path": resume_path})
        match_results = self.matcher.match(requirements, resume_path)
        self.log_trace("ResumeMatcher", "Completed matching", {
            "overall_score": match_results.get("overall_score"),
            "matched_skills": len(match_results.get("matched_skills", []))
        })
        
        # Compile final results
        results = {
            "job_posting": parsed_job,
            "requirements": requirements,
            "match_analysis": match_results,
            "workflow_traces": self.traces,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("="*60)
        logger.info("Workflow completed successfully")
        logger.info("="*60)
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save results to JSON and Markdown"""
        # Save JSON
        json_path = Path(output_path).with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {json_path}")
        
        # Save Markdown summary
        md_path = Path(output_path).with_suffix('.md')
        self._generate_markdown(results, md_path)
        logger.info(f"Summary saved to {md_path}")
    
    def _generate_markdown(self, results: Dict[str, Any], path: Path):
        """Generate a readable Markdown summary"""
        match = results["match_analysis"]
        job = results["job_posting"]
        reqs = results["requirements"]
        
        content = f"""# Job Match Analysis Report

**Generated:** {results["generated_at"]}

## Job Details
- **Title:** {job.get("title", "N/A")}
- **Company:** {job.get("company", "N/A")}
- **Location:** {job.get("location", "N/A")}

## Match Score: {match.get("overall_score", 0)}/100

### Matched Skills ({len(match.get("matched_skills", []))})
{self._format_list(match.get("matched_skills", []))}

### Missing Skills ({len(match.get("missing_skills", []))})
{self._format_list(match.get("missing_skills", []))}

### Recommended Resume Customizations
{self._format_list(match.get("recommendations", []))}

## Requirements Analysis
- **Experience Required:** {reqs.get("experience_years", "N/A")} years
- **Technical Skills:** {len(reqs.get("technical_skills", []))} identified
- **Soft Skills:** {len(reqs.get("soft_skills", []))} identified

## Workflow Execution Trace
{self._format_traces(results["workflow_traces"])}
"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _format_list(self, items):
        if not items:
            return "- None"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_traces(self, traces):
        output = []
        for trace in traces:
            output.append(f"**{trace['timestamp']}** - [{trace['agent']}] {trace['action']}")
        return "\n".join(output)


def main():
    """Main entry point"""
    job_posting_path = "docs/jobposting.txt"
    resume_path = "docs/resume.pdf" 
    output_path = "output/match_results"
    
    Path("output").mkdir(exist_ok=True)
    
    orchestrator = JobMatcherOrchestrator()
    results = orchestrator.run_workflow(job_posting_path, resume_path)
    
    orchestrator.save_results(results, output_path)
    
    # Print summary
    print("\n" + "="*60)
    print("MATCH SUMMARY")
    print("="*60)
    print(f"Job: {results['job_posting']['title']} at {results['job_posting']['company']}")
    print(f"Overall Match Score: {results['match_analysis']['overall_score']}/100")
    print(f"Matched Skills: {len(results['match_analysis']['matched_skills'])}")
    print(f"Missing Skills: {len(results['match_analysis']['missing_skills'])}")
    print(f"\nFull results saved to: output/match_results.json")
    print(f"Readable summary: output/match_results.md")
    print("="*60)


if __name__ == "__main__":
    main()