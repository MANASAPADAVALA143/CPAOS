# TARGET ARCHITECTURE
## GNANOVA CA PRACTICE OS - Technical Architecture

**Version:** 1.0  
**Date:** November 16, 2026

---

## EXECUTIVE SUMMARY

GNANOVA CA PRACTICE OS will transform CPAOS into an **enterprise-grade, multi-tenant practice management platform** for Chartered Accountant firms, built on the existing foundation.

**Target Markets:**
- Primary: India (CA firms, tax advisory firms)
- Secondary: UAE (accounting & tax firms)
- Tertiary: UK, Singapore, Australia (future expansion)

**Architecture Approach:** **Evolutionary, not revolutionary**
- Keep existing tech stack
- Extend database schema (no breaking changes)
- Add new API modules
- Enhance frontend with new pages
- Preserve all working functionality

---

## SYSTEM ARCHITECTURE OVERVIEW

### Architecture Pattern: **Modular Monolith**
- Single FastAPI backend application
- Single React SPA frontend
- Supabase PostgreSQL database
- Supabase Storage for documents
- External service integrations (WhatsApp, AI, e-signature)

**Why NOT microservices:**
- Team size likely small (1-5 developers)
- Faster development and deployment
- Easier debugging and maintenance
- Lower operational complexity
- Can refactor to microservices later if needed

---

## TECHNOLOGY STACK (PRESERVED)

### Backend
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.12
- **ASGI Server:** Uvicorn
- **Background Jobs:** APScheduler
- **AI/ML:** Anthropic Claude API
- **Email:** Resend
- **SMS/WhatsApp:** Twilio + n8n
- **E-Signature:** DocuSign
- **Storage:** Supabase Storage

### Frontend
- **Framework:** React 18
- **Language:** TypeScript 5.3
- **Build Tool:** Vite 5.0
- **Router:** React Router v6
- **State:** React Hooks (Context API for global state)
- **HTTP Client:** Axios
- **UI Library:** Radix UI (headless components)
- **Styling:** Tailwind CSS 3.4
- **Charts:** Recharts 2.10
- **Notifications:** Sonner
- **Icons:** Lucide React

### Database
- **Platform:** Supabase PostgreSQL
- **Client:** Python supabase library
- **Migrations:** SQL scripts (manual execution)
- **Backup:** Supabase automated backups

### Infrastructure
- **Deployment:** Railway / Render / Docker
- **CI/CD:** GitHub Actions (future)
- **Monitoring:** Supabase Dashboard + Sentry (future)
- **Logging:** Python logging + Supabase logs

---

## DATABASE ARCHITECTURE

### Multi-Tenancy Strategy: **Shared Database, Shared Schema**

**Tenant Isolation:**
- Every table has `firm_id UUID` foreign key
- All queries filter by `current_user.firm_id`
- Row Level Security (RLS) policies to enforce isolation
- No cross-firm data access

**Advantages:**
- Simple to implement
- Cost-effective
- Easy to maintain
- Suitable for SMB CA firms (target market)

**Schema Structure:**
```
Core Tables (Existing - Extend):
- firms
- firm_users
- clients
- checklist_items
- documents
- whatsapp_logs (→ communication_logs)
- onboarding_activity (→ activity_logs)

New Practice Management Tables:
- assignments ⭐
- assignment_reviews
- compliance_obligations
- compliance_filings
- invoices ⭐
- invoice_items
- payments
- timesheets
- audit_engagements
- audit_workpapers
- notifications

Total: 18 tables (7 existing + 11 new)
```

### Foreign Key Relationships
```
firms (root)
  ├── firm_users
  ├── clients
  │    ├── assignments
  │    │    ├── assignment_reviews
  │    │    ├── documents (via assignment_id)
  │    │    └── checklist_items (via assignment_id)
  │    ├── compliance_filings
  │    ├── invoices
  │    │    ├── invoice_items
  │    │    └── payments
  │    ├── audit_engagements
  │    │    └── audit_workpapers
  │    ├── documents
  │    └── checklist_items
  ├── compliance_obligations
  ├── timesheets
  ├── notifications
  ├── communication_logs
  └── activity_logs
```

### Indexing Strategy
- Primary keys: UUID (B-tree index)
- Foreign keys: B-tree indexes
- Tenant isolation: `(firm_id, created_at DESC)` composite indexes
- Search columns: GIN indexes on JSONB fields
- Date filters: B-tree on `due_date`, `invoice_date`, `date`

