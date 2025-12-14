#!/bin/bash

echo "========================================"
echo "AMC Stain Time Optimization System"
echo "========================================"
echo ""

echo "Starting Backend Server..."
cd backend
python main.py &
BACKEND_PID=$!

cd ..

sleep 3

echo "Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "========================================"
echo "Both servers are running!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers..."
echo "========================================"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
