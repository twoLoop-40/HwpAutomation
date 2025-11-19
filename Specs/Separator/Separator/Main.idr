||| Separator 메인 모듈
|||
||| 전체 명세 통합 및 컴파일 검증

module Main

import Types
import XmlParser
import Extractor
import FileWriter
import Workflow

%default total

||| 기본 설정 생성 (1문제 = 1파일)
public export
defaultConfig : SeparatorConfig
defaultConfig = MkConfig
  "input.hwpx"
  HwpxInput
  "output"
  (MkNamingRule "문제" 3 ".txt")
  TextFile
  True
  OnePerFile  -- 1문제 = 1파일
  Nothing
  False

||| HWP 입력용 설정 (1문제 = 1파일)
public export
hwpConfig : String -> String -> SeparatorConfig
hwpConfig inputPath outputDir = MkConfig
  inputPath
  HwpInput
  outputDir
  (MkNamingRule "문제" 3 ".txt")
  TextFile
  True
  OnePerFile  -- 1문제 = 1파일
  (Just (MkConversionConfig True "temp" 300))
  True

||| HWPX 입력용 설정 (1문제 = 1파일)
public export
hwpxConfig : String -> String -> SeparatorConfig
hwpxConfig inputPath outputDir = MkConfig
  inputPath
  HwpxInput
  outputDir
  (MkNamingRule "문제" 3 ".txt")
  TextFile
  True
  OnePerFile  -- 1문제 = 1파일
  Nothing
  True

||| 그룹화 설정 생성 (N개씩 묶기)
|||
||| @ inputPath 입력 파일 경로
||| @ outputDir 출력 디렉토리
||| @ groupSize 그룹 크기 (예: 30)
public export
groupedConfig : String -> String -> Nat -> SeparatorConfig
groupedConfig inputPath outputDir groupSize = MkConfig
  inputPath
  HwpxInput
  outputDir
  (MkNamingRule "문제" 3 ".hwpx")
  HwpxFile
  True
  (GroupByCount groupSize)  -- N개씩 묶기
  Nothing
  True

||| 30개씩 묶는 설정
public export
grouped30Config : String -> String -> SeparatorConfig
grouped30Config inputPath outputDir =
  groupedConfig inputPath outputDir 30

||| 테스트 케이스: 6. 명제_2023.hwpx
public export
testCase408 : SeparatorConfig
testCase408 = hwpxConfig
  "Tests/seperation/6. 명제_2023.hwpx"
  "Tests/seperation/output_408"

||| 실행 시뮬레이션
|||
||| 실제 구현은 Python에서 수행
public export
simulate : SeparatorConfig -> WorkflowState
simulate = separatorPipeline

||| 테스트 실행
public export
runTest : WorkflowState
runTest = simulate testCase408

||| 성공 조건 확인
public export
testSuccess : Bool
testSuccess = isSuccessful 408 runTest

||| 명세 요약
|||
||| 1. Types: 기본 데이터 타입 (EndNoteInfo, ProblemInfo, Config 등)
||| 2. XmlParser: HWPX 파싱 (HWP 변환 포함)
||| 3. Extractor: 문제 추출 (경계 식별, 본문 필터)
||| 4. FileWriter: 파일 저장 (이름 생성, 포맷팅, 쓰기)
||| 5. Workflow: 전체 파이프라인 통합
|||
||| 전체 흐름:
|||   Input (HWP/HWPX)
|||   → Parse (XML → EndNote 추출)
|||   → Extract (문제 경계 → 본문 추출)
|||   → Write (파일명 생성 → 저장)
|||   → Complete (408개 파일)
public export
specificationSummary : String
specificationSummary = """
Separator Specification Summary
================================

Modules:
  - Types: Core data types
  - XmlParser: HWP → HWPX conversion & XML parsing
  - Extractor: Problem extraction from EndNote boundaries
  - FileWriter: Individual file generation
  - Workflow: End-to-end pipeline

Input: 6. 명제_2023.hwpx
Expected Output: 408 problem files

Pipeline:
  Input → Parse → Extract → Write → Complete
  (0%)    (20%)   (50%)     (80%)   (100%)

Estimated Time: ~20 minutes for 408 problems
"""
