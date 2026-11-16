# API INVENTORY
## CPAOS - Existing API Endpoints

**Audit Date:** November 16, 2026  
**Base URL:** `/api`  
**Framework:** FastAPI 0.104+  
**Auth:** JWT Bearer tokens (Supabase Auth)

---

## OVERVIEW

**Total Endpoints:** 38 endpoints across 9 route modules  
**Authentication:** Required on all endpoints except public portal routes  
**Authorization:** Firm-level tenant isolation enforced  
**Documentation:** Auto-generated Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 1. AUTHENTICATION & USER MANAGEMENT

### Module: `auth.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/api/auth/register-firm` | Register new firm with owner | ❌ Public | ✅ Complete |
| POST | `/api/auth/login` | Staff login with Supabase token | ❌ Public | ✅ Complete |
| GET | `/api/auth/me` | Get current user and firm details | ✅ Required | ✅ Complete |

**Request/Response Models:**
- `RegisterFirmBody` - firm_name, slug, country, owner details, password
- `LoginBody` - access_token (from Supabase)

**Features:**
- ✅ Firm creation with unique slug
- ✅ Owner user creation in Supabase
- ✅ Automatic firm_user record creation
- ✅ Plan-based client limits
- ✅ Returns JWT access token

---

## 2. FIRM MANAGEMENT

### Module: `firms.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| GET | `/api/firm` | Get firm details | ✅ Required | ✅ Complete |
| PATCH | `/api/firm` | Update firm settings | ✅ Required | ✅ Complete |
| POST | `/api/firm/logo` | Upload firm logo | ✅ Required | ✅ Complete |
| GET | `/api/firm/users` | List firm users | ✅ Required | ✅ Complete |
| POST | `/api/firm/invite-user` | Invite new user | ✅ Owner/Admin | ✅ Complete |
| PATCH | `/api/firm/users/{user_id}` | Update user role/status | ✅ Owner/Admin | ✅ Complete |

**Request/Response Models:**
- `FirmPatch` - name, whatsapp_number, primary_color
- `InviteUserBody` - email, full_name, password, role
- `UserPatch` - role, is_active

**Features:**
- ✅ Firm branding configuration
- ✅ User invitation (creates Supabase user)
- ✅ Role management (owner, admin, staff)
- ✅ User activation/deactivation

---

## 3. CLIENT MANAGEMENT

### Module: `clients.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/api/clients` | Create new client | ✅ Required | ✅ Complete |
| GET | `/api/clients` | List clients (filtered) | ✅ Required | ✅ Complete |
| GET | `/api/clients/expiring-docs` | Documents expiring in 30 days | ✅ Required | ✅ Complete |
| GET | `/api/clients/{id}` | Get client details | ✅ Required | ✅ Complete |
| PATCH | `/api/clients/{id}` | Update client | ✅ Required | ✅ Complete |
| GET | `/api/clients/{id}/checklist` | Get client checklist | ✅ Required | ✅ Complete |
| POST | `/api/clients/{id}/send-reminder` | Send reminder message | ✅ Required | ✅ Complete |
| GET | `/api/clients/{id}/messages` | Get message history | ✅ Required | ✅ Complete |
| GET | `/api/clients/{id}/activity` | Get activity log | ✅ Required | ✅ Complete |
| POST | `/api/clients/{id}/resend-engagement-letter` | Resend DocuSign letter | ✅ Required | ✅ Complete |
| POST | `/api/clients/bulk-remind` | Bulk reminder to clients | ✅ Required | ✅ Complete |
| GET | `/api/clients/export-csv` | Export clients to CSV | ✅ Required | ✅ Complete |
| POST | `/api/clients/generate-report` | Generate PDF report | ✅ Required | ✅ Complete |

**Query Parameters:**
- `GET /api/clients` - status, country, search, assigned_to
- `GET /api/clients/expiring-docs` - include_expired (boolean)
- `GET /api/clients/export-csv` - ids (comma-separated)

**Request/Response Models:**
- `CreateClientBody` - All client fields + send_engagement_letter flag
- `PatchClientBody` - status, assigned_to
- `ReminderBody` - template (welcome, reminder_day2, etc.)
- `BulkRemindBody` - client_ids[]
- `GenerateReportBody` - client_ids[]

