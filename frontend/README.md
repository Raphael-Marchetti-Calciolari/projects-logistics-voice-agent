# Logistics Voice Agent - Frontend

React + Vite frontend for the Logistics Voice Agent system.

## Prerequisites

- Node.js 18+ (v20 recommended)
- npm or yarn
- Backend server running (see `backend/README.md`)

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** Make sure this matches the port your backend is running on (default: 8000)

### 3. Start Development Server

```bash
npm run dev
```

### 4. Open Application

Visit [http://localhost:5173](http://localhost:5173) in your browser.
