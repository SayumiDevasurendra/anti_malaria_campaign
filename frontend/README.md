# Stain Time Optimization Frontend

Next.js + TypeScript + React frontend for the AMC Stain Time Optimization System.

## Features

- **Home**: Overview and quick start guide
- **Single Slide Grading**: Upload and grade individual slides
- **Optimal Time Finder**: Minute-by-minute sweep analysis
- **Batch Analysis**: Compare multiple batches and sites
- **Pattern Viewer**: View national staining time patterns

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Home page
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles
│   │   ├── single-slide/         # Single slide grading page
│   │   ├── optimal-time/         # Optimal time finder page
│   │   ├── batch-analysis/       # Batch analysis page
│   │   └── pattern-viewer/       # Pattern viewer page
│   └── components/
│       └── Sidebar.tsx           # Navigation sidebar
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.ts
```

## API Integration

The frontend expects a backend API running at `http://localhost:8000`.

Key endpoints:
- `POST /api/grade-slide` - Grade a single slide
- `POST /api/optimal-time` - Find optimal staining time

## Styling

Uses Tailwind CSS for styling. Colors can be customized in `tailwind.config.ts`.

## Author

Sayumi Devasurendra
Version: 0.1.0
