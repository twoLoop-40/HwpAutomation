module Specs.Seperate2Img.Workflow

import Specs.Seperate2Img.Types

%default total

||| 주요 작업 함수 시그니처
||| 실제 구현은 Python 플러그인에서 이루어짐
public export
interface Seperate2ImgOps where
  ||| 0단계: 입력 파일 전처리 (Merger.ParallelPreprocessor 재사용)
  ||| Input: 입력 파일 경로
  ||| Output: 전처리된 임시 파일 경로 (전처리 실패 시 원본 경로 반환 가능)
  ||| 기능: 빈 문단 제거, 1단 변환 등
  preprocessInput : String -> Seperate2ImgConfig -> IO String

  ||| 1단계: HWP 파일 분리 (Separator 재사용)
  ||| Input: 설정 (전처리된 파일 경로 사용)
  ||| Output: 분리된 HWP 파일 경로 리스트
  separateProblems : Seperate2ImgConfig -> IO (List String)

  ||| 2단계: HWP -> PDF 변환 (Converter 재사용)
  ||| Input: HWP 파일 경로 리스트
  ||| Output: 생성된 PDF 파일 경로 리스트
  convertToPdf : List String -> IO (List String)

  ||| 3단계: PDF -> Image 변환 (pypdfium2 사용)
  ||| Input: PDF 파일 경로 리스트, 설정
  ||| Output: 생성된 이미지 파일 경로 리스트
  ||| 중요: 
  ||| 1. 파일 핸들 누수를 막기 위해 PDF 리소스는 반드시 해제되어야 함
  ||| 2. 다중 페이지 PDF의 경우 모든 페이지를 이미지로 변환해야 함
  ||| 3. 설정에 따라 이미지 여백 제거(Auto-Crop) 수행 (Pillow 사용)
  convertToImage : List String -> Seperate2ImgConfig -> IO (List String)

||| 전체 워크플로우 실행
||| 각 단계를 순차적으로 실행하고 결과를 집계
public export
runWorkflow : Seperate2ImgOps => Seperate2ImgConfig -> IO ProcessingResult
runWorkflow config = do
  -- 0. 전처리
  preprocessedInput <- preprocessInput config.inputPath config
  
  -- 전처리된 파일로 설정 업데이트 (명세상 표현, 실제로는 config 내부를 바꾸거나 별도 인자로 전달)
  -- 여기서는 설명을 위해 config의 inputPath를 업데이트한다고 가정
  let processedConfig = { inputPath := preprocessedInput } config
  
  -- 1. 분리
  hwpFiles <- separateProblems processedConfig
  
  -- 2. PDF 변환
  pdfFiles <- convertToPdf hwpFiles
  
  -- 3. 이미지 변환
  imgFiles <- convertToImage pdfFiles config
  
  -- 결과 반환
  pure $ MkResult 
    True 
    (length hwpFiles) 
    (length imgFiles) 
    (minus (length hwpFiles) (length imgFiles))
    imgFiles

{-
Python Implementation Guide
===========================

File: automations/seperate2Img/workflow.py

0. preprocessInput 매핑
   - Class: automations.merger.parallel_preprocessor.ParallelPreprocessor
   - Usage:
     preprocessor = ParallelPreprocessor(config)
     success_results, _ = preprocessor.preprocess_parallel([input_path])
     if success_results:
         return success_results[0].preprocessed_path
     return input_path # 실패 시 원본 사용

1. separateProblems 매핑
   - Function: automations.separator.separator.separate_problems
   - Usage:
     # 전처리된 경로 사용
     config = SeparatorConfig.for_hwpx(preprocessed_path, temp_dir)
     config.output_format = OutputFormat.HWP
     result = separate_problems(config)
     return result.output_files

2. convertToPdf 매핑
   - Function: core.hwp_to_pdf.convert_hwp_to_pdf_parallel
   - Usage:
     results = convert_hwp_to_pdf_parallel(hwp_files, max_workers=5)
     return [path for success, _, path in results if success]

3. convertToImage 매핑
   - Library: pypdfium2, Pillow
   - Multi-page Support & Trim Whitespace:
     
     from PIL import Image, ImageChops
     
     def trim(im, padding=10):
         bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
         diff = ImageChops.difference(im, bg)
         diff = ImageChops.add(diff, diff, 2.0, -100)
         bbox = diff.getbbox()
         if bbox:
             # add padding
             left, upper, right, lower = bbox
             left = max(0, left - padding)
             upper = max(0, upper - padding)
             right = min(im.size[0], right + padding)
             lower = min(im.size[1], lower + padding)
             return im.crop((left, upper, right, lower))
         return im

     # ... inside loop ...
     pil_image = bitmap.to_pil()
     
     if trim_whitespace:
         pil_image = trim(pil_image)
         
     pil_image.save(out_path)

4. 의존성
   - automations.merger (전처리 로직)
   - automations.separator (분리 로직)
   - core.hwp_to_pdf (PDF 변환 로직)
   - pypdfium2 (이미지 변환 로직)
   - Pillow (이미지 처리 및 저장)
-}
