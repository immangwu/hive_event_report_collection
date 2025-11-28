
# Configuration for Streamlit Event Report App

# Quarter 1 Calendar Activities Data (from Image 2)
QUARTER_1_ACTIVITIES = {
    "Awareness Workshop: Entrepreneurship & Innovation as Career Opportunities": {
        "Level": "1 or 2",
        "Mode": "Offline/Online",
        "Key Outputs": "No. of participants; No. of ideas submitted",
        "KPIs": "≥60% students sensitized; ≥20 ideas/session; ≥25% new participants",
        "Weightage": 0.03
    },
    "My Story/ Motivational Expert Sessions by Successful innovators & Entrepreneurs": {
        "Level": "1 or 2",
        "Mode": "Offline/Online",
        "Key Outputs": "Attendance; Engagement",
        "KPIs": "≥80% feedback rating; ≥5 sessions/quarter",
        "Weightage": 0.04
    },
    "Boot camp on Problem Solving/Ideation": {
        "Level": "2 or 3",
        "Mode": "Offline/Online",
        "Key Outputs": "No. of solutions proposed; Diversity of fields",
        "KPIs": "≥10 multi-disciplinary teams formed",
        "Weightage": 0.05
    },
    "Workshop on AI and I4.0 Tools for Innovators and Entrepreneurs": {
        "Level": "1 or 2",
        "Mode": "Offline/Online",
        "Key Outputs": "Attendance; Engagement",
        "KPIs": "≥80% feedback rating; ≥5 sessions/quarter",
        "Weightage": 0.04
    },
    "IPR Basics for Innovators & Entrepreneurs": {
        "Level": "1 or 2",
        "Mode": "Offline/Online",
        "Key Outputs": "No. of attendees; No. registering for IP clinics",
        "KPIs": "≥30% express IP interest",
        "Weightage": 0.04
    },
    "Session on Achieving Problem –Solution Fit": {
        "Level": "1 or 2",
        "Mode": "Offline/Online",
        "Key Outputs": "No. of solutions proposed; Diversity of fields",
        "KPIs": "≥10 multi-disciplinary teams formed",
        "Weightage": 0.04
    },
    "Inter/Intra Institutional Hackathon/ Idea Challenge": {
        "Level": "3 or 4",
        "Mode": "Offline/Hybrid",
        "Key Outputs": "No. of entries; No. shortlisted; Rewards given",
        "KPIs": "≥50 entries; ≥10 ideas to next phase; Ideas deposited/updated in YUKTI Innovation Repository",
        "Weightage": 0.05
    },
    "Demo Day/ Idea Showcase": {
        "Level": "3 or 4",
        "Mode": "Offline/Hybrid",
        "Key Outputs": "No. of showcases; Mentorships linked",
        "KPIs": "≥20 PoCs demonstrated; ≥15 ideas mentored by experts",
        "Weightage": 0.05
    }
}

# Self-Driven Activity Options
PROGRAM_THEMES = [
    "IPR and Technology Transfer",
    "Innovation and Design Thinking",
    "Entrepreneurship and Startup",
    "Preincubation and Incubation Management"
]

ACTIVITY_LEADS = [
    "Institute Council",
    "Student Council"
]

LEVELS = ["Level 1", "Level 2", "Level 3", "Level 4"]

MODES_OF_DELIVERY = ["Online", "Offline", "Hybrid"]

# List of required documents for upload
REQUIRED_DOCUMENTS = [
    "Event SOP (Signed by Principal)",
    "Event Photos / Screenshots",
    "Event Invitation",
    "Event Poster",
    "Event Brochure",
    "Expenditure Statement & Bills",
    "Feedback Samples",
    "Attendance Sheet (with signatures)",
    "Google Form Registration Sheets",
    "Resource Person Profile / Speaker Profile",
    "Speaker Photo",
    "Topic Title",
    "Correspondence Mail with Resource Person",
    "Acceptance Letter/Mail from Resource Person",
    "Venue Booking & Approvals",
    "Invitation/Brochure for Sub-events",
    "Proof of Invitation to Speakers/VIPs",
    "Proof of Invitation to Nominees",
    "Promotion Activity Proof",
    "Communication to Newspaper",
    "Newspaper Publication Details",
    "Agenda",
    "Presentation Materials",
    "Report Summary",
    "Scoring Sheets (if applicable)",
    "Sample Questions (if applicable)",
    "MOC Details",
    "Sample Certificates",
    "Prize Winners Details",
    "Feedback Analysis",
    "Thanks Letter to Resource Person",
    "Payment Voucher",
    "Auditor Statement",
    "Outcomes by Conveners",
    "Website Upload Proof",
    "Copy for IQAC"
]

# SDG Goals
SDG_GOALS = [
    "SDG 1: No Poverty",
    "SDG 2: Zero Hunger",
    "SDG 3: Good Health and Well-being",
    "SDG 4: Quality Education",
    "SDG 5: Gender Equality",
    "SDG 6: Clean Water and Sanitation",
    "SDG 7: Affordable and Clean Energy",
    "SDG 8: Decent Work and Economic Growth",
    "SDG 9: Industry, Innovation and Infrastructure",
    "SDG 10: Reduced Inequality",
    "SDG 11: Sustainable Cities and Communities",
    "SDG 12: Responsible Consumption and Production",
    "SDG 13: Climate Action",
    "SDG 14: Life Below Water",
    "SDG 15: Life on Land",
    "SDG 16: Peace and Justice Strong Institutions",
    "SDG 17: Partnerships to achieve the Goal"
]

# Program Outcomes (NBA)
PROGRAM_OUTCOMES = [
    "PO1: Engineering Knowledge",
    "PO2: Problem Analysis",
    "PO3: Design/Development of Solutions",
    "PO4: Conduct Investigations of Complex Problems",
    "PO5: Modern Tool Usage",
    "PO6: The Engineer and Society",
    "PO7: Environment and Sustainability",
    "PO8: Ethics",
    "PO9: Individual and Team Work",
    "PO10: Communication",
    "PO11: Project Management and Finance",
    "PO12: Life-long Learning"
]

# --- Secrets / Configuration ---
# Keys are now loaded from .streamlit/secrets.toml or environment variables
import os
try:
    import streamlit as st
    # Accessing st.secrets might fail if not running via streamlit or if file missing
    # We use a safe access pattern
    secrets = st.secrets
except Exception:
    secrets = {}

def get_secret(key, default=""):
    # Try Streamlit secrets first
    if secrets and key in secrets:
        return secrets[key]
    # Fallback to environment variables
    return os.environ.get(key, default)

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
GOOGLE_SHEET_ID = get_secret("GOOGLE_SHEET_ID")
DRIVE_PARENT_FOLDER_ID = get_secret("DRIVE_PARENT_FOLDER_ID")

