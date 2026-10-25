import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.institution import Institution
from app.models.user import User
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.config import settings
from app.auth import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEMO_INSTITUTIONS = [
    {
        "id": "i1",
        "name": "Sunrise Institute of Technology",
        "city": "Pune",
        "state": "Maharashtra",
        "type": "Engineering",
        "aicte_id": "1-4821039",
        "approved": "2009",
        "contact_email": "principal@sunrise-tech.edu.in",
        "contact_phone": "+91 20 2748 9901",
        "risk_level": "High",
    },
    {
        "id": "i2",
        "name": "Bharat College of Engineering",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "type": "Engineering",
        "aicte_id": "1-3390412",
        "approved": "2004",
        "contact_email": "director@bharatengg.ac.in",
        "contact_phone": "+91 522 289 1102",
        "risk_level": "Moderate",
    },
    {
        "id": "i3",
        "name": "Vidya Polytechnic Institute",
        "city": "Jaipur",
        "state": "Rajasthan",
        "type": "Polytechnic",
        "aicte_id": "1-5120987",
        "approved": "2012",
        "contact_email": "admin@vidyapoly.edu.in",
        "contact_phone": "+91 141 298 3341",
        "risk_level": "Moderate",
    },
    {
        "id": "i4",
        "name": "National Institute of Management Studies",
        "city": "Bengaluru",
        "state": "Karnataka",
        "type": "Management",
        "aicte_id": "1-2784561",
        "approved": "2001",
        "contact_email": "registrar@nims-blr.ac.in",
        "contact_phone": "+91 80 4123 7789",
        "risk_level": "High",
    },
    {
        "id": "i5",
        "name": "Gyan Jyoti Institute of Pharmacy",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "type": "Pharmacy",
        "aicte_id": "1-6045123",
        "approved": "2015",
        "contact_email": "info@gyanjyotipharma.org",
        "contact_phone": "+91 120 488 2011",
        "risk_level": "Low",
    },
    {
        "id": "i6",
        "name": "Himalaya Technical University",
        "city": "Dehradun",
        "state": "Uttarakhand",
        "type": "University",
        "aicte_id": "1-7210045",
        "approved": "2018",
        "contact_email": "vc-office@himalayatech.ac.in",
        "contact_phone": "+91 135 277 8890",
        "risk_level": "High",
    },
    {
        "id": "i7",
        "name": "Kalinga School of Architecture",
        "city": "Bhubaneswar",
        "state": "Odisha",
        "type": "Architecture",
        "aicte_id": "1-8930124",
        "approved": "2011",
        "contact_email": "dean@kalinga-arch.edu.in",
        "contact_phone": "+91 674 233 4455",
        "risk_level": "Low",
    },
]

DEMO_USERS = [
    {
        "id": "u0",
        "name": "Rohit Sharma",
        "email": "rohit.sharma@student.edu.in",
        "role": "Complainant",
        "designation": "Student Complainant (Citizen User)",
        "bureau": "PGRC",
        "avatar_text": "RS",
        "phone": "+91 98765 43210",
        "status": "Active",
        "department": "Complainant / Citizen Portal",
    },
    {
        "id": "u1b",
        "name": "Dr. Priya Nair",
        "email": "priya.nair@aicte-india.org",
        "role": "BureauAdmin",
        "designation": "Bureau Chief & Cell Admin (PGRC)",
        "bureau": "PGRC",
        "avatar_text": "PN",
        "phone": "+91 11 2958 1020",
        "status": "Active",
        "department": "Public Grievance Redressal Cell",
    },
    {
        "id": "u2",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@aicte-india.org",
        "role": "Officer",
        "designation": "Senior Grievance Officer, PGRC",
        "bureau": "PGRC",
        "avatar_text": "RK",
        "phone": "+91 11 2958 1042",
        "status": "Active",
        "department": "PGRC Scrutiny Cell",
    },
    {
        "id": "u1",
        "name": "Dr. S. Mehta",
        "email": "member-sec@aicte-india.org",
        "role": "Admin",
        "designation": "Member Secretary & System Admin",
        "bureau": "All",
        "avatar_text": "SM",
        "phone": "+91 11 2958 1000",
        "status": "Active",
        "department": "Executive Administration",
    },
    {
        "id": "u3",
        "name": "Anita Verma",
        "email": "anita.verma@aicte-india.org",
        "role": "Officer",
        "designation": "Director & Bureau Chief, RB",
        "bureau": "RB",
        "avatar_text": "AV",
        "phone": "+91 11 2958 1077",
        "status": "Active",
        "department": "Regulation Bureau",
    },
    {
        "id": "u4",
        "name": "Meera Iyer",
        "email": "meera.iyer@aicte-india.org",
        "role": "Officer",
        "designation": "Legal Counsel & Officer, RB / Academic",
        "bureau": "RB",
        "avatar_text": "MI",
        "phone": "+91 11 2958 1091",
        "status": "Active",
        "department": "Legal & Academic Cell",
    },
    {
        "id": "u5",
        "name": "Suresh Patel",
        "email": "suresh.patel@aicte-india.org",
        "role": "Officer",
        "designation": "Scrutiny Officer, Approval Bureau",
        "bureau": "Approval",
        "avatar_text": "SP",
        "phone": "+91 11 2958 1115",
        "status": "Active",
        "department": "Approval Bureau Scrutiny",
    },
    {
        "id": "u6",
        "name": "Dr. Arun Sharma",
        "email": "arun.sharma@aicte-india.org",
        "role": "Officer",
        "designation": "Special Inquiries Officer, PGRC",
        "bureau": "PGRC",
        "avatar_text": "AS",
        "phone": "+91 11 2958 1130",
        "status": "Active",
        "department": "Special Grievance Inquiries",
    },
]

