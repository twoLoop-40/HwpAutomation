-- HWP Action Table - Document
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Document

import Data.String

-- Document 액션 타입
public export
data DocumentAction
    = DocFindEnd  -- 문서 찾기 종료
    | DocFindInit  -- 문서 찾기 초기화
    | DocFindNext  -- 문서 찾기 계속
    | DocSummaryInfo  -- 문서 정보
    | DocumentInfo  -- 현재 문서에 대한 정보
    | DocumentSecurity  -- 문서 보안 설정
    | PageBorder  -- 쪽 테두리/배경
    | PageBorderTab
    | PageFillTab
    | PageHiding  -- 감추기
    | PageHidingModify  -- 감추기 고치기
    | PageLandscape  -- 용지 넓게
    | PageMarginSetup  -- 편집 용지(쪽 여백 설정) 한/글 2022 부터 지원
    | PageNumPos  -- 쪽 번호 매기기
    | PageNumPosModify  -- 쪽 번호 매기기
    | PagePortrait  -- 용지 좁게
    | PageSetup  -- 편집 용지
    | PageSetupDL  -- 편집 용지(쪽 여백 설정)

-- 액션 ID 문자열로 변환
public export
toString : DocumentAction -> String
toString DocFindEnd = "DocFindEnd"
toString DocFindInit = "DocFindInit"
toString DocFindNext = "DocFindNext"
toString DocSummaryInfo = "DocSummaryInfo"
toString DocumentInfo = "DocumentInfo"
toString DocumentSecurity = "DocumentSecurity"
toString PageBorder = "PageBorder"
toString PageBorderTab = "PageBorderTab"
toString PageFillTab = "PageFillTab"
toString PageHiding = "PageHiding"
toString PageHidingModify = "PageHidingModify"
toString PageLandscape = "PageLandscape"
toString PageMarginSetup = "PageMarginSetup"
toString PageNumPos = "PageNumPos"
toString PageNumPosModify = "PageNumPosModify"
toString PagePortrait = "PagePortrait"
toString PageSetup = "PageSetup"
toString PageSetupDL = "PageSetupDL"

-- ParameterSet ID
public export
paramSetID : DocumentAction -> Maybe String
paramSetID DocFindEnd = Just "FindReplace*"
paramSetID DocFindInit = Just "FindReplace*"
paramSetID DocFindNext = Just "DocFindInfo*"
paramSetID DocSummaryInfo = Just "SummaryInfo"
paramSetID DocumentInfo = Just "DocumentInfo*"
paramSetID DocumentSecurity = Just "DocSecurity"
paramSetID PageBorder = Just "SecDef"
paramSetID PageBorderTab = Just "SecDef"
paramSetID PageFillTab = Just "SecDef"
paramSetID PageHiding = Just "PageHiding"
paramSetID PageHidingModify = Just "PageHiding"
paramSetID PageLandscape = Just "SecDef"
paramSetID PageMarginSetup = Just "SecDef"
paramSetID PageNumPos = Just "PageNumPos"
paramSetID PageNumPosModify = Just "PageNumPos"
paramSetID PagePortrait = Just "SecDef"
paramSetID PageSetup = Just "SecDef"
paramSetID PageSetupDL = Just "SecDef"

-- 설명
public export
description : DocumentAction -> String
description DocFindEnd = "문서 찾기 종료"
description DocFindInit = "문서 찾기 초기화"
description DocFindNext = "문서 찾기 계속"
description DocSummaryInfo = "문서 정보"
description DocumentInfo = "현재 문서에 대한 정보"
description DocumentSecurity = "문서 보안 설정"
description PageBorder = "쪽 테두리/배경"
description PageBorderTab = "No description"
description PageFillTab = "No description"
description PageHiding = "감추기"
description PageHidingModify = "감추기 고치기"
description PageLandscape = "용지 넓게"
description PageMarginSetup = "편집 용지(쪽 여백 설정) 한/글 2022 부터 지원"
description PageNumPos = "쪽 번호 매기기"
description PageNumPosModify = "쪽 번호 매기기"
description PagePortrait = "용지 좁게"
description PageSetup = "편집 용지"
description PageSetupDL = "편집 용지(쪽 여백 설정)"

-- 총 18개 Document 액션
