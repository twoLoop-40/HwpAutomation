module Specs.Common.File

import Data.String

%default total

||| 문서/산출물 형식 (Specs 전반에서 공통 사용)
public export
data DocFormat = HWP | HWPX | PDF | IMG

public export
detectDocFormat : String -> Maybe DocFormat
detectDocFormat path =
  let lowerPath = toLower path in
  if isSuffixOf ".hwpx" lowerPath then Just HWPX
  else if isSuffixOf ".hwp" lowerPath then Just HWP
  else if isSuffixOf ".pdf" lowerPath then Just PDF
  else Nothing


