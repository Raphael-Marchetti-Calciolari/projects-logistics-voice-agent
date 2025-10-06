# Logistics Voice Agent - Frontend

React + Vite frontend for the Logistics Voice Agent system.

## 🚀 Quick Start with Docker Compose

**Recommended:** Use Docker Compose from the project root (see [main README](../README.md)).

This guide covers Docker Compose setup and local development options.

## Prerequisites

- Docker and Docker Compose (for containerized setup)
- OR Node.js 20+ (for local development)
- Backend service running (see [backend README](../backend/README.md))

## Setup Instructions

### 1. Configure Environment Variables

```bash
# From frontend directory
cp .env.example .env
```

The default configuration should work with Docker Compose:

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** This should match the port your backend is running on (default: 8000).

### 2. Run with Docker Compose

From the **project root**:
```bash
docker compose up
```

The frontend will be available at:
- **Application**: http://localhost:5173

**No code modifications are necessary** - the app is configured to work with the containerized backend.

## Local Development (Without Docker)

If you prefer to run the frontend locally:

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

The application will open at http://localhost:5173 with hot module replacement (HMR) enabled.

## 🎯 Features

### Pages

1. **Test Calls** - Initiate web-based voice calls
   - Select scenario type (Check-in or Emergency)
   - Enter driver information
   - Start real-time voice conversation

2. **Previous Calls** - View call history
   - Filter by scenario type
   - View transcripts and structured data
   - Search by driver name, phone, or load number

3. **Configuration** - Manage agent settings
   - Edit system prompts
   - Configure Retell AI settings
   - Update LLM parameters

## 🔧 Troubleshooting

### Port 5173 Already in Use
```bash
# Find and kill the process
lsof -i :5173
kill -9 <PID>

# Or change the port in vite.config.js and docker-compose.yml
```

### Backend Connection Errors
- Verify `VITE_API_BASE_URL` matches your backend URL
- Ensure backend is running: `docker compose ps`
- Check backend health: http://localhost:8000/docs

### Environment Variables Not Loading
- Vite requires the `VITE_` prefix for client-side env variables
- Restart the container after changing `.env`: `docker compose restart frontend`
- Verify `.env` file is in the `frontend/` directory

### Build Errors
```bash
# Rebuild the container from scratch
docker compose down
docker compose build --no-cache frontend
docker compose up
```

### Hot Reload Not Working
- When using Docker volumes, HMR should work automatically
- If not, try: `docker compose restart frontend`
- For local development, ensure Vite dev server is running

### Retell Web Client Issues
- Check browser console for errors
- Ensure you have microphone permissions enabled
- Verify backend webhook is configured correctly
- Test with a different browser if issues persist

## 📁 Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # Application entry point
│   ├── client.js            # Retell Web Client setup
│   ├── constants.js         # App constants
│   ├── index.css            # Global styles
│   ├── components/          # Reusable components
│   │   ├── Layout.jsx
│   │   ├── RetellWebCall.jsx
│   │   └── ErrorBoundary.jsx
│   ├── pages/               # Page components
│   │   ├── TestCalls.jsx
│   │   ├── PreviousCalls.jsx
│   │   ├── CallResults.jsx
│   │   └── Configuration.jsx
│   ├── api/                 # API client functions
│   │   ├── calls.js
│   │   └── configurations.js
│   ├── hooks/               # Custom React hooks
│   │   ├── useCalls.js
│   │   └── useConfigurations.js
│   └── utils/               # Utility functions
│       └── formatters.js
├── index.html               # HTML entry point
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
├── package.json             # Dependencies and scripts
└── Dockerfile               # Container definition
```

## 🎨 Styling

The project uses:
- **Tailwind CSS** for utility-first styling
- **PostCSS** for CSS processing
- Responsive design for mobile and desktop

## 🧪 Development Commands

```bash
# Install dependencies
npm install

# Start dev server (local)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | Yes | `http://localhost:8000` | Backend API base URL |

**Important:** Environment variables must be prefixed with `VITE_` to be accessible in the browser.

## 📚 Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **React Router** - Client-side routing
- **Retell Web SDK** - Voice AI integration
- **Axios** - HTTP client (via fetch API)

## 🆘 Getting Help

- Check the [main README](../README.md) for overall setup
- Review [backend README](../backend/README.md) for API details
- Check browser console for client-side errors
- Review Docker logs: `docker compose logs -f frontend`
