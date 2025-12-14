# Installation Guide

Complete installation instructions for the AMC Stain Time Optimization System.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**

### Verify Installation

```bash
# Check Python
python --version

# Check Node.js
node --version

# Check npm
npm --version
```

## Step-by-Step Installation

### 1. Clone or Navigate to Project

```bash
cd "c:\Users\Sayumi Devasurendra\Desktop\AMC\anti_malaria_campaign"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Navigate to backend folder
cd backend

# Install required packages
pip install -r requirements.txt
```

#### Verify Model Checkpoint

Ensure you have the trained model checkpoint:
- Path: `checkpoints/best_model.pth`
- If missing, train the model using `train_slide_grading.py`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# This will install:
# - next, react, react-dom
# - typescript, @types packages
# - tailwindcss, autoprefixer, postcss
# - axios, recharts, lucide-react
```

## Running the Application

### Option 1: Using Startup Scripts (Recommended)

#### Windows
```bash
# From project root
start.bat
```

#### Linux/Mac
```bash
# From project root
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

#### Terminal 1 - Backend
```bash
cd backend
python main.py
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Accessing the Application

Once both servers are running:

- **Frontend**: Open http://localhost:3000 in your browser
- **Backend API**: Available at http://localhost:8000
- **API Docs**: Visit http://localhost:8000/docs for interactive API documentation

## Troubleshooting

### Backend Issues

#### Error: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

#### Error: Model checkpoint not found
```bash
# Check if checkpoint exists
ls checkpoints/best_model.pth

# If missing, train the model
python train_slide_grading.py
```

#### Port 8000 already in use
```bash
# Find and kill the process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in backend/main.py
```

### Frontend Issues

#### Error: Module not found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Port 3000 already in use
```bash
# Use different port
npm run dev -- -p 3001
```

#### Build errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### Common Issues

#### CORS Errors
- Ensure backend is running at http://localhost:8000
- Check CORS settings in `backend/main.py`

#### API Connection Failed
- Verify backend is running: http://localhost:8000/api/health
- Check network firewall settings
- Ensure ports 3000 and 8000 are open

## Development Setup

### Hot Reload

Both frontend and backend support hot reload:
- **Frontend**: Automatically reloads on file changes
- **Backend**: Use `--reload` flag: `uvicorn main:app --reload`

### Environment Variables (Optional)

Create `.env.local` in frontend folder:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Build

### Frontend
```bash
cd frontend
npm run build
npm start
```

### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Folder Structure After Installation

```
anti_malaria_campaign/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── __pycache__/           # Auto-generated
│   └── README.md
│
├── frontend/
│   ├── src/
│   ├── node_modules/          # Auto-generated (large)
│   ├── .next/                 # Auto-generated
│   ├── package.json
│   ├── package-lock.json      # Auto-generated
│   └── README.md
│
├── src/                       # Python modules
├── checkpoints/               # Model weights
└── PROJECT_SETUP.md
```

## Next Steps

After successful installation:

1. **Test Single Slide Grading**
   - Navigate to http://localhost:3000/single-slide
   - Upload a test image
   - Verify grading results

2. **Test Optimal Time Finder**
   - Navigate to http://localhost:3000/optimal-time
   - Upload multiple sweep images
   - Check optimal time results

3. **Explore Other Features**
   - Batch Analysis
   - Pattern Viewer

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review logs in terminal windows
3. Verify all prerequisites are installed
4. Check file permissions
5. Contact: Sayumi Devasurendra

## Uninstallation

To remove the application:

```bash
# Remove frontend dependencies
cd frontend
rm -rf node_modules .next

# Remove Python cache
cd ..
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

The core project files will remain for future use.
