import pymysql
import json
import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
                'host': 'your_host',
                'user': 'your_username',
                'password': 'your_password',
                'db': 'ai_resume_analyzer',
                'charset': 'utf8mb4'
            }
        self._initialize_database()
    
    def _get_connection(self):
        """Get database connection"""
        try:
            return pymysql.connect(**self.connection_params)
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return None
    
    def _initialize_database(self):
        """Initialize database and tables"""
        try:
            # Create database if not exists
            connection = pymysql.connect(
                host=self.connection_params['host'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                charset=self.connection_params['charset']
            )
            
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS ai_resume_analyzer")
            
            connection.close()
            
            # Create tables
            self._create_tables()
            
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
    
    def _create_tables(self):
        """Create necessary tables"""
        connection = self._get_connection()
        if not connection:
            return
        
        try:
            with connection.cursor() as cursor:
                # Enhanced user data table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    mobile VARCHAR(20) NOT NULL,
                    resume_data JSON,
                    ai_analysis JSON,
                    recommendations JSON,
                    job_description TEXT,
                    overall_score INT,
                    ats_score INT,
                    experience_level VARCHAR(50),
                    primary_field VARCHAR(100),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    session_id VARCHAR(100),
                    INDEX idx_email (email),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_field (primary_field)
                )
                """)
                
                # Feedback table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    score INT NOT NULL,
                    category VARCHAR(100),
                    comments TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_score (score),
                    INDEX idx_category (category)
                )
                """)
                
                # Skills analysis table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_analysis_id INT,
                    skill_name VARCHAR(255),
                    skill_category VARCHAR(100),
                    proficiency_level VARCHAR(50),
                    is_missing BOOLEAN DEFAULT FALSE,
                    market_demand_score INT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_analysis_id) REFERENCES user_analysis(id),
                    INDEX idx_skill (skill_name),
                    INDEX idx_category (skill_category)
                )
                """)
                
                # Career insights table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS career_insights (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_analysis_id INT,
                    insight_type VARCHAR(100),
                    insight_content TEXT,
                    confidence_score FLOAT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_analysis_id) REFERENCES user_analysis(id),
                    INDEX idx_type (insight_type)
                )
                """)
                
                # Analytics tracking table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    event_type VARCHAR(100),
                    event_data JSON,
                    user_session VARCHAR(100),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_event_type (event_type),
                    INDEX idx_timestamp (timestamp)
                )
                """)
            
            connection.commit()
            
        except Exception as e:
            st.error(f"Table creation error: {str(e)}")
        finally:
            connection.close()
    
    def store_analysis_result(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Store complete analysis result"""
        connection = self._get_connection()
        if not connection:
            return None
        
        try:
            with connection.cursor() as cursor:
                # Insert main analysis record
                insert_query = """
                INSERT INTO user_analysis 
                (name, email, mobile, resume_data, ai_analysis, recommendations, 
                 job_description, overall_score, ats_score, experience_level, 
                 primary_field, ip_address, user_agent, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    user_data['name'],
                    user_data['email'],
                    user_data['mobile'],
                    json.dumps(user_data['resume_data']),
                    json.dumps(user_data['ai_analysis']),
                    json.dumps(user_data['recommendations']),
                    user_data.get('job_description', ''),
                    user_data['ai_analysis'].get('overall_score', 0),
                    user_data['ai_analysis'].get('ats_score', 0),
                    user_data['resume_data'].get('experience_level', ''),
                    user_data['resume_data'].get('primary_field', ''),
                    self._get_client_ip(),
                    self._get_user_agent(),
                    self._get_session_id()
                ))
                
                user_analysis_id = cursor.lastrowid
                
                # Store skills analysis
                self._store_skills_analysis(cursor, user_analysis_id, user_data)
                
                # Store career insights
                self._store_career_insights(cursor, user_analysis_id, user_data)
            
            connection.commit()
            return user_analysis_id
            
        except Exception as e:
            st.error(f"Error storing analysis result: {str(e)}")
            connection.rollback()
            return None
        finally:
            connection.close()
    
    def _store_skills_analysis(self, cursor, user_analysis_id: int, user_data: Dict[str, Any]):
        """Store detailed skills analysis"""
        resume_data = user_data['resume_data']
        ai_analysis = user_data['ai_analysis']
        
        # Store existing skills
        skills = resume_data.get('skills', {})
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                for skill in skill_list:
                    cursor.execute("""
                    INSERT INTO skills_analysis 
                    (user_analysis_id, skill_name, skill_category, proficiency_level, is_missing)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (user_analysis_id, skill, category, 'present', False))
        
        # Store missing skills
        missing_skills = ai_analysis.get('missing_skills', [])
        for skill in missing_skills:
            cursor.execute("""
            INSERT INTO skills_analysis 
            (user_analysis_id, skill_name, skill_category, proficiency_level, is_missing)
            VALUES (%s, %s, %s, %s, %s)
            """, (user_analysis_id, skill, 'recommended', 'missing', True))
    
    def _store_career_insights(self, cursor, user_analysis_id: int, user_data: Dict[str, Any]):
        """Store career insights"""
        ai_analysis = user_data['ai_analysis']
        
        # Store various insights
        insights = [
            ('strengths', ai_analysis.get('strengths', [])),
            ('recommendations', ai_analysis.get('recommendations', [])),
            ('career_trajectory', [ai_analysis.get('career_trajectory', {})])
        ]
        
        for insight_type, insight_list in insights:
            for insight in insight_list:
                cursor.execute("""
                INSERT INTO career_insights 
                (user_analysis_id, insight_type, insight_content, confidence_score)
                VALUES (%s, %s, %s, %s)
                """, (user_analysis_id, insight_type, json.dumps(insight), 0.8))
    
    def store_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Store user feedback"""
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO user_feedback (name, email, score, category, comments)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    feedback_data['name'],
                    feedback_data['email'],
                    feedback_data['score'],
                    feedback_data.get('category', 'General'),
                    feedback_data.get('comments', '')
                ))
            
            connection.commit()
            return True
            
        except Exception as e:
            st.error(f"Error storing feedback: {str(e)}")
            return False
        finally:
            connection.close()
    
    def get_analytics_data(self) -> List[Dict[str, Any]]:
        """Get analytics data for dashboard"""
        connection = self._get_connection()
        if not connection:
            return []
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT resume_data, ai_analysis, primary_field, experience_level, 
                       overall_score, ats_score, timestamp
                FROM user_analysis 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """)
                
                results = cursor.fetchall()
                analytics_data = []
                
                for row in results:
                    try:
                        resume_data = json.loads(row[0]) if row[0] else {}
                        ai_analysis = json.loads(row[1]) if row[1] else {}
                        
                        analytics_data.append({
                            'resume_data': resume_data,
                            'ai_analysis': ai_analysis,
                            'primary_field': row[2],
                            'experience_level': row[3],
                            'overall_score': row[4],
                            'ats_score': row[5],
                            'timestamp': row[6]
                        })
                    except json.JSONDecodeError:
                        continue
                
                return analytics_data
                
        except Exception as e:
            st.error(f"Error fetching analytics data: {str(e)}")
            return []
        finally:
            connection.close()
    
    def get_feedback_data(self) -> List[Dict[str, Any]]:
        """Get feedback data"""
        connection = self._get_connection()
        if not connection:
            return []
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT name, email, score, category, comments, timestamp
                FROM user_feedback 
                ORDER BY timestamp DESC
                """)
                
                results = cursor.fetchall()
                feedback_data = []
                
                for row in results:
                    feedback_data.append({
                        'name': row[0],
                        'email': row[1],
                        'score': row[2],
                        'category': row[3],
                        'comments': row[4],
                        'timestamp': row[5]
                    })
                
                return feedback_data
                
        except Exception as e:
            st.error(f"Error fetching feedback data: {str(e)}")
            return []
        finally:
            connection.close()
    
    def track_analytics_event(self, event_type: str, event_data: Dict[str, Any]):
        """Track analytics events"""
        connection = self._get_connection()
        if not connection:
            return
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO analytics_events (event_type, event_data, user_session)
                VALUES (%s, %s, %s)
                """, (event_type, json.dumps(event_data), self._get_session_id()))
            
            connection.commit()
            
        except Exception as e:
            # Silently fail for analytics to not disrupt user experience
            pass
        finally:
            connection.close()
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except:
            return '127.0.0.1'
    
    def _get_user_agent(self) -> str:
        """Get user agent"""
        return 'Streamlit App'
    
    def _get_session_id(self) -> str:
        """Get session ID"""
        if 'session_id' not in st.session_state:
            import secrets
            st.session_state.session_id = secrets.token_urlsafe(16)
        return st.session_state.session_id
