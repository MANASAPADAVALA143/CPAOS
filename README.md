# CPAOS - CPA Client Onboarding System

A comprehensive client onboarding platform designed for CPA firms and accounting practices to streamline the client intake process.

## Overview

CPAOS (CPA Onboarding System) is a full-stack web application that automates and manages the client onboarding workflow for accounting firms. It provides features for document collection, checklist management, e-signatures, and multi-channel client communication.

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Routing**: React Router v6
- **State Management**: React hooks
- **Charts**: Recharts
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (python-jose)
- **AI Integration**: Anthropic Claude
- **E-Signature**: DocuSign
- **Communication**: Twilio (SMS/Voice/WhatsApp)
- **Email**: Resend
- **Task Scheduling**: APScheduler

## Project Structure

```
.
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── routes/     # Individual route modules
│   │   ├── core/           # Core configuration and security
│   │   ├── db/             # Database connection and repository
│   │   ├── models/         # Data models and enums
│   │   └── services/       # Business logic services
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container configuration
│   └── seed_data.py       # Database seeding script
│
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utilities and API client
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
│
├── n8n/                   # n8n workflow automation
├── Dockerfile             # Root Docker configuration
└── render.yaml            # Render deployment configuration
```

## Features

- **Client Management**: Create and manage client profiles with comprehensive information
- **Country-Specific Checklists**: Automated checklist generation for USA, Canada, UK, Australia, and other countries
- **Document Management**: Upload, classify, and track client documents
- **E-Signature Integration**: DocuSign integration for document signing
- **Multi-Channel Communication**: 
  - Email notifications
  - SMS messaging
  - WhatsApp integration
  - Voice call capabilities via Vapi
- **Client Portal**: Self-service portal for clients to upload documents and track progress
- **Dashboard Analytics**: Visual analytics and reporting for firm staff
- **Document Expiry Tracking**: Automatic tracking of document expiration dates
- **Approval Workflow**: Approve, reject, or waive checklist items

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- Supabase account
- (Optional) DocuSign, Twilio, and Anthropic API keys for full functionality

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy the example environment file and configure:
```bash
cp .env.example .env
```

4. Update `.env` with your credentials:
   - Supabase URL and service key
   - API keys for third-party services
   - Generate a secure SECRET_KEY

5. Run database migrations (execute `supabase_schema.sql` in your Supabase project)

6. Start the development server:
```bash
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration:
```bash
VITE_API_URL=http://localhost:8001
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Environment Variables

### Backend Required Variables
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Supabase service role key
- `SECRET_KEY`: Secret key for JWT token generation
- `FRONTEND_URL`: Frontend application URL (for CORS)

### Backend Optional Variables (for full functionality)
- `ANTHROPIC_API_KEY`: For AI-powered features
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`: For SMS/Voice/WhatsApp
- `DOCUSIGN_INTEGRATION_KEY`, `DOCUSIGN_ACCOUNT_ID`, `DOCUSIGN_PRIVATE_KEY`: For e-signatures
- `N8N_WEBHOOK_URL`: For workflow automation

### Frontend Required Variables
- `VITE_API_URL`: Backend API URL
- `VITE_SUPABASE_URL`: Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Supabase anonymous key

## Deployment

### Railway (Current Configuration)
The project includes Railway configuration for easy deployment:

```bash
railway up
```

### Render (Alternative)
The project includes a `render.yaml` blueprint for deployment on Render:
1. Connect your GitHub repository to Render
2. Render will automatically detect the configuration
3. Configure environment variables in the Render dashboard

### Docker
Both frontend and backend include Dockerfiles for containerized deployment.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Development

### Seeding Sample Data
```bash
cd backend
python seed_data.py
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

Backend:
```bash
cd backend
# The application uses uvicorn in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Contributing

This is a private project. For questions or issues, contact the repository owner.

## License

Private - All rights reserved
