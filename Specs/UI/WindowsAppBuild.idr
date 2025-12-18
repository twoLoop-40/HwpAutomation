||| HwpAutomation - Windows 앱 빌드 명세
|||
||| 목표:
||| - PyQt5 앱을 Windows 실행 파일(.exe)로 패키징
||| - 단일 파일 또는 폴더 배포 방식 선택
||| - 아이콘, 버전 정보 등 메타데이터 설정
|||
||| 이 파일은 "명세"이며, 실제 빌드는 PyInstaller로 수행됨.
module Specs.UI.WindowsAppBuild

import Data.Vect
import Data.List

%default total

--------------------------------------------------------------------------------
-- 1. 빌드 도구 선택
--------------------------------------------------------------------------------

||| Windows 앱 빌드 도구
public export
data BuildTool : Type where
  ||| PyInstaller - 가장 널리 사용됨, PyQt5 지원 우수
  PyInstaller : BuildTool
  ||| cx_Freeze - 대안 도구
  CxFreeze : BuildTool
  ||| Nuitka - Python → C 컴파일 (더 빠르지만 복잡)
  Nuitka : BuildTool

||| 권장 도구: PyInstaller
||| 이유:
||| - PyQt5와 호환성 우수
||| - 단일 파일(.exe) 생성 지원
||| - 풍부한 문서와 커뮤니티
public export
recommendedTool : BuildTool
recommendedTool = PyInstaller

--------------------------------------------------------------------------------
-- 2. 빌드 모드
--------------------------------------------------------------------------------

||| 배포 방식
public export
data DistributionMode : Type where
  ||| 단일 실행 파일 (--onefile)
  ||| 장점: 배포 간편, 하나의 .exe만 전달
  ||| 단점: 시작 시간 느림 (임시 폴더에 압축 해제)
  SingleFile : DistributionMode

  ||| 폴더 배포 (--onedir, 기본값)
  ||| 장점: 시작 빠름, 업데이트 용이
  ||| 단점: 여러 파일/폴더 배포 필요
  Directory : DistributionMode

||| 권장: 개발 중에는 Directory, 최종 배포는 SingleFile
public export
recommendedMode : DistributionMode
recommendedMode = SingleFile

--------------------------------------------------------------------------------
-- 2.5 콘솔 모드 (Bool 대신 의미를 타입으로 표현)
--------------------------------------------------------------------------------

||| PyInstaller 콘솔/GUI 모드
public export
data ConsoleMode : Type where
  ||| 콘솔 표시 (--console)
  WithConsole : ConsoleMode
  ||| 콘솔 숨김 (--windowed)
  Windowed : ConsoleMode

--------------------------------------------------------------------------------
-- 3. 빌드 설정
--------------------------------------------------------------------------------

||| 빌드 구성
public export
record BuildConfig where
  constructor MkBuildConfig
  ||| 앱 이름
  appName : String
  ||| 메인 스크립트 경로
  mainScript : String
  ||| 배포 방식
  mode : DistributionMode
  ||| 콘솔 모드 (GUI 앱은 Windowed 권장)
  consoleMode : ConsoleMode
  ||| 아이콘 파일 경로 (.ico)
  iconPath : Maybe String
  ||| 버전 정보
  version : String
  ||| 추가 데이터 파일 (소스, 대상)
  dataFiles : List (String, String)
  ||| 숨겨진 import (자동 감지 안 되는 모듈)
  hiddenImports : List String

||| HwpAutomation 기본 빌드 설정
public export
defaultConfig : BuildConfig
defaultConfig = MkBuildConfig
  { appName = "HwpAutomation"
  , mainScript = "ui/main_pyqt.py"
  , mode = SingleFile
  , consoleMode = WithConsole   -- 에러 로그 확인을 위해 콘솔 표시 (디버깅용)
  , iconPath = Just "assets/icon.ico"
  , version = "2.0.0"
  , dataFiles = []
  , hiddenImports =
      [ "PyQt5.sip"
      , "win32com.client"
      , "pythoncom"
      ]
  }