---

## API ARCHITECTURE

### RESTful API Design

**Base URL:** `/api/v1` (add versioning)

**Module Structure:**
```
/api/v1/
  /auth         - Authentication & registration
  /firm         - Firm settings & users
  /clients      - Client management
  /assignments  - Assignment lifecycle (NEW)
  /compliance   - Compliance tracking (NEW)
  /documents    - Document management
  /billing      - Invoices & payments (NEW)
  /timesheets   - Time tracking (NEW)
  /audit        - Audit engagements (NEW)
  /staff        - Employee management (NEW)
  /analytics    - Dashboard & reports
  /portal       - Client portal (public)
  /notifications - In-app notifications (NEW)
```

**Authentication:**
- JWT tokens from Supabase Auth
- Bearer token in `Authorization` header
- Middleware: `get_current_firm_user()` dependency
- Token includes: user_id, firm_id, role

**Authorization:**
- Role-based access control (RBAC)
- Permission checks in route handlers
- Tenant isolation in all queries

**Error Handling:**
- Standard HTTP status codes
- JSON error responses
- Validation errors from Pydantic

**Response Format:**
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 150
  }
}
```

---

## FRONTEND ARCHITECTURE

### Component Structure

```
src/
  /pages              - Route components
    /Dashboard.tsx      - Partner dashboard
    /ClientList.tsx
    /ClientDetail.tsx
    /AssignmentList.tsx  (NEW)
    /AssignmentDetail.tsx (NEW)
    /AssignmentBoard.tsx (NEW - Kanban)
    /ComplianceCalendar.tsx (NEW)
    /InvoiceList.tsx (NEW)
    /InvoiceCreate.tsx (NEW)
    /BillingDashboard.tsx (NEW)
    /StaffList.tsx (NEW)
    /StaffWorkload.tsx (NEW)
    /TimesheetEntry.tsx (NEW)
    /AnalyticsDashboard.tsx
    /FirmSettings.tsx
    /Login.tsx
    /DocumentPortal.tsx
  
  /components         - Reusable UI components
    /KpiCard.tsx
    /DataTable.tsx
    /StatusBadge.tsx
    /AssignmentCard.tsx (NEW)
    /ComplianceCard.tsx (NEW)
    /InvoiceCard.tsx (NEW)
    /WorkloadChart.tsx (NEW)
    /Sidebar.tsx (NEW - App navigation)
    /Breadcrumbs.tsx (NEW)
  
  /lib                - Utilities & API client
    /api.ts             - Axios instance
    /supabase.ts        - Supabase client
    /utils.ts
    /constants.ts
  
  /hooks              - Custom React hooks
    /useFirm.ts
    /useAuth.ts
    /useAssignments.ts (NEW)
    /useNotifications.ts (NEW)
  
  /types              - TypeScript interfaces
    /client.ts
    /assignment.ts (NEW)
    /invoice.ts (NEW)
```

### State Management Strategy

**No Redux/Zustand needed.** Use:
1. **React Context** for global state (auth, firm info)
2. **React Query** (future) for server state caching
3. **Local state** for component-specific data

**Context Providers:**
```tsx
<AuthProvider>        // Current user & firm
  <NotificationProvider>  // Real-time notifications
    <App />
  </NotificationProvider>
</AuthProvider>
```

### Routing Structure

```tsx
<Routes>
  {/* Public */}
  <Route path="/" element={<LandingPage />} />
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<RegisterFirm />} />
  <Route path="/portal/:slug/:token" element={<DocumentPortal />} />
  <Route path="/onboard/:slug" element={<ClientSelfRegister />} />
  
  {/* Authenticated - Wrap in <ProtectedRoute> */}
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/clients" element={<ClientList />} />
  <Route path="/clients/:id" element={<ClientDetail />} />
  
  {/* NEW Routes */}
  <Route path="/assignments" element={<AssignmentList />} />
  <Route path="/assignments/:id" element={<AssignmentDetail />} />
  <Route path="/assignments/board" element={<AssignmentBoard />} />
  <Route path="/assignments/calendar" element={<AssignmentCalendar />} />
  
  <Route path="/compliance" element={<ComplianceCalendar />} />
  
  <Route path="/billing" element={<BillingDashboard />} />
  <Route path="/invoices" element={<InvoiceList />} />
  <Route path="/invoices/new" element={<InvoiceCreate />} />
  <Route path="/invoices/:id" element={<InvoiceDetail />} />
  
  <Route path="/staff" element={<StaffList />} />
  <Route path="/staff/:id" element={<StaffProfile />} />
  <Route path="/staff/workload" element={<StaffWorkload />} />
  
  <Route path="/timesheets" element={<TimesheetList />} />
  
  <Route path="/audit" element={<AuditList />} />
  <Route path="/audit/:id" element={<AuditWorkspace />} />
  
  <Route path="/analytics" element={<AnalyticsDashboard />} />
  
  <Route path="/settings" element={<FirmSettings />} />