**Features:**
- ✅ Country-specific checklist auto-generation
- ✅ Client filtering and search
- ✅ Document expiry tracking (30-day window)
- ✅ WhatsApp/SMS reminders
- ✅ Bulk operations (remind, export, report)
- ✅ PDF report generation with firm branding
- ✅ CSV export with assignment details
- ✅ Engagement letter automation (DocuSign)
- ✅ Activity logging

---

## 4. DOCUMENT MANAGEMENT

### Module: `documents.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/api/clients/{id}/upload` | Upload document (staff) | ✅ Required | ✅ Complete |
| GET | `/api/clients/{id}/documents` | List client documents | ✅ Required | ✅ Complete |
| GET | `/api/documents/{id}/signed-url` | Get download URL | ✅ Required | ✅ Complete |
| POST | `/api/documents/{id}/verify` | Approve/reject document | ✅ Required | ✅ Complete |

**Request/Response Models:**
- Upload: multipart/form-data with `file` and optional `expected_type`
- `VerifyBody` - action (approved/rejected), rejection_reason

**Features:**
- ✅ AI document classification (Anthropic Claude)
- ✅ Automatic checklist item matching (>80% confidence)
- ✅ Supabase Storage integration
- ✅ Signed URLs for secure access (1-hour expiry)
- ✅ Document review workflow
- ✅ Max file size: 20 MB
- ✅ Supported formats: PDF, images (JPG, PNG, WebP)

**AI Classification:**
- Document type detection (PAN, GST, ITR, Bank Statement, etc.)
- Confidence score (0-1)
- Issue detection (poor quality, missing info, etc.)
- Country-aware classification

---

## 5. CHECKLIST MANAGEMENT

### Module: `checklist.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| PATCH | `/api/clients/{client_id}/checklist-items/{item_id}` | Waive checklist item | ✅ Required | ✅ Complete |
| PATCH | `/api/checklist/{item_id}` | Update item status | ✅ Required | ✅ Complete |
| PATCH | `/api/checklist/{item_id}/expiry` | Set expiry date | ✅ Required | ✅ Complete |

**Request/Response Models:**
- `WaiveBody` - reason
- `PatchChecklistItemBody` - status (verified/pending)
- `PatchExpiryBody` - expiry_date (optional)

**Features:**
- ✅ Waive items with reason tracking
- ✅ Status updates (verified, pending)
- ✅ Expiry date management
- ✅ Auto-recompute client completion percentage

---

## 6. CLIENT PORTAL (PUBLIC)

### Module: `portal.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/api/portal/{firm_slug}/self-register` | Client self-registration | ❌ Public | ✅ Complete |
| GET | `/api/portal/{firm_slug}/{token}/client` | Get client data (portal) | 🔑 Token | ✅ Complete |
| POST | `/api/portal/{firm_slug}/{token}/upload` | Upload document (portal) | 🔑 Token | ✅ Complete |

**Features:**
- ✅ Public client self-registration
- ✅ Token-based authentication (no password)
- ✅ Client document upload from portal
- ✅ AI classification on portal uploads
- ✅ Email notifications to assigned staff
- ✅ Progress tracking
- ✅ Firm plan limit enforcement

---

## 7. ANALYTICS & REPORTING

### Module: `analytics.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| GET | `/api/analytics/dashboard` | Dashboard analytics | ✅ Required | ✅ Complete |

**Query Parameters:**
- `country` - Filter by country (optional)

**Response Structure:**
```json
{
  "kpis": {
    "active_clients": 15,
    "completed_this_month": 8,
    "avg_completion_days": 7.2,
    "docs_pending_review": 23,
    "signature_pending": 3,
    "completion_rate_pct": 65
  },
  "by_country": [
    { "country": "India", "count": 25, "avg_completion_pct": 75 }
  ],
  "by_status": [
    { "status": "in_progress", "count": 10 }
  ],
  "recent_activity": [],
  "completion_trend": [
    { "month": "Jun", "completed": 8 }
  ]
}
```

**Features:**
- ✅ Real-time KPI calculation
- ✅ Country-wise statistics
- ✅ Status distribution
- ✅ 6-month completion trend
- ✅ Recent activity feed
- ✅ Country filtering

---

## 8. E-SIGNATURE INTEGRATION

