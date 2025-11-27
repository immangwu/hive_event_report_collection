import os
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import io
import pickle
import tempfile
from pypdf import PdfWriter, PdfReader
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# --- Google Services Setup ---
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_services(client_secret_path='client_secret.json'):
    """Authenticates using OAuth 2.0 User Credentials."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                return None, None
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

# --- Gemini Integration ---
def generate_ai_content(api_key, prompt):
    """Generates content using Google Gemini."""
    if not api_key:
        return "Error: API Key missing."
    
    try:
        genai.configure(api_key=api_key)
        # Trying a specific version that is widely available
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def analyze_rough_input(api_key, text_input=None, audio_file=None):
    """
    Analyzes rough text or audio notes using Gemini to extract event details.
    Returns a JSON-like dictionary string.
    """
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = """
    Extract the following details from the input and return them in this EXACT JSON format:
    {
        "Program Name": "",
        "Theme": "",
        "Level": "",
        "Start Date": "YYYY-MM-DD",
        "End Date": "YYYY-MM-DD",
        "Duration": 0.0,
        "Student Participants": 0,
        "Faculty Participants": 0,
        "External Students": 0,
        "External Faculty": 0,
        "Objective": "",
        "Benefits": ""
    }
    If a value is not mentioned, leave it empty or 0.
    """

    content = [prompt]
    
    if text_input:
        content.append(f"NOTES: {text_input}")
    
    if audio_file:
        # Read audio bytes
        audio_bytes = audio_file.read()
        content.append({
            "mime_type": audio_file.type,
            "data": audio_bytes
        })

    try:
        response = model.generate_content(content)
        text = response.text
        # Clean up code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text
    except Exception as e:
        return f"Error analyzing input: {str(e)}"

def create_event_charts(data):
    """
    Generates charts for the event report using Matplotlib.
    Returns a list of paths to the generated chart images.
    """
    chart_paths = []
    
    try:
        # 1. Participation Pie Chart
        labels = ['Students', 'Faculty', 'Ext. Students', 'Ext. Faculty']
        sizes = [
            data.get('Student Participants', 0),
            data.get('Faculty Participants', 0),
            data.get('External Students', 0),
            data.get('External Faculty', 0)
        ]
        
        # Filter out zero values
        labels = [l for l, s in zip(labels, sizes) if s > 0]
        sizes = [s for s in sizes if s > 0]
        
        if sizes:
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
            plt.title('Participation Distribution')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                plt.savefig(tmp.name)
                chart_paths.append(tmp.name)
            plt.close()

        # 2. Ratings Bar Chart
        ratings = {
            'Planning': data.get('Plan Rating', 0),
            'Execution': data.get('Exec Rating', 0),
            'Speaker': data.get('Speak Rating', 0),
            'Learning': data.get('Learn Rating', 0),
            'Innovation': data.get('Innov Rating', 0)
        }
        
        categories = list(ratings.keys())
        scores = list(ratings.values())
        
        if any(scores):
            plt.figure(figsize=(8, 5))
            plt.bar(categories, scores, color='#6366F1')
            plt.ylim(0, 5.5)
            plt.ylabel('Rating (1-5)')
            plt.title('Event Assessment Ratings')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                plt.savefig(tmp.name)
                chart_paths.append(tmp.name)
            plt.close()
            
    except Exception as e:
        print(f"Error generating charts: {e}")
        
    return chart_paths

def generate_professional_report(api_key, data, minute_to_minute):
    """
    Generates a professional event report summary using Gemini.
    """
    if not api_key:
        return "Error: API Key missing."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an expert academic report writer. Write a professional "Event Report Summary" for the following event.
    
    Event Details:
    - Name: {data.get('Program Name')}
    - Date: {data.get('Start Date')}
    - Theme: {data.get('Program Theme')}
    - Objective: {data.get('Objective')}
    - Key Outcomes: {data.get('Benefits')}
    
    Minute-to-Minute Flow / Highlights:
    {minute_to_minute}
    
    Student Feedback Highlights:
    - Top Liked: {data.get('Top Liked')}
    - Areas to Improve: {data.get('Top Improve')}
    
    Organizer's Assessment:
    - Success Story: {data.get('Success Story')}
    - Best Thing: {data.get('Best Thing')}
    
    Instructions:
    1. Write a cohesive, professional narrative (approx. 300-400 words).
    2. Structure it with clear headings: "Introduction", "Event Highlights", "Key Outcomes", and "Conclusion".
    3. Use professional tone suitable for submission to higher authorities (e.g., AICTE, IIC).
    4. Do NOT use markdown formatting (like **bold** or # headings) in the output, just plain text with paragraph breaks.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"

# --- Google Drive Functions ---
def create_drive_folder(drive_service, folder_name, parent_id):
    """Creates a new folder in Google Drive."""
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    except Exception as e:
        print(f"Error creating folder: {e}")
        return None

def upload_to_drive(drive_service, file_obj, filename, folder_id, mimetype=None):
    """Uploads a file to Google Drive."""
    try:
        from googleapiclient.http import MediaIoBaseUpload
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        if mimetype is None:
            if hasattr(file_obj, 'type'):
                mimetype = file_obj.type
            else:
                mimetype = 'application/octet-stream'
                
        media = MediaIoBaseUpload(file_obj, mimetype=mimetype, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

# --- Google Sheets Integration ---
def append_to_sheet(sheets_service, spreadsheet_id, values):
    """Appends a row of data to Google Sheets."""
    try:
        body = {
            'values': [values]
        }
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range="Sheet1!A1",
            valueInputOption="USER_ENTERED", body=body).execute()
        return result
    except Exception as e:
        return f"Sheet Log Failed: {str(e)}"

# --- PDF Generation ---
def sanitize_image(image_path):
    """
    Converts an image to a safe PNG format using Pillow to avoid FPDF errors.
    Returns the path to the temporary sanitized image.
    """
    try:
        img = Image.open(image_path)
        # Convert to RGB to avoid transparency issues or mode mismatches
        img = img.convert('RGB')
        
        # Save to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            img.save(tmp.name, "PNG")
            return tmp.name
    except Exception as e:
        print(f"Error sanitizing image {image_path}: {e}")
        return None

class ProfessionalPDF(FPDF):
    def header(self):
        # --- Row 1: SNR Logo | Text | SRIT Logo ---
        # SNR Logo (Left)
        snr_path = "logos/snr_logo.png"
        if os.path.exists(snr_path):
            safe_snr = sanitize_image(snr_path)
            if safe_snr:
                self.image(safe_snr, 10, 8, 25)
        else:
            # Placeholder if missing
            self.set_font("Arial", "I", 8)
            self.rect(10, 8, 25, 25)
            self.text(12, 20, "SNR Logo")

        # SRIT Logo (Right)
        srit_path = "logos/srit_logo.png"
        if os.path.exists(srit_path):
            safe_srit = sanitize_image(srit_path)
            if safe_srit:
                self.image(safe_srit, 175, 8, 25)
        else:
            # Placeholder
            self.rect(175, 8, 25, 25)
            self.text(177, 20, "SRIT Logo")

        # Center Text
        self.set_y(10)
        self.set_font("Arial", "B", 14)
        self.cell(0, 5, "SRI RAMAKRISHNA INSTITUTE OF TECHNOLOGY", 0, 1, "C")
        self.set_font("Arial", "B", 12)
        self.cell(0, 5, "COIMBATORE-10", 0, 1, "C")
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "(An Autonomous Institution)", 0, 1, "C")
        self.set_font("Arial", "", 8)
        self.cell(0, 4, "Accredited by NAAC with an 'A' Grade and All eligible UG Engineering Programmes are Accredited by NBA", 0, 1, "C")
        self.cell(0, 4, "(Approved by AICTE, New Delhi - Affiliated to Anna University, Chennai)", 0, 1, "C")
        self.cell(0, 4, "Pachapalayam, Perur Chettipalayam, Coimbatore - 641 010. www.srit.org Phone - 0422-2605577", 0, 1, "C")

        # --- Row 2: Line of Logos ---
        self.ln(5)
        # List of logos to display in the second row
        # HIVE, SISH, MIC, AICTE, IIC, Idea Lab, E-Cell
        logo_files = ["hive.png", "sish.png", "mic.png", "aicte.png", "iic.png", "idea_lab.png", "ecell.png"]
        
        # Configuration for logo slots
        slot_width = 22
        slot_height = 22
        spacing = 8
        
        # Calculate total width of the logo block
        total_logos_width = (len(logo_files) * slot_width) + ((len(logo_files) - 1) * spacing)
        
        # Center the block on the page (A4 width approx 210mm)
        page_width = 210
        start_x = (page_width - total_logos_width) / 2
        
        y_pos = self.get_y()
        x_pos = start_x
        
        for logo in logo_files:
            path = f"logos/{logo}"
            if os.path.exists(path):
                safe_logo = sanitize_image(path)
                if safe_logo:
                    try:
                        # Get original dimensions to calculate aspect ratio scaling
                        with Image.open(safe_logo) as img:
                            img_w, img_h = img.size
                            
                        # Calculate scaling factor to fit inside slot_width x slot_height
                        scale = min(slot_width / img_w, slot_height / img_h)
                        
                        new_w = img_w * scale
                        new_h = img_h * scale
                        
                        # Center the image within the slot
                        x_offset = (slot_width - new_w) / 2
                        y_offset = (slot_height - new_h) / 2
                        
                        self.image(safe_logo, x_pos + x_offset, y_pos + y_offset, w=new_w, h=new_h)
                    except Exception as e:
                        print(f"Error scaling logo {logo}: {e}")
                        # Fallback
                        self.image(safe_logo, x_pos, y_pos, w=slot_width)
                else:
                    self.rect(x_pos, y_pos, slot_width, slot_height)
            else:
                self.rect(x_pos, y_pos, slot_width, slot_height)
                self.set_font("Arial", "", 6)
                self.text(x_pos+2, y_pos+10, logo.split('.')[0])
            
            # Move to next slot
            x_pos += slot_width + spacing
            
        self.ln(25)
        # Purple Line
        self.set_draw_color(128, 0, 128) # Purple
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

# Helper for separator pages (Title at top, content follows)
def add_separator(pdf, title):
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 15, title, 0, 1, "C", fill=True)
    pdf.ln(10)

def generate_pdf(data, filename, uploaded_files=None):
    pdf = ProfessionalPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Helper to clean text for Latin-1 encoding
    def clean_text(text):
        if not isinstance(text, str):
            return str(text)
        replacements = {
            '\u2018': "'", '\u2019': "'", # Smart quotes
            '\u201c': '"', '\u201d': '"', # Smart double quotes
            '\u2013': '-', '\u2014': '-', # Dashes
            '\u2026': '...',              # Ellipsis
            '\u00a0': ' '                 # Non-breaking space
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        
        # Fallback: encode to latin-1, replacing unknown chars with ?
        return text.encode('latin-1', 'replace').decode('latin-1')

    # Title
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, clean_text(f"Report on {data.get('Program Name', 'Activity')}"), 0, 1, "C")
    pdf.ln(5)

    # --- Table Data ---
    pdf.set_font("Arial", "", 10)
    
    def add_table_row(label, value):
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, clean_text(label), 1)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, clean_text(str(value)), 1)

    add_table_row("ACADEMIC YEAR:", data.get("Academic Year", "2025-26"))
    add_table_row("QUARTER:", data.get("Quarter", ""))
    add_table_row("ACTIVITY CATEGORY:", data.get("Activity Type", ""))
    add_table_row("PROGRAM TYPE:", data.get("Program Type", ""))
    add_table_row("PROGRAM NAME:", data.get("Program Name", ""))
    add_table_row("PROGRAM THEME:", data.get("Program Theme", ""))
    add_table_row("DURATION:", f"{data.get('Duration', 0)} Hours")
    add_table_row("DATE:", f"{data.get('Start Date', '')} to {data.get('End Date', '')}")
    
    # Participants
    part_str = f"Students: {data.get('Student Participants', 0)} | Faculty: {data.get('Faculty Participants', 0)}"
    add_table_row("PARTICIPANTS:", part_str)
    
    add_table_row("EXPENDITURE:", f"Rs. {data.get('Total Expense', 0)}")
    add_table_row("MODE OF DELIVERY:", data.get("Mode", ""))
    
    # SDG and PO
    sdg_list = data.get("SDG Goals", [])
    if isinstance(sdg_list, list):
        sdg_str = "\n".join(sdg_list)
    else:
        sdg_str = str(sdg_list)
    add_table_row("SDG GOALS:", sdg_str)

    po_list = data.get("Program Outcomes", [])
    if isinstance(po_list, list):
        po_str = "\n".join(po_list)
    else:
        po_str = str(po_list)
    add_table_row("PROGRAM OUTCOMES:", po_str)
    
    # Collaborations
    collab = data.get("Collaborating Department", "")
    if collab:
        add_table_row("COLLABORATIONS:", collab)
    
    # Social Media
    sm_data = data.get("Social Media", {})
    if isinstance(sm_data, dict):
        sm_str = "\n".join([f"{k}: {v}" for k, v in sm_data.items() if v])
    else:
        sm_str = str(sm_data)
    add_table_row("SOCIAL MEDIA:", sm_str)

    pdf.ln(5)
    
    # --- Part A: Student Data Summary ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "PART A: STUDENT DATA SUMMARY", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    
    # A1. Numbers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "A1. NUMBERS", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, f"Feedback Collected: {data.get('Feedback Count', 0)}", 0, 0)
    pdf.cell(50, 6, f"Total Attended: {data.get('Total Attended', 0)}", 0, 1)
    pdf.cell(50, 6, f"Male: {data.get('Male Count', 0)}", 0, 0)
    pdf.cell(50, 6, f"Female: {data.get('Female Count', 0)}", 0, 1)
    
    pdf.ln(2)
    pdf.write(5, clean_text(f"Top 3 Depts: 1. {data.get('Dept1', '')} ({data.get('Dept1 Count', 0)})  2. {data.get('Dept2', '')} ({data.get('Dept2 Count', 0)})  3. {data.get('Dept3', '')} ({data.get('Dept3 Count', 0)})\n"))
    pdf.ln(3)

    # A2. Ratings
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "A2. RATINGS", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, f"5 Star: {data.get('5 Star Count', 0)} | 4 Star: {data.get('4 Star Count', 0)}", 0, 0)
    pdf.cell(60, 6, f"Total >=4 Star: {data.get('High Star Perc', 0):.1f}%", 0, 1)
    
    pdf.cell(60, 6, f"Exp: {data.get('Exp Score', 0)}% | Content: {data.get('Cont Score', 0)}% | Speaker: {data.get('Speak Score', 0)}%", 0, 1)
    pdf.cell(0, 6, f"Avg Satisfaction: {data.get('Avg Sat', 0)}% | Target Met: {'Yes' if data.get('Target Met') else 'No'}", 0, 1)
    pdf.ln(3)

    # A3 & A4
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "A3. IMPACT & A4. INNOVATION", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.write(5, clean_text(f"Knowledge: Before {data.get('Know Before', 0)} -> After {data.get('Know After', 0)} (Gain: {data.get('Know Gain', 0):.1f})\n"))
    pdf.write(5, clean_text(f"Will Apply Learning: {data.get('Apply Learn Count', 0)} ({data.get('Apply Learn Perc', 0):.1f}%)\n"))
    pdf.write(5, clean_text(f"Got Ideas: {data.get('Got Ideas', 0)} | Work on Ideas: {data.get('Work Ideas', 0)}\n"))
    pdf.write(5, clean_text(f"Interested in Ent: {data.get('Interest Ent', 0)} | Want Mentor: {data.get('Want Mentor', 0)}\n"))
    pdf.ln(3)

    # A5. Feedback
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "A5. TOP FEEDBACK", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_text(f"Liked: {data.get('Top Liked', 'N/A')}"))
    pdf.multi_cell(0, 5, clean_text(f"Improve: {data.get('Top Improve', 'N/A')}"))
    pdf.cell(0, 6, f"Recommend %: {data.get('Recommend Perc', 0)}%", 0, 1)
    pdf.ln(5)

    # --- Part B: Assessment ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "PART B: ASSESSMENT", 0, 1, "L")
    
    # B1. Ratings
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "B1. QUICK RATINGS (1-5)", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, f"Planning: {data.get('Plan Rating', 0)} | Execution: {data.get('Exec Rating', 0)}", 0, 1)
    pdf.cell(60, 6, f"Speaker: {data.get('Speak Rating', 0)} | Learning: {data.get('Learn Rating', 0)}", 0, 1)
    pdf.cell(60, 6, f"Innovation: {data.get('Innov Rating', 0)} | Budget: {data.get('Budget Rating', 0)}", 0, 1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, f"Average Score: {data.get('Avg Score', 0):.1f}/5", 0, 1)
    pdf.ln(3)

    # B2. Outcomes
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "B2. KEY OUTCOMES", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_text(f"Objectives: {data.get('Obj Achieved', '')}"), 0, 1)
    pdf.cell(0, 6, f"Promising Ideas: {data.get('Prom Ideas', 0)} | Mentor Teams: {data.get('Mentor Teams', 0)}", 0, 1)
    pdf.cell(0, 6, f"Budget Used: {data.get('Budget Used Perc', 0)}%", 0, 1)
    pdf.ln(3)

    # B3 & B4
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "B3. FEEDBACK & B4. SUCCESS", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_text(f"Challenge: {data.get('Big Challenge', 'N/A')}"))
    pdf.multi_cell(0, 5, clean_text(f"Best Thing: {data.get('Best Thing', 'N/A')}"))
    pdf.multi_cell(0, 5, clean_text(f"Improve: {data.get('Improve Next', 'N/A')}"))
    pdf.ln(2)
    
    # --- Objectives & Benefits ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "OBJECTIVE:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_text(data.get("Objective", "N/A")))
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "BENEFITS:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_text(data.get("Benefits", "N/A")))
    pdf.ln(5)

    # --- AI Generated Report Summary ---
    ai_report = data.get("AI Report Content")
    if ai_report:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "EVENT REPORT SUMMARY", 0, 1, "C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, clean_text(ai_report))
        pdf.ln(10)

    # --- Signatures ---
    pdf.ln(10)
    if pdf.get_y() > 240:
        pdf.add_page()
        
    y_sig = pdf.get_y()
    pdf.set_font("Arial", "B", 11)
    pdf.text(30, y_sig + 20, "Event Coordinator")
    pdf.text(140, y_sig + 20, "IIC President")
    pdf.ln(30)

    # --- Event Charts (Annexure Style) ---
    chart_paths = data.get("Chart Paths", [])
    if chart_paths:
        # Title Page for Charts Section
        add_separator(pdf, "EVENT ANALYTICS")
        
        for i, chart_path in enumerate(chart_paths):
            # Each chart on a new page (after the section separator)
            if i > 0:
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"Event Analysis - Chart {i+1}", 0, 1, "C")
            
            try:
                # Center the chart
                with Image.open(chart_path) as img:
                    img_w, img_h = img.size
                
                max_w = 180
                max_h = 240
                
                scale = min(max_w / img_w, max_h / img_h)
                new_w = img_w * scale
                new_h = img_h * scale
                
                x_pos = (210 - new_w) / 2
                y_pos = pdf.get_y() + 10 # Below title
                
                pdf.image(chart_path, x=x_pos, y=y_pos, w=new_w, h=new_h)
                
            except Exception as e:
                print(f"Error embedding chart: {e}")
                pdf.cell(0, 10, f"Error embedding chart: {str(e)}", 0, 1)

    # --- Attachments ---
    temp_files = [] # Keep track to delete later
    pdfs_to_merge = []

    if uploaded_files:
        for key, file_obj in uploaded_files.items():
            if file_obj:
                file_obj.seek(0)
                # Save to temp file
                suffix = os.path.splitext(file_obj.name)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file_obj.read())
                    tmp_path = tmp.name
                    temp_files.append(tmp_path)

                if suffix in ['.jpg', '.jpeg', '.png']:
                    # Use separator page for images
                    add_separator(pdf, f"ANNEXURE: {key}")
                    
                    # Sanitize uploaded image too
                    safe_img = sanitize_image(tmp_path)
                    if safe_img:
                        try:
                            with Image.open(safe_img) as img:
                                img_w, img_h = img.size
                                
                            max_w = 190
                            max_h = 240 # Leave space for header/footer/title
                            
                            scale = min(max_w / img_w, max_h / img_h)
                            new_w = img_w * scale
                            new_h = img_h * scale
                            
                            x_pos = (210 - new_w) / 2
                            y_pos = pdf.get_y() + 10
                            
                            pdf.image(safe_img, x=x_pos, y=y_pos, w=new_w, h=new_h)
                            temp_files.append(safe_img) # Track for deletion
                        except Exception as e:
                            print(f"Error embedding image {key}: {e}")
                            pdf.cell(0, 10, f"Error embedding image: {str(e)}", 0, 1)
                    
                elif suffix == '.pdf':
                    pdfs_to_merge.append(tmp_path)

    # Save the main FPDF report
    main_pdf_path = "temp_main_report.pdf"
    pdf.output(main_pdf_path)
    temp_files.append(main_pdf_path)

    # --- Merge PDFs ---
    if pdfs_to_merge:
        merger = PdfWriter()
        
        # Add main report
        merger.append(main_pdf_path)
        
        # Add other PDFs
        for pdf_path in pdfs_to_merge:
            merger.append(pdf_path)
        
        merger.write(filename)
        merger.close()
    else:
        # No extra PDFs, just rename the main one
        if os.path.exists(filename):
            os.remove(filename)
        os.rename(main_pdf_path, filename)

    # Cleanup temp files
    for path in temp_files:
        try:
            os.remove(path)
        except:
            pass

    return filename
