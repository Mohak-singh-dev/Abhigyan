# Abhigyan (अभिज्ञान)

**Integrated Dashboard for Monitoring, Tracking, and AI-Based Classification of Institution-Related Complaint Cases Across AICTE Bureaus & Cells**

*Smart India Hackathon (SIH) — All India Council for Technical Education (AICTE)*

- **Repository:** [https://github.com/nooralam08/Abhigyan](https://github.com/nooralam08/Abhigyan)
- **Primary Branch:** `main`

---

## 1. System Overview & Architecture

Abhigyan is a specialized institutional governance and grievance redressal platform engineered for the All India Council for Technical Education (AICTE). It provides end-to-end docket intake, AI-assisted advisory routing, cross-bureau overlap detection, SLA surveillance, and immutable audit trails across AICTE administrative divisions.

### System Architecture

```mermaid
graph TD
    Client["React 18 + Vite SPA<br/>(TailwindCSS, TypeScript)"]
    API["FastAPI Backend<br/>(REST API, JWT, RBAC)"]
    DB[("PostgreSQL Database<br/>(Alembic Migrations)")]
    ML["NLP Classifier Service<br/>(TF-IDF + Logistic Regression)"]
    Rules["Statutory Routing Rules<br/>(Multi-Bureau Resolution)"]

    Client -->|REST & Bearer JWT| API
    API -->|ORM Transactions| DB
    API -->|Advisory Ingestion| ML
    ML -->|Category & Raw Probabilities| Rules
    Rules -->|Suggested Bureau & Review Flags| API
    API -->|Advisory Recommendations| Client
```

### Core Architecture Highlights

1. **AI-Based Advisory Classification**: Real-time and debounced machine learning preview that analyzes complaint subject and narrative text. Predicts category, bureau, and statutory urgency without automatically forcing suggestions onto the complainant.
2. **Hybrid Bureau Routing Engine**: Combines statistical NLP (scikit-learn Logistic Regression) with AICTE administrative domain heuristics to map complaints to the correct Bureau (Approval, Regulation, PGRC, Academic, Skill, Executive Office).
3. **Fine-Grained Role-Based Access Control (RBAC)**: Enforces strict data isolation among 4 distinct role tiers:
   - **Super Admin**: System-wide authority, cross-bureau reassignment, policy settings, analytics.
   - **Bureau Admin**: Scoped strictly to cases within their authorized Bureau jurisdiction.
   - **Handling Officer**: Scoped to assigned dockets or their Bureau cell; drives investigation lifecycle.
   - **Student / Complainant**: Self-service intake and docket tracking; strictly isolated to own submissions.
4. **Chronological Audit Trail & Immutable Timelines**: Every case intake, status transition, officer reassignment, and remark generates a timestamped database timeline event with actor verification.
5. **Cross-Bureau Overlap & Accidental Duplicate Detection**: Real-time similarity matching on campus ID and category/narrative text to prevent duplicate filings and detect concurrent cross-bureau investigations.
6. **Statutory SLA Surveillance Engine**: Dynamic resolution windows calculated from grievance priority (Critical: 3 days, High: 7 days, Medium: 14 days, Low: 21 days) with warning indicators for overdue cases.

---

## 2. Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend Framework** | React 18 | Vite 5 build tool, SPA architecture |
| **Frontend Language** | TypeScript 5 | Strict typing across models, API contracts, and components |
| **Styling & Design** | Tailwind CSS 3 | Custom AICTE institutional navy palette, responsive layout |
| **Icons & Visuals** | Lucide React, Recharts | Data visualizations, trend graphs, and SVG iconography |
| **Backend Framework** | FastAPI | High-performance Python async REST API, OpenAPI docs |
| **ORM & Database** | SQLAlchemy 2 + PostgreSQL | Relational schema, ACID transactions, connection pooling |
| **Database Migrations**| Alembic | Version-controlled schema migrations (revisions 001 - 005) |
| **Machine Learning** | scikit-learn + joblib | TF-IDF Vectorizer + Multinomial Logistic Regression |
| **Security & Auth** | PyJWT + Passlib (Bcrypt) | Stateless Bearer JWT tokens, role-based route dependencies |
| **Testing** | pytest, Node.js Test Runner | Unit, workflow, RBAC, evaluation, and client integration tests |

---

## 3. Machine Learning Pipeline & Advisory Integration

### Architecture & Non-Overriding Design Principle
The AI classification engine uses a scikit-learn pipeline consisting of a `TfidfVectorizer` (sublinear TF, unigram + bigram, 5,000 max features) and L-BFGS `LogisticRegression` models trained across 9 official AICTE complaint categories:

- Fee Regulation & Unauthorised Charges
- Faculty Norms & Shortage
- Infrastructure Deficit & Safety
- Admission & Counseling Irregularities
- Certificate & Transcript Delay
- Curriculum & Examination Irregularities
- Unapproved Courses & Bogus Programs
- Harassment & Anti-Ragging
- Skill Certification & Stipend Schemes

> [!IMPORTANT]
> **Advisory Disclaimer & Ethical Human-in-the-Loop Safeguards**:
> - AI suggestions are **strictly advisory** and do NOT constitute an official AICTE decision.
> - The application **never fabricates predictions** or automatically overrides user decisions. Users retain full freedom to select or change category, bureau, and priority dropdowns at any time.
> - When confidence is below the configured threshold (`AI_CONFIDENCE_THRESHOLD=0.40`) or multi-bureau ambiguity is detected, the system flags `needsManualReview = true` to mandate human officer scrutiny.

### Model Evaluation Benchmark (Held-Out Stratified Test Split)

| Evaluation Target | Method / Architecture | Accuracy | Macro F1 | Performance Summary |
| :--- | :--- | :--- | :--- | :--- |
| **Category** (9 Classes) | TF-IDF + Logistic Regression | **72.2%** | **0.6974** | Strong baseline on distinctive terminology |
| **Bureau** (Direct ML) | TF-IDF + Logistic Regression | **44.4%** | **0.1713** | Limited on raw text due to multi-bureau keywords |
| **Bureau** (Hybrid Rules+ML)| Administrative Domain Heuristics | **83.3%** | **0.7337** | **+38.9% accuracy gain** through domain routing |
| **Priority** (4 Classes) | TF-IDF + Logistic Regression | **38.9%** | **0.1726** | Biased to majority class; priority requires external calendar context |

*(Evaluated strictly on 180 synthetic complaints generated for prototype evaluation. See [backend/ml/artifacts/evaluation_report.md](file:///c:/Users/Princ/Abhigyan/backend/ml/artifacts/evaluation_report.md) for full confusion matrices and class distributions).*

---

## 4. Getting Started & Installation

### Prerequisites

- **Node.js**: v18.x or v20.x LTS
- **Python**: v3.10, v3.11, or v3.12
- **PostgreSQL**: v14, v15, or v16 running locally or in Docker

---

### Step 1: Clone Repository

```bash
git clone https://github.com/nooralam08/Abhigyan.git
cd Abhigyan
```

---

### Step 2: Backend Setup & Virtual Environment

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Step 3: Database & Environment Configuration

1. Create a local PostgreSQL database:
   ```sql
   CREATE DATABASE abhigyan_db;
   ```

2. Copy the environment template and configure your local settings:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your PostgreSQL credentials:
   ```ini
   DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/abhigyan_db
   CORS_ORIGINS=http://localhost:5173,http://localhost:4173
   ENVIRONMENT=development
   API_PREFIX=/api
   JWT_SECRET_KEY=your-secure-random-secret-key-min-32-chars
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   DEMO_AUTH_ENABLED=True
   AI_CONFIDENCE_THRESHOLD=0.40
   ```

---

### Step 4: Run Database Migrations

Apply Alembic migrations to set up the schema (users, institutions, complaints, timelines, AI classification columns):

```bash
alembic upgrade head
```

Verify migration status:
```bash
alembic current
# Output should indicate: 005_ai_classification (head)
```

---

### Step 5: Train and Evaluate Machine Learning Model

Generate artifacts (`vectorizer.joblib`, `category_model.joblib`, `bureau_model.joblib`, `priority_model.joblib`, `metadata.json`):

```bash
python ml/train_model.py
```

Run reproducible stratified evaluation benchmark and generate report:
```bash
python ml/evaluate_model.py
```

---

### Step 6: Frontend Setup

Open a new terminal at the project root (`Abhigyan/`):

```bash
npm install
```

---

## 5. Clean-Start Commands & Running Locally

### Start Backend API Server

```bash
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://localhost:8000/api`
- Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Start Frontend Application

In another terminal at the project root:

```bash
npm run dev
```

- Web Application: `http://localhost:5173`

---

## 6. Seed Accounts & Demo Credentials

When `DEMO_AUTH_ENABLED=True` (default in development), you can log in instantly via the role selector or standard credentials:

| Role Persona | Display Name | Email / Login ID | Bureau Jurisdiction | Password |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | Dr. S. Mehta | `member-sec@aicte-india.org` | All Bureaus (System-wide) | `AicteDemo@2026` |
| **Bureau Admin** | Dr. Priya Nair | `priya.nair@aicte-india.org` | PGRC Bureau | `AicteDemo@2026` |
| **Bureau Admin** | Anita Verma | `anita.verma@aicte-india.org` | Regulation Bureau (RB) | `AicteDemo@2026` |
| **Handling Officer** | Rajesh Kumar | `rajesh.kumar@aicte-india.org` | PGRC Scrutiny Cell | `AicteDemo@2026` |
| **Handling Officer** | Suresh Patel | `suresh.patel@aicte-india.org` | Approval Bureau Cell | `AicteDemo@2026` |
| **Student / Citizen** | Rohit Sharma | `rohit.sharma@student.edu.in` | Self-Service Complainant | `AicteDemo@2026` |

---

## 7. Automated Verification & Testing Suites

### Running Backend Tests (`pytest`)

Run all 76 unit, integration, RBAC, workflow, and evaluation tests:

```bash
cd backend
.\.venv\Scripts\pytest.exe -v
```

Test coverage includes:
- `tests/test_complete_audit_workflows.py`: Complete Student, Officer, Bureau Admin, Super Admin workflows and error guards.
- `tests/test_auth_rbac.py`: JWT login, password verification, expiration, demo-login isolation, and case access authorization.
- `tests/test_complaint_workflows.py`: Status transitions, permitted lifecycle paths, assignment rollback, and timeline actor auditing.
- `tests/test_ai_complaint_integration.py`: Live classification preview, non-override creation, missing model fallbacks.
- `tests/test_ai_classifier.py`: Text preprocessing, model loading, thresholding, rule-based bureau resolution.
- `tests/test_model_evaluation.py`: Reproducible stratified splits, zero data leakage checks, metric math validity.
- `tests/test_institutions.py` & `tests/test_health.py`: Registry queries, search filters, and database connectivity.

### Running Frontend Tests (`node:test`)

Run all 15 frontend client integration tests against the live API:

```bash
# Ensure backend is running on http://127.0.0.1:8000
npm run test
```

### Building for Production

Verify TypeScript compilation and Vite bundling:

```bash
npm run build
```

---

## 8. Repository File Structure

```
Abhigyan/
├── backend/
│   ├── alembic/                    # Database migration scripts
│   │   ├── versions/               # Revisions 001 through 005 (AI columns)
│   │   └── env.py                  # Alembic migration environment
│   ├── app/
│   │   ├── models/                 # SQLAlchemy DB models (complaint, user, institution, timeline)
│   │   ├── routers/                # FastAPI endpoints (auth, complaints, institutions, health)
│   │   ├── schemas/                # Pydantic validation schemas and response contracts
│   │   ├── services/
│   │   │   └── ai_classifier.py    # Lazy-loading AI classifier and bureau routing engine
│   │   ├── auth.py                 # JWT validation, password hashing, RBAC check_case_access
│   │   ├── config.py               # Settings and environment configuration
│   │   ├── database.py             # SQLAlchemy sessionmaker and engine
│   │   └── main.py                 # FastAPI application factory and CORS middleware
│   ├── ml/
│   │   ├── artifacts/              # Local model weights (.joblib, metadata.json, evaluation_report.md)
│   │   ├── evaluate_model.py       # Standalone stratified evaluation benchmark
│   │   ├── generate_dataset.py     # Synthetic dataset generator
│   │   ├── train_model.py          # TF-IDF + LogisticRegression training pipeline
│   │   └── training_data.csv       # Labeled synthetic complaint examples (180 rows)
│   ├── tests/                      # Automated pytest test suites (76 tests)
│   ├── .env.example                # Documented configuration template
│   └── requirements.txt            # Python dependencies
├── src/
│   ├── api/
│   │   ├── __tests__/              # Node.js automated integration test suites (15 tests)
│   │   ├── client.ts               # Axios / fetch HTTP client with automatic Bearer token injection
│   │   └── complaints.ts           # Complaint API client (classify preview, submit, list, get)
│   ├── components/                 # Reusable UI components (ComplaintTable, AppLayout, Sidebar, TopBar)
│   ├── pages/                      # Application pages (Complaints, Dashboard, Institutions, Reports, Overlaps)
│   ├── types.ts                    # Shared TypeScript interfaces (Complaint, AIClassificationResult, User)
│   ├── App.tsx                     # Main application view coordinator and auth state
│   └── main.tsx                    # Vite entry point
├── .gitignore                      # Git exclusion rules (excluding .env, secrets, binary artifacts)
├── package.json                    # Frontend dependencies and test scripts
├── tailwind.config.js              # Institutional navy styling theme
├── tsconfig.json                   # TypeScript configuration
└── vite.config.ts                  # Vite build configuration
```

---

## 9. Production Hardening & Deployment Notes

Before deploying Abhigyan to a production environment:

1. **Disable Demo Authentication**: Set `DEMO_AUTH_ENABLED=False` in environment variables.
2. **Generate Strong JWT Secret**: Set `JWT_SECRET_KEY` to a cryptographically random string (`openssl rand -hex 32`).
3. **Restrict CORS**: Configure `CORS_ORIGINS` to specify only the official production domain(s).
4. **Use Production ASGI Server**: Run FastAPI behind Gunicorn with Uvicorn workers:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
5. **Real-World Model Retraining**: The current prototype model is trained on 180 synthetic complaint examples for architectural demonstration. Real-world operational deployment requires training on anonymized institutional complaint dossiers, continuous drift monitoring, and periodic recalibration.