### Module: `signature.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| (Webhook) | `/api/signature/docusign-webhook` | DocuSign status updates | 🔑 Webhook | ✅ Complete |

**Features:**
- ✅ DocuSign envelope creation
- ✅ Embedded signing workflow
- ✅ Webhook status updates
- ✅ Engagement letter automation

**Service Integration:**
- `signature_service.py` - DocuSign API wrapper

---

## 9. VOICE AI INTEGRATION

### Module: `voice.py`

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/api/voice/call-complete` | VAPI post-call webhook | 🔑 Webhook | ✅ Complete |

**Features:**
- ✅ VAPI call completion webhook
- ✅ Call transcript processing
- ✅ Client action extraction
- ✅ Activity logging

---

## 10. HEALTH CHECK

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| GET | `/health` | Health check | ❌ Public | ✅ Complete |

**Response:**
```json
{
  "status": "healthy",
  "product": "CPAOS",
  "version": "2.0.0"
}
```

---

## MISSING ENDPOINTS FOR CA PRACTICE OS

### ⚠️ ASSIGNMENT MANAGEMENT (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/assignments` | Create assignment | ⭐ CRITICAL |
| GET | `/api/assignments` | List assignments (filtered) | ⭐ CRITICAL |
| GET | `/api/assignments/{id}` | Assignment details | ⭐ CRITICAL |
| PATCH | `/api/assignments/{id}` | Update assignment | ⭐ CRITICAL |
| DELETE | `/api/assignments/{id}` | Delete assignment | ⭐ CRITICAL |
| POST | `/api/assignments/{id}/submit` | Submit for review | ⭐ CRITICAL |
| POST | `/api/assignments/{id}/review` | Review assignment | ⭐ CRITICAL |
| POST | `/api/assignments/{id}/approve` | Approve assignment | ⭐ CRITICAL |
| GET | `/api/assignments/calendar` | Calendar view | HIGH |
| GET | `/api/assignments/my-tasks` | Current user tasks | HIGH |
| GET | `/api/assignments/team-tasks` | Team tasks | HIGH |
| GET | `/api/assignments/review-queue` | Pending reviews | HIGH |

---

### ⚠️ COMPLIANCE MANAGEMENT (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/compliance/calendar` | Compliance calendar | ⭐ CRITICAL |
| GET | `/api/compliance/obligations` | Compliance rules | HIGH |
| POST | `/api/compliance/obligations` | Create obligation rule | MEDIUM |
| GET | `/api/compliance/filings` | Client filings | ⭐ CRITICAL |
| POST | `/api/compliance/filings` | Create filing record | ⭐ CRITICAL |
| PATCH | `/api/compliance/filings/{id}` | Update filing | ⭐ CRITICAL |
| GET | `/api/compliance/upcoming` | Upcoming deadlines | HIGH |
| GET | `/api/compliance/overdue` | Overdue filings | HIGH |

---

### ⚠️ BILLING & INVOICING (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/invoices` | Create invoice | ⭐ CRITICAL |
| GET | `/api/invoices` | List invoices | ⭐ CRITICAL |
| GET | `/api/invoices/{id}` | Invoice details | ⭐ CRITICAL |
| PATCH | `/api/invoices/{id}` | Update invoice | ⭐ CRITICAL |
| POST | `/api/invoices/{id}/send` | Send invoice to client | HIGH |
| GET | `/api/invoices/{id}/pdf` | Download invoice PDF | HIGH |
| POST | `/api/payments` | Record payment | ⭐ CRITICAL |
| GET | `/api/payments` | List payments | HIGH |
| GET | `/api/billing/outstanding` | Outstanding receivables | HIGH |
| GET | `/api/billing/ageing` | Ageing analysis | HIGH |

---

### ⚠️ STAFF & WORKLOAD (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/staff/workload` | Staff workload analytics | HIGH |
| POST | `/api/timesheets` | Create timesheet entry | MEDIUM |
| GET | `/api/timesheets` | List timesheets | MEDIUM |
| PATCH | `/api/timesheets/{id}` | Update timesheet | MEDIUM |
| POST | `/api/timesheets/{id}/submit` | Submit timesheet | MEDIUM |
| POST | `/api/timesheets/{id}/approve` | Approve timesheet | MEDIUM |

---

