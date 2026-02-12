# setup_workspace.ps1
# สคริปต์สำหรับเตรียม Workspace: ติดตั้งเครื่องมือ, Docker, สร้างโครงสร้างไฟล์ และย้ายไฟล์เก่า

# 1. ตรวจสอบสิทธิ์ Admin
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Please Run as Administrator!" -ForegroundColor Red; Start-Sleep 3; Exit
}

Write-Host "=== CKLab Workspace Setup (Django + Docker + uv) ===" -ForegroundColor Cyan

# 2. ติดตั้ง uv ผ่าน Winget
Write-Host "`n[1/6] Checking System Tools..." -ForegroundColor Yellow
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    winget install --id astral-sh.uv --exact --accept-source-agreements --silent
} else { Write-Host "uv is already installed." -ForegroundColor Green }

# 3. ติดตั้ง VS Code Extensions
Write-Host "`n[2/6] Installing VS Code Extensions..." -ForegroundColor Yellow
if (Get-Command code -ErrorAction SilentlyContinue) {
    $exts = @("ms-python.python", "charliermarsh.ruff", "ms-azuretools.vscode-docker", "humao.rest-client")
    foreach ($e in $exts) { code --install-extension $e --force | Out-Null; Write-Host "Installed: $e" -ForegroundColor Gray }
}

# 4. สร้าง docker-compose.yml
Write-Host "`n[3/6] Creating docker-compose.yml..." -ForegroundColor Yellow
@"
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: cklab_postgres
    restart: always
    environment:
      POSTGRES_DB: cklab_db
      POSTGRES_USER: cklab_admin
      POSTGRES_PASSWORD: secretpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
"@ | Set-Content -Path "docker-compose.yml" -Encoding UTF8

# 5. สร้างโครงสร้าง Django App (lab_management)
Write-Host "`n[4/6] Creating App Structure (lab_management)..." -ForegroundColor Yellow
$dirs = @(
    "lab_management", "lab_management/migrations",
    "lab_management/static/cklab/css", "lab_management/static/cklab/js", "lab_management/static/cklab/img",
    "lab_management/templates/cklab/kiosk", "lab_management/templates/cklab/admin"
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }

# สร้างไฟล์ว่างและ Config เริ่มต้น
New-Item -ItemType File -Path "lab_management/__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "lab_management/migrations/__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "lab_management/urls.py" -Force | Out-Null

# สร้าง apps.py (แทนการ run startapp)
@"
from django.apps import AppConfig
class LabManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lab_management'
"@ | Set-Content "lab_management/apps.py" -Encoding UTF8

# 6. ย้ายไฟล์เก่า (Auto-Migration)
Write-Host "`n[5/6] Migrating Old Files..." -ForegroundColor Yellow
if (Test-Path "cklab") {
    Copy-Item "cklab/*.css" "lab_management/static/cklab/css" -Force -ErrorAction SilentlyContinue
    Copy-Item "cklab/*.js" "lab_management/static/cklab/js" -Force -ErrorAction SilentlyContinue
    if (Test-Path "cklab/img") { Copy-Item "cklab/img/*" "lab_management/static/cklab/img" -Recurse -Force }
    
    # แยก HTML
    Get-ChildItem "cklab/*.html" | ForEach-Object {
        if ($_.Name -like "admin-*") { Copy-Item $_.FullName "lab_management/templates/cklab/admin" -Force }
        else { Copy-Item $_.FullName "lab_management/templates/cklab/kiosk" -Force }
    }
    Write-Host "Files migrated successfully!" -ForegroundColor Green
} else { Write-Host "Old 'cklab' folder not found. Skipping migration." -ForegroundColor Red }

Write-Host "`n=== Setup Complete! Next Steps in Terminal: ===" -ForegroundColor Cyan
Write-Host "1. uv venv"
Write-Host "2. .\.venv\Scripts\activate"
Write-Host "3. uv pip install django psycopg2-binary python-dotenv"
Write-Host "4. django-admin startproject cklab_project ."
Write-Host "5. docker compose up -d"
Write-Host "6. (IMPORTANT) Update settings.py, urls.py, models.py, views.py from the Guide."
Write-Host "7. python manage.py makemigrations && python manage.py migrate"