# Smart University Admin - React Frontend

Modern React + TypeScript + Vite frontend for Smart University Admin, a natural language to SQL query interface with an immersive UI.

## Features

- 🎨 **Modern UI**: Dark theme with video background, glassmorphism, and smooth animations
- 💬 **Chat Interface**: Natural language queries converted to SQL
- 📊 **DBMS Demo**: Interactive presentation of 50+ pre-built SQL queries across 10 categories
- ⚡ **Real-time Results**: Instant query execution with table visualization
- 🔄 **Caching**: Backend caching for improved performance
- 📱 **Responsive**: Works on all screen sizes

## Tech Stack

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS 4 + Custom CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Backend**: FastAPI (separate service)

## Setup & Run

### Prerequisites

- Node.js 18+
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env.local
   # Edit .env.local if needed (default: http://localhost:8000/api)
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:3000`

### Backend Integration

The frontend expects the FastAPI backend to be running at `http://localhost:8000` with the following endpoints:

- `POST /api/query` - Submit natural language query
- `GET /api/demo/categories` - Get demo categories
- `GET /api/demo/{category}` - Get category queries
- `GET /api/cache/stats` - Get cache statistics
- `DELETE /api/cache/clear` - Clear cache

## Production Build

1. Build the React app:
   ```bash
   npm run build
   ```

2. The `dist/` directory will contain the production build.

3. The FastAPI backend is configured to serve these static files in production mode.

## Project Structure

```
frontend-v2/
├── src/
│   ├── components/
│   │   ├── SQLDisplay.tsx      # SQL syntax display
│   │   ├── ResultsTable.tsx    # Query results table
│   │   └── DemoPanel.tsx       # DBMS Demo presenter
│   ├── services/
│   │   └── apiService.ts       # Backend API client
│   ├── App.tsx                 # Main application
│   ├── types.ts                # TypeScript definitions
│   ├── constants.ts            # App constants
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Type-check with TypeScript

## Notes

- This frontend was migrated from a Google AI Studio template to work with our custom FastAPI backend
- The Gemini API integration was replaced with direct backend API calls
- Mock data was replaced with real database queries

