-- HWP Action Table - Field
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Field

import Data.String

-- Field 액션 타입
public export
data FieldAction
    = MailMergeField  -- 메일 머지 필드(표시달기 or 고치기)
    | MailMergeGenerate  -- 메일 머지 만들기
    | MailMergeInsert  -- 메일 머지 표시 달기
    | MailMergeModify  -- 메일 머지 고치기

-- 액션 ID 문자열로 변환
public export
toString : FieldAction -> String
toString MailMergeField = "MailMergeField"
toString MailMergeGenerate = "MailMergeGenerate"
toString MailMergeInsert = "MailMergeInsert"
toString MailMergeModify = "MailMergeModify"

-- ParameterSet ID
public export
paramSetID : FieldAction -> Maybe String
paramSetID MailMergeField = Nothing
paramSetID MailMergeGenerate = Just "MailMergeGenerate"
paramSetID MailMergeInsert = Just "FieldCtrl"
paramSetID MailMergeModify = Just "FieldCtrl"

-- 설명
public export
description : FieldAction -> String
description MailMergeField = "메일 머지 필드(표시달기 or 고치기)"
description MailMergeGenerate = "메일 머지 만들기"
description MailMergeInsert = "메일 머지 표시 달기"
description MailMergeModify = "메일 머지 고치기"

-- 총 4개 Field 액션
