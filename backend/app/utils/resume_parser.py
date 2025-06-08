import os
import re
import PyPDF2
from docx import Document
from typing import Dict, List, Any
import spacy

class ResumeParser:
    def __init__(self):
        # Load spaCy model (you'll need to install: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common skills keywords (expand this list based on your needs)
        self.skills_keywords = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'typescript', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'sql', 'html',
                'css', 'xml', 'json', 'yaml'
            ],
            'frameworks_libraries': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                'spring', 'laravel', 'rails', 'tensorflow', 'pytorch', 'pandas',
                'numpy', 'matplotlib', 'scikit-learn', 'opencv', 'jquery', 'bootstrap',
                'tailwind', 'sass', 'less'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
                'sql server', 'cassandra', 'elasticsearch', 'dynamodb'
            ],
            'tools_technologies': [
                'git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp',
                'linux', 'unix', 'windows', 'bash', 'powershell', 'terraform',
                'ansible', 'nginx', 'apache', 'postman', 'jira', 'confluence'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd',
                'microservices', 'restful', 'graphql', 'soap', 'mvc', 'mvvm'
            ]
        }
        
        # Flatten skills for easier searching
        self.all_skills = []
        for category in self.skills_keywords.values():
            self.all_skills.extend(category)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""

    def extract_text_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file (basic implementation)"""
        # For .doc files, you might need python-docx2txt or other libraries
        # This is a placeholder - implement based on your needs
        try:
            # You can use python-docx2txt: pip install docx2txt
            import docx2txt
            return docx2txt.process(file_path)
        except ImportError:
            print("docx2txt not installed. Install with: pip install docx2txt")
            return ""
        except Exception as e:
            print(f"Error extracting DOC text: {e}")
            return ""

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type.lower() == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type.lower() == 'docx':
            return self.extract_text_from_docx(file_path)
        elif file_type.lower() == 'doc':
            return self.extract_text_from_doc(file_path)
        else:
            return ""

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates

    def extract_email(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    def extract_phone(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 10 digits
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience (basic implementation)"""
        experience = []
        
        # Look for common experience indicators
        experience_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\w+)',  # 2020-2023 or 2020-Present
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\w+)',  # Jan 2020 - Dec 2023
        ]
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for pattern in experience_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    # Try to find job title and company in surrounding lines
                    context_start = max(0, i-2)
                    context_end = min(len(lines), i+3)
                    context = ' '.join(lines[context_start:context_end])
                    
                    experience.append({
                        'period': matches[0],
                        'context': context[:200],  # Limit context length
                        'line': line.strip()
                    })
        
        return experience

    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university',
            'college', 'institute', 'school', 'certification', 'certificate',
            'diploma', 'b.s.', 'b.a.', 'm.s.', 'm.a.', 'mba', 'ph.d.'
        ]
        
        education = []
        lines = text.lower().split('\n')
        
        for line in lines:
            for keyword in education_keywords:
                if keyword in line:
                    education.append(line.strip())
                    break
        
        return list(set(education))  # Remove duplicates

    def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Main parsing function"""
        try:
            # Extract text
            text = self.extract_text(file_path, file_type)
            
            if not text:
                return {'error': 'Could not extract text from file'}
            
            # Extract various components
            skills = self.extract_skills(text)
            emails = self.extract_email(text)
            phones = self.extract_phone(text)
            experience = self.extract_experience(text)
            education = self.extract_education(text)
            
            # Use spaCy for named entity recognition if available
            entities = []
            if self.nlp:
                doc = self.nlp(text[:1000])  # Limit text length for processing
                entities = [
                    {'text': ent.text, 'label': ent.label_}
                    for ent in doc.ents
                    if ent.label_ in ['PERSON', 'ORG', 'GPE']  # Person, Organization, Location
                ]
            
            return {
                'text': text,
                'skills': skills,
                'emails': emails,
                'phones': phones,
                'experience': experience,
                'education': education,
                'entities': entities,
                'word_count': len(text.split()),
                'character_count': len(text)
            }
            
        except Exception as e:
            return {'error': f'Error parsing resume: {str(e)}'}

# Example usage and testing function
def test_parser():
    """Test function for the resume parser"""
    parser = ResumeParser()
    
    # Test with sample text
    sample_text = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    Experience:
    Senior Developer at TechCorp (2020-2023)
    - Developed web applications using Python, React, and PostgreSQL
    - Implemented CI/CD pipelines with Docker and Jenkins
    
    Education:
    Bachelor of Science in Computer Science
    University of Technology (2016-2020)
    
    Skills:
    Python, JavaScript, React, Node.js, PostgreSQL, Docker, AWS, Git
    """
    
    # Test skill extraction
    skills = parser.extract_skills(sample_text)
    print(f"Extracted skills: {skills}")
    
    # Test email extraction
    emails = parser.extract_email(sample_text)
    print(f"Extracted emails: {emails}")
    
    # Test phone extraction
    phones = parser.extract_phone(sample_text)
    print(f"Extracted phones: {phones}")

if __name__ == "__main__":
    test_parser()