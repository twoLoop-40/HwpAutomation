-- ParameterSet: ColDef
-- 단 정의 속성
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.ColDef

import Data.String

-- ColDef ParameterSet
public export
record ColDefParams where
    constructor MkColDefParams
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "단 정의 속성"