||| 배포용 빌드 설정 (콘솔 숨김 + 로그 파일)
||| 에러는 로그 파일로 저장
public export
releaseConfig : BuildConfig
releaseConfig = MkBuildConfig
  { appName = "HwpAutomation"
  , mainScript = "ui/main_pyqt.py"
  , mode = SingleFile
  , consoleMode = Windowed  -- 배포용: 콘솔 숨김
  , iconPath = Just "assets/icon.ico"
  , version = "2.0.0"
  , dataFiles = []
  , hiddenImports =
      [ "PyQt5.sip"
      , "win32com.client"
      , "pythoncom"
      ]
  }

--------------------------------------------------------------------------------
-- 4. PyInstaller 명령어 생성
--------------------------------------------------------------------------------

||| 모드 → 플래그 변환
public export
modeFlag : DistributionMode -> String
modeFlag SingleFile = "--onefile"
modeFlag Directory = "--onedir"

||| 콘솔 플래그
public export
consoleFlag : ConsoleMode -> String
consoleFlag WithConsole = "--console"
consoleFlag Windowed = "--windowed"

||| 아이콘 플래그
public export
iconArgs : Maybe String -> List String
iconArgs Nothing = []
iconArgs (Just path) = ["--icon=" ++ path]

||| add-data 플래그들 (PyInstaller 포맷: src;dest)
public export
dataFileArgs : List (String, String) -> List String
dataFileArgs [] = []
dataFileArgs ((src, dest) :: rest) =
  ("--add-data=" ++ src ++ ";" ++ dest) :: dataFileArgs rest

||| hidden-import 플래그들
public export
hiddenImportArgs : List String -> List String
hiddenImportArgs [] = []
hiddenImportArgs (m :: ms) = ("--hidden-import=" ++ m) :: hiddenImportArgs ms

||| PyInstaller 커맨드(토큰 리스트) 생성
public export
pyinstallerCommand : BuildConfig -> List String
pyinstallerCommand cfg =
  [ "pyinstaller"
  , "--name"
  , cfg.appName
  , modeFlag cfg.mode
  , consoleFlag cfg.consoleMode
  ]
  ++ iconArgs cfg.iconPath
  ++ dataFileArgs cfg.dataFiles
  ++ hiddenImportArgs cfg.hiddenImports
  ++ [ cfg.mainScript ]

--------------------------------------------------------------------------------
-- 5. 빌드 단계
--------------------------------------------------------------------------------

||| 빌드 단계
public export
data BuildStep : Type where
  ||| 1. PyInstaller 설치
  InstallPyInstaller : BuildStep
  ||| 2. 아이콘 준비 (선택)
  PrepareIcon : BuildStep
  ||| 3. spec 파일 생성/수정
  CreateSpecFile : BuildStep
  ||| 4. 빌드 실행
  RunBuild : BuildStep
  ||| 5. 테스트 실행
  TestExecutable : BuildStep
  ||| 6. 배포 패키징 (ZIP 등)
  PackageDistribution : BuildStep

||| 빌드 순서
public export
buildOrder : Vect 6 BuildStep
buildOrder =
  [ InstallPyInstaller
  , PrepareIcon
  , CreateSpecFile
  , RunBuild
  , TestExecutable
  , PackageDistribution
  ]

--------------------------------------------------------------------------------
-- 6. 주의사항
--------------------------------------------------------------------------------

||| 빌드 시 주의사항
public export
data BuildWarning : Type where
  ||| win32com은 genpy 캐시 문제가 있을 수 있음
  Win32comCache : BuildWarning
  ||| PyQt5는 플러그인 경로 설정 필요할 수 있음
  PyQt5Plugins : BuildWarning
  ||| 상대 경로 대신 절대 경로 또는 리소스 경로 사용
  ResourcePaths : BuildWarning
  ||| 바이러스 백신이 오탐지할 수 있음
  AntivirusFalsePositive : BuildWarning

--------------------------------------------------------------------------------
-- 7. 구현 가이드
--------------------------------------------------------------------------------

