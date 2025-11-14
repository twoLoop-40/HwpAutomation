-- ParameterSet: CharShape
-- 글자 모양
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.CharShape

import Data.String

-- CharShape ParameterSet
public export
record CharShapeParams where
    constructor MkCharShapeParams
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "글자 모양"
