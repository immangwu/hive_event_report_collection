"""
IIC Event Report Submission System
Advanced Streamlit Application for Institution's Innovation Council
Author: AI Assistant (IQ 140+)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from datetime import datetime, timedelta
import json
import io
import os
from typing import Dict, List, Tuple, Optional
import re
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from PIL import Image as PILImage

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Application configuration and constants"""
    
    # IIC Calendar Activities - Quarter 1
    Q1_ACTIVITIES = {
        "1": {
            "name": "Awareness Workshop: Entrepreneurship & Innovation as Career Opportunities",
            "level": "1 or 2",
            "mode": "Offline/Online",
            "outputs": ["No. of participants", "No. of ideas submitted"],
            "kpis": ["≥60% students sensitized", "≥20 ideas/session", "≥25% new participants"],
            "weightage": 0.03,
            "duration": "2-4 hours"
        },
        "2": {
            "name": "My Story/Motivational Expert Sessions by Successful Innovators & Entrepreneurs",
            "level": "1 or 2",
            "mode": "Offline/Online",
            "outputs": ["Attendance", "Engagement"],
            "kpis": ["≥80% feedback rating", "≥5 sessions/quarter"],
            "weightage": 0.04,
            "duration": "2-4 hours"
        },
        "3": {
            "name": "Boot camp on Problem Solving/Ideation",
            "level": "2 or 3",
            "mode": "Offline/Online",
            "outputs": ["No. of solutions proposed", "Diversity of fields"],
            "kpis": ["≥10 multidisciplinary teams formed"],
            "weightage": 0.05,
            "duration": "5-18 hours"
        },
        "4": {
            "name": "Workshop on AI and I4.0 Tools for Innovators and Entrepreneurs",
            "level": "1 or 2",
            "mode": "Offline/Online",
            "outputs": ["Attendance", "Engagement"],
            "kpis": ["≥80% feedback rating", "≥5 sessions/quarter"],
            "weightage": 0.04,
            "duration": "2-4 hours"
        },
        "5": {
            "name": "IPR Basics for Innovators & Entrepreneurs",
            "level": "1 or 2",
            "mode": "Offline/Online",
            "outputs": ["No. of attendees", "No. registering for IP clinics"],
            "kpis": ["≥30% express IP interest"],
            "weightage": 0.04,
            "duration": "2-4 hours"
        },
        "6": {
            "name": "Session on Achieving Problem-Solution Fit",
            "level": "1 or 2",
            "mode": "Offline/Online",
            "outputs": ["No. of solutions proposed", "Diversity of fields"],
            "kpis": ["≥10 multidisciplinary teams formed"],
            "weightage": 0.04,
            "duration": "2-4 hours"
        },
        "7": {
            "name": "Inter/Intra Institutional Hackathon/Idea Challenge",
            "level": "3 or 4",
            "mode": "Offline/Hybrid",
            "outputs": ["No. of entries", "No. shortlisted", "Rewards given"],
            "kpis": ["≥50 entries", "≥10 ideas to next phase", "Ideas deposited in YUKTI"],
            "weightage": 0.05,
            "duration": "9-18+ hours"
        },
        "8": {
            "name": "Demo Day/Idea Showcase",
            "level": "3 or 4",
            "mode": "Offline/Hybrid",
            "outputs": ["No. of showcases", "Mentorships linked"],
            "kpis": ["≥20 PoCs demonstrated", "≥15 ideas mentored by experts"],
            "weightage": 0.05,
            "duration": "9-18+ hours"
        }
    }
    
    # Program Themes
    PROGRAM_THEMES = [
        "IPR and Technology Transfer",
        "Innovation and Design Thinking",
        "Entrepreneurship and Startup",
        "Preincubation and Incubation Management"
    ]
    
    # Activity Lead Options
    ACTIVITY_LEAD = [
        "Institute Council",
        "Student Council"
    ]
    
    # Mode of Delivery
    DELIVERY_MODE = ["Online", "Offline", "Hybrid"]
    
    # Event Levels
    EVENT_LEVELS = {
        "Level 1": "Expert Talk, Mentoring Session, Exposure Visit (2-4 hours)",
        "Level 2": "Seminar, Workshop, Conference, Panel Discussion (5-8 hours)",
        "Level 3": "Boot Camp, Exhibition, Demo Day, Competition, Hackathon (9-18 hours)",
        "Level 4": "Challenge, Tech Fest, Extended Hackathon (>18 hours)"
    }
    
    # Required Documents
    REQUIRED_DOCUMENTS = [
        "Event SOP signed by Principal",
        "Event Photos/Online Screenshots",
        "Event Invitation",
        "Event Poster",
        "Event Brochure",
        "Expenditure Statement and Bills",
        "Feedback Samples",
        "Attendance Sheet with Signatures",
        "Google Form Registration Sheets",
        "Resource Person Profile"
    ]
    
    # Optional Documents
    OPTIONAL_DOCUMENTS = [
        "Letter/Correspondence with Resource Person",
        "Acceptance Letter from Resource Person",
        "Venue Booking Details",
        "Invitation Proof (Email)",
        "Promotion Activity Proof",
        "Newspaper Publication",
        "Presentation Materials",
        "Sample Certificates",
        "Prize Winners Details",
        "Feedback Analysis",
        "Thanks Letter to Resource Person",
        "Payment Voucher",
        "Auditor Statement"
    ]

