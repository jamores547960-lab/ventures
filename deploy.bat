@echo off
echo.
echo  ========================================
echo   VenturePulse Pro - Deployment Helper
echo  ========================================
echo.
echo  Choose a deployment method:
echo.
echo   [1] Streamlit Community Cloud (free, easiest)
echo   [2] Docker - Standalone app.py
echo   [3] Docker Compose - Full stack (backend + frontend)
echo   [4] Render / Railway (cloud PaaS)
echo   [5] Exit
echo.
set /p choice="  Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo  --- Streamlit Community Cloud ---
    echo  1. Push this project to GitHub
    echo  2. Go to https://share.streamlit.io
    echo  3. Sign in with GitHub
    echo  4. Click "New app" and select:
    echo       Repo:   your-repo
    echo       Branch: main
    echo       File:   app.py
    echo  5. Click Deploy - done!
    echo.
    pause
)

if "%choice%"=="2" (
    echo.
    echo  --- Building Docker Image ---
    docker build -t venturepulse .
    echo.
    echo  --- Running Container ---
    echo  Access at: http://localhost:8501
    docker run -p 8501:8501 venturepulse
)

if "%choice%"=="3" (
    echo.
    echo  --- Starting Full Stack with Docker Compose ---
    echo  Backend at:  http://localhost:8000
    echo  Frontend at: http://localhost:8501
    echo.
    docker-compose up --build
)

if "%choice%"=="4" (
    echo.
    echo  --- Render / Railway Deployment ---
    echo  1. Push this project to GitHub
    echo  2. Go to https://render.com or https://railway.app
    echo  3. Create a new Web Service
    echo  4. Connect your GitHub repo
    echo  5. Set build command:  pip install -r requirements.txt
    echo  6. Set start command:  streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    echo  7. Deploy!
    echo.
    pause
)

if "%choice%"=="5" (
    exit
)
