# AMC Stain Time Optimization System

Complete migration from Streamlit to Next.js + TypeScript + React frontend with FastAPI backend.

## Project Structure

```
anti_malaria_campaign/
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/                # Pages
│   │   │   ├── page.tsx        # Home
│   │   │   ├── single-slide/   # Single slide grading
│   │   │   ├── optimal-time/   # Optimal time finder
│   │   │   ├── batch-analysis/ # Batch analysis
│   │   │   └── pattern-viewer/ # Pattern viewer
│   │   └── components/         # Shared components
│   │       └── Sidebar.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── README.md
│
├── backend/                     # FastAPI backend
│   ├── main.py                 # API server
│   ├── requirements.txt
│   └── README.md
│
├── src/                        # ML models and utilities
│   ├── models/
│   ├── data/
│   ├── evaluation/
│   └── utils/
│
├── checkpoints/                # Trained model weights
└── PROJECT_SETUP.md           # This file
```

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python main.py
```

The backend will run at http://localhost:8000

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will run at http://localhost:3000

### 3. Access the Application

Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

## Features

### 1. Home Page
- Overview of the system
- Quick start guide
- AMC grade scale reference

### 2. Single Slide Grading
- Upload individual slide images
- Get automated grading (I-V)
- View confidence scores
- Pass/fail determination
- Detailed failure diagnosis

### 3. Optimal Time Finder
- Upload minute-by-minute sweep images
- Automated time assignment from filenames
- Visual pass probability charts
- Detailed minute-by-minute results
- Recommended optimal staining time

### 4. Batch Analysis
- Upload batch data CSV
- Compare optimal times across batches
- Site-level analysis
- Interactive visualizations
- Export capabilities

### 5. Pattern Viewer
- National staining time patterns
- Regional comparisons
- Recommended starting times
- Statistical summaries

## Technology Stack

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **ML Framework**: PyTorch
- **Image Processing**: Pillow
- **Server**: Uvicorn

## API Endpoints

- `POST /api/grade-slide` - Grade single slide
- `POST /api/optimal-time` - Find optimal staining time
- `GET /api/health` - Health check

## Development Notes

### Why Next.js over Streamlit?

1. **Performance**: Next.js provides better performance with client-side rendering and code splitting
2. **Scalability**: Easier to scale and deploy in production environments
3. **Flexibility**: More control over UI/UX and component structure
4. **Modern Stack**: TypeScript ensures type safety and better developer experience
5. **SEO**: Better support for search engine optimization if needed

### Code Organization

- **Simple and Clean**: Minimal complexity, easy to understand
- **Modular**: Each page is self-contained
- **Type-Safe**: TypeScript ensures type safety
- **Reusable**: Shared components in components folder

### Styling Approach

- Tailwind CSS for utility-first styling
- No complex CSS frameworks
- Consistent color scheme (primary: #1f77b4)
- Responsive design for all screen sizes

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy to Vercel or similar platform
```

### Backend (Docker)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
COPY src/ ../src/
COPY checkpoints/ ../checkpoints/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Author

**Sayumi Devasurendra**
- Component: Stain Time Optimization
- Version: 0.1.0
- Organization: Anti-Malaria Campaign Sri Lanka

## License

Proprietary - Anti-Malaria Campaign Sri Lanka
