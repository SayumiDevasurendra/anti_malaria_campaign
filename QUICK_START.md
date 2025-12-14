# Quick Start Guide

Get up and running with the AMC Stain Time Optimization System in 5 minutes.

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm

## Installation (One-Time Setup)

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option 1: Automated Start (Easiest)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the Application

Open your browser: **http://localhost:3000**

## Key URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Folder Structure

```
anti_malaria_campaign/
├── frontend/          # Next.js app (port 3000)
├── backend/           # FastAPI server (port 8000)
├── src/               # Python ML modules
└── checkpoints/       # Model weights
```

## Common Commands

### Backend
```bash
cd backend
python main.py                    # Start server
uvicorn main:app --reload         # Start with hot reload
```

### Frontend
```bash
cd frontend
npm run dev                       # Development mode
npm run build                     # Production build
npm start                         # Production server
```

## Pages Overview

1. **Home** (`/`) - Overview and quick start
2. **Single Slide** (`/single-slide`) - Grade individual slides
3. **Optimal Time** (`/optimal-time`) - Find optimal staining time
4. **Batch Analysis** (`/batch-analysis`) - Compare batches
5. **Pattern Viewer** (`/pattern-viewer`) - National patterns

## Stopping the Application

- **Automated scripts**: Close the terminal windows
- **Manual start**: Press `Ctrl+C` in each terminal

## Troubleshooting

**Port already in use:**
```bash
# Windows - Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac - Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Module not found:**
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install
```

**Backend can't find model:**
- Ensure `checkpoints/best_model.pth` exists
- Train model using `train_slide_grading.py`

## First Time Usage

1. Start both servers
2. Navigate to http://localhost:3000
3. Click "Single Slide Grading" in sidebar
4. Upload a test image
5. Click "Analyze Slide"
6. View results

## Need Help?

- Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
- Check [PROJECT_SETUP.md](PROJECT_SETUP.md) for architecture
- Review [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for changes

## Tips

- Keep both terminal windows open while using the app
- Backend must be running for frontend to work
- Use Chrome or Firefox for best experience
- Check browser console for errors if something doesn't work

---

**Ready to go!** 🚀

Start the application and visit http://localhost:3000