DEMO_COMPLAINTS = [
    {
        "id": "RB-2026-0141",
        "institution_id": "i1",
        "institution_permanent_id": "1-4821039",
        "bureau": "RB",
        "category": "Fee Regulation",
        "priority": "Critical",
        "officer": "Anita Verma",
        "status": "Pending",
        "date": "2026-09-28",
        "due": "2026-10-12",
        "title": "Excess tuition fee collected above approved regulatory cap",
        "description": "Parents allege the institute collects tuition roughly 40% above the fee approved by the state Fee Regulatory Committee, with no formal receipts issued for the additional amount.",
        "complainant_type": "Parent",
        "complainant_name": "S. Sundaram",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Jurisdiction verification and preliminary scrutiny by RB Cell",
        "last_action_date": "2026-09-28",
    },
    {
        "id": "PGRC-2026-0873",
        "institution_id": "i1",
        "institution_permanent_id": "1-4821039",
        "bureau": "PGRC",
        "category": "Fee Regulation",
        "priority": "High",
        "officer": "Rajesh Kumar",
        "status": "In Progress",
        "date": "2026-10-02",
        "due": "2026-10-30",
        "title": 'Students report compulsory "development charges" exceeding fee norm',
        "description": "A group of third-year B.Tech students submitted a formal grievance stating the 2026-27 fee notice exceeds the approved schedule by Rs 35,000 under mandatory development charges.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Examine institution counter-affidavit and verify official registers",
        "last_action_date": "2026-10-05",
    },
    {
        "id": "RB-2026-0152",
        "institution_id": "i2",
        "institution_permanent_id": "1-3390412",
        "bureau": "RB",
        "category": "Faculty Norms",
        "priority": "High",
        "officer": "Meera Iyer",
        "status": "In Progress",
        "date": "2026-10-01",
        "due": "2026-10-25",
        "title": "Severe faculty shortage in Computer Science Department",
        "description": "Whistleblower complaint with staff roster stating the CSE department operates at only 42% of required cadre ratio; ghost faculty signatures observed in biometric submissions.",
        "complainant_type": "Whistleblower",
        "complainant_name": "Verified Whistleblower",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Examine institution counter-affidavit and verify official registers",
        "last_action_date": "2026-10-04",
    },
    {
        "id": "PGRC-2026-0890",
        "institution_id": "i2",
        "institution_permanent_id": "1-3390412",
        "bureau": "PGRC",
        "category": "Faculty Norms",
        "priority": "Medium",
        "officer": "Rajesh Kumar",
        "status": "Pending",
        "date": "2026-10-05",
        "due": "2026-11-02",
        "title": "Core subjects skipped due to unavailability of qualified faculty",
        "description": "CSE 5th semester students petition that AI and Cloud Computing lab sessions have been stalled for over 6 weeks due to resignations not filled by the management.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Jurisdiction verification and preliminary scrutiny by PGRC Cell",
        "last_action_date": "2026-10-05",
    },
    {
        "id": "AB-2026-0310",
        "institution_id": "i3",
        "institution_permanent_id": "1-5120987",
        "bureau": "Approval",
        "category": "Infrastructure",
        "priority": "Medium",
        "officer": "Suresh Patel",
        "status": "Resolved",
        "date": "2026-08-14",
        "due": "2026-09-14",
        "title": "Laboratory machinery and licensed software shortfall",
        "description": "Scrutiny committee found deficiencies in CAD software licenses and CNC machines versus declared figures. Institute has procured licenses and submitted compliance evidence.",
        "complainant_type": "General Public",
        "complainant_name": "Verified Whistleblower",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Final compliance order signed and archived",
        "last_action_date": "2026-08-17",
    },
    {
        "id": "RB-2026-0166",
        "institution_id": "i3",
        "institution_permanent_id": "1-5120987",
        "bureau": "RB",
        "category": "Infrastructure",
        "priority": "Critical",
        "officer": "Anita Verma",
        "status": "Escalated",
        "date": "2026-10-08",
        "due": "2026-10-20",
        "title": "Hostel fire safety non-compliance and overcrowding",
        "description": "Municipal fire clearance was revoked in August 2026. The boys hostel houses 180 students beyond structural design limit with obstructed fire escape staircases.",
        "complainant_type": "Whistleblower",
        "complainant_name": "Verified Whistleblower",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Convene expedited joint hearing with institution management",
        "last_action_date": "2026-10-11",
    },
    {
        "id": "PGRC-2026-0902",
        "institution_id": "i4",
        "institution_permanent_id": "1-2784561",
        "bureau": "PGRC",
        "category": "Admission Irregularity",
        "priority": "High",
        "officer": "Rajesh Kumar",
        "status": "Pending",
        "date": "2026-10-10",
        "due": "2026-11-05",
        "title": "Direct MBA admissions bypassing centralised state counselling",
        "description": "Candidate claims management demanded Rs 2.5 Lakh cash donation for an MBA seat outside the designated CAT/CMAT institutional round.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Jurisdiction verification and preliminary scrutiny by PGRC Cell",
        "last_action_date": "2026-10-10",
    },
    {
        "id": "RB-2026-0171",
        "institution_id": "i4",
        "institution_permanent_id": "1-2784561",
        "bureau": "RB",
        "category": "Admission Irregularity",
        "priority": "High",
        "officer": "Meera Iyer",
        "status": "Pending",
        "date": "2026-10-11",
        "due": "2026-10-22",
        "title": "Management quota seat intake exceeded sanctioned threshold",
        "description": "Investigation referral that total sanctioned intake of 120 seats was breached, with 148 candidates enrolled in the 2026 MBA batch.",
        "complainant_type": "Whistleblower",
        "complainant_name": "Verified Whistleblower",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Jurisdiction verification and preliminary scrutiny by RB Cell",
        "last_action_date": "2026-10-11",
    },
    {
        "id": "PGRC-2026-0915",
        "institution_id": "i5",
        "institution_permanent_id": "1-6045123",
        "bureau": "PGRC",
        "category": "Certificate Delay",
        "priority": "Low",
        "officer": "Suresh Patel",
        "status": "Resolved",
        "date": "2026-09-20",
        "due": "2026-10-10",
        "title": "Withholding of B.Pharm provisional degree and migration documents",
        "description": "Graduate was denied clearance certificates citing pending alumni association contribution. Notice served; institute has released all credentials.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Final compliance order signed and archived",
        "last_action_date": "2026-09-23",
    },
    {
        "id": "ACD-2026-0044",
        "institution_id": "i5",
        "institution_permanent_id": "1-6045123",
        "bureau": "Academic",
        "category": "Curriculum",
        "priority": "Low",
        "officer": "Meera Iyer",
        "status": "Resolved",
        "date": "2026-09-02",
        "due": "2026-10-02",
        "title": "Failure to implement AICTE Model Curriculum 2024 revision",
        "description": "Faculty complaint that college continues teaching outdated 2019 syllabus ignoring PCI and AICTE revised elective modules. Syllabus alignment verified.",
        "complainant_type": "Faculty",
        "complainant_name": "Dr. K. Ramanathan",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Final compliance order signed and archived",
        "last_action_date": "2026-09-05",
    },
    {
        "id": "RB-2026-0180",
        "institution_id": "i6",
        "institution_permanent_id": "1-7210045",
        "bureau": "RB",
        "category": "Unapproved Courses",
        "priority": "Critical",
        "officer": "Anita Verma",
        "status": "In Progress",
        "date": "2026-10-15",
        "due": "2026-10-28",
        "title": "Operating unapproved M.Tech in Data Science & Cyber Security",
        "description": "Admissions enrolled 45 candidates for an M.Tech program without obtaining approval in the current approval process handbook cycle.",
        "complainant_type": "Whistleblower",
        "complainant_name": "Verified Whistleblower",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Examine institution counter-affidavit and verify official registers",
        "last_action_date": "2026-10-18",
    },
    {
        "id": "PGRC-2026-0921",
        "institution_id": "i6",
        "institution_permanent_id": "1-7210045",
        "bureau": "PGRC",
        "category": "Unapproved Courses",
        "priority": "High",
        "officer": "Rajesh Kumar",
        "status": "In Progress",
        "date": "2026-10-16",
        "due": "2026-11-08",
        "title": "Enrolled students demand refund and transfer for unapproved degree",
        "description": "Students discovered their course is not listed on the AICTE portal and petitioned PGRC for immediate refund of first semester tuition and migration assistance.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Examine institution counter-affidavit and verify official registers",
        "last_action_date": "2026-10-19",
    },
    {
        "id": "PGRC-2026-0930",
        "institution_id": "i2",
        "institution_permanent_id": "1-3390412",
        "bureau": "PGRC",
        "category": "Harassment & Ragging",
        "priority": "Critical",
        "officer": "Dr. Arun Sharma",
        "status": "Escalated",
        "date": "2026-10-18",
        "due": "2026-10-23",
        "title": "Failure of Institutional Anti-Ragging Committee to respond to complaint",
        "description": "First-year student submitted police report extract alleging systemic harassment in hostel block 3 without action by the college anti-ragging squad.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Convene expedited joint hearing with institution management",
        "last_action_date": "2026-10-21",
    },
    {
        "id": "AB-2026-0322",
        "institution_id": "i1",
        "institution_permanent_id": "1-4821039",
        "bureau": "Approval",
        "category": "Infrastructure",
        "priority": "Low",
        "officer": "Rajesh Kumar",
        "status": "Pending",
        "date": "2026-10-19",
        "due": "2026-11-12",
        "title": "Library digital access and volume count below mandatory norm",
        "description": "Complaint notes e-journal subscriptions expired in June and reading hall area does not meet 400 sq. meter requirement.",
        "complainant_type": "Faculty",
        "complainant_name": "Dr. K. Ramanathan",
        "complainant_email": "citizen.grievance@aicte-portal.in",
        "next_action": "Jurisdiction verification and preliminary scrutiny by Approval Cell",
        "last_action_date": "2026-10-19",
    },
    {
        "id": "SB-2026-0051",
        "institution_id": "i7",
        "institution_permanent_id": "1-8930124",
        "bureau": "SB",
        "category": "Skill Certification",
        "priority": "Medium",
        "officer": "Anita Verma",
        "status": "In Progress",
        "date": "2026-10-14",
        "due": "2026-11-04",
        "title": "B.Des interior design apprenticeship stipend deduction grievance",
        "description": "Trainees under the NEAT initiative report unauthorized deduction of 30% from the mandated monthly government stipend.",
        "complainant_type": "Student",
        "complainant_name": "Rohit Sharma",
        "complainant_email": "rohit.sharma@student.edu.in",
        "next_action": "Examine institution counter-affidavit and verify official registers",
        "last_action_date": "2026-10-17",
    },
]