</Routes>
```

---

## DESIGN SYSTEM: GNANOVA BRAND

### Color Palette

**Primary (Deep Navy):**
- `primary-900: #0B1D33` - Main backgrounds
- `primary-800: #162945` - Card backgrounds
- `primary-700: #1E3554` - Borders, dividers

**Accent (Gold):**
- `accent-500: #C9A227` - Primary actions, highlights
- `accent-400: #D4B03A` - Hover states
- `accent-600: #A88820` - Active states

**Neutrals:**
- `white: #FFFFFF` - Text on dark backgrounds
- `gray-100: #F8F9FA` - Light backgrounds
- `gray-500: #64748B` - Secondary text
- `gray-700: #334155` - Borders

**Status Colors:**
- `success: #10B981` (Emerald)
- `warning: #F59E0B` (Amber)
- `error: #EF4444` (Red)
- `info: #3B82F6` (Blue)

### Typography

**Font Family:**
- Headings: `Inter` (sans-serif)
- Body: `Inter`
- Monospace: `JetBrains Mono` (for numbers, codes)

**Scale:**
- `text-xs: 11px` - Labels, captions
- `text-sm: 13px` - Body text
- `text-base: 14px` - Default
- `text-lg: 16px` - Subheadings
- `text-xl: 20px` - Page headings
- `text-2xl: 24px` - Dashboard titles

### Component Design Principles

1. **Consistency** - Reuse components across modules
2. **Clarity** - High contrast, readable at all sizes
3. **Professional** - Enterprise fintech aesthetic
4. **Responsive** - Mobile, tablet, desktop optimized
5. **Accessible** - WCAG 2.1 AA standards (future goal)

### Layout System

**Application Shell:**
```
┌─────────────────────────────────────┐
│ Top Navigation Bar                  │
├─────┬───────────────────────────────┤
│     │ Breadcrumbs                   │
│     ├───────────────────────────────┤
│ S   │                               │
│ i   │                               │
│ d   │   Main Content Area           │
│ e   │                               │
│ b   │                               │
│ a   │                               │
│ r   │                               │
│     │                               │
└─────┴───────────────────────────────┘
```

**Sidebar Navigation:**
- Logo & firm name
- Search bar (global)
- Primary navigation (collapsible sections)
- User profile & settings
- Notification bell

**Top Bar:**
- Breadcrumbs
- Page actions (primary button)
- Filters
- Search (contextual)

---

## SERVICE LAYER ARCHITECTURE

### Backend Services (Python)

**Location:** `backend/app/services/`

**Existing Services (Keep & Extend):**
- `checklist_generator.py` - Extend for compliance rules
- `document_classifier.py` - Enhance with data extraction
- `storage_service.py` - Keep as-is
- `email_service.py` - Keep as-is
- `sms_service.py` - Keep as-is
- `whatsapp_service.py` - Keep as-is
- `messaging.py` - Keep as-is
- `signature_service.py` - Keep as-is
- `reminder_engine.py` - Enhance for compliance
- `completion.py` - Extend for assignments
- `completion_service.py` - Extend for assignments

**New Services (Build):**
- `assignment_service.py` - Assignment logic, allocation
- `compliance_service.py` - Due date calculation, rules engine
- `billing_service.py` - Invoice generation, revenue calculations
- `workload_service.py` - Staff capacity, allocation optimization
- `analytics_service.py` - Practice metrics, profitability
- `notification_service.py` - In-app notifications
- `audit_service.py` - Audit workflows
- `ai_assistant_service.py` - AI query processing

### Service Responsibilities

