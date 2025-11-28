
import streamlit as st
import pandas as pd
from datetime import date
import config
import utils
import os

# --- Page Config ---
st.set_page_config(
    page_title="Event Report Submission Portal",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E40AF;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🔧 Configuration")
st.sidebar.info("Credentials are loaded from `config.py`.")
st.sidebar.markdown("---")
st.sidebar.info("Ensure `client_secret.json` (OAuth) is present in the app directory.")

# Check for logos
if not os.path.exists("logos") or not os.listdir("logos"):
    st.sidebar.warning("⚠️ 'logos' folder is empty or missing! PDF header will be incomplete.")
    st.sidebar.markdown("Please add: `snr_logo.png`, `srit_logo.png`, `hive.png`, `sish.png`, `mic.png`, `aicte.png`, `iic.png`, `idea_lab.png`")

# Test Connection Button
if st.sidebar.button("🧪 Test Google Sheet Connection"):
    try:
        ds, ss = utils.get_google_services()
        if ss:
            test_data = {"Program Name": "TEST_CONNECTION", "Activity Type": "Test", "Timestamp": str(datetime.now())}
            if utils.append_to_sheet(ss, config.GOOGLE_SHEET_ID, test_data):
                st.sidebar.success("✅ Connected to 'IIC8 reports'!")
            else:
                st.sidebar.error("❌ Write Failed")
        else:
            st.sidebar.error("❌ Auth Failed")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("🔄 Re-Authenticate Google Drive"):
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    st.sidebar.info("Please check your browser/terminal for Google Login...")
    try:
        ds, ss = utils.get_google_services()
        if ds:
            st.sidebar.success("✅ Authentication Successful! You can now upload.")
        else:
            st.sidebar.error("❌ Authentication Failed. Check terminal output.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- Main App ---
# ... (existing code) ...

# ... inside the submit logic ...
                if drive_service:
                    # ... upload logic ...
                else:
                    st.warning("⚠️ Google Drive Service not connected. Files will NOT be uploaded.")
                    st.info("👉 Please click '🔄 Re-Authenticate Google Drive' in the sidebar to fix this.")

# --- Main App ---
st.markdown('<div class="main-header">📝 Event Report Submission Portal</div>', unsafe_allow_html=True)

# Initialize Session State for Auto-Fill
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}



# Helper to get value from session state or default
def get_val(key, default):
    return st.session_state.form_data.get(key, default)



# ==========================================
# SECTION 2: EVENT DETAILS
# ==========================================
st.markdown('<div class="sub-header">📌 Event Details</div>', unsafe_allow_html=True)



col_top1, col_top2 = st.columns(2)
with col_top1:
    academic_year = st.selectbox("Academic Year", ["2024-25", "2025-26", "2026-27"], index=1)
    quarter = st.selectbox("Quarter", ["Semester 1-Quarter I", "Semester 1-Quarter II", "Semester 2-Quarter III", "Semester 2-Quarter IV"])

with col_top2:
    program_driven_by = st.selectbox("Program driven by", ["IIC Calendar Activity", "Self-Driven Activity", "MIC Driven Activity"], index=1)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    program_type = st.selectbox("Program Type *", 
        [
            "Select",
            "Level 1 - Expert Talk",
            "Level 1 - Exposure Visit",
            "Level 1 - Mentoring Session",
            "Level 1 - Exhibition",
            "Level 2 - Conference",
            "Level 2 - Exposure Visit",
            "Level 2 - Seminar",
            "Level 2 - Workshop",
            "Level 2 - Competition",
            "Level 3 - Bootcamp",
            "Level 3 - Competition/Hackathon",
            "Level 3 - Demo Day",
            "Level 3 - Exhibition",
            "Level 3 - Workshop",
            "Level 3 - Exposure Visit",
            "Level 4 - Challenges",
            "Level 4 - Competition/Hackathon",
            "Level 4 - Tech Fest",
            "Level 4 - Bootcamp",
            "Level 4 - Workshop",
            "Level 4 - Exhibition/Demo Day"
        ],
        index=0)
    program_name = st.text_input("Program/Activity Name *", value=get_val("Program Name", ""))
    program_theme = st.selectbox("Program Theme *", config.PROGRAM_THEMES)
    activity_lead = st.selectbox("Activity Lead By *", config.ACTIVITY_LEADS)
    collaborating_dept = st.text_input("Collaborating Department/Association (Optional)", value=get_val("Collaborating Department", ""))

with col2:
    level = st.selectbox("Level of Event", config.LEVELS)
    mode = st.selectbox("Mode of Session Delivery *", config.MODES_OF_DELIVERY)
        
# --- Common Fields ---
st.markdown("### 📅 Schedule & Participation")

c1, c2, c3 = st.columns(3)
with c1:
    # Handle date parsing safely
    d_val = date.today()
    if get_val("Start Date", ""):
        try: d_val = datetime.strptime(get_val("Start Date", ""), "%Y-%m-%d").date()
        except: pass
    start_date = st.date_input("Start Date *", value=d_val)
    
    duration = st.number_input("Duration (in Hrs) *", min_value=0.5, step=0.5, value=float(get_val("Duration", 1.0)))
with c2:
    d_val_end = date.today()
    if get_val("End Date", ""):
        try: d_val_end = datetime.strptime(get_val("End Date", ""), "%Y-%m-%d").date()
        except: pass
    end_date = st.date_input("End Date *", value=d_val_end)

c4, c5, c6, c7 = st.columns(4)
with c4:
    stud_participants = st.number_input("Student Participants *", min_value=0, value=int(get_val("Student Participants", 0)))
with c5:
    fac_participants = st.number_input("Faculty Participants *", min_value=0, value=int(get_val("Faculty Participants", 0)))
with c6:
    ext_stud_participants = st.number_input("External Students", min_value=0, value=int(get_val("External Students", 0)))
with c7:
    ext_fac_participants = st.number_input("External Faculty", min_value=0, value=int(get_val("External Faculty", 0)))

# --- Objectives & Benefits ---
st.markdown("### 🎯 Objectives & Outcomes")

col_obj1, col_obj2 = st.columns(2)
with col_obj1:
    sdg_goals = st.multiselect("SDG Goals Mapped", config.SDG_GOALS, default=get_val("SDG Goals", []))
with col_obj2:
    program_outcomes = st.multiselect("Program Outcomes (NBA) Mapped", config.PROGRAM_OUTCOMES, default=get_val("Program Outcomes", []))

objective = st.text_area("Objective", value=get_val("Objective", ""), height=100)
benefits = st.text_area("Benefits (Learning/Skill/Knowledge)", value=get_val("Benefits", ""), height=100)


st.markdown('<div class="sub-header">💰 Expenditure & Balance Sheet</div>', unsafe_allow_html=True)
st.info("Enter income sources and expenditure items below.")

# Data Editor for Financials
default_data = pd.DataFrame([
    {"Description": "Registration Fees", "Type": "Income", "Amount": 0.0},
    {"Description": "Sponsorship", "Type": "Income", "Amount": 0.0},
    {"Description": "Honorarium", "Type": "Expense", "Amount": 0.0},
    {"Description": "Refreshments", "Type": "Expense", "Amount": 0.0},
])

financial_df = st.data_editor(
    default_data,
    num_rows="dynamic",
    column_config={
        "Type": st.column_config.SelectboxColumn(
            "Type",
            options=["Income", "Expense"],
            required=True,
        ),
        "Amount": st.column_config.NumberColumn(
            "Amount (₹)",
            min_value=0.0,
            format="₹%.2f"
        )
    },
    use_container_width=True
)

# Calculate Totals
total_income = financial_df[financial_df["Type"] == "Income"]["Amount"].sum()
total_expense = financial_df[financial_df["Type"] == "Expense"]["Amount"].sum()
balance = total_income - total_expense

fc1, fc2, fc3 = st.columns(3)
fc1.metric("Total Income", f"₹{total_income:,.2f}")
fc2.metric("Total Expense", f"₹{total_expense:,.2f}")
fc3.metric("Net Balance", f"₹{balance:,.2f}", delta_color="normal")

expenditure_stmt = st.text_area("Additional Financial Remarks", placeholder="Notes on budget approval, etc.")


# ==========================================
# SECTION 4: ATTACHMENTS
# ==========================================
st.markdown('<div class="sub-header">📎 Attachments & Documents</div>', unsafe_allow_html=True)

video_url = st.text_input("Video URL (Optional)")

st.info("Please upload the following required documents.")

uploaded_files = {}

with st.expander("📸 Photos & Media", expanded=True):
    st.info("Please upload 5 Geotagged photos and 5 Non-Geotagged photos.")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("##### 📍 Geotagged Photos")
        for i in range(1, 6):
            uploaded_files[f"Geotagged Photo {i}"] = st.file_uploader(f"Geotagged Photo {i}", type=['png', 'jpg', 'jpeg'], key=f"geo_{i}")
            
    with col_p2:
        st.markdown("##### 🖼️ Non-Geotagged Photos")
        for i in range(1, 6):
            uploaded_files[f"Non-Geotagged Photo {i}"] = st.file_uploader(f"Non-Geotagged Photo {i}", type=['png', 'jpg', 'jpeg'], key=f"non_geo_{i}")

with st.expander("📄 Core Documents", expanded=False):
    uploaded_files["Event SOP"] = st.file_uploader("Event SOP (Signed by Principal)", type=['pdf'])
    # Report Summary upload removed - replaced by AI generation
    minute_to_minute = st.text_area("Minute-to-Minute Flow / Event Highlights (for AI Report)", height=150, placeholder="Enter the detailed flow of the event...")
    uploaded_files["Attendance"] = st.file_uploader("Attendance Sheet", type=['pdf'])
    uploaded_files["Registration Forms"] = st.file_uploader("Registration Forms (Google Form)", type=['pdf', 'csv', 'xlsx'])

with st.expander("📂 Additional Evidence (Bulk Upload Optional)", expanded=False):
    st.write("Upload other documents as per the checklist (Brochures, Feedback, etc.)")
    uploaded_files["Brochure"] = st.file_uploader("Event Brochure/Poster", type=['pdf', 'png', 'jpg'])
    uploaded_files["Feedback"] = st.file_uploader("Feedback Samples", type=['pdf', 'png', 'jpg'])
    uploaded_files["Speaker Profile"] = st.file_uploader("Resource Person Profile", type=['pdf'])

# ==========================================
# SECTION 5: SOCIAL MEDIA
# ==========================================
st.markdown('<div class="sub-header">🌐 Promotion in Social Media</div>', unsafe_allow_html=True)

social_media = {}
col_sm1, col_sm2 = st.columns([1, 3])

with col_sm1:
    sm_twitter = st.checkbox("Twitter")
    sm_facebook = st.checkbox("Facebook")
    sm_instagram = st.checkbox("Instagram")
    sm_linkedin = st.checkbox("LinkedIn")

with col_sm2:
    social_media["Twitter"] = st.text_input("Twitter URL", disabled=not sm_twitter)
    social_media["Facebook"] = st.text_input("Facebook URL", disabled=not sm_facebook)
    social_media["Instagram"] = st.text_input("Instagram URL", disabled=not sm_instagram)
    social_media["LinkedIn"] = st.text_input("LinkedIn URL", disabled=not sm_linkedin)


# ==========================================
# SECTION 6: PART A - STUDENT DATA SUMMARY
# ==========================================
st.markdown('<div class="sub-header">📊 Part A: Student Data Summary</div>', unsafe_allow_html=True)
st.info("Please fill in the data from the student feedback forms.")

with st.expander("A1. NUMBERS", expanded=True):
    c_a1_1, c_a1_2, c_a1_3, c_a1_4 = st.columns(4)
    with c_a1_1: feedback_count = st.number_input("Feedback forms collected", min_value=0, value=int(get_val("Feedback Count", 0)))
    with c_a1_2: total_attended = st.number_input("Total students attended", min_value=0, value=int(get_val("Total Attended", 0)))
    with c_a1_3: male_count = st.number_input("Male", min_value=0, value=int(get_val("Male Count", 0)))
    with c_a1_4: female_count = st.number_input("Female", min_value=0, value=int(get_val("Female Count", 0)))
    
    st.markdown("**Top 3 Departments:**")
    c_dept1, c_dept2, c_dept3 = st.columns(3)
    with c_dept1: 
        dept1 = st.text_input("1. Dept Name", value=get_val("Dept1", ""), key="d1")
        dept1_count = st.number_input("Count", min_value=0, value=int(get_val("Dept1 Count", 0)), key="d1c")
    with c_dept2: 
        dept2 = st.text_input("2. Dept Name", value=get_val("Dept2", ""), key="d2")
        dept2_count = st.number_input("Count", min_value=0, value=int(get_val("Dept2 Count", 0)), key="d2c")
    with c_dept3: 
        dept3 = st.text_input("3. Dept Name", value=get_val("Dept3", ""), key="d3")
        dept3_count = st.number_input("Count", min_value=0, value=int(get_val("Dept3 Count", 0)), key="d3c")

with st.expander("A2. RATINGS (Count 5⭐ and 4⭐ responses)", expanded=False):
    c_a2_1, c_a2_2 = st.columns(2)
    with c_a2_1: star5_count = st.number_input("Students giving 5⭐", min_value=0, value=int(get_val("5 Star Count", 0)))
    with c_a2_2: star4_count = st.number_input("Students giving 4⭐", min_value=0, value=int(get_val("4 Star Count", 0)))
    
    total_high_star = star5_count + star4_count
    high_star_perc = (total_high_star / feedback_count * 100) if feedback_count > 0 else 0.0
    st.metric("Total ≥4⭐ %", f"{high_star_perc:.1f}%")
    
    st.markdown("**Percentage Scores:**")
    c_exp, c_cont, c_speak = st.columns(3)
    with c_exp: exp_score = st.number_input("Overall Experience %", min_value=0.0, max_value=100.0, value=float(get_val("Exp Score", 0.0)))
    with c_cont: cont_score = st.number_input("Content Quality %", min_value=0.0, max_value=100.0, value=float(get_val("Cont Score", 0.0)))
    with c_speak: speak_score = st.number_input("Speaker Quality %", min_value=0.0, max_value=100.0, value=float(get_val("Speak Score", 0.0)))
    
    avg_sat = st.number_input("Average satisfaction (% students gave ≥4⭐)", min_value=0.0, max_value=100.0, value=float(get_val("Avg Sat", 0.0)))
    target_met = st.checkbox("✅ Target Met (≥80%)", value=get_val("Target Met", False))

with st.expander("A3. LEARNING IMPACT", expanded=False):
    c_a3_1, c_a3_2 = st.columns(2)
    with c_a3_1: know_before = st.number_input("Average knowledge BEFORE (0-10)", min_value=0.0, max_value=10.0, value=float(get_val("Know Before", 0.0)))
    with c_a3_2: know_after = st.number_input("Average knowledge AFTER (0-10)", min_value=0.0, max_value=10.0, value=float(get_val("Know After", 0.0)))
    
    know_gain = know_after - know_before
    st.metric("Knowledge Gain", f"{know_gain:.1f}")
    
    apply_learn_count = st.number_input("Students who will apply learning (Count)", min_value=0, value=int(get_val("Apply Learn Count", 0)))
    apply_learn_perc = (apply_learn_count / feedback_count * 100) if feedback_count > 0 else 0.0
    st.write(f"Percentage: {apply_learn_perc:.1f}%")

with st.expander("A4. INNOVATION RESULTS", expanded=False):
    c_a4_1, c_a4_2 = st.columns(2)
    with c_a4_1: 
        got_ideas = st.number_input("Students who got ideas (Count)", min_value=0, value=int(get_val("Got Ideas", 0)))
        work_ideas = st.number_input("Students who will work on ideas (Count)", min_value=0, value=int(get_val("Work Ideas", 0)))
    with c_a4_2:
        interest_ent = st.number_input("Students interested in entrepreneurship (Count)", min_value=0, value=int(get_val("Interest Ent", 0)))
        want_mentor = st.number_input("Students wanting mentorship (Count)", min_value=0, value=int(get_val("Want Mentor", 0)))

with st.expander("A5. TOP FEEDBACK", expanded=False):
    top_liked = st.text_area("Top 3 things students LIKED", value=get_val("Top Liked", ""))
    top_improve = st.text_area("Top 3 things to IMPROVE", value=get_val("Top Improve", ""))
    recommend_perc = st.number_input("Will students recommend? (≥4⭐) %", min_value=0.0, max_value=100.0, value=float(get_val("Recommend Perc", 0.0)))


# ==========================================
# SECTION 7: PART B - YOUR ASSESSMENT
# ==========================================
st.markdown('<div class="sub-header">📝 Part B: Your Assessment</div>', unsafe_allow_html=True)
st.info("Please provide your assessment of the event.")

with st.expander("B1. QUICK RATINGS (Rate 1-5)", expanded=True):
    c_b1_1, c_b1_2, c_b1_3 = st.columns(3)
    with c_b1_1: plan_rating = st.slider("Planning & Preparation", 1, 5, value=int(get_val("Plan Rating", 3)))
    with c_b1_2: exec_rating = st.slider("Execution Quality", 1, 5, value=int(get_val("Exec Rating", 3)))
    with c_b1_3: speak_rating = st.slider("Speaker Performance", 1, 5, value=int(get_val("Speak Rating", 3)))
    
    c_b1_4, c_b1_5, c_b1_6 = st.columns(3)
    with c_b1_4: learn_rating = st.slider("Learning Outcomes", 1, 5, value=int(get_val("Learn Rating", 3)))
    with c_b1_5: innov_rating = st.slider("Innovation Impact", 1, 5, value=int(get_val("Innov Rating", 3)))
    with c_b1_6: budget_rating = st.slider("Budget Utilization", 1, 5, value=int(get_val("Budget Rating", 3)))
    
    avg_score = (plan_rating + exec_rating + speak_rating + learn_rating + innov_rating + budget_rating) / 6
    st.metric("Your Average Score", f"{avg_score:.1f}/5")

with st.expander("B2. KEY OUTCOMES", expanded=False):
    obj_achieved = st.selectbox("Q1. Were objectives achieved?", 
        ["Fully achieved (5)", "Mostly achieved (4)", "Partially achieved (3)", "Not achieved (2)"],
        index=0)
    
    c_b2_1, c_b2_2, c_b2_3 = st.columns(3)
    with c_b2_1: prom_ideas = st.number_input("Q2. Number of promising ideas", min_value=0, value=int(get_val("Prom Ideas", 0)))
    with c_b2_2: mentor_teams = st.number_input("Q3. Teams you'll mentor", min_value=0, value=int(get_val("Mentor Teams", 0)))
    with c_b2_3: budget_used_perc = st.number_input("Q4. Budget used % (Target: 90-100%)", min_value=0.0, max_value=100.0, value=float(get_val("Budget Used Perc", 0.0)))

with st.expander("B3. BRIEF FEEDBACK", expanded=False):
    big_challenge = st.text_area("Q5. Biggest challenge", value=get_val("Big Challenge", ""))
    best_thing = st.text_area("Q6. Best thing that worked", value=get_val("Best Thing", ""))
    improve_next = st.text_area("Q7. One thing to improve next time", value=get_val("Improve Next", ""))

with st.expander("B4. SUCCESS HIGHLIGHT", expanded=False):
    success_story = st.text_area("Q8. Best success story (Student/Team & Achievement)", value=get_val("Success Story", ""))

# Acknowledgement
st.markdown("---")
acknowledgement = st.checkbox("I acknowledge that I am aware of the details provided above and they are accurate to the best of my knowledge.")

# --- Submit Section ---
st.markdown("---")

# Initialize Session State for Workflow
if "report_stage" not in st.session_state:
    st.session_state.report_stage = "input" # input -> draft_generated -> submitted
if "ai_report_content" not in st.session_state:
    st.session_state.ai_report_content = ""

# Stage 1: Generate Draft
if st.session_state.report_stage == "input":
    if st.button("📝 Generate Draft Report", type="primary"):
        if not program_name:
            st.error("Program Name is required!")
        elif program_type == "Select":
            st.error("Please select a valid Program Type!")
        elif not acknowledgement:
            st.error("Please acknowledge the details before submitting.")
        elif not config.GOOGLE_SHEET_ID or "PASTE" in config.GOOGLE_SHEET_ID:
            st.error("Please configure GOOGLE_SHEET_ID in config.py")
        elif not config.DRIVE_PARENT_FOLDER_ID or "PASTE" in config.DRIVE_PARENT_FOLDER_ID:
            st.error("Please configure DRIVE_PARENT_FOLDER_ID in config.py")
        else:
            # Prepare Data for AI Generation
            # Format Financials as a string summary for the sheet
            financial_summary = f"Income: {total_income} | Expense: {total_expense} | Balance: {balance}\n"
            for index, row in financial_df.iterrows():
                financial_summary += f"{row['Description']} ({row['Type']}): {row['Amount']}\n"

            temp_data = {
                "Program Name": program_name,
                "Start Date": str(start_date),
                "Program Theme": program_theme,
                "Objective": objective,
                "Benefits": benefits,
                "Top Liked": top_liked,
                "Top Improve": top_improve,
                "Success Story": success_story,
                "Best Thing": best_thing
            }
            
            with st.spinner("Analyzing data and generating report draft..."):
                # AI Report
                ai_content = utils.generate_professional_report(config.GEMINI_API_KEY, temp_data, minute_to_minute)
                st.session_state.ai_report_content = ai_content
                st.session_state.report_stage = "draft_generated"
                st.rerun()

# Stage 2: Review & Final Submit
if st.session_state.report_stage == "draft_generated":
    st.success("✅ Draft Report Generated! Please review and edit below.")
    
    st.markdown("### ✏️ Edit Report Summary")
    edited_report = st.text_area("AI Generated Content (Editable)", value=st.session_state.ai_report_content, height=400)
    st.session_state.ai_report_content = edited_report
    
    c_sub1, c_sub2 = st.columns([1, 1])
    with c_sub1:
        if st.button("🔙 Back to Edit Data"):
            st.session_state.report_stage = "input"
            st.rerun()
            
    with c_sub2:
        if st.button("🚀 Confirm & Upload Report", type="primary"):
            with st.spinner("Finalizing Submission..."):
                # 1. Authenticate Google Services
                drive_service, sheets_service = utils.get_google_services()
                
                # 2. Upload Files to Drive
                file_links = {}
                if drive_service:
                    folder_name = f"{program_name}_{date.today()}"
                    # Sanitize folder name
                    folder_name = folder_name.replace("/", "_").replace(":", "-")
                    
                    event_folder_id = utils.create_drive_folder(drive_service, folder_name, config.DRIVE_PARENT_FOLDER_ID)
                    
                    if event_folder_id:
                        for key, file_obj in uploaded_files.items():
                            if file_obj:
                                # Reset pointer for upload
                                file_obj.seek(0)
                                link = utils.upload_to_drive(drive_service, file_obj, f"{key}_{program_name}", event_folder_id)
                                file_links[key] = link
                    else:
                        st.error("Failed to create event folder in Drive. Check permissions.")
                else:
                    st.warning("⚠️ Google Drive Service not connected. Files will NOT be uploaded.")
                    st.info("👉 Please click '🔄 Re-Authenticate Google Drive' in the sidebar to fix this.")

                # 3. Prepare Final Data Dictionary
                financial_summary = f"Income: {total_income} | Expense: {total_expense} | Balance: {balance}\n"
                for index, row in financial_df.iterrows():
                    financial_summary += f"{row['Description']} ({row['Type']}): {row['Amount']}\n"

                data = {
                    "Academic Year": academic_year,
                    "Quarter": quarter,
                    "Activity Type": program_driven_by,
                    "Program Type": program_type,
                    "Program Name": program_name,
                    "Program Theme": program_theme,
                    "Activity Lead": activity_lead,
                    "Collaborating Department": collaborating_dept,
                    "Level": level,
                    "Mode": mode,
                    "Start Date": str(start_date),
                    "End Date": str(end_date),
                    "Duration": duration,
                    "Student Participants": stud_participants,
                    "Faculty Participants": fac_participants,
                    "External Students": ext_stud_participants,
                    "External Faculty": ext_fac_participants,
                    "Total Income": total_income,
                    "Total Expense": total_expense,
                    "Net Balance": balance,
                    "Financial Details": financial_summary,
                    "Objective": objective,
                    "Benefits": benefits,
                    "Minute to Minute": minute_to_minute,
                    "SDG Goals": sdg_goals,
                    "Program Outcomes": program_outcomes,
                    "Video URL": video_url,
                    "Social Media": social_media,
                    
                    # Part A Data
                    "Feedback Count": feedback_count,
                    "Total Attended": total_attended,
                    "Male Count": male_count,
                    "Female Count": female_count,
                    "Dept1": dept1, "Dept1 Count": dept1_count,
                    "Dept2": dept2, "Dept2 Count": dept2_count,
                    "Dept3": dept3, "Dept3 Count": dept3_count,
                    "5 Star Count": star5_count,
                    "4 Star Count": star4_count,
                    "High Star Perc": high_star_perc,
                    "Exp Score": exp_score,
                    "Cont Score": cont_score,
                    "Speak Score": speak_score,
                    "Avg Sat": avg_sat,
                    "Target Met": target_met,
                    "Know Before": know_before,
                    "Know After": know_after,
                    "Know Gain": know_gain,
                    "Apply Learn Count": apply_learn_count,
                    "Apply Learn Perc": apply_learn_perc,
                    "Got Ideas": got_ideas,
                    "Work Ideas": work_ideas,
                    "Interest Ent": interest_ent,
                    "Want Mentor": want_mentor,
                    "Top Liked": top_liked,
                    "Top Improve": top_improve,
                    "Recommend Perc": recommend_perc,
                    
                    # Part B Data
                    "Plan Rating": plan_rating,
                    "Exec Rating": exec_rating,
                    "Speak Rating": speak_rating,
                    "Learn Rating": learn_rating,
                    "Innov Rating": innov_rating,
                    "Budget Rating": budget_rating,
                    "Avg Score": avg_score,
                    "Obj Achieved": obj_achieved,
                    "Prom Ideas": prom_ideas,
                    "Mentor Teams": mentor_teams,
                    "Budget Used Perc": budget_used_perc,
                    "Big Challenge": big_challenge,
                    "Best Thing": best_thing,
                    "Improve Next": improve_next,
                    "Success Story": success_story,
                    "Acknowledgement": acknowledgement,

                    **file_links 
                }

                # 4. Generate Charts & Finalize Data
                with st.spinner("Generating Visualizations & Final Report..."):
                    # Use the EDITED AI content
                    data["AI Report Content"] = st.session_state.ai_report_content
                    
                    # Charts
                    chart_paths = utils.create_event_charts(data)
                    data["Chart Paths"] = chart_paths
                    
                    # Upload Charts to Drive
                    if drive_service and event_folder_id:
                        for path in chart_paths:
                            try:
                                with open(path, 'rb') as f:
                                    utils.upload_to_drive(drive_service, f, os.path.basename(path), event_folder_id)
                            except Exception as e:
                                print(f"Error uploading chart: {e}")

                # 5. Generate PDF
                # Sanitize filename to prevent FileNotFoundError
                safe_prog_name = program_name.replace(" ", "_").replace("/", "_").replace(":", "-")
                pdf_filename = f"Report_{safe_prog_name}.pdf"
                
                # Pass uploaded_files dictionary to generate_pdf for embedding
                utils.generate_pdf(data, pdf_filename, uploaded_files)
                
                with open(pdf_filename, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    
                    # Upload generated PDF to Drive
                    if drive_service and event_folder_id:
                        try:
                            pdf_file.seek(0) # Reset pointer
                            report_link = utils.upload_to_drive(drive_service, pdf_file, pdf_filename, event_folder_id, mimetype='application/pdf')
                            if report_link:
                                data["Report Link"] = report_link
                                st.success(f"✅ Generated Report uploaded to Drive!")
                        except Exception as e:
                            st.error(f"Failed to upload report to Drive: {e}")
                    
                    # Provide Download Button
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label="📥 Download Generated Report",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )

                # 6. Log to Sheets
                if sheets_service:
                    # Flatten social media for sheet
                    sm_str = ", ".join([f"{k}: {v}" for k, v in social_media.items() if v])
                    data["Social Media"] = sm_str
                    
                    utils.append_to_sheet(sheets_service, config.GOOGLE_SHEET_ID, data)
                    st.success("✅ Data logged to Google Sheet!")
                    
                st.balloons()
                
                # Reset State
                st.session_state.report_stage = "input"
                st.session_state.ai_report_content = ""
