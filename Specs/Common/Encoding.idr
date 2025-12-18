module Specs.Common.Encoding

import Data.List

%default total

{-
  Windows CP949 호환성을 위한 인코딩 명세
  
  목적: Windows 콘솔 환경(CP949)에서 유니코드 이모지/특수문자로 인한 인코딩 에러 방지
  전략: 콘솔 출력용 이모지는 ASCII 대체 텍스트로 변환하고, 로직용 특수문자는 보존
-}

--------------------------------------------------------------------------------
-- 1. Core Types & Logic (Dependent Types)
--------------------------------------------------------------------------------

||| 상태 표시 종류 (의미론적 분류)
public export
data StatusType = Success | Failure | Processing | Warning | Info | Directory | Arrow | Done

||| 상태 표시 정의 (Emoji <-> ASCII 매핑)
||| 타입에 따라 이모지와 ASCII 표현을 강제함
public export
record StatusRepresentation (type : StatusType) where
  constructor MkStatusRep
  ||| 유니코드 이모지 (Windows 콘솔 출력 불가 가능성 있음)
  emoji : String
  ||| CP949 안전한 ASCII 대체 문자열
  ascii : String

||| 각 상태별 표현 정의 (총체적 함수, 누락 방지)
|||
||| Python 구현 시 매핑 참조:
|||   EMOJI_REPLACEMENTS = {
|||     "✅": "[OK]",      "✓": "[OK]",
|||     "❌": "[FAIL]",    "✗": "[FAIL]",
|||     "🔄": "[...]",
|||     "⚠️": "[WARN]",    "⚠": "[WARN]",
|||     "ℹ️": "[INFO]",
|||     "📁": "[DIR]",
|||     "→": "->",
|||     "🎉": "[DONE]"
|||   }
public export
getStatusRep : (t : StatusType) -> StatusRepresentation t
getStatusRep Success    = MkStatusRep "✅" "[OK]"     -- U+2705
getStatusRep Failure    = MkStatusRep "❌" "[FAIL]"   -- U+274C
getStatusRep Processing = MkStatusRep "🔄" "[...]"    -- U+1F504
getStatusRep Warning    = MkStatusRep "⚠"  "[WARN]"    -- U+26A0
getStatusRep Info       = MkStatusRep "ℹ"  "[INFO]"    -- U+2139
getStatusRep Directory  = MkStatusRep "📁" "[DIR]"     -- U+1F4C1
getStatusRep Arrow      = MkStatusRep "→"  "->"        -- U+2192
getStatusRep Done       = MkStatusRep "🎉" "[DONE]"    -- U+1F389

||| CP949 호환 문자열로 변환하는 헬퍼
public export
toCP949 : StatusType -> String
toCP949 t = (getStatusRep t).ascii

--------------------------------------------------------------------------------
-- 2. File & Configuration Structure
--------------------------------------------------------------------------------

||| 파일 헤더 설정
public export
utf8Header : String
utf8Header = "# -*- coding: utf-8 -*-"

||| 파일 카테고리 (변환 정책 결정을 위해)
public export
data FileCategory
  = AutomationPlugin  -- 자동화 플러그인 (UI 출력 많음 -> 적극 변환)
  | CoreLogic         -- 핵심 로직 (로그 출력 있음 -> 안전하게 변환)
  | ConverterLogic    -- 변환 로직 (주의: 수식 변환 등은 데이터이므로 변환 금지)

||| 변환 대상 파일 정의
public export
record FixTarget where
  constructor MkFixTarget
  path : String
  category : FileCategory
  description : String

--------------------------------------------------------------------------------
-- 3. Target Files Definition (중복 제거 및 구조화)
--------------------------------------------------------------------------------

||| 자동화 플러그인 파일들 (UI/로그 중심)
automationFiles : List String
automationFiles =
  [ "automations/consolidator/plugin.py"
  , "automations/converter/plugin.py"
  , "automations/latex2hwp/plugin.py"
  , "automations/mcp/tools.py"
  , "automations/merger/plugin.py"
  , "automations/separator/plugin.py"
  , "automations/seperate2Img/plugin.py"
  ]

||| 로직 및 워크플로우 파일들 (로그에 이모지 사용 확인됨)
||| 주의: hwp_equation_syntax.py 등 수식 로직 파일은 제외됨
logicFiles : List String
logicFiles =
  [ "automations/latex2hwp/batch_converter.py"
  , "automations/latex2hwp/converter.py"
  , "automations/merger/integrated_merger.py"
  , "automations/merger/parallel_preprocessor.py"
  , "automations/merger/parallel_workflow.py"
  , "automations/seperate2Img/workflow.py"
  , "automations/seperate2Img/pdf_to_image.py"
  , "core/hwpx_converter.py"
  , "core/hwp_to_pdf.py"              -- 추가: 화살표 사용
  , "core/hwp_extractor_copypaste.py" -- 추가: 화살표 사용
  ]

||| 전체 수정 대상 목록 생성
public export
filesToFix : List FixTarget
filesToFix =
  map (\p => MkFixTarget p AutomationPlugin "UI Plugin") automationFiles ++
  map (\p => MkFixTarget p CoreLogic "Core/Workflow Logic") logicFiles

--------------------------------------------------------------------------------
-- 4. Validation & Task Types
--------------------------------------------------------------------------------

||| 변환 작업 결과 추적
public export
record ConversionResult where
  constructor MkResult
  target : FixTarget
  headerAdded : Bool
  emojisReplaced : Nat
  success : Bool