{-
=== Windows 앱 빌드 가이드 ===

※ ConsoleMode 타입 (Idris2 명세):
   - WithConsole: --console (에러 로그 확인 가능)
   - Windowed: --windowed (콘솔 숨김, 배포용)

1. PyInstaller 설치
   ```
   pip install pyinstaller
   ```
   또는
   ```
   uv pip install pyinstaller
   ```

2. 디버깅 빌드 (WithConsole - 에러 확인용)
   ```
   cd c:\Users\joonho.lee\Projects\AutoHwp
   pyinstaller --onefile --console ui/main_pyqt.py
   ```
   ※ 개발/테스트 시 반드시 --console 사용!
   ※ win32com 캐시 오류 등 확인 가능

3. 배포용 빌드 (Windowed - 콘솔 숨김)
   ```
   pyinstaller ^
     --name "HwpAutomation" ^
     --onefile ^
     --windowed ^
     --icon "assets/icon.ico" ^
     --add-data "automations;automations" ^
     --add-data "core;core" ^
     --hidden-import "PyQt5.sip" ^
     --hidden-import "win32com.client" ^
     --hidden-import "pythoncom" ^
     ui/main_pyqt.py
   ```
   ※ 배포 시 로그 파일 저장 코드 필수 (아래 참조)

4. 로그 파일 저장 (Windowed 모드 필수)
   main_pyqt.py의 main() 함수 시작 부분에 추가:
   ```python
   import sys
   import os
   from datetime import datetime

   def setup_logging():
       '''Windowed 모드에서 에러 로그를 파일로 저장'''
       if getattr(sys, 'frozen', False):
           # PyInstaller로 빌드된 경우
           log_dir = os.path.dirname(sys.executable)
           log_file = os.path.join(log_dir, 'hwpautomation.log')
           sys.stdout = open(log_file, 'a', encoding='utf-8')
           sys.stderr = sys.stdout
           print(f"\n=== {datetime.now()} ===")

   def main():
       setup_logging()  # 로그 설정
       # ... 기존 코드 ...
   ```

5. spec 파일 사용 (권장)
   - 처음 빌드 후 HwpAutomation.spec 파일 생성됨
   - spec 파일 수정하여 세부 설정 가능
   - 이후 빌드: `pyinstaller HwpAutomation.spec`

5. 출력 위치
   - dist/HwpAutomation.exe (단일 파일 모드)
   - dist/HwpAutomation/ (폴더 모드)

6. 아이콘 만들기
   - 256x256 PNG 이미지 준비
   - 온라인 변환기로 .ico 변환 (예: convertio.co)
   - 또는 GIMP/Photoshop에서 .ico로 저장

7. 빌드 크기 최적화
   - --exclude-module으로 불필요한 모듈 제외
   - UPX 압축 사용 (--upx-dir)
   - 예상 크기: 50-100MB (PyQt5 포함)

8. 문제 해결

   a) win32com 오류
      - 빌드 전: `python -c "import win32com.client"`
      - gen_py 캐시 삭제 후 재빌드

   b) PyQt5 플러그인 오류
      ```
      --add-data "C:\Python39\Lib\site-packages\PyQt5\Qt5\plugins;PyQt5\Qt5\plugins"
      ```

   c) 모듈 못 찾는 오류
      - --hidden-import 추가
      - hook 파일 작성 (hook-모듈명.py)

   d) 바이러스 오탐지
      - Windows Defender 예외 추가
      - 서명 인증서 구매하여 코드 서명 (정식 배포 시)

9. 자동화 스크립트 (build.bat)
   ```batch
   @echo off
   echo Building HwpAutomation...

   pyinstaller ^
     --name "HwpAutomation" ^
     --onefile ^
     --windowed ^
     --clean ^
     ui/main_pyqt.py

   echo Build complete! Check dist/HwpAutomation.exe
   pause
   ```

10. 배포 체크리스트
    [ ] 빌드된 exe 실행 테스트
    [ ] 플러그인 기능 모두 동작 확인
    [ ] 다른 PC에서 테스트 (의존성 누락 확인)
    [ ] README 또는 사용 설명서 포함
    [ ] ZIP으로 압축하여 배포

=== 폴더 구조 (빌드 후) ===

dist/
├── HwpAutomation.exe     # 실행 파일 (단일 파일 모드)
└── HwpAutomation/        # (폴더 모드일 경우)
    ├── HwpAutomation.exe
    ├── PyQt5/
    ├── win32com/
    └── ...

=== 권장 워크플로우 ===

개발 중:
  python ui/main_pyqt.py

테스트 빌드:
  pyinstaller --onedir --windowed ui/main_pyqt.py

최종 배포:
  pyinstaller --onefile --windowed --icon=icon.ico ui/main_pyqt.py

-}
