"""
Requirement Analyzer Agent
Extracts and categorizes job requirements
"""

import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    """Structured job requirements"""
    technical_skills: List[str] = Field(description="Required technical skills")
    soft_skills: List[str] = Field(description="Required soft skills")
    experience_years: int = Field(description="Years of experience required")
    education: str = Field(description="Education requirements")
    nice_to_have: List[str] = Field(description="Nice-to-have skills or qualifications")


class RequirementAnalyzerAgent:
    """Agent responsible for analyzing job requirements"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-oss-120b",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            temperature=0
        )
        self.parser = PydanticOutputParser(pydantic_object=JobRequirements)
        
        self.prompt = PromptTemplate(
            template="""You are an expert job requirements analyzer. Extract and categorize all requirements from the job description.

Job Title: {title}
Company: {company}
Description: {description}

{format_instructions}

Be thorough in extracting:
- Technical skills (programming languages, frameworks, tools)
- Soft skills (communication, leadership, etc.)
- Years of experience (estimate if not explicitly stated)
- Education requirements
- Nice-to-have qualifications""",
            input_variables=["title", "company", "description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    def analyze(self, job_posting: Dict) -> Dict:
        """Analyze requirements from parsed job posting"""
        chain = self.prompt | self.llm | self.parser
        
        result = chain.invoke({
            "title": job_posting["title"],
            "company": job_posting["company"],
            "description": job_posting["description"]
        })
        
        return result.dict()