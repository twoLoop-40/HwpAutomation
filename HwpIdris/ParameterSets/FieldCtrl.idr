-- ParameterSet: FieldCtrl
-- 필드 컨트롤의 공통 데이터
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.FieldCtrl

import Data.String

-- FieldCtrl ParameterSet
public export
record FieldCtrlParams where
    constructor MkFieldCtrlParams
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "필드 컨트롤의 공통 데이터"
