import json
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
import streamlit as st

class AdvancedResumeParser:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="your openai key"
        )
        
        # Field mapping for better categorization
        self.field_keywords = {
            'data_science': ['machine learning', 'data science', 'python', 'r', 'statistics', 'analytics', 'tensorflow', 'pytorch', 'pandas', 'numpy'],
            'web_development': ['javascript', 'react', 'angular', 'vue', 'node.js', 'html', 'css', 'php', 'django', 'flask'],
            'mobile_development': ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'xamarin'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform', 'ansible'],
            'cybersecurity': ['security', 'penetration testing', 'ethical hacking', 'firewall', 'encryption'],
            'ui_ux_design': ['figma', 'sketch', 'adobe xd', 'user experience', 'user interface', 'wireframe'],
            'cloud_computing': ['aws', 'azure', 'gcp', 'cloud architecture', 'serverless'],
            'blockchain': ['blockchain', 'cryptocurrency', 'smart contracts', 'ethereum', 'solidity'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'nlp'],
            'game_development': ['unity', 'unreal engine', 'game design', 'c#', 'c++'],
            'quality_assurance': ['testing', 'automation testing', 'selenium', 'quality assurance', 'test cases'],
            'product_management': ['product management', 'agile', 'scrum', 'roadmap', 'stakeholder'],
            'digital_marketing': ['seo', 'sem', 'social media marketing', 'google analytics', 'content marketing'],
            'business_analysis': ['business analysis', 'requirements gathering', 'process improvement', 'stakeholder management'],
            'project_management': ['project management', 'pmp', 'agile', 'scrum master', 'waterfall']
        }
    
    def extract_comprehensive_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract comprehensive resume data using AI"""
        
        extraction_prompt = f"""
        Analyze the following resume text and extract detailed information in JSON format.
        
        Resume Text:
        {resume_text}
        
        Extract the following information and return as valid JSON:
        {{
            "name": "Full name of the person",
            "email": "Email address",
            "phone": "Phone number",
            "location": "Location/Address",
            "linkedin": "LinkedIn profile URL if mentioned",
            "github": "GitHub profile URL if mentioned",
            "summary": "Professional summary or objective",
            "experience": [
                {{
                    "company": "Company name",
                    "position": "Job title",
                    "duration": "Employment duration",
                    "description": "Job description",
                    "achievements": ["List of achievements and accomplishments"]
                }}
            ],
            "education": [
                {{
                    "institution": "Educational institution",
                    "degree": "Degree type",
                    "field": "Field of study",
                    "year": "Graduation year",
                    "gpa": "GPA if mentioned"
                }}
            ],
            "skills": {{
                "technical": ["List of technical skills"],
                "soft": ["List of soft skills"],
                "languages": ["Programming languages"],
                "frameworks": ["Frameworks and libraries"],
                "tools": ["Tools and software"]
            }},
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"],
                    "link": "Project link if available"
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification name",
                    "issuer": "Issuing organization",
                    "date": "Date obtained"
                }}
            ],
            "experience_level": "entry/junior/mid/senior/executive",
            "primary_field": "Most relevant career field",
            "years_of_experience": "Estimated years of experience as number"
        }}
        
        Be thorough and accurate. If information is not available, use null or empty arrays.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser. Extract structured information from resumes accurately and return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = completion.choices[0].message.content
            
            # Clean and parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                resume_data = json.loads(json_text)
                
                # Post-process and enhance data
                resume_data = self._enhance_extracted_data(resume_data, resume_text)
                return resume_data
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            st.error(f"Error in AI extraction: {str(e)}")
            return self._fallback_extraction(resume_text)
    
    def _enhance_extracted_data(self, data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """Enhance extracted data with additional analysis"""
        
        # Determine primary field based on skills and experience
        if not data.get('primary_field'):
            data['primary_field'] = self._determine_primary_field(data)
        
        # Estimate experience level if not determined
        if not data.get('experience_level'):
            data['experience_level'] = self._estimate_experience_level(data)
        
        # Calculate years of experience
        if not data.get('years_of_experience'):
            data['years_of_experience'] = self._calculate_years_of_experience(data)
        
        # Extract additional metrics
        data['resume_length'] = len(resume_text.split())
        data['sections_present'] = self._identify_sections(resume_text)
        data['contact_completeness'] = self._assess_contact_completeness(data)
        
        return data
    
    def _determine_primary_field(self, data: Dict[str, Any]) -> str:
        """Determine primary career field based on skills and experience"""
        
        all_text = ""
        
        # Combine skills
        skills = data.get('skills', {})
        for skill_category in skills.values():
            if isinstance(skill_category, list):
                all_text += " " + " ".join(skill_category)
        
        # Add experience descriptions
        for exp in data.get('experience', []):
            all_text += " " + exp.get('description', '') + " " + exp.get('position', '')
        
        all_text = all_text.lower()
        
        # Score each field
        field_scores = {}
        for field, keywords in self.field_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in all_text)
            field_scores[field] = score
        
        # Return field with highest score
        if field_scores:
            return max(field_scores, key=field_scores.get)
        
        return 'general'
    
    def _estimate_experience_level(self, data: Dict[str, Any]) -> str:
        """Estimate experience level based on various factors"""
        
        years = data.get('years_of_experience', 0)
        experience_count = len(data.get('experience', []))
        education_level = len(data.get('education', []))
        
        if years == 0 and experience_count == 0:
            return 'entry'
        elif years <= 2 or experience_count <= 1:
            return 'junior'
        elif years <= 5 or experience_count <= 3:
            return 'mid'
        elif years <= 10 or experience_count <= 5:
            return 'senior'
        else:
            return 'executive'
    
    def _calculate_years_of_experience(self, data: Dict[str, Any]) -> int:
        """Calculate total years of experience"""
        
        total_months = 0
        
        for exp in data.get('experience', []):
            duration = exp.get('duration', '')
            months = self._parse_duration(duration)
            total_months += months
        
        return max(0, total_months // 12)
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string and return months"""
        
        if not duration_str:
            return 0
        
        duration_str = duration_str.lower()
        months = 0
        
        # Look for year patterns
        year_match = re.search(r'(\d+)\s*year', duration_str)
        if year_match:
            months += int(year_match.group(1)) * 12
        
        # Look for month patterns
        month_match = re.search(r'(\d+)\s*month', duration_str)
        if month_match:
            months += int(month_match.group(1))
        
        # If no specific duration found, assume 12 months
        if months == 0:
            months = 12
        
        return months
    
    def _identify_sections(self, resume_text: str) -> List[str]:
        """Identify which sections are present in the resume"""
        
        sections = []
        text_lower = resume_text.lower()
        
        section_keywords = {
            'summary': ['summary', 'objective', 'profile'],
            'experience': ['experience', 'work history', 'employment'],
            'education': ['education', 'academic', 'degree'],
            'skills': ['skills', 'competencies', 'technical skills'],
            'projects': ['projects', 'portfolio'],
            'certifications': ['certifications', 'certificates', 'licenses'],
            'achievements': ['achievements', 'accomplishments', 'awards'],
            'interests': ['interests', 'hobbies'],
            'references': ['references', 'referees']
        }
        
        for section, keywords in section_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                sections.append(section)
        
        return sections
    
    def _assess_contact_completeness(self, data: Dict[str, Any]) -> float:
        """Assess completeness of contact information"""
        
        contact_fields = ['name', 'email', 'phone', 'location']
        present_fields = sum(1 for field in contact_fields if data.get(field))
        
        return (present_fields / len(contact_fields)) * 100
    
    def _fallback_extraction(self, resume_text: str) -> Dict[str, Any]:
        """Fallback extraction using basic regex patterns"""
        
        # Basic regex patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        
        email_match = re.search(email_pattern, resume_text)
        phone_match = re.search(phone_pattern, resume_text)
        
        return {
            'name': None,
            'email': email_match.group() if email_match else None,
            'phone': phone_match.group() if phone_match else None,
            'location': None,
            'linkedin': None,
            'github': None,
            'summary': None,
            'experience': [],
            'education': [],
            'skills': {'technical': [], 'soft': [], 'languages': [], 'frameworks': [], 'tools': []},
            'projects': [],
            'certifications': [],
            'experience_level': 'unknown',
            'primary_field': 'general',
            'years_of_experience': 0,
            'resume_length': len(resume_text.split()),
            'sections_present': [],
            'contact_completeness': 0
        }
