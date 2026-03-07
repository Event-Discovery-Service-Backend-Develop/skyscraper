@echo off
echo === Scientific Data Harvester - Quick API Test ===

set BASE_URL=http://127.0.0.1:8000

echo 1. Testing health endpoint...
curl -s %BASE_URL%/health/

echo.
echo 2. Getting JWT token...
curl -s -X POST %BASE_URL%/api/token/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" > token.json

echo.
echo 3. Extracting access token...
powershell -Command "$json = Get-Content token.json | ConvertFrom-Json; $json.access" > access_token.txt
set /p ACCESS_TOKEN=<access_token.txt

echo Token obtained: !ACCESS_TOKEN!

echo.
echo 4. Testing API with token...
curl -s -H "Authorization: Bearer !ACCESS_TOKEN!" "%BASE_URL%/api/works/?page=1&page_size=2"

echo.
echo 5. Testing search...
curl -s -H "Authorization: Bearer !ACCESS_TOKEN!" "%BASE_URL%/api/works/?search=machine"

echo.
echo === Test completed ===
echo.
echo Open in browser:
echo - Main page: %BASE_URL%/
echo - Admin panel: %BASE_URL%/admin/ (admin/admin123)
echo - API Tester: %BASE_URL%/api-test/
echo - Health: %BASE_URL%/health/

del token.json access_token.txt 2>nul