-- ParameterSet: ParaShape
-- 문단 모양
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.ParaShape

import Data.String

-- ParaShape ParameterSet
public export
record ParaShapeParams where
    constructor MkParaShapeParams
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "문단 모양"
