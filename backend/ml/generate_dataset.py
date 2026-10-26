"""
Script to generate synthetic training dataset for AI-based complaint classification prototype.
This dataset is strictly synthetic and created for local development and testing purposes.
"""
import csv
import os

DATASET = [
    # Fee Regulation (20 examples) -> bureau: PGRC or RB
    {
        "title": "Excess tuition fee charged above regulatory cap",
        "description": "The private technical institute is charging 50000 rupees extra as mandatory development fee above the prescribed state fee committee ceiling without issuing proper receipts.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Refusal to refund capitation and admission fee after cancellation",
        "description": "Student withdrew admission within the designated cutoff period, but the college administration is withholding the entire tuition deposit citing internal management rules.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Demand for donation during management quota seat allotment",
        "description": "College authorities are demanding cash donation payments over and above the regular tuition fees for BTech computer engineering admissions.",
        "category": "Fee Regulation",
        "bureau": "RB",
        "priority": "Critical"
    },
    {
        "title": "Compulsory purchase of expensive uniform and books from campus store",
        "description": "First-year engineering students are being forced to pay double retail prices for uniform and stationary kits exclusively sold by the principal's vendor.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Illegal examination registration penalty fee imposed without notice",
        "description": "The institution levied an arbitrary late fine of ten thousand rupees for semester exam enrollment despite portal downtime on the last date.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Non-refund of hostel caution deposit to graduating batch",
        "description": "Final year students who completed their degree 6 months ago have still not received their refundable hostel security deposit.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Overcharging bus transport charges during remote online classes",
        "description": "Management is levying full annual transportation and fuel fees even when all semester lectures were conducted remotely.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Low"
    },
    {
        "title": "Arbitrary hiking of semester tuition fee mid-course",
        "description": "The engineering college suddenly raised tuition fees by twenty-five percent in third year, contrary to the prospectus terms agreed at admission.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Withholding original documents until extra payment is settled",
        "description": "College office refuses to return 10th and 12th original certificates unless student pays extra unapproved library enhancement charge.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Charging fee for campus placement and aptitude training without consent",
        "description": "Institute deducted fifteen thousand rupees directly from caution money under mandatory training fee heads that were never authorized.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Excess laboratory breakage charges billed uniformly to all students",
        "description": "Department issued a blanket penalty invoice to every student without investigating specific equipment damage in the mechanics lab.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Low"
    },
    {
        "title": "Extortionate fee for issuing duplicate identity cards and hall tickets",
        "description": "Students are being charged two thousand rupees per exam hall ticket re-print when the actual printing cost is negligible.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Low"
    },
    {
        "title": "Failure to provide fee receipts for cash payments",
        "description": "Accounts department collects cash for sports amenities and alumni association fees without generating valid computerized receipts.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Forced donation to college trust for issuance of migration certificate",
        "description": "Passing out diploma students are compelled to donate funds to the founder's trust in order to obtain clearance certificates.",
        "category": "Fee Regulation",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Overcharging fee from scholarship students",
        "description": "Reserved category students receiving government scholarships are being pressured to pay full tuition in advance under threat of suspension.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Unreasonable fee increase for MBA executive evening batch",
        "description": "Tuition fees were inflated by 40 percent without following state fee regulatory norms or taking prior approval.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Unregulated fine for low classroom attendance",
        "description": "College management charges 500 rupees per missed lecture hour as condonation fee, operating an extortion racket on students.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Disproportionate internet and wifi maintenance levy",
        "description": "Annual wifi fee collected from campus hostellers despite non-functional broadband routers throughout the academic year.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Low"
    },
    {
        "title": "Refusal to adjust excess fee paid during counseling round",
        "description": "Candidate deposited surplus amount during centralized seat allotment which the college registrar refuses to credit towards semester dues.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Direct bribe demand by clerk for clearing fee concession file",
        "description": "Administrative clerk asked for ten thousand cash bribe to process government fee waiver application for eligible student.",
        "category": "Fee Regulation",
        "bureau": "RB",
        "priority": "Critical"
    },

    # Faculty Norms (20 examples) -> bureau: Approval
    {
        "title": "Severe faculty shortage in Computer Science and Engineering department",
        "description": "CSE department is operating with only 4 full-time teachers against the required 24 sanctioned posts under council student-faculty ratio norms.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unqualified faculty teaching postgraduate engineering programs",
        "description": "MTech VLSI courses are being handled by fresh BTech passout ad-hoc instructors who lack requisite Master's degrees and research qualifications.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Ghost faculty listed in compliance portal during annual inspection",
        "description": "College presented fake faculty Aadhaar records and guest lecturers as full-time regular professors during surprise regulatory inspection.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Non-payment of faculty salaries for six consecutive months",
        "description": "Assistant professors and lab staff have not received their monthly pay according to 7th pay commission scales, disrupting classes.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Lack of required PhD professors and department heads in Mechanical stream",
        "description": "The mechanical branch has zero doctorate holders and no eligible professor to serve as authorized head of department.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Biometric attendance fraud practiced by teaching faculty",
        "description": "Permanent faculty members register morning biometric attendance and leave campus to teach at private coaching institutes all day.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Contractual adjunct lecturers deployed for entire core curriculum",
        "description": "Over eighty percent of engineering subjects are taught by temporary contract staff with high turnover, affecting syllabus completion.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Withholding faculty original degree certificates and relieving letters",
        "description": "College management confiscated original certificates of teaching staff to prevent them from resigning or seeking other appointments.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Incompetent faculty unable to conduct required laboratory practicals",
        "description": "Newly recruited electrical teachers are unable to demonstrate power electronics lab experiments due to complete lack of training.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Violation of teacher-student ratio in Architecture branch",
        "description": "Architecture department has 1 teacher for 40 students against mandatory council guidelines of 1 to 10 ratio.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "No regular full-time Principal appointed for past three years",
        "description": "Technical institute running without a qualified statutory Principal, relying on non-academic trustee as acting head.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unapproved mass termination of senior professors before semester start",
        "description": "Management fired tenured faculty members without inquiry or notice period to replace them with underpaid trainees.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Faculty forced to do non-academic marketing and admission sales duties",
        "description": "Professors are forced to distribute admission pamphlets and meet enrollment quotas instead of conducting research and teaching.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Absence of qualified lab technicians in chemical engineering workshops",
        "description": "Hazardous chemistry labs are run without certified laboratory technicians, causing dangerous chemical handling by students.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Fabricated faculty experience credentials submitted for AICTE approval",
        "description": "Institute submitted forged service certificates for 5 teaching members to satisfy minimum experience criteria for NBA accreditation.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Faculty absent from lectures without assigning substitute mentors",
        "description": "Mathematics and Digital Signal Processing classes are repeatedly cancelled due to chronic absenteeism of assigned faculty.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Underpayment of ad-hoc faculty below minimum wage statutory limits",
        "description": "Visiting lecturers are paid an exploitative sum of 200 rupees per hour with no social security or provident fund contribution.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Excessive teaching workload exceeding 30 credit hours per week",
        "description": "Assistant professors are burdened with 32 teaching contact hours weekly, violating workload guidelines and quality standards.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Lack of required research publications among postgraduate faculty",
        "description": "PG faculty in Artificial Intelligence have zero peer-reviewed Scopus publications, contrary to university qualification rules.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Faculty recruitment conducted without publicly advertised open selection",
        "description": "College appointed family relatives of trust members to associate professor posts without publishing any recruitment advertisement.",
        "category": "Faculty Norms",
        "bureau": "Approval",
        "priority": "Medium"
    },

    # Infrastructure (20 examples) -> bureau: Approval
    {
        "title": "Dilapidated building with severe structural cracks and roof leakage",
        "description": "Academic block classroom ceilings have chunks of concrete falling during monsoon, posing immediate life hazards to students.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Lack of fire safety NOC and absent emergency exit stairs",
        "description": "Four-story engineering library operates without fire extinguisher maintenance, smoke alarms, or mandatory fire department clearance.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Computer laboratories lacking functional computers and software licenses",
        "description": "Out of 60 terminals in the data structures lab, 45 systems are permanently out of order with broken monitors and power cables.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "No clean drinking water facility available across campus",
        "description": "Water filtration plants are completely broken and students are falling ill due to contaminated groundwater in water coolers.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Absence of disabled accessible ramps and elevators in multi-story blocks",
        "description": "Physically handicapped students are unable to reach 3rd floor classrooms because no lifts or wheelchair ramps are provided.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unhygienic student toilets with broken plumbing and zero maintenance",
        "description": "Boys and girls washrooms lack running water, doors have broken latches, and extreme stench makes facilities unusable.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Defunct equipment in electrical machines and thermodynamics lab",
        "description": "All major motors and calorimeters shown in the lab brochure are non-functional junk models, preventing hands-on practicals.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Overcrowded hostel dormitories with poor ventilation and pest infestation",
        "description": "Rooms approved for double occupancy have 6 students crammed in with bedbug infestation and no functioning ceiling fans.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Non-functional campus internet and absence of digital library terminals",
        "description": "Institute boasts 100 Mbps fiber connectivity on brochure but Wi-Fi has been dead for 4 months with no library internet access.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Lack of proper campus boundary wall endangering student safety",
        "description": "Open boundary allows stray animals and unauthorized trespassers into girls hostel vicinity at night with no security guards.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Inadequate books and outdated volume editions in central library",
        "description": "Library lacks required AICTE recommended national and international journals and books are more than 15 years old.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Frequent power outages in labs due to lack of diesel generator backup",
        "description": "Power cuts halt lab exams midway and institute has not installed required DG sets or UPS backup for computing centers.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Dangerous chemical storage in chemistry lab without exhaust fume hoods",
        "description": "Toxic acids and volatile reagents are stored in unventilated wooden cabinets without emergency eye-wash showers.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Absence of sports ground and physical education amenities",
        "description": "Institute built commercial shops on designated playground land, leaving zero sports facilities for students.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Substandard mess food causing multiple food poisoning incidents",
        "description": "Hostel cafeteria serves stale rotten food cooked in unhygienic conditions leading to hospital admission of 8 hostelers.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Absence of basic medical dispensary and first aid on campus",
        "description": "No doctor, nurse, or basic emergency stretcher available when a student suffered an injury in the mechanical workshop.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Air conditioning and ventilation breakdown in seminar halls",
        "description": "Central auditoriums lack cross-ventilation and broken AC units render workshops unbearable during peak summer.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Encroachment on green buffer zones and unpaved muddy approach roads",
        "description": "Access road to engineering college is completely waterlogged and impassable during rains with heavy construction debris.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Low"
    },
    {
        "title": "Workshop machinery lacks protective guards and safety gear",
        "description": "Lathe machines and welding stations do not have spark guards, face shields, or safety helmets for student operators.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unapproved rooftop temporary shed structures used as regular lecture rooms",
        "description": "Tin-sheet sheds built without municipal sanction are used to conduct second-year lectures under extreme weather conditions.",
        "category": "Infrastructure",
        "bureau": "Approval",
        "priority": "Critical"
    },

    # Admission Irregularity (20 examples) -> bureau: Approval or RB
    {
        "title": "Admissions granted beyond sanctioned intake capacity in BTech IT",
        "description": "The college admitted 150 students against an approved intake capacity of only 60 seats by issuing fake provisional letters.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Violation of state merit list and cutoff ranks in institutional quota",
        "description": "Candidates with ranks lower than 50000 were allotted engineering seats while deserving top rankers were denied admission.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Backdoor management quota admissions without qualifying entrance test",
        "description": "Students who never appeared in state CET or JEE were admitted directly after paying under-the-table cash amounts.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Critical"
    },
    {
        "title": "Reservation policy and category quota ignored during seat allotment",
        "description": "Institute converted reserved SC/ST/OBC category seats into unreserved paid quota seats without government de-reservation permission.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Refusal to return original 10th and 12th marksheets after admission verification",
        "description": "College registry confiscated original migration and school certificates to forcibly retain students who wished to transfer.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Misleading advertisement promising false 100% placement guarantees",
        "description": "Prospectus falsely claimed tier-1 tech company recruitment tie-ups and artificial NIRF ranking badges to trap new applicants.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Admission cancelled arbitrarily without notice to accommodate high-paying candidate",
        "description": "Provisional seat confirmed through centralized counseling round was cancelled overnight without explanation by college dean.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Critical"
    },
    {
        "title": "Fake lateral entry admissions directly into third semester diploma",
        "description": "Institute enrolled candidates lacking ITI or 12th vocational credentials directly into 2nd year polytechnic programs.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Charging counseling registration processing fee exceeding official ceiling",
        "description": "College charged ten thousand rupees as spot counseling form fee against the statutory limit of one thousand.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Medium"
    },
    {
        "title": "Non-reporting of vacant seats to state centralized admission authority",
        "description": "Management concealed 30 vacant BTech seats from public portal to sell them off at inflated rates in offline spot rounds.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Admission granted after prescribed national cutoff closing deadline",
        "description": "Institute admitted candidates two months after the national closing deadline, leaving students unregistered with the university.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Falsification of eligibility certificates during NRI quota admissions",
        "description": "Domestic resident candidates were illegally enrolled under NRI sponsorship category with forged relation affidavits.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Forced transfer of students to unapproved sister branch",
        "description": "Students enrolled in Computer Science were forcibly shifted to Mining engineering citing internal branch restructuring.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Discriminatory denial of admission to students with disabilities",
        "description": "Candidate with locomotor disability was denied allotted seat despite qualifying state merit quota cutoff.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Critical"
    },
    {
        "title": "Unfair cancellation fee deduction during early withdrawal window",
        "description": "Institute deducted 80 percent of paid fees upon withdrawal three weeks before class commencement date.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Medium"
    },
    {
        "title": "Tampering with institutional counseling attendance register",
        "description": "Staff marked eligible candidates as absent during spot counseling to favor local acquaintances.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Non-recognition of entrance test scores from other authorized states",
        "description": "College arbitrarily disqualified valid national scorecards contrary to national technical entrance guidelines.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "Medium"
    },
    {
        "title": "Unregistered admission agents soliciting commissions outside campus",
        "description": "Touts operating outside campus promise confirmed BTech admission against cash commission with insider staff collusion.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "High"
    },
    {
        "title": "Withholding seat cancellation acknowledgment receipt",
        "description": "Student submitted withdrawal letter within legal period but management delayed receipt until cutoff date passed.",
        "category": "Admission Irregularity",
        "bureau": "RB",
        "priority": "Medium"
    },
    {
        "title": "Falsification of candidate domicile records for local state quota",
        "description": "Non-domicile candidates were awarded state quota seats through forged residence certificates arranged by college agents.",
        "category": "Admission Irregularity",
        "bureau": "Approval",
        "priority": "High"
    },

    # Certificate Delay (20 examples) -> bureau: Academic or SB
    {
        "title": "Delay of over two years in issuing final BTech degree certificate",
        "description": "Graduates of 2024 batch have still not been awarded their official degree certificates by the university exam cell.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Withholding consolidated marksheet and provisional passing certificate",
        "description": "University examination division has delayed issuing consolidated grade cards for 8 months, affecting student job offers.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Non-issuance of diploma transcripts required for overseas university application",
        "description": "Registrar office has not processed verified official academic transcripts despite payment of expedited fees two months ago.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Delay in releasing migration certificate for postgraduate studies",
        "description": "Student is unable to complete Master's enrollment at an IIT because previous college has withheld migration certificate for 90 days.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Delay in rectification of spelling mistake on degree certificate",
        "description": "Degree certificate printed candidate name incorrectly; correction application pending for 10 months without action.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Unreasonable delay in issuing backlog revaluation marksheet",
        "description": "Revaluation result declared six months ago but updated grade sheet has not been dispatched, blocking campus placement joining.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Delay in issuing internship completion certificate",
        "description": "Vocational cell has withheld AICTE-mandated industrial internship certificates for an entire batch without valid reason.",
        "category": "Certificate Delay",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Loss of original records by exam cell and refusal to issue duplicate",
        "description": "University exam branch lost physical ledger records and is asking student to re-appear for passed semesters.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Critical"
    },
    {
        "title": "Delay in delivery of convocation degree to overseas distance students",
        "description": "Convocation was held a year ago but degree parcels have not been dispatched to overseas engineering graduates.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Delay in issuing character and conduct transfer certificate",
        "description": "College office keeps postponing issuance of TC and conduct certificate, jeopardizing admission into defense academy.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Delay in releasing skill certification assessment report",
        "description": "National vocational program trainees have not received assessment certificates 6 months after practical exam.",
        "category": "Certificate Delay",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Online certificate download portal throwing server errors for months",
        "description": "University digital repository generates corrupt PDF certificates and technical support fails to respond to tickets.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Bureaucratic delay in issuing medium of instruction certificate",
        "description": "Dean's office taking over 6 weeks to issue simple one-page English medium of instruction certificate for visa processing.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Delay in issuing provisional certificate to passed diploma students",
        "description": "Polytechnic students cannot register with state employment exchange due to five-month delay in diploma certificates.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Withholding degree due to internal dispute between college and affiliating university",
        "description": "Students are victimized as affiliating university withheld degrees because college failed to pay annual affiliation fee.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Failure to issue duplicate certificate after fire in examination office",
        "description": "Applicant filed for duplicate marksheet after disaster but exam controller has sat on request for over a year.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Delay in attestation of marksheets for WES credential evaluation",
        "description": "Registrar desk is not clearing pending WES transcript verification requests within stipulated university timelines.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Delay in releasing AICTE scholarship verification certificate",
        "description": "Institute nodal officer failed to endorse scholarship eligibility certificate, delaying disbursal of student stipend.",
        "category": "Certificate Delay",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Failure to dispatch provisional degree certificate to student home address",
        "description": "Postal dispatch charges collected from all outstation candidates but certificates remain piled up in college basement.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Extortionate demands by clerk to expedite marksheet verification",
        "description": "Dispatch clerk demanded five thousand rupees bribe to stamp and release degree verification document for public sector job.",
        "category": "Certificate Delay",
        "bureau": "Academic",
        "priority": "Critical"
    },

    # Curriculum (20 examples) -> bureau: Academic
    {
        "title": "Outdated engineering syllabus failing to cover modern computing topics",
        "description": "Computer science curriculum still teaches obsolete 1990s Pascal and Turbo C compiler without any cloud or modern programming topics.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Failure to complete 50 percent of syllabus before semester end examinations",
        "description": "Teachers barely covered unit 1 and unit 2 before university declared final exam dates without completing the remaining 3 units.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Non-implementation of revised AICTE model curriculum guidelines",
        "description": "The autonomous institution has not adopted the AICTE recommended credit framework and mandatory humanities electives.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Lack of practical laboratory experiments matching theoretical syllabus",
        "description": "Students are tested on advanced VLSI circuit design in exams while labs only have basic breadboard resistor setups.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Refusal to permit academic credit transfer under National Education Policy",
        "description": "College denies credit transfer for SWAYAM and NPTEL online MOOC courses completed with distinction by students.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Arbitrary change of examination syllabus one week prior to exams",
        "description": "Academic council introduced two brand new textbook reference units right before exams, triggering extreme student anxiety.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Absence of elective choice in multi-disciplinary curriculum",
        "description": "Prospectus promised artificial intelligence and robotics electives, but college forcibly allocated power plant engineering to all.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Total omission of industrial internship credits from curriculum evaluation",
        "description": "Department refused to assess or award credits for mandatory two-month summer internships completed at certified industries.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Discrepancy between syllabus guidelines and questions set in final exam",
        "description": "Entire question paper was prepared from non-prescribed foreign syllabi outside the published curriculum blueprint.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Lack of open source and practical software tools in curriculum delivery",
        "description": "Students are forced to memorize rote syntax on blackboards without any compiler access or hands-on software labs.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Non-provision of course materials and lecture notes for regional language students",
        "description": "No translated course content or bilingual learning material provided despite AICTE regional language technical education policy.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Sudden reduction of semester teaching days below mandatory 90-day threshold",
        "description": "College concluded the entire semester in barely 45 working days, compromising core curriculum depth.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Failure to constitute Board of Studies for new emerging technology courses",
        "description": "College launched BTech in Data Science without convening Board of Studies or getting academic council curriculum approval.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },
    {
        "title": "Excessive continuous assessment weightage with subjective evaluation bias",
        "description": "Internal assessment rubrics are non-transparent and manipulated by faculty to favor specific students.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Exclusion of environmental studies and professional ethics from diploma syllabus",
        "description": "Polytechnic syllabus bypassed mandatory statutory environmental engineering and professional ethics modules.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Absence of project guide mentorship for final year capstone thesis",
        "description": "Final year engineering students are left without guides for senior projects, forcing them to buy ready-made projects from vendors.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Unapproved cancellation of foreign language open elective courses",
        "description": "Japanese and German language courses were terminated midway through semester without refund or substitute options.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Non-alignment of vocational diploma curriculum with National Skill Qualification Framework",
        "description": "D.Voc syllabus does not align with NSQF level 5 standards, rendering passing students ineligible for industry apprenticeships.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Medium"
    },
    {
        "title": "Repetition of identical exam questions for three consecutive examination cycles",
        "description": "University question paper setters simply photocopied past year papers word-for-word, degrading educational assessment standards.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "Low"
    },
    {
        "title": "Syllabus revision implemented retroactively on graduating final year batch",
        "description": "Graduating seniors were retroactively told to clear two extra foundation subjects to be eligible for degree conferral.",
        "category": "Curriculum",
        "bureau": "Academic",
        "priority": "High"
    },

    # Unapproved Courses (20 examples) -> bureau: Approval
    {
        "title": "College offering BTech Artificial Intelligence without AICTE approval",
        "description": "Institute enrolled 120 students in AI & Data Science course that has not received approval or letter of extension from AICTE.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Fake collaborative twinning program with foreign university",
        "description": "College launched an international dual-degree engineering diploma with a non-existent European partner university.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Running unauthorized off-campus study center and evening diploma batches",
        "description": "Polytechnic opened illegal extension centers in commercial complexes without AICTE approval or university affiliation.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Commercial coaching institute awarding unapproved technical diplomas",
        "description": "Private coaching academy is issuing fake mechanical and electrical engineering diploma certificates claiming AICTE equivalency.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Offering unapproved MBA executive programs under disguise of autonomous status",
        "description": "Business school admitted 200 candidates in a two-year PGDM course whose AICTE approval was formally revoked last year.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Unapproved distance education engineering degrees offered online",
        "description": "Institute is advertising fully online BTech degrees in civil engineering despite Supreme Court and AICTE bans on distance engineering.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Operating engineering college during zero admission regulatory penalty year",
        "description": "Institute placed under no-admission sanction by AICTE due to severe deficiencies admitted fresh students in violation of ban.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Offering unapproved short-term certification claiming government recognition",
        "description": "Center offers six-month robotics certificates falsely using AICTE logo and deceptive government endorsement seals.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unauthorized branch name alteration to attract computer science aspirants",
        "description": "College disguised its sanctioned Civil Engineering seats as 'Computational Infrastructure Engineering' without regulatory approval.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Unapproved dual-degree integrated MTech program without university sanction",
        "description": "Institute enrolled undergraduates in a five-year integrated MTech program that has no affiliation or board approval.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Instituting unaccredited medical electronics diploma in engineering facility",
        "description": "Management started para-medical polytechnic course without obtaining clearances from technical and medical regulatory bodies.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Displaying forged AICTE Approval Process Handbook clearance letter on website",
        "description": "Institution published altered extension of approval document on its website with forged signatures of regional director.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Running unauthorized second shift in engineering polytechnic",
        "description": "Polytechnic is running an evening shift with 180 extra seats without obtaining AICTE second-shift sanction.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Operating technical college from leased unapproved residential premises",
        "description": "Institute relocated its classrooms to an unauthorized residential apartment building without regulatory site inspection.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Marketing fake micro-credentials as AICTE accredited diploma units",
        "description": "Private edtech entity sells python coding badges claiming they provide official AICTE polytechnic diploma equivalence.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Admitting students to defunct branch after formal closure notice",
        "description": "Institute took admissions in Information Technology branch despite applying for and receiving formal closure order from AICTE.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Unapproved conversion of diploma seats into degree seats",
        "description": "Polytechnic wing converted 60 diploma seats into BTech degree seats unilaterally without state or AICTE sanction.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Misleading franchise model using reputed college name to run illegal courses",
        "description": "Unregistered coaching center opened illegal franchise using reputed engineering college brand name to award bogus certificates.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },
    {
        "title": "Conducting unapproved online MCA degree programs",
        "description": "College started an online Master of Computer Applications course without DEB-UGC or AICTE online learning approvals.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "High"
    },
    {
        "title": "Issuing fake vocational degrees under fictitious skill board affiliation",
        "description": "College issued Bachelor of Vocation certificates bearing forged seals of national skill development council.",
        "category": "Unapproved Courses",
        "bureau": "Approval",
        "priority": "Critical"
    },

    # Harassment & Ragging (20 examples) -> bureau: PGRC or EO
    {
        "title": "Severe physical ragging and assault of first-year hostel residents",
        "description": "Senior hostel students physically assaulted freshmen, stripped them, and forced them to perform degrading acts until midnight.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Failure of college Anti-Ragging Committee to investigate filed complaint",
        "description": "A junior student formally lodged a ragging complaint 3 weeks ago, but the squad took no action and shielded the accused seniors.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Sexual harassment by senior professor during project viva evaluation",
        "description": "Female student reports persistent inappropriate messages, sexually suggestive demands, and threats of failing thesis from professor.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "Critical"
    },
    {
        "title": "Absence of functioning Internal Complaints Committee for gender harassment",
        "description": "College lacks a legally constituted POSH Internal Complaints Committee, leaving female students with no recourse against harassment.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "Critical"
    },
    {
        "title": "Caste-based verbal abuse and social boycott by department faculty",
        "description": "Head of Department repeatedly used derogatory caste slurs against reserved category students and openly humiliated them in class.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "Critical"
    },
    {
        "title": "Senior students extorting money and demanding domestic chores from juniors",
        "description": "Hostel freshers are threatened with beatings unless they wash seniors' laundry and pay weekly alcohol allowances.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Cyberbullying and morphing of student photos on social media groups",
        "description": "Senior students created abusive WhatsApp and Telegram groups circulating manipulated photographs of junior female students.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Victimization and threats of expulsion for reporting ragging to police",
        "description": "Hostel warden and college director threatened to rusticate the ragging victim unless they withdraw their local police FIR.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Mental torture and sleep deprivation of new entrants in campus hostel",
        "description": "Juniors are kept awake standing until 4 AM by senior students performing forced roll calls and psychological humiliation.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Intimidation and stalking of girl students outside campus main gate",
        "description": "Local rowdies and expelled former students loiter and stalk female students daily because security guards refuse to intervene.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Hostel warden turning a blind eye to continuous late-night ragging",
        "description": "Despite repeated distress calls from victims, hostel warden locks office and instructs security guards not to interfere.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Inappropriate physical touch by physical education instructor",
        "description": "Sports coach engaged in unwelcome physical contact with female athletes during sports training sessions.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "Critical"
    },
    {
        "title": "Religious discrimination and derogatory remarks made by lecturer",
        "description": "Assistant professor made derogatory comments targeting minority students' faith during open engineering physics lecture.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "High"
    },
    {
        "title": "Forced tonsuring and haircut rituals imposed on first year students",
        "description": "Senior hostel students shaved heads of junior boys as a mandatory ritual and beat those who resisted.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Critical"
    },
    {
        "title": "Public humiliation and character assassination by department dean",
        "description": "Dean used abusive language on microphone during assembly, publicly insulting a student's family background.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Denial of mess food and drinking water to boycotted junior students",
        "description": "Seniors instructed mess workers to deny dinner to freshers who refused to surrender their smartphones.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Absence of emergency anti-ragging helpline posters on campus",
        "description": "College deliberately removed national anti-ragging toll-free numbers and UGC helpline details from all notice boards.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "Medium"
    },
    {
        "title": "Retaliatory grading and marks deduction after filing harassment complaint",
        "description": "Professor gave zero internal marks to student who reported his unprofessional conduct to the grievance cell.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "High"
    },
    {
        "title": "Intimidation of junior hostelers during night study hours",
        "description": "Senior batch barged into first-year dormitories, destroying laptops and tearing course notebooks of juniors.",
        "category": "Harassment & Ragging",
        "bureau": "PGRC",
        "priority": "High"
    },
    {
        "title": "Blackmail of student using private dormitory surveillance footage",
        "description": "Unauthorized hidden recording device found in hostel washroom; footage used to extort money from student.",
        "category": "Harassment & Ragging",
        "bureau": "EO",
        "priority": "Critical"
    },

    # Skill Certification (20 examples) -> bureau: SB
    {
        "title": "Non-disbursal of AICTE Pragati and Saksham scholarship stipend",
        "description": "Empowered scholarship beneficiary students have not received their annual stipend of 50000 rupees for two consecutive terms.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Delay in issuing PMKVY national skill qualification certificates",
        "description": "Trainees completed 400 hours of solar technician course under PMKVY but have not been awarded certified skill credentials.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Non-payment of mandatory National Apprenticeship Training Scheme stipend",
        "description": "Graduate engineering apprentices deployed in plant operations have not been paid their government-mandated monthly stipend for 5 months.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Fraudulent skill assessment center taking exam fees without conducting test",
        "description": "Skill certification center collected 1500 assessment fee from candidates but closed office without issuing hall tickets or exam results.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Non-credit of AICTE PG GATE scholarship to MTech scholars",
        "description": "GATE qualified postgraduate engineering students have not received monthly direct benefit transfer stipend for six months.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Substandard training machinery in vocational skill development center",
        "description": "CNC training machines and 3D printing equipment in approved skill hub are completely dysfunctional, preventing practical training.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Withholding internship completion certificates by partnering industry",
        "description": "Private corporate partner refused to sign AICTE internship completion certificates after making students work unpaid 50 hour weeks.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Delay in verification of student profiles on National Apprenticeship Portal",
        "description": "Institutional nodal supervisor has not verified NATS apprenticeship candidate profiles, causing portal registration timeout.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Issuance of skill certificates with misspelled candidate details",
        "description": "Automotive skill certification cards printed with wrong Aadhaar number and mismatched names; replacement pending for 4 months.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Unapproved cancellation of PMKVY training batch midway",
        "description": "Training institute cancelled data entry operator course halfway through syllabus without refunding government or candidate funds.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Non-issuance of SWAYAM course credit transfer certificate",
        "description": "Student passed AICTE approved SWAYAM online exam with 90 percent score but digital certificate has not been generated for 3 months.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Irregularity in biometric attendance recording for skill trainees",
        "description": "Skill center administrator manually manipulated candidate attendance to siphon off government skill development subsidies.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Failure to provide placement assistance guaranteed under skill scheme",
        "description": "Government skill scheme guidelines mandate 70 percent placement assistance, but training center provided zero employer drives.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Charging unauthorized examination fee for government funded skill test",
        "description": "Vocational institute charged 2000 rupees cash from underprivileged youth for free government-funded NSQF skill exam.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Denial of skill training toolkit allowance to enrolled candidates",
        "description": "Electrician trade trainees under welfare skill scheme did not receive designated toolkits or reimbursement allowances.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Delay in disbursal of AICTE Swanath scholarship for orphan students",
        "description": "Orphan student enrolled in polytechnic diploma has not received Swanath educational assistance despite state approval.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    },
    {
        "title": "Unqualified vocational trainers conducting technical skill modules",
        "description": "Advanced drone pilot training course handled by instructor who lacks basic DGCA certification or pilot credential.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Failure to upload skill training assessment results to DigiLocker portal",
        "description": "Skill certification council has not integrated 2025 passout digital badges with National Academic Depository or DigiLocker.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Low"
    },
    {
        "title": "Extortionate charges for re-assessment of failed skill practical modules",
        "description": "Skill center demanding 5000 rupees for re-taking a single one-hour practical module when official fee is 250 rupees.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "Medium"
    },
    {
        "title": "Non-recognition of skill certificate by affiliated state technical board",
        "description": "State technical board rejected community college vocational certificate claiming program was not aligned with state rules.",
        "category": "Skill Certification",
        "bureau": "SB",
        "priority": "High"
    }
]

def generate_csv(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "category", "bureau", "priority"])
        writer.writeheader()
        for row in DATASET:
            writer.writerow(row)
    print(f"Generated {len(DATASET)} synthetic complaint examples at: {output_path}")

if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "training_data.csv")
    generate_csv(dest)
