@echo off
echo === Scientific Data Harvester - Quick Test ===
echo.

echo 1. Checking health...
curl -s http://127.0.0.1:8000/health/
echo.
echo.

echo 2. Checking API (first 2 works)...
curl -s "http://127.0.0.1:8000/api/works/?page=1&page_size=2" | python -m json.tool
echo.
echo.

echo 3. Checking search...
curl -s "http://127.0.0.1:8000/api/works/?search=Drosophila" | python -m json.tool
echo.
echo.

echo 4. Checking admin access...
curl -s -I http://127.0.0.1:8000/admin/ | findstr HTTP
echo.
echo.

echo === Test complete! ===
echo Open browser: http://127.0.0.1:8000/
echo Admin login: admin / admin123