# =============================================================================
# GOOGLE SERVICES INTEGRATION
# =============================================================================

class GoogleServicesManager:
    """Manages Google Sheets, Drive, and Gemini AI integration"""
    
    def __init__(self, credentials_dict: Dict, gemini_api_key: str):
        """Initialize Google Services"""
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        
        # Initialize Gemini AI
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def write_to_sheets(self, spreadsheet_id: str, range_name: str, values: List[List]) -> bool:
        """Write data to Google Sheets"""
        try:
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return True
        except Exception as e:
            st.error(f"Error writing to sheets: {str(e)}")
            return False
    
    def upload_to_drive(self, file_content, file_name: str, folder_id: str, mime_type: str) -> Optional[str]:
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            if isinstance(file_content, bytes):
                media = MediaIoBaseUpload(
                    io.BytesIO(file_content),
                    mimetype=mime_type,
                    resumable=True
                )
            else:
                media = MediaFileUpload(file_content, mimetype=mime_type, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return file.get('webViewLink')
        except Exception as e:
            st.error(f"Error uploading to Drive: {str(e)}")
            return None
    
    def generate_content_with_ai(self, prompt: str) -> str:
        """Generate content using Gemini AI"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating AI content: {str(e)}")
            return ""

# =============================================================================
# DATA MODELS
# =============================================================================

class EventData:
    """Data model for event information"""
    
    def __init__(self):
        self.activity_type = None
        self.calendar_activity = None
        self.program_theme = None
        self.activity_lead = None
        self.event_level = None
        self.event_title = None
        self.event_description = None
        self.start_date = None
        self.end_date = None
        self.duration_hours = None
        self.mode_of_delivery = None
        self.venue = None
        
        # Participants
        self.num_students = 0
        self.num_faculty = 0
        self.num_external_students = 0
        self.num_external_faculty = 0
        
        # Resource Persons
        self.resource_persons = []
        
        # Financials
        self.expenditure_items = []
        self.total_expenditure = 0
        
        # Outcomes
        self.objectives = None
        self.benefits = None
        self.outcomes = None
        self.feedback_received = False
        self.feedback_summary = None
        
        # KPIs
        self.kpi_achievements = {}
        
        # Documents
        self.documents = {}
        self.video_url = None
        self.photos = []
        
        # Remarks
        self.remarks = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'activity_type': self.activity_type,
            'calendar_activity': self.calendar_activity,
            'program_theme': self.program_theme,
            'activity_lead': self.activity_lead,
            'event_level': self.event_level,
            'event_title': self.event_title,
            'event_description': self.event_description,
            'start_date': str(self.start_date) if self.start_date else None,
            'end_date': str(self.end_date) if self.end_date else None,
            'duration_hours': self.duration_hours,
            'mode_of_delivery': self.mode_of_delivery,
            'venue': self.venue,
            'num_students': self.num_students,
            'num_faculty': self.num_faculty,
            'num_external_students': self.num_external_students,
            'num_external_faculty': self.num_external_faculty,
            'total_participants': self.num_students + self.num_faculty + self.num_external_students + self.num_external_faculty,
            'resource_persons': self.resource_persons,
            'total_expenditure': self.total_expenditure,
            'expenditure_items': self.expenditure_items,
            'objectives': self.objectives,
            'benefits': self.benefits,
            'outcomes': self.outcomes,
            'feedback_received': self.feedback_received,
            'feedback_summary': self.feedback_summary,
            'kpi_achievements': self.kpi_achievements,
            'video_url': self.video_url,
            'remarks': self.remarks
        }

# =============================================================================
# PDF REPORT GENERATOR
# =============================================================================

class PDFReportGenerator:
    """Generates professional PDF reports for IIC events"""
    
    def __init__(self, event_data: EventData):
        self.event_data = event_data
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def generate(self, output_path: str) -> bool:
        """Generate PDF report"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            story = []
            
            # Header
            story.append(Paragraph("INSTITUTION'S INNOVATION COUNCIL", self.styles['CustomTitle']))
            story.append(Paragraph("Event Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Event Details Section
            story.append(Paragraph("EVENT DETAILS", self.styles['CustomHeading']))
            event_details = [
                ["Event Title:", self.event_data.event_title or "N/A"],
                ["Activity Type:", self.event_data.activity_type or "N/A"],
                ["Program Theme:", self.event_data.program_theme or "N/A"],
                ["Event Level:", self.event_data.event_level or "N/A"],
                ["Mode of Delivery:", self.event_data.mode_of_delivery or "N/A"],
                ["Duration:", f"{self.event_data.duration_hours} hours" if self.event_data.duration_hours else "N/A"],
                ["Start Date:", str(self.event_data.start_date) if self.event_data.start_date else "N/A"],
                ["End Date:", str(self.event_data.end_date) if self.event_data.end_date else "N/A"],
                ["Venue:", self.event_data.venue or "N/A"],
            ]
            
            event_table = Table(event_details, colWidths=[2*inch, 4*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(event_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Objectives
            if self.event_data.objectives:
                story.append(Paragraph("OBJECTIVES", self.styles['CustomHeading']))
                story.append(Paragraph(self.event_data.objectives, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # Participants Section
            story.append(Paragraph("PARTICIPATION STATISTICS", self.styles['CustomHeading']))
            participant_data = [
                ["Category", "Count"],
                ["Internal Students", str(self.event_data.num_students)],
                ["Internal Faculty", str(self.event_data.num_faculty)],
                ["External Students", str(self.event_data.num_external_students)],
                ["External Faculty", str(self.event_data.num_external_faculty)],
                ["Total Participants", str(self.event_data.num_students + self.event_data.num_faculty + 
                                          self.event_data.num_external_students + self.event_data.num_external_faculty)]
            ]
            
            participant_table = Table(participant_data, colWidths=[3*inch, 2*inch])
            participant_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(participant_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Resource Persons
            if self.event_data.resource_persons:
                story.append(Paragraph("RESOURCE PERSONS", self.styles['CustomHeading']))
                for i, rp in enumerate(self.event_data.resource_persons, 1):
                    story.append(Paragraph(f"<b>{i}. {rp['name']}</b>", self.styles['CustomBody']))
                    story.append(Paragraph(f"Designation: {rp['designation']}", self.styles['CustomBody']))
                    story.append(Paragraph(f"Organization: {rp['organization']}", self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Expenditure Section
            if self.event_data.expenditure_items:
                story.append(PageBreak())
                story.append(Paragraph("EXPENDITURE STATEMENT", self.styles['CustomHeading']))
                
                exp_data = [["S.No", "Particular", "Amount (₹)"]]
                for i, item in enumerate(self.event_data.expenditure_items, 1):
                    exp_data.append([str(i), item['particular'], f"₹{item['amount']:,.2f}"])
                exp_data.append(["", "Total", f"₹{self.event_data.total_expenditure:,.2f}"])
                
                exp_table = Table(exp_data, colWidths=[0.7*inch, 3.5*inch, 1.5*inch])
                exp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(exp_table)
                story.append(Spacer(1, 0.3*inch))
            
            # Benefits & Outcomes
            if self.event_data.benefits:
                story.append(Paragraph("BENEFITS & LEARNING OUTCOMES", self.styles['CustomHeading']))
                story.append(Paragraph(self.event_data.benefits, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            if self.event_data.outcomes:
                story.append(Paragraph("EVENT OUTCOMES", self.styles['CustomHeading']))
                story.append(Paragraph(self.event_data.outcomes, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # KPI Achievements
            if self.event_data.kpi_achievements:
                story.append(Paragraph("KPI ACHIEVEMENTS", self.styles['CustomHeading']))
                for kpi, achievement in self.event_data.kpi_achievements.items():
                    story.append(Paragraph(f"<b>{kpi}:</b> {achievement}", self.styles['CustomBody']))
            
            # Feedback
            if self.event_data.feedback_received and self.event_data.feedback_summary:
                story.append(Paragraph("FEEDBACK SUMMARY", self.styles['CustomHeading']))
                story.append(Paragraph(self.event_data.feedback_summary, self.styles['CustomBody']))
            
            # Remarks
            if self.event_data.remarks:
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("REMARKS", self.styles['CustomHeading']))
                story.append(Paragraph(self.event_data.remarks, self.styles['CustomBody']))
            
            # Signature Section
            story.append(Spacer(1, 0.5*inch))
            signature_data = [
                ["", ""],
                ["_____________________", "_____________________"],
                ["Faculty Coordinator", "Principal"],
                ["Date: _______________", "Date: _______________"]
            ]
            signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(signature_table)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return False

# =============================================================================
# STREAMLIT UI COMPONENTS
# =============================================================================

class StreamlitUI:
    """Manages Streamlit UI components"""
    
    @staticmethod
    def setup_page():
        """Setup page configuration"""
        st.set_page_config(
            page_title="IIC Event Report System",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1a237e;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #283593;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #3f51b5;
            padding-bottom: 0.5rem;
        }
        .info-box {
            background-color: #e8eaf6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #3f51b5;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #e8f5e9;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #4caf50;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: #fff3e0;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ff9800;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Render application header"""
        st.markdown('<h1 class="main-header">🎓 IIC Event Report Submission System</h1>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Ministry of Education\'s Innovation Cell - Institution\'s Innovation Council</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_activity_type_selection() -> str:
        """Render activity type selection"""
        st.markdown('<h2 class="sub-header">📋 Activity Type Selection</h2>', unsafe_allow_html=True)
        
        activity_type = st.radio(
            "Select Activity Type:",
            ["IIC Calendar Driven Activity - Quarter 1", "Self Driven Activity"],
            help="Choose whether this is a prescribed IIC calendar activity or a self-initiated activity"
        )
        
        return activity_type
    
    @staticmethod
    def render_calendar_activity_form(google_services: GoogleServicesManager) -> Optional[EventData]:
        """Render form for calendar activities"""
        event_data = EventData()
        event_data.activity_type = "IIC Calendar Driven Activity"
        
        st.markdown('<h2 class="sub-header">📅 Calendar Activity Details</h2>', unsafe_allow_html=True)
        
        # Activity Selection
        activity_options = {k: v["name"] for k, v in Config.Q1_ACTIVITIES.items()}
        selected_activity_key = st.selectbox(
            "Select Calendar Activity:",
            options=list(activity_options.keys()),
            format_func=lambda x: f"{x}. {activity_options[x]}"
        )
        
        activity_info = Config.Q1_ACTIVITIES[selected_activity_key]
        event_data.calendar_activity = activity_info["name"]
        event_data.event_level = activity_info["level"]
        
        # Display Activity Information
        with st.expander("📊 Activity Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Level:** {activity_info['level']}")
                st.info(f"**Mode:** {activity_info['mode']}")
                st.info(f"**Duration:** {activity_info['duration']}")
            with col2:
                st.info(f"**Weightage:** {activity_info['weightage']}")
                st.success("**Key Outputs:**\n" + "\n".join([f"• {o}" for o in activity_info['outputs']]))
        
        with st.expander("🎯 KPIs to Achieve", expanded=True):
            for kpi in activity_info['kpis']:
                st.warning(f"✓ {kpi}")
        
                                                       value=4)
        
        with col2:
            event_data.mode_of_delivery = st.selectbox("Mode of Delivery*", 
                                                       activity_info['mode'].split('/'))
            event_data.end_date = st.date_input("End Date*")
            event_data.venue = st.text_input("Venue*", 
                                           placeholder="Online/Offline venue details")
        
        event_data.event_description = st.text_area("Event Description*", 
                                                    height=150,
                                                    placeholder="Detailed description of the event...")
        
        # Activity Lead
        event_data.activity_lead = st.radio("Activity Led By*", Config.ACTIVITY_LEAD, horizontal=True)
        
        # Participants
        st.markdown('<h3 class="sub-header">👥 Participant Details</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            event_data.num_students = st.number_input("Internal Students", min_value=0, value=0)
        with col2:
            event_data.num_faculty = st.number_input("Internal Faculty", min_value=0, value=0)
        with col3:
            event_data.num_external_students = st.number_input("External Students", min_value=0, value=0)
        with col4:
            event_data.num_external_faculty = st.number_input("External Faculty", min_value=0, value=0)
        
        total_participants = (event_data.num_students + event_data.num_faculty + 
                            event_data.num_external_students + event_data.num_external_faculty)
        st.success(f"**Total Participants:** {total_participants}")
        
        # Resource Persons
        st.markdown('<h3 class="sub-header">🎤 Resource Person(s) Details</h3>', unsafe_allow_html=True)
        
        num_resource_persons = st.number_input("Number of Resource Persons", min_value=1, max_value=10, value=1)
        
        for i in range(num_resource_persons):
            with st.expander(f"Resource Person {i+1}", expanded=(i==0)):
                col1, col2 = st.columns(2)
                with col1:
                    rp_name = st.text_input(f"Name*", key=f"rp_name_{i}")
                    rp_designation = st.text_input(f"Designation*", key=f"rp_designation_{i}")
                with col2:
                    rp_organization = st.text_input(f"Organization*", key=f"rp_organization_{i}")
                    rp_email = st.text_input(f"Email", key=f"rp_email_{i}")
                
                rp_bio = st.text_area(f"Brief Profile", key=f"rp_bio_{i}", height=100)
                
                if rp_name and rp_designation and rp_organization:
                    event_data.resource_persons.append({
                        'name': rp_name,
                        'designation': rp_designation,
                        'organization': rp_organization,
                        'email': rp_email,
                        'bio': rp_bio
                    })
        
        # KPI Achievement Tracking
        st.markdown('<h3 class="sub-header">📊 KPI Achievement Tracking</h3>', unsafe_allow_html=True)
        
        for i, kpi in enumerate(activity_info['kpis']):
            event_data.kpi_achievements[kpi] = st.text_input(
                f"Achievement for: {kpi}*",
                key=f"kpi_{i}",
                placeholder="Describe how this KPI was achieved..."
            )
        
        # Measure Key Outputs
        st.markdown('<h3 class="sub-header">📈 Key Outputs Measurement</h3>', unsafe_allow_html=True)
        
        for output in activity_info['outputs']:
            st.text_input(f"{output}*", key=f"output_{output}")
        
        # Expenditure Statement
        st.markdown('<h3 class="sub-header">💰 Expenditure Statement</h3>', unsafe_allow_html=True)
        
        num_expenditure_items = st.number_input("Number of Expenditure Items", 
                                               min_value=1, 
                                               max_value=50, 
                                               value=1)
        
        event_data.expenditure_items = []
        event_data.total_expenditure = 0
        
        for i in range(num_expenditure_items):
            col1, col2 = st.columns([3, 1])
            with col1:
                particular = st.text_input(f"Particular {i+1}*", key=f"exp_particular_{i}",
                                          placeholder="Description of expense")
            with col2:
                amount = st.number_input(f"Amount (₹)*", min_value=0.0, key=f"exp_amount_{i}",
                                       format="%.2f")
            
            if particular and amount > 0:
                event_data.expenditure_items.append({
                    'particular': particular,
                    'amount': amount
                })
                event_data.total_expenditure += amount
        
        st.success(f"**Total Expenditure: ₹{event_data.total_expenditure:,.2f}**")
        
        # AI-Generated Content
        st.markdown('<h3 class="sub-header">🤖 AI-Generated Content</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Generate Objectives", use_container_width=True):
                with st.spinner("Generating objectives..."):
                    prompt = f"""Generate comprehensive and professional objectives for the following IIC event:
                    
Event: {event_data.event_title}
Description: {event_data.event_description}
Activity Type: {activity_info['name']}
Target Participants: {total_participants} participants
Duration: {event_data.duration_hours} hours

Generate 4-6 SMART objectives that align with IIC's mission of fostering innovation and entrepreneurship."""
                    
                    event_data.objectives = google_services.generate_content_with_ai(prompt)
                    st.session_state['generated_objectives'] = event_data.objectives
        
        with col2:
            if st.button("💡 Generate Benefits & Learning Outcomes", use_container_width=True):
                with st.spinner("Generating benefits..."):
                    prompt = f"""Generate comprehensive learning benefits and outcomes for the following IIC event:
                    
Event: {event_data.event_title}
Description: {event_data.event_description}
Participants: {total_participants} (Students: {event_data.num_students}, Faculty: {event_data.num_faculty})
Duration: {event_data.duration_hours} hours

Generate detailed benefits in terms of:
1. Knowledge Gained
2. Skills Developed
3. Network Opportunities
4. Innovation Mindset
5. Career Opportunities"""
                    
                    event_data.benefits = google_services.generate_content_with_ai(prompt)
                    st.session_state['generated_benefits'] = event_data.benefits
        
        # Display generated content
        if 'generated_objectives' in st.session_state:
            event_data.objectives = st.text_area("Event Objectives*", 
                                                value=st.session_state['generated_objectives'],
                                                height=200,
                                                help="You can edit the AI-generated objectives")
        else:
            event_data.objectives = st.text_area("Event Objectives*", 
                                                height=200,
                                                placeholder="Objectives will be generated or enter manually...")
        
        if 'generated_benefits' in st.session_state:
            event_data.benefits = st.text_area("Benefits & Learning Outcomes*", 
                                              value=st.session_state['generated_benefits'],
                                              height=200,
                                              help="You can edit the AI-generated benefits")
        else:
            event_data.benefits = st.text_area("Benefits & Learning Outcomes*", 
                                              height=200,
                                              placeholder="Benefits will be generated or enter manually...")
        
        # Outcomes Report
        if st.button("📋 Generate Overall Event Outcomes Report", use_container_width=True):
            with st.spinner("Generating comprehensive outcomes report..."):
                prompt = f"""Generate a comprehensive event outcomes report for the following IIC activity:

Event Title: {event_data.event_title}
Activity Type: {activity_info['name']}
Date: {event_data.start_date} to {event_data.end_date}
Duration: {event_data.duration_hours} hours
Mode: {event_data.mode_of_delivery}
Total Participants: {total_participants}

Objectives Achieved:
{event_data.objectives}

Benefits Delivered:
{event_data.benefits}

KPI Achievements:
{json.dumps(event_data.kpi_achievements, indent=2)}

Resource Persons: {len(event_data.resource_persons)} expert(s)

Generate a professional outcomes report covering:
1. Executive Summary
2. Event Execution Summary
3. Participant Engagement Analysis
4. Key Achievements
5. Impact Assessment
6. Recommendations for Future Events
7. Conclusion

Make it suitable for institutional records and MoE reporting."""
                
                event_data.outcomes = google_services.generate_content_with_ai(prompt)
                st.session_state['generated_outcomes'] = event_data.outcomes
        
        if 'generated_outcomes' in st.session_state:
            event_data.outcomes = st.text_area("Overall Event Outcomes*", 
                                              value=st.session_state['generated_outcomes'],
                                              height=300,
                                              help="You can edit the AI-generated outcomes report")
        
        # Feedback
        st.markdown('<h3 class="sub-header">📝 Feedback</h3>', unsafe_allow_html=True)
        
        event_data.feedback_received = st.checkbox("Was feedback received from participants?")
        
        if event_data.feedback_received:
            event_data.feedback_summary = st.text_area("Feedback Summary*", 
                                                       height=150,
                                                       placeholder="Summarize the feedback received...")
        
        # Remarks
        event_data.remarks = st.text_area("Additional Remarks", 
                                         height=100,
                                         placeholder="Any additional remarks or observations...")
        
        # Documents Upload
        st.markdown('<h3 class="sub-header">📎 Document Uploads</h3>', unsafe_allow_html=True)
        
        # Required Documents
        st.markdown("##### Required Documents")
        for doc in Config.REQUIRED_DOCUMENTS:
            uploaded_file = st.file_uploader(f"{doc}*", 
                                           key=f"req_doc_{doc}",
                                           help=f"Upload {doc}")
            if uploaded_file:
                event_data.documents[doc] = uploaded_file
        
        # Optional Documents
        with st.expander("Optional Documents"):
            for doc in Config.OPTIONAL_DOCUMENTS:
                uploaded_file = st.file_uploader(f"{doc}", 
                                               key=f"opt_doc_{doc}")
                if uploaded_file:
                    event_data.documents[doc] = uploaded_file
        
        # Photos
        st.markdown("##### Event Photographs")
        photo1 = st.file_uploader("Photograph 1*", type=['jpg', 'jpeg', 'png'], key="photo1")
        photo2 = st.file_uploader("Photograph 2*", type=['jpg', 'jpeg', 'png'], key="photo2")
        
        if photo1:
            event_data.photos.append(photo1)
        if photo2:
            event_data.photos.append(photo2)
        
        # Video URL (Optional)
        event_data.video_url = st.text_input("Event Video URL (Optional)", 
                                            placeholder="https://youtube.com/...")
        
        return event_data
    
    @staticmethod
    def render_self_driven_activity_form(google_services: GoogleServicesManager) -> Optional[EventData]:
        """Render form for self-driven activities"""
        event_data = EventData()
        event_data.activity_type = "Self Driven Activity"
        
        st.markdown('<h2 class="sub-header">🚀 Self Driven Activity Details</h2>', unsafe_allow_html=True)
        
        # Program Theme
        col1, col2 = st.columns(2)
        with col1:
            event_data.program_theme = st.selectbox("Program Theme*", Config.PROGRAM_THEMES)
            event_data.event_level = st.selectbox("Event Level*", list(Config.EVENT_LEVELS.keys()),
                                                  format_func=lambda x: f"{x}: {Config.EVENT_LEVELS[x]}")
        
        with col2:
            event_data.activity_lead = st.radio("Activity Led By*", Config.ACTIVITY_LEAD)
            event_data.mode_of_delivery = st.selectbox("Mode of Delivery*", Config.DELIVERY_MODE)
        
        # Event Details
        st.markdown('<h3 class="sub-header">📝 Event Details</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            event_data.event_title = st.text_input("Event Title*")
            event_data.start_date = st.date_input("Start Date*")
            event_data.duration_hours = st.number_input("Duration (hours)*", min_value=1, max_value=72)
        
        with col2:
            event_data.venue = st.text_input("Venue*")
            event_data.end_date = st.date_input("End Date*")
        
        event_data.event_description = st.text_area("Event Description*", height=150)
        
        # Participants
        st.markdown('<h3 class="sub-header">👥 Participant Details</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            event_data.num_students = st.number_input("Internal Students", min_value=0, value=0)
        with col2:
            event_data.num_faculty = st.number_input("Internal Faculty", min_value=0, value=0)
        with col3:
            event_data.num_external_students = st.number_input("External Students", min_value=0, value=0)
        with col4:
            event_data.num_external_faculty = st.number_input("External Faculty", min_value=0, value=0)
        
        # Resource Persons (same as calendar activity)
        st.markdown('<h3 class="sub-header">🎤 Resource Person(s) Details</h3>', unsafe_allow_html=True)
        
        num_resource_persons = st.number_input("Number of Resource Persons", min_value=0, max_value=10, value=1)
        
        for i in range(num_resource_persons):
            with st.expander(f"Resource Person {i+1}", expanded=(i==0)):
                col1, col2 = st.columns(2)
                with col1:
                    rp_name = st.text_input(f"Name*", key=f"sd_rp_name_{i}")
                    rp_designation = st.text_input(f"Designation*", key=f"sd_rp_designation_{i}")
                with col2:
                    rp_organization = st.text_input(f"Organization*", key=f"sd_rp_organization_{i}")
                    rp_email = st.text_input(f"Email", key=f"sd_rp_email_{i}")
                
                if rp_name and rp_designation and rp_organization:
                    event_data.resource_persons.append({
                        'name': rp_name,
                        'designation': rp_designation,
                        'organization': rp_organization,
                        'email': rp_email
                    })
        
        # Expenditure (same structure)
        st.markdown('<h3 class="sub-header">💰 Expenditure Statement</h3>', unsafe_allow_html=True)
        
        num_expenditure_items = st.number_input("Number of Expenditure Items", 
                                               min_value=1, max_value=50, value=1)
        
        event_data.expenditure_items = []
        event_data.total_expenditure = 0
        
        for i in range(num_expenditure_items):
            col1, col2 = st.columns([3, 1])
            with col1:
                particular = st.text_input(f"Particular {i+1}*", key=f"sd_exp_particular_{i}")
            with col2:
                amount = st.number_input(f"Amount (₹)*", min_value=0.0, key=f"sd_exp_amount_{i}", format="%.2f")
            
            if particular and amount > 0:
                event_data.expenditure_items.append({'particular': particular, 'amount': amount})
                event_data.total_expenditure += amount
        
        st.success(f"**Total Expenditure: ₹{event_data.total_expenditure:,.2f}**")
        
        # AI-Generated Content (same as calendar)
        st.markdown('<h3 class="sub-header">🤖 AI-Generated Content</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Generate Objectives", key="sd_gen_obj", use_container_width=True):
                with st.spinner("Generating objectives..."):
                    prompt = f"""Generate professional objectives for this IIC self-driven activity:
Event: {event_data.event_title}
Theme: {event_data.program_theme}
Level: {event_data.event_level}
Description: {event_data.event_description}

Generate 4-6 SMART objectives."""
                    event_data.objectives = google_services.generate_content_with_ai(prompt)
                    st.session_state['sd_generated_objectives'] = event_data.objectives
        
        with col2:
            if st.button("💡 Generate Benefits", key="sd_gen_ben", use_container_width=True):
                with st.spinner("Generating benefits..."):
                    prompt = f"""Generate learning benefits for:
Event: {event_data.event_title}
Theme: {event_data.program_theme}
Level: {event_data.event_level}

Cover: Knowledge, Skills, Innovation Mindset, Career Opportunities."""
                    event_data.benefits = google_services.generate_content_with_ai(prompt)
                    st.session_state['sd_generated_benefits'] = event_data.benefits
        
        # Text areas for AI content
        event_data.objectives = st.text_area("Event Objectives*", 
                                            value=st.session_state.get('sd_generated_objectives', ''),
                                            height=200)
        
        event_data.benefits = st.text_area("Benefits & Learning Outcomes*", 
                                          value=st.session_state.get('sd_generated_benefits', ''),
                                          height=200)
        
        # Overall outcomes
        if st.button("📋 Generate Overall Report", key="sd_gen_report", use_container_width=True):
            with st.spinner("Generating report..."):
                total_participants = (event_data.num_students + event_data.num_faculty + 
                                    event_data.num_external_students + event_data.num_external_faculty)
                
                prompt = f"""Generate comprehensive outcomes report:
Event: {event_data.event_title}
Theme: {event_data.program_theme}
Level: {event_data.event_level}
Participants: {total_participants}
Objectives: {event_data.objectives}
Benefits: {event_data.benefits}

Include: Summary, Execution, Engagement, Achievements, Impact, Recommendations."""
                
                event_data.outcomes = google_services.generate_content_with_ai(prompt)
                st.session_state['sd_generated_outcomes'] = event_data.outcomes
        
        event_data.outcomes = st.text_area("Overall Event Outcomes*", 
                                          value=st.session_state.get('sd_generated_outcomes', ''),
                                          height=300)
        
        # Feedback
        st.markdown('<h3 class="sub-header">📝 Feedback</h3>', unsafe_allow_html=True)
        event_data.feedback_received = st.checkbox("Was feedback received?")
        if event_data.feedback_received:
            event_data.feedback_summary = st.text_area("Feedback Summary*", height=150)
        
        # Remarks
        event_data.remarks = st.text_area("Additional Remarks", height=100)
        
        # Documents (same structure)
        st.markdown('<h3 class="sub-header">📎 Document Uploads</h3>', unsafe_allow_html=True)
        
        st.markdown("##### Required Documents")
        for doc in Config.REQUIRED_DOCUMENTS:
            uploaded_file = st.file_uploader(f"{doc}*", key=f"sd_req_doc_{doc}")
            if uploaded_file:
                event_data.documents[doc] = uploaded_file
        
        with st.expander("Optional Documents"):
            for doc in Config.OPTIONAL_DOCUMENTS:
                uploaded_file = st.file_uploader(f"{doc}", key=f"sd_opt_doc_{doc}")
                if uploaded_file:
                    event_data.documents[doc] = uploaded_file
        
        # Photos
        st.markdown("##### Event Photographs")
        photo1 = st.file_uploader("Photograph 1*", type=['jpg', 'jpeg', 'png'], key="sd_photo1")
        photo2 = st.file_uploader("Photograph 2*", type=['jpg', 'jpeg', 'png'], key="sd_photo2")
        
        if photo1:
            event_data.photos.append(photo1)
        if photo2:
            event_data.photos.append(photo2)
        
        event_data.video_url = st.text_input("Event Video URL (Optional)", 
                                            placeholder="https://youtube.com/...",
                                            key="sd_video_url")
        
        return event_data

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    
    # Setup
    StreamlitUI.setup_page()
    StreamlitUI.render_header()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google Gemini API Key
    # Activity Type Selection
    activity_type = StreamlitUI.render_activity_type_selection()
    
    # Render appropriate form
    event_data = None
    
    if "Calendar" in activity_type:
        event_data = StreamlitUI.render_calendar_activity_form(google_services)
    else:
        event_data = StreamlitUI.render_self_driven_activity_form(google_services)
    
    # Submit Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📤 Submit Event Report", type="primary", use_container_width=True):
            if event_data:
                with st.spinner("Processing submission..."):
                    # Validate required fields
                    if not event_data.event_title or not event_data.start_date:
                        st.error("❌ Please fill in all required fields marked with *")
                        return
                    
                    # Generate PDF Report
                    pdf_filename = f"IIC_Event_Report_{event_data.event_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf_path = f"/home/claude/{pdf_filename}"
                    
                    pdf_generator = PDFReportGenerator(event_data)
                    if pdf_generator.generate(pdf_path):
                        st.success("✅ PDF report generated successfully!")
                        
                        # Upload PDF to Google Drive
                        with open(pdf_path, 'rb') as f:
                            pdf_url = google_services.upload_to_drive(
                                f.read(),
                                pdf_filename,
                                drive_folder_id,
                                'application/pdf'
                            )
                        
                        if pdf_url:
                            st.success(f"✅ PDF uploaded to Google Drive: [View Report]({pdf_url})")
                        
                        # Upload documents to Google Drive
                        document_urls = {}
                        for doc_name, doc_file in event_data.documents.items():
                            doc_url = google_services.upload_to_drive(
                                doc_file.getvalue(),
                                f"{event_data.event_title}_{doc_name}_{doc_file.name}",
                                drive_folder_id,
                                doc_file.type
                            )
                            if doc_url:
                                document_urls[doc_name] = doc_url
                        
                        # Upload photos
                        photo_urls = []
                        for i, photo in enumerate(event_data.photos, 1):
                            photo_url = google_services.upload_to_drive(
                                photo.getvalue(),
                                f"{event_data.event_title}_Photo_{i}_{photo.name}",
                                drive_folder_id,
                                photo.type
                            )
                            if photo_url:
                                photo_urls.append(photo_url)
                        
                        # Prepare data for Google Sheets
                        sheet_data = [
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            event_data.activity_type,
                            event_data.calendar_activity or "N/A",
                            event_data.program_theme or "N/A",
                            event_data.event_level,
                            event_data.event_title,
                            str(event_data.start_date),
                            str(event_data.end_date),
                            event_data.duration_hours,
                            event_data.mode_of_delivery,
                            event_data.venue,
                            event_data.activity_lead or "N/A",
                            event_data.num_students,
                            event_data.num_faculty,
                            event_data.num_external_students,
                            event_data.num_external_faculty,
                            event_data.num_students + event_data.num_faculty + event_data.num_external_students + event_data.num_external_faculty,
                            len(event_data.resource_persons),
                            json.dumps([rp['name'] for rp in event_data.resource_persons]),
                            event_data.total_expenditure,
                            event_data.objectives or "N/A",
                            event_data.benefits or "N/A",
                            event_data.outcomes or "N/A",
                            event_data.feedback_received,
                            event_data.feedback_summary or "N/A",
                            json.dumps(event_data.kpi_achievements),
                            pdf_url or "N/A",
                            json.dumps(document_urls),
                            json.dumps(photo_urls),
                            event_data.video_url or "N/A",
                            event_data.remarks or "N/A"
                        ]
                        
                        # Write to Google Sheets
                        if google_services.write_to_sheets(spreadsheet_id, f"{sheet_name}!A:AE", [sheet_data]):
                            st.success("✅ Data written to Google Sheets successfully!")
                            
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 🎉 Submission Successful!")
                            st.markdown(f"""
                            Your event report has been submitted successfully!
                            
                            **Next Steps:**
                            1. Download the PDF report for principal's signature
                            2. Upload the signed PDF back to the system
                            3. Submit to IQAC for final approval
                            
                            **Report Details:**
                            - Event: {event_data.event_title}
                            - Date: {event_data.start_date}
                            - Participants: {event_data.num_students + event_data.num_faculty + event_data.num_external_students + event_data.num_external_faculty}
                            """)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Provide download link for PDF
                            with open(pdf_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download PDF Report",
                                    data=f,
                                    file_name=pdf_filename,
                                    mime='application/pdf',
                                    use_container_width=True
                                )
                        else:
                            st.error("❌ Error writing to Google Sheets")
                    else:
                        st.error("❌ Error generating PDF report")

if __name__ == "__main__":
    main()