**Example: Assignment Service**
```python
class AssignmentService:
    def create_assignment(self, data: CreateAssignmentDTO) -> Assignment:
        # 1. Validate data
        # 2. Generate assignment code
        # 3. Allocate staff (if auto-allocation)
        # 4. Create checklist from template
        # 5. Set up recurring if needed
        # 6. Send notifications
        # 7. Log activity
        pass
    
    def submit_for_review(self, assignment_id: UUID, user_id: UUID) -> AssignmentReview:
        # 1. Check if complete
        # 2. Create review record
        # 3. Notify reviewer
        # 4. Update status
        pass
    
    def calculate_workload(self, user_id: UUID, date_range: DateRange) -> Workload:
        # 1. Get assigned assignments
        # 2. Sum estimated hours
        # 3. Calculate capacity utilization
        pass
```

---

## INTEGRATION ARCHITECTURE

### External Services

**AI/ML:**
- Anthropic Claude API
- Use cases: Document classification, data extraction, AI assistant queries
- Rate limits: Monitor usage, implement fallback

**Communication:**
- Twilio (SMS)
- n8n (WhatsApp automation)
- Resend (Email)
- Delivery tracking in `communication_logs` table

**E-Signature:**
- DocuSign eSignature API
- Webhook for status updates
- Use for: Engagement letters, audit reports, client approvals

**Storage:**
- Supabase Storage
- Buckets: `cpaos-documents`, `firm-logos`, `invoice-pdfs`
- Access control via signed URLs

**Payment Gateways (Future):**
- Razorpay (India)
- Stripe (International)
- Integration for client online payments

---

## SECURITY ARCHITECTURE

### Authentication & Authorization

**Multi-Layer Security:**
1. **Database Level:** Row Level Security (RLS) policies
2. **API Level:** JWT validation, firm_id checks
3. **Application Level:** Role-based permissions
4. **Frontend Level:** Route guards, conditional rendering

**Permission Matrix:**
```
Role: Managing Partner
  - Full access to all modules
  - Can view all data
  - Can modify firm settings
  - Can manage users

Role: Partner
  - Access to assigned clients
  - Can approve assignments
  - Can view team data
  - Cannot modify firm settings

Role: Manager
  - Access to assigned clients
  - Can review assignments
  - Cannot approve final
  - Cannot modify settings

Role: Staff (Accountant, Article)
  - Access to assigned tasks only
  - Can submit assignments
  - Cannot approve
  - Read-only on analytics

Role: Client
  - Portal access only
  - Own data only
  - Cannot access firm data
```

### Data Security

**At Rest:**
- Database encryption (Supabase)
- Encrypted backups
- Secure environment variables

**In Transit:**
- HTTPS/TLS 1.3
- Signed URLs for documents
- Secure cookies

**Sensitive Data:**
- PAN, TAN, GSTIN - encrypt at application level (future)
- Passwords - hashed via Supabase Auth
- API keys - environment variables, never committed

### Compliance

**Data Protection:**
- GDPR-ready (for international clients)
- Data retention policies
- Client data export
- Right to deletion

**Audit Trail:**
- All actions logged in `activity_logs`
- Immutable logs (no deletion)
- Timestamp + user + IP address

---

## PERFORMANCE & SCALABILITY

### Database Optimization

**Indexing:**
- All foreign keys indexed
- Composite indexes on `(firm_id, date_field)` for filtering
- GIN indexes on JSONB columns for search

**Query Optimization:**
- Use Supabase REST client efficiently
- Avoid N+1 queries (fetch related data in one query)
- Pagination on all list endpoints (default 50 per page)

**Caching (Future):**
- Redis for session data
- Cache dashboard KPIs (5-minute TTL)
- Cache compliance rules (1-hour TTL)

### Frontend Optimization

**Code Splitting:**
- Route-based code splitting (automatic with Vite)
- Lazy load heavy components (charts, editors)

**Asset Optimization:**
- Minified JS/CSS in production
- Compressed images (WebP format)
- CDN for static assets (future)

**Performance Targets:**
- Time to Interactive (TTI): < 3 seconds
- First Contentful Paint (FCP): < 1.5 seconds
- API response time: < 500ms (95th percentile)

### Scalability

**Vertical Scaling (Initial):**
- Increase server resources as needed
- Supabase auto-scales database

