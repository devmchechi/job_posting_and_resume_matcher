"""
PDF Reader Utility
Extracts text from PDF files
"""

from pathlib import Path
from typing import Union
import pypdf


def read_pdf(file_path: Union[str, Path]) -> str:
    """
    Extract text content from a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content as a string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If PDF reading fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    try:
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(page_text)
        
        # Join all pages with double newline
        full_text = "\n\n".join(text_content)
        
        if not full_text.strip():
            raise ValueError(f"No text content extracted from PDF: {file_path}")
        
        return full_text
    
    except Exception as e:
        raise Exception(f"Error reading PDF {file_path}: {str(e)}")


def read_file(file_path: Union[str, Path]) -> str:
    """
    Read content from a file (supports .txt and .pdf)
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as a string
        
    Raises:
        ValueError: If file type is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    extension = file_path.suffix.lower()
    
    if extension == '.pdf':
        return read_pdf(file_path)
    elif extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {extension}. Supported types: .txt, .pdf")