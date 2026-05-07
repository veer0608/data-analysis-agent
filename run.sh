#!/usr/bin/env bash
# Start both the FastAPI backend and Streamlit frontend

set -e
cd "$(dirname "$0")"

# Load env vars
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "==========================================="
echo "  Data Analysis Tool — Startup"
echo "==========================================="
echo ""

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "[*] Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "[*] Starting FastAPI backend  → http://localhost:8000"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 2  # Give the backend time to start

echo "[*] Starting Streamlit frontend → http://localhost:8501"
cd frontend
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "==========================================="
echo "  Backend  : http://localhost:8000"
echo "  Frontend : http://localhost:8501"
echo "  API Docs : http://localhost:8000/docs"
echo "==========================================="
echo "Press Ctrl+C to stop both servers."

# Wait and clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" EXIT INT TERM
wait
