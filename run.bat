@echo off
rem ----------------------------
rem run.bat — Flask + Cloudflared
rem ----------------------------
chcp 65001 >nul

rem pindah ke folder script (workdir = folder project)
cd /d "%~dp0"

rem ---------- cek python ----------
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python tidak ditemukan di PATH. Pastikan Python terinstall dan PATH sudah diset.
  echo Jika kamu pakai virtualenv, edit file ini untuk mengaktifkan venv secara manual.
  pause
  exit /b 1
)

rem ---------- cek cloudflared ----------
where cloudflared >nul 2>&1
if errorlevel 1 (
  echo [WARNING] cloudflared tidak ditemukan di PATH.
  echo Jika cloudflared terinstall tapi tidak di PATH, buka file ini dan ubah variabel CLOUD ke path lengkap.
  echo Contoh: set "CLOUD=C:\Tools\cloudflared.exe"
  echo.
  set "CLOUD="
) else (
  set "CLOUD=cloudflared"
)

rem ---------- opsional: jika pakai virtualenv, uncomment dan sesuaikan path ----------
rem set "USE_VENV=1"
rem set "VENV_PATH=venv\Scripts\activate"

rem ---------- jalankan Flask di jendela baru (tetap terbuka) ----------
if defined USE_VENV (
  start "Flask Server" cmd /k "%VENV_PATH% && python app.py"
) else (
  start "Flask Server" cmd /k "python app.py"
)

rem beri waktu Flask booting
timeout /t 5 /nobreak >nul

rem ---------- jalankan cloudflared (atau tampilkan instruksi jika tidak ada) ----------
if "%CLOUD%"=="" (
  echo cloudflared tidak ditemukan — tidak menjalankan tunnel otomatis.
  echo Untuk menjalankan tunnel secara manual:
  echo   1) Install cloudflared dan tambahkan ke PATH, atau
  echo   2) Edit run.bat dan set variabel CLOUD ke path lengkap cloudflared.exe
  echo Contoh perintah manual:
  echo   "C:\path\to\cloudflared.exe" tunnel --url http://localhost:5000
  echo.
  pause
  exit /b 0
) else (
  start "Cloudflared Tunnel" cmd /k "%CLOUD% tunnel --url http://localhost:5000"
)

echo.
echo Flask dan Cloudflared sudah dijalankan di jendela terpisah.
echo - Jendela "Flask Server" menampilkan log server (http://localhost:5000).
echo - Jendela "Cloudflared Tunnel" menampilkan URL publik dari Cloudflare.
echo.
echo Launcher ini bisa ditutup; kedua jendela akan tetap berjalan.
pause >nul
