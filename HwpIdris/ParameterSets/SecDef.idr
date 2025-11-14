-- ParameterSet: SecDef
-- 구역의 속성
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.SecDef

import Data.String

-- SecDef ParameterSet
public export
record SecDefParams where
    constructor MkSecDefParams
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "구역의 속성"
