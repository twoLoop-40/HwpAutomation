module Specs.Common.Encoding

import Data.String

{-
  Windows CP949 호환성을 위한 인코딩 명세

  문제: Windows 콘솔은 기본적으로 CP949 인코딩을 사용하며,
        이모지(U+2713, U+274C 등)를 출력할 수 없음

  해결 전략 (2가지 옵션):

  Option A: UTF-8 출력 설정 (채택)
    - 앱 시작 시 sys.stdout/stderr를 UTF-8로 래핑
    - 콘솔 출력 시 errors='replace'로 안전 처리
    - 기존 이모지 코드 유지 가능
    - 구현: ui/main.py 시작 부분

  Option B: 이모지 -> ASCII 변환 (미채택)
    - 모든 print()의 이모지를 ASCII로 변환
    - 콘솔 호환성 보장
    - 단점: 앱 추가 시마다 수정 필요
-}

-----------------------------------------------------------
-- 파일 분류
-----------------------------------------------------------

||| 파일 유형에 따른 처리 방식
public export
data FileCategory : Type where
  ||| 콘솔 출력용 - 이모지를 ASCII로 변환
  ConsoleOutput : FileCategory
  ||| 로직/데이터용 - 특수문자 유지 (수식 변환 등)
  LogicData : FileCategory
  ||| 기존 파일 - 건드리지 않음
  Legacy : FileCategory

||| 파일 분류 규칙
|||
||| ConsoleOutput (수정 대상):
|||   - 새로 작성한 파일
|||   - print() 문에서 이모지 사용
|||   - 예: core/hwpx_converter.py
|||
||| LogicData (수정 제외):
|||   - 수식/변환 로직에 특수문자 사용
|||   - 예: automations/latex2hwp/hwp_equation_syntax.py
|||   - 화살표(U+2192), 그리스 문자 등은 데이터
|||
||| Legacy (수정 제외):
|||   - 기존에 문제없이 동작하던 파일
|||   - pyhwpx 시절부터 사용하던 코드
public export
classifyFile : String -> FileCategory
classifyFile path =
  if isInfixOf "hwp_equation_syntax" path then LogicData
  else if isInfixOf "latex2hwp" path then LogicData
  else Legacy

-----------------------------------------------------------
-- 상태 표시 문자열
-----------------------------------------------------------

||| 상태 표시 타입
public export
data StatusIndicator : Type where
  Success : StatusIndicator
  Failure : StatusIndicator
  InProgress : StatusIndicator
  Warning : StatusIndicator
  Info : StatusIndicator

||| CP949 호환 문자열로 변환
|||
||| 변환 규칙:
|||   U+2705 (check mark button) -> "[OK]"
|||   U+274C (cross mark) -> "[FAIL]"
|||   U+1F504 (counterclockwise) -> "[...]"
|||   U+26A0 (warning) -> "[WARN]"
|||   U+1F4C1 (folder) -> "[DIR]"
|||   U+2192 (rightwards arrow) -> "->"
|||   U+1F389 (party popper) -> "[DONE]"
|||   U+2713 (check mark) -> "[OK]"
|||   U+2717 (ballot x) -> "[FAIL]"
public export
toCP949Safe : StatusIndicator -> String
toCP949Safe Success = "[OK]"
toCP949Safe Failure = "[FAIL]"
toCP949Safe InProgress = "[...]"
toCP949Safe Warning = "[WARN]"
toCP949Safe Info = "[INFO]"

-----------------------------------------------------------
-- 변환 테이블 (코드포인트만 기록)
-----------------------------------------------------------

||| 이모지 -> ASCII 변환 레코드
public export
record EmojiReplacement where
  constructor MkReplacement
  codepoint : String   -- 유니코드 코드포인트 (예: "U+2705")
  ascii : String       -- ASCII 대체 문자열

||| 변환 테이블
|||
||| Python 구현 시:
|||   EMOJI_REPLACEMENTS = {
|||     "\u2705": "[OK]",      # check mark button
|||     "\u274C": "[FAIL]",    # cross mark
|||     "\u1F504": "[...]",    # counterclockwise
|||     "\u26A0": "[WARN]",    # warning
|||     "\u1F4C1": "[DIR]",    # folder
|||     "\u2192": "->",        # rightwards arrow
|||     "\u1F389": "[DONE]",   # party popper
|||     "\u2713": "[OK]",      # check mark
|||     "\u2717": "[FAIL]",    # ballot x
|||   }
public export
replacementTable : List EmojiReplacement
replacementTable =
  [ MkReplacement "U+2705" "[OK]"
  , MkReplacement "U+274C" "[FAIL]"
  , MkReplacement "U+1F504" "[...]"
  , MkReplacement "U+26A0" "[WARN]"
  , MkReplacement "U+1F4C1" "[DIR]"
  , MkReplacement "U+2192" "->"
  , MkReplacement "U+1F389" "[DONE]"
  , MkReplacement "U+2713" "[OK]"
  , MkReplacement "U+2717" "[FAIL]"
  ]

-----------------------------------------------------------
-- 수정 대상 파일
-----------------------------------------------------------

||| 수정이 필요한 파일 (ConsoleOutput 카테고리)
|||
||| 조건:
|||   1. 새로 작성한 파일
|||   2. print()에서 이모지 출력
|||   3. 로직용 특수문자가 아님
public export
filesToFix : List String
filesToFix =
  [ "core/hwpx_converter.py"           -- 새로 작성, 이모지 출력
  , "core/hwp_to_pdf.py"               -- 화살표(U+2192) 출력
  , "core/hwp_extractor_copypaste.py"  -- 화살표(U+2192) 출력
  ]

||| 수정 제외 파일 (LogicData 카테고리)
|||
||| 이유: 특수문자가 로직/데이터의 일부
public export
filesExcluded : List String
filesExcluded =
  [ "automations/latex2hwp/hwp_equation_syntax.py"  -- 수식 변환 로직
  ]

||| 기존 파일 (Legacy 카테고리)
|||
||| 이유: 이전에 문제없이 동작했음
||| 전략: 건드리지 않음 (if it works, don't fix it)
public export
legacyFiles : List String
legacyFiles =
  [ "automations/consolidator/plugin.py"
  , "automations/converter/plugin.py"
  , "automations/merger/merger.py"
  , "automations/separator/plugin.py"
  -- ... 기타 기존 파일들
  ]

-----------------------------------------------------------
-- 해결 전략
-----------------------------------------------------------

{-
  해결 전략 요약:

  1. 근본 원인 분석
     - pyhwpx 제거 후 core/hwpx_converter.py 새로 작성
     - 새 파일에 이모지 사용 -> import 시 CP949 에러

  2. 최소 침습 원칙
     - 새로 작성한 파일만 수정
     - 기존에 동작하던 파일은 건드리지 않음
     - 로직용 특수문자는 유지

  3. 수정 방법
     a) core/hwpx_converter.py: 이미 수정 완료 ([OK], [FAIL])
     b) core/hwp_to_pdf.py: 화살표 -> ASCII
     c) core/hwp_extractor_copypaste.py: 화살표 -> ASCII

  4. 검증
     - UI 실행 테스트
     - Seperate2Img 플러그인 로드 확인
-}
