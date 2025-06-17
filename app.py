import streamlit as st
import pandas as pd
import base64
import time
import datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io
import random
import json
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from PIL import Image
import nltk
from openai import OpenAI
from streamlit_option_menu import option_menu

# Download required NLTK data
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    pass

# Import our custom modules
from ai_resume_parser import AdvancedResumeParser
from career_intelligence import CareerIntelligenceEngine
from database_manager import DatabaseManager
from courses_data import *

# Page configuration
st.set_page_config(
    page_title="Elevate CV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for professional corporate UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
        min-height: 100vh;
    }
    
    /* Header Styles */
    .main-header {
        background-color: #1a3c61;
        padding: 2.5rem 2rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Card Styles */
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #1a3c61;
        transition: all 0.2s ease;
        text-align: left;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 180px;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card h3 {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        color: #1a3c61;
    }
    
    /* Professional Sections */
    .analysis-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .analysis-section h3 {
        color: #2d3748;
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background-color: #1a3c61;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        background-color: #15325a;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Skill Tags */
    .skill-tag {
        background-color: #e2e8f0;
        color: #2d3748;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        margin: 0.3rem;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .skill-tag:hover {
        background-color: #cbd5e0;
    }
    
    /* Recommendation Items */
    .recommendation-item {
        background-color: #f8fafc;
        padding: 1.25rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        border-left: 4px solid #2c7a7b;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .recommendation-item:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .warning-item {
        background-color: #fffbeb;
        padding: 1.25rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        border-left: 4px solid #d97706;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .warning-item:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-item {
        background-color: #f0fdf4;
        padding: 1.25rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        border-left: 4px solid #16a34a;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .success-item:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1a3c61;
        box-shadow: 0 0 0 2px rgba(26, 60, 97, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1a3c61;
        box-shadow: 0 0 0 2px rgba(26, 60, 97, 0.1);
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background-color: #ffffff;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        border: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a3c61;
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #1a3c61;
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background-color: #f8f9fa;
        border: 2px dashed #cbd5e0;
        border-radius: 6px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* Professional Logo */
    .sidebar-logo {
        text-align: center;
        padding: 1.5rem 1rem;
        background-color: #1a3c61;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-logo h2 {
        color: #ced6de;
        margin-bottom: 0.25rem;
    }
    .sidebar-logo p {
        color: #e9eef5;
        font-size: 0.9rem;
        margin-top: 0;
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.5rem;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #1a3c61;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    div[data-testid="stSidebar"] ul li a {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        color: #2d3748;
    }
    
    div[data-testid="stSidebar"] ul li a:hover {
        font-weight: 600;
        color: #1a3c61;
    }

    div[data-testid="stSidebar"] ul li a:focus,
    div[data-testid="stSidebar"] ul li a:active {
        color: white;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Chat Messages */
    .chat-message {
        background-color: #ffffff;
        padding: 1.25rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Form Styles */
    .stForm {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>AI-Powered Resume Analyzer</h1>
        <p>Advanced analysis with career intelligence for professionals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    try:
        db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.info("The app will continue without database features.")
        db_manager = None
    
    # Enhanced Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>Elevate CV</h2>
            <p>Professional Career Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Analytics", "AI Assistant", "Feedback", "About"],
            icons=["house", "graph-up", "robot", "chat-dots", "info-circle"],
            menu_icon="list",
            default_index=0,
            styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent",
                "font-family": "Inter, sans-serif"
            },
            "nav-link": {
                "font-family": "Inter, sans-serif",
                "font-size": "0.95rem",
                "text-align": "left",
                "margin": "4px 0px",
                "padding": "0.75rem 1rem",
                "border-radius": "6px",
                "background-color": "#f8f9fa",
                "border": "1px solid #e2e8f0",
                "color": "#1a202c",  # dark gray text for visibility
                "--hover-color": "#edf2f7"
            },
            "nav-link-selected": {
                "font-family": "Inter, sans-serif",
                "background-color": "#1a3c61",
                "color": "white",
                "font-weight": "500"
            }
        }
        )
        
        # Add some professional info in sidebar
        st.markdown("---")

    
    if selected == "Home":
        home_page(db_manager)
    elif selected == "Analytics":
        analytics_page(db_manager)
    elif selected == "AI Assistant":
        ai_assistant_page()
    elif selected == "Feedback":
        feedback_page(db_manager)
    elif selected == "About":
        about_page()
        
st.markdown("""
    <style>
    /* Change tab label color to black */
    .stTabs [data-baseweb="tab"] button {
        color: #2d3748 !important;
        font-weight: 500;
    }

    /* Optional: Highlight active tab with custom underline or bold */
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #1a3c61 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

def home_page(db_manager):
    if not st.session_state.get("analysis_complete", False):
        # User information collection with enhanced styling
        st.markdown("### Personal Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="margin-bottom: -10px;">
                <label style="font-weight: 500; font-size: 0.95rem;">Full Name <span style="color: #e53e3e;">*</span></label>
            </div>
            """, unsafe_allow_html=True)

            act_name = st.text_input(
                label=" ",
                placeholder="Enter your full name",
                help="Your complete professional name",
                label_visibility="collapsed"
            )


        with col2:
            st.markdown("""
            <div style="margin-bottom: -10px;">
                <label style="font-weight: 500; font-size: 0.95rem;">Email Address <span style="color: #e53e3e;">*</span></label>
            </div>
            """, unsafe_allow_html=True)

            act_mail = st.text_input(
                label=" ",
                placeholder="your.email@example.com",
                help="Professional email address",
                label_visibility="collapsed"
            )
        with col3:
            st.markdown("""
            <div style="margin-bottom: -10px;">
                <label style="font-weight: 500; font-size: 0.95rem;">Mobile Number <span style="color: #e53e3e;">*</span></label>
            </div>
            """, unsafe_allow_html=True)

            act_mob = st.text_input(
                label=" ",
                placeholder="+1234567890",
                help="Contact number with country code",
                label_visibility="collapsed"
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Resume upload section with enhanced UI
        st.markdown("### Resume Upload & Analysis")
        resume_text = ""
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF only)",
            type=["pdf"],
            help="Upload your resume in .pdf format"
        )

        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()

            with st.spinner("Extracting text from file..."):
                if file_type == "pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    st.error("Unsupported file type.")

            if resume_text:
                st.success(f"File uploaded successfully!")

                with st.expander("View Resume Content"):
                    show_pdf_preview(uploaded_file)
            else:
                st.error("Could not extract text. Please upload a valid resume file.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Job description for matching (optional)
        st.markdown("### Job Description Matching (Optional)")        
        job_description = st.text_area(
            "Paste job description for targeted analysis:",
            height=150,
            placeholder="Paste the job description you're targeting for personalized recommendations...",
            help="This helps our AI provide more targeted advice and skill recommendations"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Analysis button
        st.markdown('<div style="text-align: center; margin: 1.5rem 0;">', unsafe_allow_html=True)
        if st.button("Start AI Analysis", type="primary", use_container_width=True):
            if not all([act_name, act_mail, act_mob, resume_text]):
                st.error("Please fill in all required fields and upload/paste your resume.")
                return
            
            # Start analysis with enhanced progress tracking
            with st.container():
                st.markdown("""
                <div style="text-align: center; padding: 1.5rem; background-color: #f8f9fa; border-radius: 6px; margin: 1rem 0;">
                    <h3 style="color: #2d3748;">AI Analysis in Progress</h3>
                    <p style="color: #4a5568;">Our advanced AI is analyzing your resume...</p>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    # Initialize AI parser
                    ai_parser = AdvancedResumeParser()
                    
                    # Extract resume data
                    progress_bar = st.progress(0)
                    st.info("Extracting resume information...")
                    progress_bar.progress(25)
                    time.sleep(1)  # Visual feedback
                    
                    resume_data = ai_parser.extract_comprehensive_data(resume_text)
                    progress_bar.progress(50)
                    
                    # Perform AI analysis
                    st.info("Performing intelligent analysis...")
                    career_engine = CareerIntelligenceEngine()
                    ai_analysis = career_engine.analyze_resume(resume_data, job_description)
                    progress_bar.progress(75)
                    time.sleep(1)  # Visual feedback
                    
                    # Generate recommendations
                    st.info("Generating personalized recommendations...")
                    recommendations = career_engine.generate_recommendations(resume_data, ai_analysis)
                    progress_bar.progress(100)
                    time.sleep(0.5)  # Visual feedback
                    
                    # Store in session state
                    st.session_state.resume_data = resume_data
                    st.session_state.ai_analysis = ai_analysis
                    st.session_state.recommendations = recommendations
                    st.session_state.analysis_complete = True

                    # Store in database if available
                    if db_manager:
                        try:
                            user_data = {
                                'name': act_name,
                                'email': act_mail,
                                'mobile': act_mob,
                                'resume_data': resume_data,
                                'ai_analysis': ai_analysis,
                                'recommendations': recommendations,
                                'job_description': job_description,
                                'timestamp': datetime.datetime.now()
                            }
                            db_manager.store_analysis_result(user_data)
                        except Exception as e:
                            st.warning(f"Analysis completed but couldn't save to database: {str(e)}")

                    progress_bar.empty()

                    # ✅ Rerun at the very end
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("Please check your internet connection and try again.")
                    return
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if analysis is complete
    else:
        display_analysis_results()
        
st.markdown("""
    <style>
    /* Unselected tab label color */
    .stTabs [data-baseweb="tab"] {
        color: #1a202c !important;  /* dark gray text */
        background-color: #f8f9fa !important;  /* light gray background */
        border: 1px solid #e2e8f0 !important;
        border-bottom: none !important;
        font-weight: 500;
    }

    /* Selected tab */
    .stTabs [aria-selected="true"] {
        color: white !important;
        background-color: #1a3c61 !important;
    }

    /* Optional: improve tab layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    </style>
""", unsafe_allow_html=True)

def display_analysis_results():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <h1 style="color: #bbbfc4; font-weight: 600;">AI Analysis Results</h1>
    </div>
    """, unsafe_allow_html=True)
    
    resume_data = st.session_state.resume_data
    ai_analysis = st.session_state.ai_analysis
    
    # Enhanced Overview metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        score = ai_analysis.get('overall_score', 0)
        color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Overall Score</h3>
            <h2 style="color: {color};">{score}/100</h2>
            <div style="width: 100%; background: #e2e8f0; border-radius: 4px; height: 6px; margin-top: 1rem;">
                <div style="width: {score}%; background: {color}; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ats_score = ai_analysis.get('ats_score', 0)
        ats_color = "#16a34a" if ats_score >= 80 else "#d97706" if ats_score >= 60 else "#dc2626"
        st.markdown(f"""
        <div class="metric-card">
            <h3>ATS Compatibility</h3>
            <h2 style="color: {ats_color};">{ats_score}/100</h2>
            <div style="width: 100%; background: #e2e8f0; border-radius: 4px; height: 6px; margin-top: 1rem;">
                <div style="width: {ats_score}%; background: {ats_color}; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        exp_level = resume_data.get('experience_level', 'Unknown').title()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Experience Level</h3>
            <h2 style="color: #1a3c61;">{exp_level}</h2>
            <p style="color: #4a5568; margin-top: 1rem; font-size: 0.85rem;">
                {resume_data.get('years_of_experience', 0)} years
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        field = resume_data.get('primary_field', 'General').replace('_', ' ').title()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Career Field</h3>
            <h2 style="color: #1a3c61;">{field}</h2>
            <p style="color: #4a5568; margin-top: 1rem; font-size: 0.85rem;">
                Primary specialization
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Personal Profile", 
        "Skills Analysis", 
        "Career Insights", 
        "Recommendations", 
        "Detailed Report"
    ])
    
    with tab1:
        display_personal_info(resume_data)
    
    with tab2:
        display_skills_analysis(resume_data, ai_analysis)
    
    with tab3:
        display_career_insights(ai_analysis)
    
    with tab4:
        display_recommendations(st.session_state.get('recommendations', {}))
    
    with tab5:
        display_detailed_report(resume_data, ai_analysis)

def display_personal_info(resume_data):
    st.markdown("### Extracted Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Contact Information")
        contact_info = [
            ("Name", resume_data.get('name', 'Not found')),
            ("Email", resume_data.get('email', 'Not found')),
            ("Phone", resume_data.get('phone', 'Not found')),
            ("Location", resume_data.get('location', 'Not found')),
            ("LinkedIn", resume_data.get('linkedin', 'Not found')),
            ("GitHub", resume_data.get('github', 'Not found'))
        ]
        
        for label, value in contact_info:
            if value != 'Not found':
                st.markdown(f"**{label}:** {value}")
            else:
                st.markdown(f"**{label}:** <span style='color: #dc2626;'>{value}</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Professional Summary")
        if resume_data.get('summary'):
            st.markdown(f"""
            <div style="background-color: #f0fdf4;
                        padding: 1.25rem;
                        border-radius: 6px;
                        border-left: 4px solid #16a34a;
                        color: #2d3748;
                        font-weight: 400;">
                {resume_data['summary']}
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
                <div style="background-color: #fffbeb;
                            padding: 1.25rem;
                            border-radius: 6px;
                            border-left: 4px solid #d97706;
                            color: #2d3748;
                            font-weight: 400;">
                    No professional summary found. Consider adding one to improve your resume.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Experience section with enhanced styling
    if resume_data.get('experience'):
        st.markdown("### Work Experience")
        
        for i, exp in enumerate(resume_data['experience']):
            with st.expander(f"{exp.get('position', 'Position')} at {exp.get('company', 'Company')}", expanded=i==0):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"<span style='color:#2d3748; font-weight:500;'><strong>Duration:</strong> {exp.get('duration', 'Not specified')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#2d3748; font-weight:400;'><strong>Description:</strong> {exp.get('description', 'No description')}</span>", unsafe_allow_html=True)
                
                with col2:
                    if exp.get('achievements'):
                        st.markdown("<span style='color:#2d3748; font-weight:500;'><strong>Key Achievements:</strong></span>", unsafe_allow_html=True)
                        for achievement in exp['achievements']:
                            st.markdown(f"<span style='color:#2d3748;'>• {achievement}</span>", unsafe_allow_html=True)

    
    # Education section with enhanced styling
    if resume_data.get('education'):
        st.markdown("### Education")
        
        for edu in resume_data['education']:
            st.markdown(f"""
            <div style="background-color: #f8fafc;
                        padding: 1.25rem;
                        border-radius: 6px;
                        margin: 0.75rem 0;
                        border-left: 4px solid #1a3c61;
                        color: #2d3748;
                        font-weight: 400;">
                <strong>{edu.get('degree', 'Degree')}</strong> in {edu.get('field', 'Field')}<br>
                <strong>Institution:</strong> {edu.get('institution', 'Institution')}<br>
                <strong>Year:</strong> {edu.get('year', 'Year not specified')}
                {f"<br><strong>GPA:</strong> {edu.get('gpa')}" if edu.get('gpa') else ""}
            </div>
            """, unsafe_allow_html=True)


def display_skills_analysis(resume_data, ai_analysis):
    st.markdown("### Skills Breakdown")
    
    # Skills categories with enhanced visualization
    skills_data = resume_data.get('skills', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Technical Skills")
        if skills_data.get('technical'):
            skills_html = ""
            for skill in skills_data['technical']:
                skills_html += f'<span class="skill-tag">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No technical skills found")
        
        st.markdown("#### Frameworks & Tools")
        frameworks = skills_data.get('frameworks', []) + skills_data.get('tools', [])
        if frameworks:
            frameworks_html = ""
            for framework in frameworks:
                frameworks_html += f'<span class="skill-tag">{framework}</span>'
            st.markdown(frameworks_html, unsafe_allow_html=True)
        else:
            st.info("No frameworks/tools found")
    
    with col2:
        st.markdown("#### Soft Skills")
        if skills_data.get('soft'):
            soft_skills_html = ""
            for skill in skills_data['soft']:
                soft_skills_html += f'<span class="skill-tag">{skill}</span>'
            st.markdown(soft_skills_html, unsafe_allow_html=True)
        else:
            st.info("No soft skills found")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Skills gap analysis with enhanced styling
    if ai_analysis.get('missing_skills'):
        st.markdown("### Skills Gap Analysis")
        st.markdown("**Recommended skills to enhance your profile:**")
        
        missing_skills_cols = st.columns(3)
        for i, skill in enumerate(ai_analysis['missing_skills'][:9]):  # Show up to 9 skills in 3 columns
            with missing_skills_cols[i % 3]:
                st.markdown(f"""
                    <div style="background-color: #FFFFFF;
                                padding: 0.75rem 1rem;
                                border-radius: 6px;
                                margin-bottom: 0.75rem;
                                border-left: 4px solid #d97706;
                                color: #2d3748;
                                font-weight: 400;">
                        {skill}
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_career_insights(ai_analysis):
    st.markdown("### AI-Powered Career Insights")
    
    # Strengths with enhanced styling
    if ai_analysis.get('strengths'):
        st.markdown("#### Your Key Strengths")
        strengths_cols = st.columns(2)
        for i, strength in enumerate(ai_analysis['strengths']):
            with strengths_cols[i % 2]:
                    st.markdown(f'''
                        <div class="success-item" style="color: #2d3748; font-weight: 400;">
                            {strength}
                        </div>
                    ''', unsafe_allow_html=True)

    
    # Areas for improvement with priority-based styling
    if ai_analysis.get('improvement_areas'):
        st.markdown("#### Areas for Improvement")
        for area in ai_analysis['improvement_areas']:
            priority = area.get('priority', 'medium').lower()
            priority_colors = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}
            
            color = priority_colors.get(priority, "#d97706")
            
            st.markdown(f"""
                    <div class="warning-item">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: {color};">{priority.upper()} PRIORITY</strong>
                        </div>
                        <div style="color: #2d3748; font-weight: 500; margin-bottom: 0.3rem;">
                            {area.get('area', 'Improvement needed')}
                        </div>
                        <div style="color: #4a5568; font-weight: 400; font-size: 0.9rem;">
                            {area.get('suggestion', 'No specific suggestion')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market insights with enhanced metrics
    if ai_analysis.get('market_insights'):
        st.markdown("### Market Intelligence")
        
        insights = ai_analysis['market_insights']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            demand_score = insights.get('demand_score', 0)
            demand_color = "#16a34a" if demand_score >= 70 else "#d97706" if demand_score >= 40 else "#dc2626"
            st.markdown(f"""
            <div style="text-align: center; padding: 1.25rem; background-color: #ffffff; border-radius: 6px; border-left: 4px solid {demand_color};">
                <h4 style="color: #2d3748; margin-bottom: 0.5rem;">Market Demand</h4>
                <h2 style="color: {demand_color}; margin: 0;">{demand_score}/100</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 1.25rem; background-color: #ffffff; border-radius: 6px; border-left: 4px solid #1a3c61;">
                <h4 style="color: #2d3748; margin-bottom: 0.5rem;">Salary Range</h4>
                <h3 style="color: #1a3c61; margin: 0;">{insights.get('salary_range', 'Not available')}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            competition = insights.get('competition_level', 'Medium')
            comp_colors = {"Low": "#16a34a", "Medium": "#d97706", "High": "#dc2626"}
            comp_color = comp_colors.get(competition, "#d97706")
            st.markdown(f"""
            <div style="text-align: center; padding: 1.25rem; background-color: #ffffff; border-radius: 6px; border-left: 4px solid {comp_color};">
                <h4 style="color: #2d3748; margin-bottom: 0.5rem;">Competition</h4>
                <h3 style="color: {comp_color}; margin: 0;">{competition}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            growth_score = insights.get('growth_potential', 0)
            growth_color = "#16a34a" if growth_score >= 70 else "#d97706" if growth_score >= 40 else "#dc2626"
            st.markdown(f"""
            <div style="text-align: center; padding: 1.25rem; background-color: #ffffff; border-radius: 6px; border-left: 4px solid {growth_color};">
                <h4 style="color: #2d3748; margin-bottom: 0.5rem;">Growth Potential</h4>
                <h2 style="color: {growth_color}; margin: 0;">{growth_score}/100</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_recommendations(recommendations):
    
    # Course recommendations with enhanced styling
    if recommendations.get('courses'):
        st.markdown("#### Recommended Courses")
        
        courses_cols = st.columns(2)
        for i, course in enumerate(recommendations['courses'][:8]):  # Show top 8 courses
            if isinstance(course, list) and len(course) >= 2:
                with courses_cols[i % 2]:
                    st.markdown(f"""
                    <div class="recommendation-item">
                        <a href="{course[1]}" target="_blank" style="text-decoration: none; color: #1a3c61; font-weight: 500;">
                            {course[0]}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Skill development with enhanced layout
    if recommendations.get('skill_development'):
        st.markdown("#### Skill Development Plan")
        for skill_rec in recommendations['skill_development'][:5]:  # Top 5 recommendations
            st.markdown(f'<div class="recommendation-item" style="color: #2d3748; font-weight: 400;" >{skill_rec}</div>', unsafe_allow_html=True)
    
    # Career moves with timeline
    if recommendations.get('career_moves'):
        st.markdown("#### Career Advancement Path")
        for i, move in enumerate(recommendations['career_moves'][:4]):  # Top 4 moves
            st.markdown(f'<div class="recommendation-item" style="color: #2d3748; font-weight: 400;" ><strong>Step {i+1}:</strong> {move}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_detailed_report(resume_data, ai_analysis):
    import datetime
    import json
    import streamlit as st

    # Create a summary report
    summary_report = f"""
    RESUME ANALYSIS SUMMARY REPORT
    Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    CANDIDATE INFORMATION:
    Name: {resume_data.get('name', 'N/A')}
    Email: {resume_data.get('email', 'N/A')}
    Experience Level: {resume_data.get('experience_level', 'N/A')}
    Primary Field: {resume_data.get('primary_field', 'N/A')}
    
    ANALYSIS SCORES:
    Overall Score: {ai_analysis.get('overall_score', 0)}/100
    ATS Score: {ai_analysis.get('ats_score', 0)}/100
    
    KEY STRENGTHS:
    {chr(10).join([f"• {strength}" for strength in ai_analysis.get('strengths', [])])}
    
    IMPROVEMENT AREAS:
    {chr(10).join([f"• {area.get('area', '')}: {area.get('suggestion', '')}" for area in ai_analysis.get('improvement_areas', [])])}
    
    MISSING SKILLS:
    {chr(10).join([f"• {skill}" for skill in ai_analysis.get('missing_skills', [])])}
    """

    # Show download button for TXT only
    st.download_button(
        label="Download Summary Report (TXT)",
        data=summary_report,
        file_name=f"Resume Summary {datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )


def analytics_page(db_manager):
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <h1 style="color: #a7c0db; font-weight: 600;">Analytics Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if not db_manager:
        st.error("Database not available. Analytics features are disabled.")
        return
    
    # Fetch analytics data
    try:
        analytics_data = db_manager.get_analytics_data()
    except Exception as e:
        st.error(f"Error fetching analytics data: {str(e)}")
        return
    
    if not analytics_data:
        st.info("No analytics data available yet. Analyze some resumes first!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Analyses</h3>
            <h2 style="color: #1a3c61;">{len(analytics_data)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = sum([data.get('overall_score', 0) for data in analytics_data]) / len(analytics_data)
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Score</h3>
            <h2 style="color: #16a34a;">{avg_score:.1f}/100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        fields = [data.get('primary_field', 'Unknown') for data in analytics_data]
        unique_fields = len(set(fields))
        st.markdown(f"""
        <div class="metric-card">
            <h3>Career Fields</h3>
            <h2 style="color: #d97706;">{unique_fields}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_scores = len([data for data in analytics_data if data.get('overall_score', 0) >= 80])
        st.markdown(f"""
        <div class="metric-card">
            <h3>High Scores (80+)</h3>
            <h2 style="color: #1a3c61;">{high_scores}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Create enhanced visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Field distribution
        field_counts = {}
        for data in analytics_data:
            field = data.get('primary_field', 'Unknown').replace('_', ' ').title()
            field_counts[field] = field_counts.get(field, 0) + 1
        
        if field_counts:
            fig_pie = px.pie(
                values=list(field_counts.values()),
                names=list(field_counts.keys()),
                title="Career Field Distribution",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pie.update_layout(
                font=dict(size=12),
                title_font_size=16,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Experience level distribution
        exp_counts = {}
        for data in analytics_data:
            exp = data.get('experience_level', 'Unknown').title()
            exp_counts[exp] = exp_counts.get(exp, 0) + 1
        
        if exp_counts:
            fig_bar = px.bar(
                x=list(exp_counts.keys()),
                y=list(exp_counts.values()),
                title="Experience Level Distribution",
                color=list(exp_counts.values()),
                color_continuous_scale="Blues"
            )
            fig_bar.update_layout(
                font=dict(size=12),
                title_font_size=16,
                xaxis_title="Experience Level",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Score distribution with enhanced styling
    scores = [data.get('overall_score', 0) for data in analytics_data if data.get('overall_score')]
    if scores:
        fig_hist = px.histogram(
            x=scores,
            title="Resume Score Distribution",
            nbins=20,
            color_discrete_sequence=['#1a3c61']
        )
        fig_hist.update_layout(
            font=dict(size=12),
            title_font_size=16,
            xaxis_title="Overall Score",
            yaxis_title="Frequency"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

def ai_assistant_page():
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <h1 style="color: #cee0f5; font-weight: 600;">AI Career Assistant</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 1.25rem; border-radius: 6px; margin: 1.5rem 0; border-left: 4px solid #16a34a;">
        <h4 style="color: #2d3748; margin-bottom: 0.75rem;">How can I help you today?</h4>
        <p style="color: #4a5568; margin: 0;">Ask me anything about:</p>
        <ul style="color: #4a5568; margin: 0.5rem 0;">
            <li>Resume optimization and improvement</li>
            <li>Career transition strategies</li>
            <li>Skill development recommendations</li>
            <li>Interview preparation tips</li>
            <li>Industry insights and trends</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages with enhanced styling
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 6px;
                    border-left: 4px solid #1a3c61;
                    color: #2d3748;
                    font-size: 0.95rem;
                ">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background-color: #f0fdf4;
                    padding: 1rem;
                    border-radius: 6px;
                    border-left: 4px solid #16a34a;
                    color: #2d3748;
                    font-size: 0.95rem;
                ">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)

    
    # Chat input
    if prompt := st.chat_input("Ask your career question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 6px;
                    border-left: 4px solid #1a3c61;
                    color: #2d3748;
                    font-size: 0.95rem;
                ">
                    {prompt}
                </div>
                """, unsafe_allow_html=True)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key="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"
                    )
                    
                    # Include resume context if available
                    context = ""
                    if st.session_state.get('resume_data'):
                        context = f"\nUser's Resume Context: {json.dumps(st.session_state.resume_data, default=str)}"
                    
                    completion = client.chat.completions.create(
                        model="deepseek/deepseek-chat",
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are an expert career counselor and resume advisor with 20+ years of experience. Provide helpful, actionable advice about careers, job searching, resume writing, and professional development. Be encouraging, specific, and professional in your responses.{context}"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    response = completion.choices[0].message.content
                    st.markdown(f"""
                            <div style="
                            background-color: #f0fdf4;
                            padding: 1rem;
                            border-radius: 6px;
                            border-left: 4px solid #16a34a;
                            color: #2d3748;
                            font-size: 0.95rem;
                        ">
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Please check your internet connection and try again.")

def feedback_page(db_manager):
    # Inject dark label styles for this page only
    st.markdown("""
    <style>
    /* Input & textarea labels */
    label, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #2d3748 !important;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <h1 style="color: #c8d1db; font-weight: 600;">Feedback & Reviews</h1>
        <p style="color: #edf0f2; font-size: 1.1rem;">Help us improve by sharing your experience</p>
    </div>
    """, unsafe_allow_html=True)

    # Feedback form
    with st.form("feedback_form"):
        st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <h2 style="color: #1a3c61; font-weight: 600;">Share Your Experience</h2>
    </div>
    """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # Custom HTML with no bottom margin
            st.markdown("""
                <div style="font-weight:bold; color:black; margin-bottom:0.2rem;">
                    Full Name
                </div>
            """, unsafe_allow_html=True)
            feed_name = st.text_input("", placeholder="Enter your name", label_visibility="collapsed")
            
            st.markdown("""
                <div style="font-weight:bold; color:black; margin-bottom:0.2rem;">
                    Email Address
                </div>
            """, unsafe_allow_html=True)
                        
            feed_email = st.text_input("", placeholder="your.email@example.com", label_visibility="collapsed")
            
        with col2:
            st.markdown("""
                <div style="font-weight:bold; color:black; margin-bottom:0.2rem;">
                    Rating (1-5)
                </div>
            """, unsafe_allow_html=True)            
            feed_score = st.slider("", 1, 5, 5, help="1 = Poor, 5 = Excellent", label_visibility="collapsed")
            
            st.markdown("""
                <div style="font-weight:bold; color:black; margin-bottom:0.2rem;">
                    How can we improve?
                </div>
            """, unsafe_allow_html=True)
                        
            # Selectbox with no label (custom label is shown above)
            category = st.selectbox(
                label="", 
                options=["General", "UI/UX", "AI Accuracy", "Features", "Bug Report", "Performance"],
                label_visibility="collapsed"  # hides the default label space
            )
        st.markdown("""
                <div style="font-weight:bold; color:black; margin-bottom:0.2rem;">
                   Comments & Suggestions
                </div>
            """, unsafe_allow_html=True)  
        
        comments = st.text_area("", 
                                placeholder="Please share your detailed feedback, suggestions, or report any issues...",
                                height=150,
                label_visibility="collapsed")

        submitted = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)

        if submitted and feed_name and feed_email:
            if db_manager:
                try:
                    feedback_data = {
                        'name': feed_name,
                        'email': feed_email,
                        'score': feed_score,
                        'category': category,
                        'comments': comments,
                        'timestamp': datetime.datetime.now()
                    }

                    db_manager.store_feedback(feedback_data)
                    st.markdown("""
                        <div style="
                            background-color: #f0fdf4;
                            padding: 1rem 1.25rem;
                            border-left: 4px solid #16a34a;
                            border-radius: 6px;
                            color: #166534;
                            font-size: 1rem;
                            font-weight: 500;
                            margin-top: 1rem;
                        ">
                        Thank you for your feedback!
                        </div>
                        """, unsafe_allow_html=True)
                     
                except Exception as e:
                    st.error(f"Error submitting feedback: {str(e)}")
            else:
                st.success("Thank you for your feedback! (Database not available)")
                 

    st.markdown("---")
    # Analytics (unchanged)
    if db_manager:
        st.markdown("### User Feedback Analytics")

        try:
            feedback_data = db_manager.get_feedback_data()

            if feedback_data:
                ratings = [f['score'] for f in feedback_data]
                avg_rating = sum(ratings) / len(ratings)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Average Rating</h3>
                        <h2 style="color: #16a34a;">{avg_rating:.1f}/5</h2>
                        <div style="color: #eab308; font-size: 1.25rem;">
                            {'★' * int(avg_rating)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Reviews</h3>
                        <h2 style="color: #1a3c61;">{len(feedback_data)}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    five_star = ratings.count(5)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>5-Star Reviews</h3>
                        <h2 style="color: #1a3c61;">{five_star}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    satisfaction = (five_star / len(ratings)) * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Satisfaction Rate</h3>
                        <h2 style="color: #d97706;">{satisfaction:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)

                rating_counts = {i: ratings.count(i) for i in range(1, 6)}
                fig = px.bar(
                    x=[f"{i} Star{'s' if i != 1 else ''}" for i in rating_counts.keys()],
                    y=list(rating_counts.values()),
                    title="Rating Distribution",
                    color=list(rating_counts.values()),
                    color_continuous_scale="Blues"
                )
                fig.update_layout(
                    font=dict(size=12),
                    title_font_size=16,
                    xaxis_title="Rating",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading feedback analytics: {str(e)}")

    st.markdown("---")
    
def about_page():
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #c8d1db; font-size: 2rem; font-weight: 600;">About Elevate CV</h1>
    </div>
    """, unsafe_allow_html=True)

    # Features Section
    st.markdown("### Key Features")
    features = [
        ("Advanced AI Analysis", "Powered by LLaMA and DeepSeek models for accurate insights"),
        ("Smart Field Detection", "Auto-identifies 15+ career paths"),
        ("Comprehensive Resume Score", "ATS compatibility, readability & impact metrics"),
        ("Personalized Suggestions", "AI-tailored tips to enhance your profile"),
        ("Skills Gap Finder", "Detect missing skills vs target roles"),
        ("Career Market Trends", "Insights based on current hiring data"),
        ("AI Career Coach", "Chat with our AI for guidance & tips"),
        ("Professional Reports", "Get downloadable analysis PDFs")
    ]

    cols = st.columns(2)
    for i, (title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1.1rem; border-radius: 6px; border-left: 4px solid #1a3c61; margin: 0.6rem 0;">
                <h4 style="margin-bottom: 0.3rem; color: #2d3748; font-weight: 500;">{title}</h4>
                <p style="color: #4a5568; font-size: 0.9rem; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


    # Tech Stack
    st.markdown("### Technology Stack")
    tech_stack = [
        ("Frontend", "Streamlit + Custom CSS UI", "#1a3c61"),
        ("AI Models", "LLaMA 3.1, DeepSeek", "#16a34a"),
        ("Database", "MySQL (User, Analysis Data)", "#d97706"),
        ("NLP Engine", "Custom parsing and embedding pipelines", "#dc2626"),
        ("Security", "Token-auth & encrypted data handling", "#2c7a7b")
    ]
    for tech, desc, color in tech_stack:
        st.markdown(f"""
        <div style="background-color: #ffffff; border-left: 4px solid {color}; padding: 1rem 1.1rem; margin: 0.5rem 0; border-radius: 6px;">
            <strong style="color: {color};">{tech}</strong>: <span style="color: #4a5568;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)
    # Contact Section
    st.markdown("### Contact & Support")
    st.markdown("""
    <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 1.5rem; border-radius: 6px;">
        <h4 style="color: #2d3748;">Questions or Feedback?</h4>
        <p style="color: #4a5568;">Reach out via the Feedback tab in the sidebar. We're happy to help within 24 hours on business days.</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #4a5568; padding: 1.25rem;">
        <p style="margin: 0; font-size: 1rem;">Built with care using cutting-edge AI</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">© 2024 Elevate CV</p>
    </div>
    """, unsafe_allow_html=True)


# Utility functions
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        from pdfminer3.layout import LAParams, LTTextBox
        from pdfminer3.pdfpage import PDFPage
        from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer3.converter import TextConverter
        
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        
        # Reset file pointer
        pdf_file.seek(0)
        
        for page in PDFPage.get_pages(pdf_file, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        
        text = fake_file_handle.getvalue()
        converter.close()
        fake_file_handle.close()
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def show_pdf_preview(pdf_file):
    """Display PDF preview"""
    try:
        # Reset file pointer
        pdf_file.seek(0)
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_display = f'''
        <div style="border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
        </div>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")

if __name__ == '__main__':
    main()
