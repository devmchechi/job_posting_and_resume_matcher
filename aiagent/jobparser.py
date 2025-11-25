"""
Job Parser Agent
Reads and structures job posting data
"""

import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Structured job posting data"""
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str = Field(description="Job location")
    description: str = Field(description="Job description")
    raw_text: str = Field(description="Original job posting text")


class JobParserAgent:
    """Agent responsible for parsing job postings"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-oss-120b",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            temperature=0
        )
        self.parser = PydanticOutputParser(pydantic_object=JobPosting)
        
        self.prompt = PromptTemplate(
            template="""You are a job posting parser. Extract structured information from the job posting.

Job Posting:
{job_text}

{format_instructions}

Extract the title, company, location, and description accurately.""",
            input_variables=["job_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    def parse(self, job_posting_path: str) -> Dict:
        """Parse job posting from file"""
        # Read job posting
        with open(job_posting_path, 'r') as f:
            job_text = f.read()
        
        # Create chain
        chain = self.prompt | self.llm | self.parser
        
        # Execute
        result = chain.invoke({"job_text": job_text})
        
        return result.dict()