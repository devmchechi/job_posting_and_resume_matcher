"""
Resume Matcher Agent
Matches resume against job requirements and provides recommendations
"""

import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class MatchAnalysis(BaseModel):
    """Match analysis results"""
    overall_score: int = Field(description="Overall match score out of 100")
    matched_skills: List[str] = Field(description="Skills from resume matching requirements")
    missing_skills: List[str] = Field(description="Required skills not found in resume")
    recommendations: List[str] = Field(description="Specific recommendations for tailoring resume")
    strengths: List[str] = Field(description="Key strengths to emphasize")


class ResumeMatcherAgent:
    """Agent responsible for matching resume to job requirements"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-oss-120b",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            temperature=0.3
        )
        self.parser = PydanticOutputParser(pydantic_object=MatchAnalysis)
        
        self.prompt = PromptTemplate(
            template="""You are an expert resume consultant. Analyze how well the resume matches the job requirements and provide actionable recommendations.

RESUME:
{resume_text}

JOB REQUIREMENTS:
Technical Skills: {technical_skills}
Soft Skills: {soft_skills}
Experience: {experience_years} years
Education: {education}
Nice-to-have: {nice_to_have}

{format_instructions}

Provide:
1. An honest overall match score (0-100)
2. Which required skills are present in the resume
3. Which required skills are missing
4. Specific, actionable recommendations for tailoring this resume
5. Key strengths from the resume relevant to this role

Be specific and helpful.""",
            input_variables=["resume_text", "technical_skills", "soft_skills", 
                           "experience_years", "education", "nice_to_have"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    def match(self, requirements: Dict, resume_path: str) -> Dict:
        """Match resume against requirements (supports .txt and .pdf)"""
        # Import here to avoid circular dependency
        from utils.pdfreader import read_file
        
        # Read resume (automatically detects .txt or .pdf)
        resume_text = read_file(resume_path)
        
        # Create chain
        chain = self.prompt | self.llm | self.parser
        
        # Execute
        result = chain.invoke({
            "resume_text": resume_text,
            "technical_skills": ", ".join(requirements["technical_skills"]),
            "soft_skills": ", ".join(requirements["soft_skills"]),
            "experience_years": requirements["experience_years"],
            "education": requirements["education"],
            "nice_to_have": ", ".join(requirements["nice_to_have"])
        })
        
        return result.dict()