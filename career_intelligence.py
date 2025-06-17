import json
from typing import Dict, List, Any
from openai import OpenAI
import streamlit as st

class CareerIntelligenceEngine:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=" your api key"
        )
    
    def analyze_resume(self, resume_data: Dict[str, Any], job_description: str = None) -> Dict[str, Any]:
        """Perform comprehensive AI analysis of resume"""
        
        analysis_prompt = f"""
        Perform a comprehensive analysis of this resume data and provide detailed insights.
        
        Resume Data: {json.dumps(resume_data, indent=2)}
        
        {f"Target Job Description: {job_description}" if job_description else ""}
        
        Provide analysis in the following JSON format:
        {{
            "overall_score": "Score out of 100 based on completeness, quality, and relevance",
            "ats_score": "ATS compatibility score out of 100",
            "strengths": ["List of candidate's key strengths"],
            "improvement_areas": [
                {{
                    "area": "Area needing improvement",
                    "priority": "high/medium/low",
                    "suggestion": "Specific suggestion for improvement"
                }}
            ],
            "missing_skills": ["Skills that should be added based on field/target role"],
            "content_quality": {{
                "writing_quality": "Score out of 100",
                "quantifiable_achievements": "Number of quantifiable achievements found",
                "action_verbs_usage": "Quality of action verbs used"
            }},
            "market_insights": {{
                "demand_score": "Market demand for this profile (0-100)",
                "salary_range": "Expected salary range",
                "competition_level": "Low/Medium/High",
                "growth_potential": "Career growth potential (0-100)"
            }},
            "recommendations": ["Specific actionable recommendations"],
            "career_trajectory": {{
                "current_level": "Assessment of current career level",
                "next_steps": ["Suggested next career moves"],
                "timeline": "Suggested timeline for career advancement"
            }}
        }}
        
        Be thorough, specific, and provide actionable insights.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor and resume analyst with 20+ years of experience. Provide detailed, actionable insights about resumes and career development."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            response_text = completion.choices[0].message.content
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                analysis_result = json.loads(json_text)
                return analysis_result
            else:
                raise ValueError("No valid JSON found in analysis response")
                
        except Exception as e:
            st.error(f"Error in AI analysis: {str(e)}")
            return self._fallback_analysis(resume_data)
    
    def generate_recommendations(self, resume_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        
        primary_field = resume_data.get('primary_field', 'general')
        experience_level = resume_data.get('experience_level', 'entry')
        
        recommendations = {
            'courses': self._get_field_courses(primary_field),
            'skill_development': self._generate_skill_recommendations(resume_data, analysis),
            'career_moves': self._suggest_career_moves(resume_data, analysis),
            'networking': self._suggest_networking_strategies(resume_data),
            'certifications': self._recommend_certifications(primary_field, experience_level)
        }
        
        return recommendations
    
    def _get_field_courses(self, field: str) -> List[List[str]]:
        """Get course recommendations based on field"""
        
        # Import course data
        from courses_data import ds_course, web_course, android_course, ios_course, uiux_course
        
        course_mapping = {
            'data_science': ds_course,
            'ai_ml': ds_course,
            'web_development': web_course,
            'mobile_development': android_course + ios_course,
            'ui_ux_design': uiux_course,
            'android_development': android_course,
            'ios_development': ios_course
        }
        
        return course_mapping.get(field, ds_course)[:10]  # Return top 10 courses
    
    def _generate_skill_recommendations(self, resume_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate skill development recommendations"""
        
        recommendations = []
        missing_skills = analysis.get('missing_skills', [])
        
        for skill in missing_skills[:5]:  # Top 5 missing skills
            recommendations.append(f"Learn {skill} to enhance your profile in {resume_data.get('primary_field', 'your field')}")
        
        # Add general recommendations
        experience_level = resume_data.get('experience_level', 'entry')
        
        if experience_level in ['entry', 'junior']:
            recommendations.extend([
                "Focus on building a strong portfolio with 3-5 projects",
                "Contribute to open-source projects to gain visibility",
                "Obtain relevant certifications in your field"
            ])
        elif experience_level in ['mid', 'senior']:
            recommendations.extend([
                "Develop leadership and mentoring skills",
                "Learn emerging technologies in your field",
                "Consider specializing in a niche area"
            ])
        
        return recommendations
    
    def _suggest_career_moves(self, resume_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Suggest career advancement moves"""
        
        moves = []
        current_level = resume_data.get('experience_level', 'entry')
        field = resume_data.get('primary_field', 'general')
        
        level_progression = {
            'entry': ['Junior Developer', 'Associate Analyst', 'Trainee'],
            'junior': ['Mid-level Developer', 'Senior Analyst', 'Team Lead'],
            'mid': ['Senior Developer', 'Principal Analyst', 'Engineering Manager'],
            'senior': ['Staff Engineer', 'Director', 'VP of Engineering'],
            'executive': ['CTO', 'Chief Data Officer', 'CEO']
        }
        
        next_levels = {
            'entry': 'junior',
            'junior': 'mid',
            'mid': 'senior',
            'senior': 'executive'
        }
        
        if current_level in next_levels:
            next_level = next_levels[current_level]
            possible_roles = level_progression.get(next_level, [])
            
            for role in possible_roles[:3]:
                moves.append(f"Target {role} positions in the next 1-2 years")
        
        # Add field-specific moves
        if field == 'data_science':
            moves.extend([
                "Consider specializing in MLOps or AI Engineering",
                "Explore opportunities in AI product management",
                "Look into data science consulting roles"
            ])
        elif field == 'web_development':
            moves.extend([
                "Transition to full-stack architecture roles",
                "Explore DevOps and cloud engineering",
                "Consider technical product management"
            ])
        
        return moves[:5]
    
    def _suggest_networking_strategies(self, resume_data: Dict[str, Any]) -> List[str]:
        """Suggest networking strategies"""
        
        field = resume_data.get('primary_field', 'general')
        
        strategies = [
            f"Join professional associations in {field.replace('_', ' ')}",
            "Attend industry conferences and meetups",
            "Engage actively on LinkedIn with industry content",
            "Participate in online communities and forums",
            "Consider mentoring junior professionals"
        ]
        
        return strategies
    
    def _recommend_certifications(self, field: str, experience_level: str) -> List[str]:
        """Recommend relevant certifications"""
        
        cert_mapping = {
            'data_science': [
                'Google Data Analytics Certificate',
                'AWS Certified Machine Learning',
                'Microsoft Azure Data Scientist Associate',
                'Coursera Machine Learning Specialization'
            ],
            'web_development': [
                'AWS Certified Developer',
                'Google Cloud Professional Developer',
                'Microsoft Azure Developer Associate',
                'MongoDB Certified Developer'
            ],
            'cloud_computing': [
                'AWS Solutions Architect',
                'Azure Solutions Architect Expert',
                'Google Cloud Professional Architect',
                'Kubernetes Certified Administrator'
            ],
            'cybersecurity': [
                'CISSP (Certified Information Systems Security Professional)',
                'CEH (Certified Ethical Hacker)',
                'CompTIA Security+',
                'CISM (Certified Information Security Manager)'
            ]
        }
        
        return cert_mapping.get(field, [
            'Project Management Professional (PMP)',
            'Agile Certified Practitioner',
            'ITIL Foundation',
            'Six Sigma Green Belt'
        ])[:4]
    
    def _fallback_analysis(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        
        # Basic scoring based on completeness
        sections_present = resume_data.get('sections_present', [])
        contact_completeness = resume_data.get('contact_completeness', 0)
        
        overall_score = min(100, (len(sections_present) * 10) + contact_completeness)
        
        return {
            'overall_score': overall_score,
            'ats_score': 70,  # Default ATS score
            'strengths': ['Profile shows relevant experience', 'Good educational background'],
            'improvement_areas': [
                {
                    'area': 'Resume completeness',
                    'priority': 'high',
                    'suggestion': 'Add missing sections like summary, skills, or projects'
                }
            ],
            'missing_skills': ['Communication', 'Leadership', 'Problem Solving'],
            'content_quality': {
                'writing_quality': 75,
                'quantifiable_achievements': 2,
                'action_verbs_usage': 'Good'
            },
            'market_insights': {
                'demand_score': 70,
                'salary_range': 'Competitive',
                'competition_level': 'Medium',
                'growth_potential': 75
            },
            'recommendations': [
                'Add a professional summary',
                'Include more quantifiable achievements',
                'Update skills section with current technologies'
            ],
            'career_trajectory': {
                'current_level': resume_data.get('experience_level', 'entry'),
                'next_steps': ['Gain more experience', 'Develop new skills'],
                'timeline': '1-2 years for next career move'
            }
        }
