# Job Posting Analyzer & Resume Matcher

An AI-powered multi-agent system that analyzes job postings, extracts requirements, and provides intelligent resume matching recommendations using LangChain and Cerebras AI.

## Overview

This project implements a three-agent workflow that coordinates reasoning and actions to help job seekers understand how well their resume matches a specific job posting and provides actionable recommendations for customization.

## Architecture

### Agent Structure

The system consists of three specialized agents that work in sequence:

```
┌─────────────────┐
│  Job Parser     │  Reads job posting and structures data
│     Agent       │  (title, company, location, description)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Requirement    │  Analyzes structured job data
│   Analyzer      │  Extracts: skills, experience, education
│     Agent       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Resume        │  Matches resume against requirements
│   Matcher       │  Outputs: score, gaps, recommendations
│     Agent       │
└─────────────────┘
```

### Agent Responsibilities

1. **JobParserAgent** (`jobparser.py`)
   - Reads raw job posting text from file
   - Uses LLM to extract structured information (title, company, location, description)
   - Returns validated Pydantic model

2. **RequirementAnalyzerAgent** (`requirementanalyzer.py`)
   - Takes structured job data as input
   - Categorizes requirements into:
     - Technical skills (languages, frameworks, tools)
     - Soft skills (communication, leadership, etc.)
     - Experience requirements (years)
     - Education requirements
     - Nice-to-have qualifications
   - Uses LLM reasoning to extract implicit requirements

3. **ResumeMatcherAgent** (`resumematcher.py`)
   - Reads resume text
   - Compares resume content against extracted requirements
   - Generates:
     - Overall match score (0-100)
     - List of matched skills
     - List of missing skills
     - Specific recommendations for tailoring resume
     - Key strengths to emphasize

### Data Flow

```
Input Files → JobParser → Structured Job Data → RequirementAnalyzer → Requirements → ResumeMatcher + Resume → Match Results → Output (JSON/MD)
```

### Orchestration Pattern

The `JobMatcherOrchestrator` class in `main.py` coordinates the workflow:
- Sequential agent execution with clear data dependencies
- Logging and trace collection for transparency
- Error handling and validation between stages
- Multiple output formats (JSON for programmatic use, Markdown for human reading)

## Technology Stack

- **Framework**: LangChain for agent orchestration
- **LLM**: Cerebras AI (gpt-oss-120b) via OpenAI-compatible API
- **Data Validation**: Pydantic for structured outputs
- **PDF Processing**: pypdf for PDF resume support
- **Testing**: Python unittest with mocking


### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your CEREBRAS_API_KEY
   ```

### Project Structure

```
job-matcher/
├── aiagent/
│   ├── __init__.py
│   ├── jobparser.py           # Agent 1: Parse job postings
│   ├── requirementanalyzer.py # Agent 2: Extract requirements
│   └── resumematcher.py       # Agent 3: Match resume
├── docs/
│   ├── jobposting.txt         # Sample job posting
│   └── resume.txt              # Sample resume
├── tests/
│   ├── __init__.py
│   └── test.py          # Unit tests
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Logging utility
│   └── pdfreader.py           # PDF text extraction utility
├── output/                     # Generated results (created on run)
├── logs/                       # Workflow logs (created on run)
├── main.py                     # Main orchestration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## Usage

### Basic Usage

Run the workflow with sample data:

```bash
python main.py
```

This will:
1. Parse the job posting from `docs/jobposting.txt`
2. Extract and analyze requirements
3. Match against resume in `docs/resume.pdf`
4. Generate results in `output/` directory

### Using Your Own Data

1. **Replace job posting**
   - Edit `docs/jobposting.txt` with your target job posting
   - Or modify `main.py` to point to a different file

2. **Replace resume** (supports .txt and .pdf!)
   - **Option A (PDF)**: Copy your PDF resume to `docs/resume.pdf` and update `main.py`:
     ```python
     resume_path = "docs/resume.pdf"
     ```
   - **Option B (Text)**: Edit `docs/resume.txt` with your resume content

3. **Run the workflow**
   ```bash
   python main.py
   ```

### Output Files

After running, you'll find:
- `output/match_results.json` - Complete structured results
- `output/match_results.md` - Human-readable summary
- `logs/workflow.log` - Detailed execution traces

### Sample Output

```
============================================================
MATCH SUMMARY
============================================================
Job: Software Engineer - Full Stack at TechCorp Innovation Labs
Overall Match Score: 85/100
Matched Skills: 8
Missing Skills: 2

Full results saved to: output/match_results.json
Readable summary: output/match_results.md
============================================================
```

## Testing

The project includes comprehensive unit tests covering:
- Individual agent functionality
- Pydantic model validation
- Complete workflow integration
- Mock-based testing for LLM calls

### Run Tests

```bash
python -m unittest tests.test -v
```

### Test Coverage

- `TestJobParserAgent`: Tests job posting parsing and structuring
- `TestRequirementAnalyzerAgent`: Tests requirement extraction
- `TestResumeMatcherAgent`: Tests resume matching logic
- `TestWorkflowIntegration`: Tests end-to-end workflow

## Logging and Transparency

The system provides detailed logging at multiple levels:

1. **Console Output**: Real-time progress updates
2. **File Logging**: Detailed logs saved to `logs/workflow.log`
3. **Workflow Traces**: JSON-formatted trace of agent actions in output

Example trace entry:
```json
{
  "timestamp": "2024-11-24T10:30:45.123456",
  "agent": "JobParser",
  "action": "Completed parsing",
  "data": {
    "title": "Software Engineer",
    "company": "TechCorp"
  }
}
```
