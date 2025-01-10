import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
import io




if not os.path.exists("uploads"):
    os.makedirs("uploads")

def reset_db():
    conn = sqlite3.connect('student_registration.db')
    c = conn.cursor()
    
    # Drop existing tables
    c.execute("DROP TABLE IF EXISTS course_registration")
    c.execute("DROP TABLE IF EXISTS student_info")
    c.execute("DROP TABLE IF EXISTS admin")
    
    conn.commit()
    conn.close()
    
    # Reinitialize the database
    init_db()

def init_db():
    conn = sqlite3.connect('student_registration.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert two admin users if they don't exist
    admins = [
        ('admin1', 'admin123', 'admin1@school.edu'),
        ('admin2', 'admin456', 'admin2@school.edu')
    ]
    
    for admin in admins:
        c.execute('''
            INSERT OR IGNORE INTO admin (username, password, email) 
            VALUES (?, ?, ?)
        ''', admin)
    
    c.execute('''
        INSERT OR IGNORE INTO admin (username, password, email) 
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', 'admin@school.edu'))
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_info (
            student_id TEXT PRIMARY KEY,
            surname TEXT,
            other_names TEXT,
            date_of_birth DATE,
            place_of_birth TEXT,
            home_town TEXT,
            residential_address TEXT,
            postal_address TEXT,
            email TEXT,
            telephone TEXT,
            nationality TEXT,
            marital_status TEXT,
            gender TEXT,
            religion TEXT,
            denomination TEXT,
            disability_status TEXT,
            disability_description TEXT,
            guardian_name TEXT,
            guardian_relationship TEXT,
            guardian_occupation TEXT,
            guardian_address TEXT,
            guardian_telephone TEXT,
            previous_school TEXT,
            qualification_type TEXT,
            completion_year TEXT,
            aggregate_score TEXT,
            ghana_card_path TEXT,
            passport_photo_path TEXT,
            transcript_path TEXT,
            certificate_path TEXT,
            approval_status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS course_registration (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            index_number TEXT,
            programme TEXT,
            specialization TEXT,
            level TEXT,
            session TEXT,
            academic_year TEXT,
            semester TEXT,
            courses TEXT,
            total_credits INTEGER,
            date_registered DATE,
            approval_status TEXT DEFAULT 'pending',
            FOREIGN KEY (student_id) REFERENCES student_info (student_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
def get_program_courses(program):
    courses = {
        "CIMG": {
            "Foundation": [
                "CIMG101|Marketing Essentials|3",
                "CIMG102|Marketing Environment|3",
                "CIMG103|Customer Insights|3",
                "CIMG104|Integrated Marketing Communications|3"
            ],
            "Professional Certificate": [
                "CIMG201|Strategic Marketing|3",
                "CIMG202|Marketing Planning Process|3",
                "CIMG203|Marketing Implementation|3",
                "CIMG204|Marketing Metrics|3"
            ],
            "Professional Diploma": [
                "CIMG301|Marketing Strategy Development|6",
                "CIMG302|Leading Marketing|6",
                "CIMG303|Marketing Leadership Decisions|6",
                "CIMG304|Contemporary Marketing Issues|6"
            ]
        },
        "CIM-UK": {
            "Foundation Certificate": [
                "CIM101|Marketing Principles|6",
                "CIM102|Communications in Practice|6",
                "CIM103|Customer Communications|6"
            ],
            "Certificate in Professional Marketing": [
                "CIM201|Applied Marketing|6",
                "CIM202|Planning Campaigns|6",
                "CIM203|Customer Insights|6"
            ],
            "Diploma in Professional Marketing": [
                "CIM301|Marketing & Digital Strategy|6",
                "CIM302|Innovation in Marketing|6",
                "CIM303|Resource Management|6"
            ],
            "Postgraduate Diploma": [
                "CIM401|Global Marketing Decisions|6",
                "CIM402|Corporate Digital Communications|6",
                "CIM403|Creating Entrepreneurial Change|6"
            ]
        },
        "ICAG": {
            "Level 1": [
                "ICAG101|Financial Accounting|3",
                "ICAG102|Business Management & Information Systems|3",
                "ICAG103|Business Law|3",
                "ICAG104|Introduction to Management Accounting|3"
            ],
            "Level 2": [
                "ICAG201|Financial Reporting|3",
                "ICAG202|Management Accounting|3",
                "ICAG203|Audit & Assurance|3",
                "ICAG204|Financial Management|3",
                "ICAG205|Corporate Law|3",
                "ICAG206|Public Sector Accounting|3"
            ],
            "Level 3": [
                "ICAG301|Corporate Reporting|3",
                "ICAG302|Advanced Management Accounting|3",
                "ICAG303|Advanced Audit & Assurance|3",
                "ICAG304|Advanced Financial Management|3",
                "ICAG305|Strategy & Governance|3",
                "ICAG306|Advanced Taxation|3"
            ]
        },
        "ACCA": {
            "Applied Knowledge": [
                "AB101|Accountant in Business|3",
                "MA101|Management Accounting|3",
                "FA101|Financial Accounting|3"
            ],
            "Applied Skills": [
                "LW201|Corporate and Business Law|3",
                "PM201|Performance Management|3",
                "TX201|Taxation|3",
                "FR201|Financial Reporting|3",
                "AA201|Audit and Assurance|3",
                "FM201|Financial Management|3"
            ],
            "Strategic Professional (Essentials)": [
                "SBL301|Strategic Business Leader|6",
                "SBR301|Strategic Business Reporting|6"
            ],
            "Strategic Professional (Options)": [
                "AFM401|Advanced Financial Management|6",
                "APM401|Advanced Performance Management|6",
                "ATX401|Advanced Taxation|6",
                "AAA401|Advanced Audit and Assurance|6"
            ]
        }
    }
    return courses.get(program, {})

def generate_student_info_pdf(data):
    filename = f"student_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=30
    )
    elements.append(Paragraph("STUDENT INFORMATION FORM", header_style))
    
    # Add passport photo if available
    if data['passport_photo_path']:
        try:
            img = Image(data['passport_photo_path'], width=2*inch, height=2*inch)
            elements.append(img)
        except:
            pass
    
    # Personal Information
    elements.append(Paragraph("Personal Information", styles['Heading2']))
    personal_info = [
        ["Student ID:", data['student_id']],
        ["Surname:", data['surname']],
        ["Other Names:", data['other_names']],
        ["Date of Birth:", str(data['date_of_birth'])],
        ["Place of Birth:", data['place_of_birth']],
        ["Home Town:", data['home_town']],
        ["Nationality:", data['nationality']],
        ["Gender:", data['gender']],
        ["Marital Status:", data['marital_status']],
        ["Religion:", data['religion']],
        ["Denomination:", data['denomination']]
    ]
    
    t = Table(personal_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Contact Information
    elements.append(Paragraph("Contact Information", styles['Heading2']))
    contact_info = [
        ["Residential Address:", data['residential_address']],
        ["Postal Address:", data['postal_address']],
        ["Email:", data['email']],
        ["Telephone:", data['telephone']]
    ]
    
    t = Table(contact_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Guardian Information
    elements.append(Paragraph("Guardian Information", styles['Heading2']))
    guardian_info = [
        ["Name:", data['guardian_name']],
        ["Relationship:", data['guardian_relationship']],
        ["Occupation:", data['guardian_occupation']],
        ["Address:", data['guardian_address']],
        ["Telephone:", data['guardian_telephone']]
    ]
    
    t = Table(guardian_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Educational Background
    elements.append(Paragraph("Educational Background", styles['Heading2']))
    education_info = [
        ["Previous School:", data['previous_school']],
        ["Qualification Type:", data['qualification_type']],
        ["Completion Year:", data['completion_year']],
        ["Aggregate Score:", data['aggregate_score']]
    ]
    
    t = Table(education_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    
    doc.build(elements)
    return filename
    
    doc.build(elements)
    return filename

def generate_course_registration_pdf(data):
    filename = f"course_registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=30
    )
    elements.append(Paragraph("COURSE REGISTRATION FORM (A7)", header_style))
    
    # Registration Details
    reg_info = [
        ["Student ID:", data['student_id']],
        ["Index Number:", data['index_number']],
        ["Programme:", data['programme']],
        ["Specialization:", data['specialization']],
        ["Level:", data['level']],
        ["Session:", data['session']],
        ["Academic Year:", data['academic_year']],
        ["Semester:", data['semester']]
    ]
    
    t = Table(reg_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Courses
    elements.append(Paragraph("Selected Courses", styles['Heading2']))
    courses_list = data['courses'].split('\n')
    courses_data = [["Course Code", "Course Title", "Credit Hours"]]
    for course in courses_list:
        if '|' in course:
            courses_data.append(course.split('|'))
    
    t = Table(courses_data, colWidths=[2*inch, 3*inch, 1*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    
    doc.build(elements)
    return filename

def review_student_info(form_data, uploaded_files):
    st.subheader("Review Student Information")
    
    cols = st.columns(2)
    with cols[0]:
        st.write("**Personal Information**")
        st.write(f"Student ID: {form_data['student_id']}")
        st.write(f"Surname: {form_data['surname']}")
        st.write(f"Other Names: {form_data['other_names']}")
        st.write(f"Date of Birth: {form_data['date_of_birth']}")
        st.write(f"Place of Birth: {form_data['place_of_birth']}")
        st.write(f"Home Town: {form_data['home_town']}")
        st.write(f"Nationality: {form_data['nationality']}")
        st.write(f"Gender: {form_data['gender']}")
        st.write(f"Marital Status: {form_data['marital_status']}")
        st.write(f"Religion: {form_data['religion']}")
        st.write(f"Denomination: {form_data['denomination']}")
        
    with cols[1]:
        st.write("**Contact Information**")
        st.write(f"Residential Address: {form_data['residential_address']}")
        st.write(f"Postal Address: {form_data['postal_address']}")
        st.write(f"Email: {form_data['email']}")
        st.write(f"Telephone: {form_data['telephone']}")
        
    st.write("**Guardian Information**")
    st.write(f"Name: {form_data['guardian_name']}")
    st.write(f"Relationship: {form_data['guardian_relationship']}")
    st.write(f"Occupation: {form_data['guardian_occupation']}")
    st.write(f"Address: {form_data['guardian_address']}")
    st.write(f"Telephone: {form_data['guardian_telephone']}")
    
    st.write("**Educational Background**")
    st.write(f"Previous School: {form_data['previous_school']}")
    st.write(f"Qualification: {form_data['qualification_type']}")
    st.write(f"Completion Year: {form_data['completion_year']}")
    st.write(f"Aggregate Score: {form_data['aggregate_score']}")
    
    st.write("**Uploaded Documents**")
    for doc_name, file in uploaded_files.items():
        if file:
            st.write(f"✅ {doc_name} uploaded")
        else:
            st.write(f"❌ {doc_name} not uploaded")
            
def review_student_info(form_data, uploaded_files):
    st.subheader("Review Student Information")
    
    cols = st.columns(2)
    with cols[0]:
        st.write("**Personal Information**")
        st.write(f"Student ID: {form_data['student_id']}")
        st.write(f"Surname: {form_data['surname']}")
        st.write(f"Other Names: {form_data['other_names']}")
        st.write(f"Date of Birth: {form_data['date_of_birth']}")
        st.write(f"Place of Birth: {form_data['place_of_birth']}")
        st.write(f"Home Town: {form_data['home_town']}")
        st.write(f"Nationality: {form_data['nationality']}")
        st.write(f"Gender: {form_data['gender']}")
        st.write(f"Marital Status: {form_data['marital_status']}")
        st.write(f"Religion: {form_data['religion']}")
        st.write(f"Denomination: {form_data['denomination']}")
        
    with cols[1]:
        st.write("**Contact Information**")
        st.write(f"Residential Address: {form_data['residential_address']}")
        st.write(f"Postal Address: {form_data['postal_address']}")
        st.write(f"Email: {form_data['email']}")
        st.write(f"Telephone: {form_data['telephone']}")
        
    st.write("**Guardian Information**")
    st.write(f"Name: {form_data['guardian_name']}")
    st.write(f"Relationship: {form_data['guardian_relationship']}")
    st.write(f"Occupation: {form_data['guardian_occupation']}")
    st.write(f"Address: {form_data['guardian_address']}")
    st.write(f"Telephone: {form_data['guardian_telephone']}")
    
    st.write("**Educational Background**")
    st.write(f"Previous School: {form_data['previous_school']}")
    st.write(f"Qualification: {form_data['qualification_type']}")
    st.write(f"Completion Year: {form_data['completion_year']}")
    st.write(f"Aggregate Score: {form_data['aggregate_score']}")
    
    st.write("**Uploaded Documents**")
    for doc_name, file in uploaded_files.items():
        if file:
            st.write(f"✅ {doc_name} uploaded")
        else:
            st.write(f"❌ {doc_name} not uploaded")
  
def student_info_form():
    st.header("📝 Student Information Form")
    
    form_data = {}
    
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        form_data['student_id'] = st.text_input("Student ID")
        form_data['surname'] = st.text_input("Surname")
        form_data['other_names'] = st.text_input("Other Names")
        form_data['date_of_birth'] = st.date_input("Date of Birth")
        form_data['place_of_birth'] = st.text_input("Place of Birth")
        form_data['home_town'] = st.text_input("Home Town")
        form_data['nationality'] = st.text_input("Nationality")
        
    with col2:
        form_data['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"])
        form_data['marital_status'] = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
        form_data['religion'] = st.text_input("Religion")
        form_data['denomination'] = st.text_input("Denomination")
        disability_status = st.selectbox("Disability Status", ["None", "Yes"])
        form_data['disability_status'] = disability_status
        if disability_status == "Yes":
            form_data['disability_description'] = st.text_area("Disability Description")
        else:
            form_data['disability_description'] = "None"

    st.subheader("Contact Information")
    col3, col4 = st.columns(2)
    
    with col3:
        form_data['residential_address'] = st.text_area("Residential Address")
        form_data['postal_address'] = st.text_area("Postal Address")
        form_data['email'] = st.text_input("Email Address")
        
    with col4:
        form_data['telephone'] = st.text_input("Telephone Number")

    st.subheader("Guardian Information")
    col5, col6 = st.columns(2)
    
    with col5:
        form_data['guardian_name'] = st.text_input("Guardian's Name")
        form_data['guardian_relationship'] = st.text_input("Relationship to Guardian")
        form_data['guardian_occupation'] = st.text_input("Guardian's Occupation")
        
    with col6:
        form_data['guardian_address'] = st.text_area("Guardian's Address")
        form_data['guardian_telephone'] = st.text_input("Guardian's Telephone")

    st.subheader("Educational Background")
    col7, col8 = st.columns(2)
    
    with col7:
        form_data['previous_school'] = st.text_input("Previous School")
        form_data['qualification_type'] = st.text_input("Qualification Type")
        
    with col8:
        form_data['completion_year'] = st.text_input("Year of Completion")
        form_data['aggregate_score'] = st.text_input("Aggregate Score")

    st.subheader("📎 Required Documents")
    col9, col10 = st.columns(2)
    
    with col9:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        ghana_card = st.file_uploader("Upload Ghana Card", type=['pdf', 'jpg', 'png'])
        passport_photo = st.file_uploader("Upload Passport Photo", type=['jpg', 'png'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col10:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        transcript = st.file_uploader("Upload Transcript", type=['pdf'])
        certificate = st.file_uploader("Upload Certificate", type=['pdf'])
        st.markdown('</div>', unsafe_allow_html=True)

    uploaded_files = {
        'Ghana Card': ghana_card,
        'Passport Photo': passport_photo,
        'Transcript': transcript,
        'Certificate': certificate
    }

    if st.button("Review Information"):
        st.session_state.review_mode = True
        st.session_state.form_data = form_data
        st.session_state.uploaded_files = uploaded_files
        st.rerun()
    
    if 'review_mode' in st.session_state and st.session_state.review_mode:
        review_student_info(st.session_state.form_data, st.session_state.uploaded_files)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Information"):
                st.session_state.review_mode = False
                st.rerun()
        
        with col2:
            if st.button("Confirm and Submit"):
                ghana_card_path = save_uploaded_file(ghana_card, "uploads")
                passport_photo_path = save_uploaded_file(passport_photo, "uploads")
                transcript_path = save_uploaded_file(transcript, "uploads")
                certificate_path = save_uploaded_file(certificate, "uploads")
                
                conn = sqlite3.connect('student_registration.db')
                c = conn.cursor()
                
                try:
                    c.execute('''
                        INSERT INTO student_info VALUES 
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (form_data['student_id'], form_data['surname'], form_data['other_names'],
                          form_data['date_of_birth'], form_data['place_of_birth'], form_data['home_town'],
                          form_data['residential_address'], form_data['postal_address'], form_data['email'],
                          form_data['telephone'], form_data['nationality'], form_data['marital_status'],
                          form_data['gender'], form_data['religion'], form_data['denomination'],
                          form_data['disability_status'], form_data['disability_description'],
                          form_data['guardian_name'], form_data['guardian_relationship'],
                          form_data['guardian_occupation'], form_data['guardian_address'],
                          form_data['guardian_telephone'], form_data['previous_school'],
                          form_data['qualification_type'], form_data['completion_year'],
                          form_data['aggregate_score'], ghana_card_path, passport_photo_path,
                          transcript_path, certificate_path, 'pending'))
                    conn.commit()
                    st.success("Information submitted successfully! Pending admin approval.")
                    st.session_state.review_mode = False
                except sqlite3.IntegrityError:
                    st.error("Student ID already exists!")
                finally:
                    conn.close()
                    
                    
def course_registration_form():
    st.header("📚 Course Registration Form (A7)")
    
    form_data = {}
    col1, col2 = st.columns(2)
    
    with col1:
        form_data['student_id'] = st.text_input("Student ID")
        form_data['index_number'] = st.text_input("Index Number")
        form_data['programme'] = st.selectbox(
            "Programme",
            ["CIMG", "CIM-UK", "ICAG", "ACCA"]
        )
        
        # Get program levels
        program_levels = list(get_program_courses(form_data['programme']).keys())
        form_data['level'] = st.selectbox("Level/Part", program_levels)
        
        form_data['specialization'] = st.text_input("Specialization")
        
    with col2:
        form_data['session'] = st.selectbox("Session", ["Morning", "Evening", "Weekend"])
        form_data['academic_year'] = st.selectbox(
            "Academic Year", 
            [f"{year}-{year+1}" for year in range(2023, 2030)]
        )
        form_data['semester'] = st.selectbox("Semester", ["First", "Second", "Third"])
    
    st.subheader("Course Selection")
    # Get courses for selected program and level
    available_courses = get_program_courses(form_data['programme']).get(form_data['level'], [])
    
    # Create multiselect for courses
    selected_courses = st.multiselect(
        "Select Courses",
        available_courses,
        format_func=lambda x: f"{x.split('|')[0]} - {x.split('|')[1]} ({x.split('|')[2]} credits)"
    )
    
    # Calculate total credits
    total_credits = sum([int(course.split("|")[2]) for course in selected_courses])
    
    # Display selected courses in text area
    form_data['courses'] = "\n".join(selected_courses)
    st.text_area("Selected Courses", form_data['courses'], height=150, disabled=True)
    
    # Display and store total credits
    form_data['total_credits'] = st.number_input(
        "Total Credit Hours", 
        value=total_credits,
        min_value=0,
        max_value=24,
        disabled=True
    )
    
    if total_credits > 24:
        st.error("Total credits cannot exceed 24 hours!")
        return

    if st.button("Review Registration"):
        st.session_state.review_mode = True
        st.session_state.form_data = form_data
        st.rerun()
    
    if 'review_mode' in st.session_state and st.session_state.review_mode:
        review_course_registration(form_data)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Registration"):
                st.session_state.review_mode = False
                st.rerun()
        
        with col2:
            if st.button("Confirm and Submit"):
                conn = sqlite3.connect('student_registration.db')
                c = conn.cursor()
                
                try:
                    c.execute('''
                        INSERT INTO course_registration 
                        (student_id, index_number, programme, specialization, level, 
                        session, academic_year, semester, courses, total_credits, 
                        date_registered, approval_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (form_data['student_id'], form_data['index_number'],
                          form_data['programme'], form_data['specialization'],
                          form_data['level'], form_data['session'],
                          form_data['academic_year'], form_data['semester'],
                          form_data['courses'], form_data['total_credits'],
                          datetime.now().date(), 'pending'))
                    conn.commit()
                    st.success("Course registration submitted! Pending admin approval.")
                    # Generate PDF after successful submission
                    pdf_file = generate_course_registration_pdf(form_data)
                    with open(pdf_file, "rb") as file:
                        st.download_button(
                            label="Download Registration Form",
                            data=file,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
                    st.session_state.review_mode = False
                except sqlite3.IntegrityError:
                    st.error("Error in registration. Please check if student ID exists.")
                finally:
                    conn.close()

def admin_dashboard():
    st.title("Admin Dashboard")
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["Pending Approvals", "Student Records", "Course Registrations", 
         "Generate Reports", "Download Forms"]
    )
    
    if menu == "Pending Approvals":
        show_pending_approvals()
    elif menu == "Student Records":
        manage_student_records()
    elif menu == "Course Registrations":
        manage_course_registrations()
    elif menu == "Generate Reports":
        generate_reports()
    else:
        download_forms()

def show_pending_approvals():
    st.subheader("Pending Approvals")
    
    tabs = st.tabs(["Student Information", "Course Registrations"])
    
    with tabs[0]:
        conn = sqlite3.connect('student_registration.db')
        pending_students = pd.read_sql_query(
            "SELECT * FROM student_info WHERE approval_status='pending'", 
            conn
        )
        
        for _, student in pending_students.iterrows():
            with st.expander(f"Student: {student['surname']} {student['other_names']}"):
                st.write(student)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_{student['student_id']}"):
                        c = conn.cursor()
                        c.execute(
                            "UPDATE student_info SET approval_status='approved' WHERE student_id=?",
                            (student['student_id'],)
                        )
                        conn.commit()
                        st.success("Approved!")
                        st.rerun()
                with col2:
                    if st.button("Reject", key=f"reject_{student['student_id']}"):
                        c = conn.cursor()
                        c.execute(
                            "UPDATE student_info SET approval_status='rejected' WHERE student_id=?",
                            (student['student_id'],)
                        )
                        conn.commit()
                        st.error("Rejected!")
                        st.rerun()
    
    with tabs[1]:
        pending_registrations = pd.read_sql_query(
            "SELECT * FROM course_registration WHERE approval_status='pending'", 
            conn
        )
        
        for _, registration in pending_registrations.iterrows():
            with st.expander(f"Registration ID: {registration['registration_id']}"):
                st.write(registration)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_reg_{registration['registration_id']}"):
                        c = conn.cursor()
                        c.execute(
                            "UPDATE course_registration SET approval_status='approved' WHERE registration_id=?",
                            (registration['registration_id'],)
                        )
                        conn.commit()
                        st.success("Approved!")
                        st.rerun()
                with col2:
                    if st.button("Reject", key=f"reject_reg_{registration['registration_id']}"):
                        c = conn.cursor()
                        c.execute(
                            "UPDATE course_registration SET approval_status='rejected' WHERE registration_id=?",
                            (registration['registration_id'],)
                        )
                        conn.commit()
                        st.error("Rejected!")
                        st.rerun()
        
        conn.close()
        
def manage_student_records():
    st.subheader("Student Records Management")
    
    # Search functionality
    search_col1, search_col2 = st.columns([3,1])
    with search_col1:
        search_term = st.text_input("Search by Student ID, Name or Email")
    with search_col2:
        search_status = st.selectbox("Filter by Status", 
            ["All", "Pending", "Approved", "Rejected"])
    
    conn = sqlite3.connect('student_registration.db')
    query = "SELECT * FROM student_info WHERE 1=1"
    
    if search_term:
        query += f''' AND (student_id LIKE '%{search_term}%' 
                    OR surname LIKE '%{search_term}%' 
                    OR other_names LIKE '%{search_term}%'
                    OR email LIKE '%{search_term}%')'''
    
    if search_status != "All":
        query += f" AND approval_status='{search_status.lower()}'"
    
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        for _, student in df.iterrows():
            with st.expander(f"{student['surname']} {student['other_names']} ({student['student_id']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Personal Information**")
                    st.write(f"Student ID: {student['student_id']}")
                    st.write(f"Name: {student['surname']} {student['other_names']}")
                    st.write(f"Date of Birth: {student['date_of_birth']}")
                    st.write(f"Gender: {student['gender']}")
                    
                with col2:
                    st.write("**Contact Information**")
                    st.write(f"Email: {student['email']}")
                    st.write(f"Phone: {student['telephone']}")
                    st.write(f"Address: {student['residential_address']}")
                
                # Generate PDF button
                if st.button("Generate PDF", key=f"pdf_{student['student_id']}"):
                    pdf_file = generate_student_info_pdf(student)
                    with open(pdf_file, "rb") as file:
                        st.download_button(
                            label="Download Student Info",
                            data=file,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
    else:
        st.info("No records found")
    
    conn.close()

def manage_course_registrations():
    st.subheader("Course Registration Management")
    
    search_col1, search_col2 = st.columns([3,1])
    with search_col1:
        search_term = st.text_input("Search by Student ID or Programme")
    with search_col2:
        search_status = st.selectbox("Filter by Status", 
            ["All", "Pending", "Approved", "Rejected"])
    
    conn = sqlite3.connect('student_registration.db')
    query = """
        SELECT cr.*, si.surname, si.other_names 
        FROM course_registration cr 
        LEFT JOIN student_info si ON cr.student_id = si.student_id 
        WHERE 1=1
    """
    
    if search_term:
        query += f''' AND (cr.student_id LIKE '%{search_term}%' 
                    OR cr.programme LIKE '%{search_term}%')'''
    
    if search_status != "All":
        query += f" AND cr.approval_status='{search_status.lower()}'"
    
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        for _, registration in df.iterrows():
            with st.expander(f"Registration ID: {registration['registration_id']} - {registration['surname']} {registration['other_names']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Registration Details**")
                    st.write(f"Student ID: {registration['student_id']}")
                    st.write(f"Programme: {registration['programme']}")
                    st.write(f"Level: {registration['level']}")
                    st.write(f"Session: {registration['session']}")
                
                with col2:
                    st.write("**Academic Information**")
                    st.write(f"Academic Year: {registration['academic_year']}")
                    st.write(f"Semester: {registration['semester']}")
                    st.write(f"Total Credits: {registration['total_credits']}")
                
                st.write("**Courses**")
                st.write(registration['courses'])
                
                # Generate PDF button
                if st.button("Generate PDF", key=f"pdf_reg_{registration['registration_id']}"):
                    pdf_file = generate_course_registration_pdf(registration)
                    with open(pdf_file, "rb") as file:
                        st.download_button(
                            label="Download Registration Form",
                            data=file,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
    else:
        st.info("No records found")
    
    conn.close()

def generate_reports():
    st.subheader("Generate Reports")
    
    report_type = st.selectbox("Select Report Type", [
        "Student Statistics",
        "Course Registration Summary",
        "Approval Status Summary",
        "Programme Statistics"
    ])
    
    conn = sqlite3.connect('student_registration.db')
    
    if report_type == "Student Statistics":
        # Gender distribution
        gender_dist = pd.read_sql_query(
            "SELECT gender, COUNT(*) as count FROM student_info GROUP BY gender",
            conn
        )
        st.write("**Gender Distribution**")
        st.bar_chart(gender_dist.set_index('gender'))
        
        # Programme distribution
        prog_dist = pd.read_sql_query(
            "SELECT programme, COUNT(*) as count FROM course_registration GROUP BY programme",
            conn
        )
        st.write("**Programme Distribution**")
        st.bar_chart(prog_dist.set_index('programme'))
        
    elif report_type == "Course Registration Summary":
        summary = pd.read_sql_query("""
            SELECT cr.programme, cr.level, cr.semester, 
                   COUNT(*) as registrations,
                   AVG(cr.total_credits) as avg_credits
            FROM course_registration cr
            GROUP BY cr.programme, cr.level, cr.semester
        """, conn)
        st.write(summary)
        
    elif report_type == "Approval Status Summary":
        student_status = pd.read_sql_query(
            "SELECT approval_status, COUNT(*) as count FROM student_info GROUP BY approval_status",
            conn
        )
        course_status = pd.read_sql_query(
            "SELECT approval_status, COUNT(*) as count FROM course_registration GROUP BY approval_status",
            conn
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Student Info Approval Status**")
            st.pie_chart(student_status.set_index('approval_status'))
        with col2:
            st.write("**Course Registration Approval Status**")
            st.pie_chart(course_status.set_index('approval_status'))
    
    conn.close()
    
def save_uploaded_file(uploaded_file, directory):
    if uploaded_file is not None:
        file_path = os.path.join("uploads", f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def download_forms():
    st.subheader("Download Forms")
    
    conn = sqlite3.connect('student_registration.db')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Student Information Database**")
        student_df = pd.read_sql_query("SELECT * FROM student_info", conn)
        
        if not student_df.empty:
            csv = student_df.to_csv(index=False)
            st.download_button(
                label="Download Student Database (CSV)",
                data=csv,
                file_name=f"student_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No student records available")
    
    with col2:
        st.write("**Course Registration Database**")
        registration_df = pd.read_sql_query("SELECT * FROM course_registration", conn)
        
        if not registration_df.empty:
            csv = registration_df.to_csv(index=False)
            st.download_button(
                label="Download Course Registrations (CSV)",
                data=csv,
                file_name=f"course_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No registration records available")
    
    st.markdown("---")
    
    # Additional filtering options
    st.subheader("Download Filtered Data")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by Approval Status",
            ["All", "Pending", "Approved", "Rejected"]
        )
    
    with filter_col2:
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        
        # Modified query to handle cases where created_at might not exist
        query = """
            SELECT * FROM student_info 
            WHERE date_of_birth BETWEEN ? AND ?
        """
        
        if status_filter != "All":
            query += f" AND approval_status = '{status_filter.lower()}'"
        
        try:
            filtered_df = pd.read_sql_query(
                query,
                conn,
                params=(start_date, end_date)
            )
            
            if not filtered_df.empty:
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download Filtered Data (CSV)",
                    data=csv,
                    file_name=f"filtered_student_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No records found for the selected filters")
                
        except pd.errors.DatabaseError:
            st.error("Error filtering data. Please try different filter criteria.")
            
    conn.close()

def main():
    st.set_page_config(
        page_title="Student Registration System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
        }
        .upload-section {
            padding: 1rem;
            border-radius: 5px;
            background-color: #f0f2f6;
            margin: 1rem 0;
        }
        .login-form {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add this at the start of your main() function:
    if 'db_initialized' not in st.session_state:
        reset_db()
        st.session_state.db_initialized = True
    
    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    
    # Admin login in sidebar
    if not st.session_state.admin_logged_in:
        with st.sidebar:
            st.subheader("Admin Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                conn = sqlite3.connect('student_registration.db')
                c = conn.cursor()
                c.execute('SELECT * FROM admin WHERE username=? AND password=?', 
                         (username, password))
                admin = c.fetchone()
                conn.close()
                
                if admin:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    # Main navigation
    if st.session_state.admin_logged_in:
        admin_dashboard()
    else:
        page = st.sidebar.radio("Navigation", 
                              ["Student Information", "Course Registration"])
        
        if page == "Student Information":
            student_info_form()
        else:
            course_registration_form()

if __name__ == "__main__":
    init_db()
    main()


