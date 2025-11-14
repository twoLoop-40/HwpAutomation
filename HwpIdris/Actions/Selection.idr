-- HWP Action Table - Selection
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Selection

import Data.String

-- Selection 액션 타입
public export
data SelectionAction
    = Cancel  -- ESC
    | Select  -- 선택 (F3 Key를 누른 효과)
    | SelectAll  -- 모두 선택
    | SelectColumn  -- 칸 블록 선택 (F4 Key를 누른 효과)
    | SelectCtrlFront  -- 개체선택 정방향
    | SelectCtrlReverse  -- 개체선택 역방향
    | SelectPageNumShape  -- 쪽 번호 모양

-- 액션 ID 문자열로 변환
public export
toString : SelectionAction -> String
toString Cancel = "Cancel"
toString Select = "Select"
toString SelectAll = "SelectAll"
toString SelectColumn = "SelectColumn"
toString SelectCtrlFront = "SelectCtrlFront"
toString SelectCtrlReverse = "SelectCtrlReverse"
toString SelectPageNumShape = "SelectPageNumShape"

-- ParameterSet ID
public export
paramSetID : SelectionAction -> Maybe String
paramSetID Cancel = Nothing
paramSetID Select = Nothing
paramSetID SelectAll = Nothing
paramSetID SelectColumn = Nothing
paramSetID SelectCtrlFront = Nothing
paramSetID SelectCtrlReverse = Nothing
paramSetID SelectPageNumShape = Just "AutoNum"

-- 설명
public export
description : SelectionAction -> String
description Cancel = "ESC"
description Select = "선택 (F3 Key를 누른 효과)"
description SelectAll = "모두 선택"
description SelectColumn = "칸 블록 선택 (F4 Key를 누른 효과)"
description SelectCtrlFront = "개체선택 정방향"
description SelectCtrlReverse = "개체선택 역방향"
description SelectPageNumShape = "쪽 번호 모양"

-- 총 7개 Selection 액션
