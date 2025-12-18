@echo off
REM HwpAutomation Windows 빌드 스크립트
REM Specs/UI/WindowsAppBuild.idr 명세 기반
REM
REM 빌드 모드:
REM   --debug    : WithConsole 모드 (콘솔 표시, 디버깅용)
REM   --release  : Windowed 모드 (콘솔 숨김, 배포용) - 기본값

setlocal enabledelayedexpansion

REM 프로젝트 루트로 이동
cd /d "%~dp0"

REM 빌드 모드 파싱
set BUILD_MODE=release
if "%1"=="--debug" set BUILD_MODE=debug
if "%1"=="-d" set BUILD_MODE=debug

echo ===============================================
echo HwpAutomation Windows App Builder
echo ===============================================
echo.
echo Build mode: %BUILD_MODE%
echo.

REM 이전 빌드 정리
if exist "dist\HwpAutomation.exe" (
    echo Cleaning previous build...
    del /f /q "dist\HwpAutomation.exe"
)
if exist "build" (
    rmdir /s /q "build"
)

REM 빌드 실행
if "%BUILD_MODE%"=="debug" (
    echo Building with console (debug mode)...
    echo.
    pyinstaller ^
        --name "HwpAutomation" ^
        --onefile ^
        --console ^
        --clean ^
        --hidden-import "PyQt5.sip" ^
        --hidden-import "win32com.client" ^
        --hidden-import "pythoncom" ^
        ui/main_pyqt.py
) else (
    echo Building windowed (release mode)...
    echo.
    pyinstaller ^
        --name "HwpAutomation" ^
        --onefile ^
        --windowed ^
        --clean ^
        --hidden-import "PyQt5.sip" ^
        --hidden-import "win32com.client" ^
        --hidden-import "pythoncom" ^
        ui/main_pyqt.py
)

echo.
if exist "dist\HwpAutomation.exe" (
    echo ===============================================
    echo Build successful!
    echo ===============================================
    echo.
    echo Output: dist\HwpAutomation.exe
    echo.
    if "%BUILD_MODE%"=="release" (
        echo Note: Errors will be logged to hwpautomation.log
        echo       in the same folder as the executable.
    )
) else (
    echo ===============================================
    echo Build failed!
    echo ===============================================
    echo Check the error messages above.
)

echo.
pause
