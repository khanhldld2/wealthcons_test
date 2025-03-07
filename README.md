# Resume Parser & Candidate Evaluation System

A web application that parses resumes, extracts candidate information, scores candidates based on their qualifications, and generates personalized interview questions.

## Features

- **Multiple File Format Support**: Process resumes in PDF, DOCX, TXT, and image formats
- **Intelligent Extraction**: Extract candidate information including:
  - Personal details (name, email, phone, address)
  - Education background
  - Work experience
  - Skills
  - Certifications
- **HTML Structure Recognition**: Special handling for structured HTML-based PDFs
- **Candidate Scoring**: Automatic evaluation based on experience, skills, and qualifications
- **Interview Questions**: AI-generated personalized interview questions based on candidate profile
- **Database Storage**: Store parsed resume data and analysis for future reference

## Technology Stack

- **Programming Language**: Python 3.9
- **Backend Framework**: Flask
- **Database**: PostgreSQL with SQLAlchemy
- **Text Processing**: 
  - PDF processing with pdfplumber and PyMuPDF
  - DOCX processing with docx2txt
  - OCR capabilities with pytesseract
- **AI Components**: Transformer models for text generation and interview question creation

## Installation

1. Clone the repository
2. Load a virtual environment and activate it in bash: venv\Scripts\activate
3. Run project: python -m app