**Horizontal Scaling (Future):**
- Load balancer for multiple backend instances
- Read replicas for analytics queries
- Separate job queue for background tasks (Celery + Redis)

**Capacity Planning:**
- Small firm: 10 users, 50 clients, 500 assignments/year
- Mid-size firm: 50 users, 500 clients, 5000 assignments/year
- Large firm: 200 users, 2000 clients, 20000 assignments/year

---

## DEPLOYMENT ARCHITECTURE

### Environment Strategy

**Environments:**
1. **Development** - Local dev machines
2. **Staging** - Pre-production testing
3. **Production** - Live customer environment

**Configuration:**
- Environment variables via `.env` files
- Secrets via platform (Railway Secrets, Render Environment Variables)
- Feature flags for gradual rollout (future)

### Deployment Pipeline

**Current (Manual):**
```
1. Developer commits to GitHub
2. Manual deployment to Railway/Render
3. Database migrations run manually
4. Smoke testing
```

**Target (Automated - Future):**
```
1. Developer commits to GitHub
2. GitHub Actions triggers
3. Run tests (backend + frontend)
4. Build Docker images
5. Deploy to staging
6. Automated smoke tests
7. Manual approval for production
8. Deploy to production
9. Run database migrations
10. Health check
```

### Monitoring & Observability

**Application Monitoring:**
- Sentry for error tracking
- Custom metrics endpoint `/metrics` (Prometheus format - future)

**Database Monitoring:**
- Supabase Dashboard (query performance, connections)
- Alert on slow queries (> 1 second)

**Infrastructure Monitoring:**
- Railway/Render built-in monitoring
- Uptime monitoring (UptimeRobot or similar)

**Logging:**
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log aggregation (Supabase logs, Railway logs)

---

## DISASTER RECOVERY & BACKUP

**Database Backups:**
- Supabase automated daily backups (retained 7 days)
- Weekly manual snapshots (retained 30 days)
- Backup verification monthly

**Document Storage:**
- Supabase Storage redundancy (3 copies)
- Optional external backup to S3 (future)

**Recovery Time Objective (RTO):** 4 hours  
**Recovery Point Objective (RPO):** 24 hours (daily backups)

---

## FUTURE ARCHITECTURAL ENHANCEMENTS

**Phase 6+ (Post-MVP):**
1. **Mobile Apps** - React Native for iOS/Android
2. **Real-time Features** - WebSocket for live updates
3. **Advanced Search** - Elasticsearch for full-text search
4. **Report Builder** - Custom report designer for partners
5. **API for Third-Party** - Public API for integrations
6. **Microservices** - If scale demands, separate:
   - Assignment service
   - Billing service
   - Notification service
7. **Machine Learning** - Predictive analytics:
   - Client churn prediction
   - Revenue forecasting
   - Compliance risk scoring
8. **Multi-Region** - Deploy in multiple regions for latency

---

## TECHNOLOGY DEBT & REFACTORING

**Current Technical Debt (Acceptable):**
1. No API versioning - Add `/api/v1/` prefix
2. Manual database migrations - Consider migration tool (Alembic)
3. No automated tests - Add unit tests, integration tests
4. No CI/CD pipeline - Set up GitHub Actions
5. Limited error handling - Standardize error responses

**Refactoring Opportunities (Low Priority):**
1. Repository pattern inconsistency - Standardize all database access
2. Service layer thin - Move business logic from routes to services
3. Frontend state management - Add React Query for server state
4. Component library - Extract reusable components to shared package

**Recommendation:** Accept technical debt for MVP. Refactor iteratively in Phases 4-5.

---

## SUMMARY: ARCHITECTURAL PRINCIPLES

1. **Evolutionary Architecture** - Build on what exists, don't rebuild
2. **Modular Monolith** - Simple to develop, easy to deploy
3. **API-First** - Backend exposes REST API, frontend consumes
4. **Mobile-Ready** - Responsive design, future mobile app support
5. **Secure by Default** - Multi-tenant isolation, RLS, role-based access
6. **Performance-Conscious** - Indexed queries, paginated responses
7. **Operationally Simple** - Managed services (Supabase, Railway), minimal DevOps
8. **Future-Proof** - Can scale horizontally, can extract microservices later

**This architecture supports 100+ firms with 10,000+ clients on a single instance.**

---

**Next Document:** Implementation Roadmap - Detailed phase-wise execution plan.