### ⚠️ AUDIT MANAGEMENT (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/audit/engagements` | Create engagement | MEDIUM |
| GET | `/api/audit/engagements` | List engagements | MEDIUM |
| GET | `/api/audit/engagements/{id}` | Engagement details | MEDIUM |
| POST | `/api/audit/workpapers` | Create workpaper | MEDIUM |
| GET | `/api/audit/workpapers` | List workpapers | MEDIUM |
| PATCH | `/api/audit/workpapers/{id}` | Update workpaper | MEDIUM |

---

### ⚠️ NOTIFICATIONS (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/notifications` | List notifications | HIGH |
| PATCH | `/api/notifications/{id}/read` | Mark as read | HIGH |
| PATCH | `/api/notifications/read-all` | Mark all as read | MEDIUM |
| GET | `/api/notifications/unread-count` | Unread count | HIGH |

---

### ⚠️ ANALYTICS EXTENSIONS (NEW)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/analytics/practice-dashboard` | Partner dashboard | HIGH |
| GET | `/api/analytics/staff-productivity` | Staff metrics | MEDIUM |
| GET | `/api/analytics/revenue` | Revenue analytics | HIGH |
| GET | `/api/analytics/client-profitability` | Client profitability | MEDIUM |

---

## API TECHNOLOGY STACK

**Framework:** FastAPI 0.104+
- Automatic OpenAPI/Swagger documentation
- Pydantic model validation
- Async support (not currently used)
- Dependency injection

**Authentication:**
- Supabase Auth JWT tokens
- Bearer token in Authorization header
- Token validation via `get_current_firm_user()` dependency

**Database:**
- Supabase REST client (Python library)
- PostgreSQL queries via Supabase client
- Repository pattern (`app/db/repo.py`)

**Security:**
- Firm-level tenant isolation in all queries
- Role-based access control (owner, admin, staff)
- Input validation via Pydantic
- File size limits (20 MB)
- CORS middleware configured

**File Upload:**
- Multipart/form-data
- Supabase Storage integration
- Signed URLs for downloads

**Background Jobs:**
- APScheduler for daily reminders (9 AM)
- Scheduled task: `run_daily_reminders()`

---

## REUSABILITY ASSESSMENT

### ✅ HIGHLY REUSABLE (Keep as-is or minor extensions)
- Authentication endpoints (3) - ✅ 100%
- Firm management (6) - ✅ 90% (extend user fields)
- Client management (13) - ✅ 85% (extend client model)
- Document management (4) - ✅ 95% (add assignment linking)
- Checklist management (3) - ✅ 100%
- Portal endpoints (3) - ✅ 100%
- Analytics (1) - ✅ 70% (extend for practice metrics)

**Total reusable:** 33 out of 38 endpoints (~87%)

### ⚠️ BUILD NEW (Critical for CA Practice)
- Assignment management (12 endpoints) - ⭐ PHASE 1
- Compliance management (8 endpoints) - ⭐ PHASE 2
- Billing & invoicing (10 endpoints) - ⭐ PHASE 3
- Staff workload (6 endpoints) - PHASE 1
- Audit management (6 endpoints) - PHASE 4
- Notifications (4 endpoints) - PHASE 2

**Total new:** ~46 endpoints

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Foundation)
- Assignment CRUD + workflow (12 endpoints)
- Staff workload (6 endpoints)
- **Estimated:** 2-3 weeks

### Phase 2 (Compliance)
- Compliance calendar + filings (8 endpoints)
- Notifications (4 endpoints)
- **Estimated:** 2 weeks

### Phase 3 (Billing)
- Invoicing + payments (10 endpoints)
- **Estimated:** 2 weeks

### Phase 4 (Audit)
- Audit engagements + workpapers (6 endpoints)
- **Estimated:** 1-2 weeks

### Phase 5 (Analytics)
- Extended analytics (4 endpoints)
- **Estimated:** 1 week

**Total Endpoint Count (Post-Transformation):**
- Existing: 38
- New: 46
- **Total: 84 endpoints**

---

## API DOCUMENTATION

**Current:**
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- Auto-generated from Pydantic models

**Recommendation:** Keep auto-generated docs, add:
- API versioning (v1, v2)
- Rate limiting
- Webhook documentation
- Postman collection export