def seed_demo_data(db: Session) -> None:
    logger.info("Starting idempotent seeding for Abhigyan Phase 1 & 2A...")

    # 1. Seed Institutions
    inst_count = 0
    for item in DEMO_INSTITUTIONS:
        existing = db.query(Institution).filter(
            (Institution.id == item["id"]) | (Institution.aicte_id == item["aicte_id"])
        ).first()

        if existing:
            # Update fields
            existing.name = item["name"]
            existing.city = item["city"]
            existing.state = item["state"]
            existing.type = item["type"]
            existing.approved = item["approved"]
            existing.contact_email = item["contact_email"]
            existing.contact_phone = item["contact_phone"]
            existing.risk_level = item["risk_level"]
        else:
            new_inst = Institution(**item)
            db.add(new_inst)
            inst_count += 1

    # 2. Seed Users
    user_count = 0
    default_pwd_hash = hash_password(settings.DEFAULT_SEED_PASSWORD)
    for item in DEMO_USERS:
        existing = db.query(User).filter(
            (User.id == item["id"]) | (User.email == item["email"])
        ).first()

        if existing:
            existing.name = item["name"]
            existing.role = item["role"]
            existing.designation = item["designation"]
            existing.bureau = item["bureau"]
            existing.avatar_text = item["avatar_text"]
            existing.phone = item["phone"]
            existing.status = item["status"]
            existing.department = item.get("department")
            if not existing.password_hash:
                existing.password_hash = default_pwd_hash
        else:
            user_data = dict(item)
            user_data["password_hash"] = default_pwd_hash
            new_user = User(**user_data)
            db.add(new_user)
            user_count += 1

    db.flush()

    # 3. Seed Complaints
    complaint_count = 0
    for item in DEMO_COMPLAINTS:
        existing = db.query(Complaint).filter(Complaint.id == item["id"]).first()

        # Resolve assigned_user_id
        assigned_user = db.query(User).filter(User.name == item["officer"]).first()
        assigned_user_id = assigned_user.id if assigned_user else None

        if existing:
            existing.institution_id = item["institution_id"]
            existing.institution_permanent_id = item["institution_permanent_id"]
            existing.bureau = item["bureau"]
            existing.category = item["category"]
            existing.priority = item["priority"]
            existing.officer = item["officer"]
            existing.assigned_user_id = assigned_user_id
            existing.status = item["status"]
            existing.date = item["date"]
            existing.due = item["due"]
            existing.title = item["title"]
            existing.description = item["description"]
            existing.complainant_type = item["complainant_type"]
            existing.complainant_name = item["complainant_name"]
            existing.complainant_email = item["complainant_email"]
            existing.next_action = item["next_action"]
            existing.last_action_date = item["last_action_date"]
        else:
            complaint_dict = dict(item)
            complaint_dict["assigned_user_id"] = assigned_user_id
            new_complaint = Complaint(**complaint_dict)
            db.add(new_complaint)
            complaint_count += 1

    db.flush()

    # 4. Seed Complaint Timeline events idempotently
    timeline_count = 0
    for item in DEMO_COMPLAINTS:
        existing_timeline = db.query(ComplaintTimeline).filter(ComplaintTimeline.complaint_id == item["id"]).first()
        if not existing_timeline:
            c_date = item["date"]
            # 1. Intake
            db.add(ComplaintTimeline(
                complaint_id=item["id"],
                label="Complaint registered and verified on AICTE portal",
                date=f"{c_date} 10:00",
                by="System / Portal",
                role="Complainant",
                note="Portal intake verified; acknowledgement issued to complainant.",
                user_id=None,
            ))
            # 2. Assignment
            assigned_user = db.query(User).filter(User.name == item["officer"]).first()
            user_id = assigned_user.id if assigned_user else None
            db.add(ComplaintTimeline(
                complaint_id=item["id"],
                label=f"Assigned to {item['officer']} ({item['bureau']} Bureau)",
                date=f"{c_date} 11:30",
                by="Dr. S. Mehta (Member Secretary & System Admin)",
                role="Admin",
                note=f"Initial statutory assignment to {item['bureau']} Bureau based on subject classification.",
                user_id=user_id,
            ))
            # 3. Status transition if not Pending
            if item["status"] != "Pending":
                action_label = "Investigation complete & Marked Resolved" if item["status"] == "Resolved" else f"Case status updated to {item['status']}"
                esc_note = "Escalated to Bureau Head due to SLA breach and severity." if item["status"] == "Escalated" else None
                db.add(ComplaintTimeline(
                    complaint_id=item["id"],
                    label=action_label,
                    date=f"{item['last_action_date']} 14:00",
                    by=f"{item['officer']} (Handling Officer)",
                    role="Officer",
                    note=esc_note,
                    user_id=user_id,
                ))
            timeline_count += 1

    db.commit()
    logger.info(
        "Idempotent seed complete! Added %d new institutions, %d new users, %d new complaints, seeded timelines for %d complaints.",
        inst_count,
        user_count,
        complaint_count,
        timeline_count
    )

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_demo_data(db)
    except Exception as e:
        logger.error("Seeding failed: %s", str(e))
        sys.exit(1)
    finally:
        db.close()
