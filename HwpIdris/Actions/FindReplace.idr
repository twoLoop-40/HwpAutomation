-- HWP Action Table - FindReplace
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.FindReplace

import Data.String

-- FindReplace 액션 타입
public export
data FindReplaceAction
    = FindAll  -- 모두 찾기
    | FindDlg  -- 찾기
    | FindForeBackBookmark  -- 앞뒤로 찾아가기 : 책갈피
    | FindForeBackCtrl  -- 앞뒤로 찾아가기 : 조판 부호
    | FindForeBackFind  -- 앞뒤로 찾아가기 : 찾기
    | FindForeBackLine  -- 앞뒤로 찾아가기 : 줄
    | FindForeBackPage  -- 앞뒤로 찾아가기 : 페이지
    | FindForeBackSection  -- 앞뒤로 찾아가기 : 구역
    | FindForeBackStyle  -- 앞뒤로 찾아가기 : 스타일
    | FindOption  -- 찾기 옵션 한/글 2024 부터 지원
    | ReplaceDlg  -- 찾아 바꾸기
    | ReplacePrivateInfoDlg  -- 개인 정보 찾아 숨기기(문자열 치환)
    | SearchAddress  -- 주소 검색
    | SearchForeign  -- 외래어사전검색
    | SearchPrivateInfo  -- 개인 정보 찾아 감추기(암호화)

-- 액션 ID 문자열로 변환
public export
toString : FindReplaceAction -> String
toString FindAll = "FindAll"
toString FindDlg = "FindDlg"
toString FindForeBackBookmark = "FindForeBackBookmark"
toString FindForeBackCtrl = "FindForeBackCtrl"
toString FindForeBackFind = "FindForeBackFind"
toString FindForeBackLine = "FindForeBackLine"
toString FindForeBackPage = "FindForeBackPage"
toString FindForeBackSection = "FindForeBackSection"
toString FindForeBackStyle = "FindForeBackStyle"
toString FindOption = "FindOption"
toString ReplaceDlg = "ReplaceDlg"
toString ReplacePrivateInfoDlg = "ReplacePrivateInfoDlg"
toString SearchAddress = "SearchAddress"
toString SearchForeign = "SearchForeign"
toString SearchPrivateInfo = "SearchPrivateInfo"

-- ParameterSet ID
public export
paramSetID : FindReplaceAction -> Maybe String
paramSetID FindAll = Just "FindReplace*"
paramSetID FindDlg = Just "FindReplace"
paramSetID FindForeBackBookmark = Nothing
paramSetID FindForeBackCtrl = Nothing
paramSetID FindForeBackFind = Nothing
paramSetID FindForeBackLine = Nothing
paramSetID FindForeBackPage = Nothing
paramSetID FindForeBackSection = Nothing
paramSetID FindForeBackStyle = Nothing
paramSetID FindOption = Just "FindReplace"
paramSetID ReplaceDlg = Just "FindReplace"
paramSetID ReplacePrivateInfoDlg = Nothing
paramSetID SearchAddress = Just "+"  -- Internal
paramSetID SearchForeign = Just "+"  -- Internal
paramSetID SearchPrivateInfo = Nothing

-- 설명
public export
description : FindReplaceAction -> String
description FindAll = "모두 찾기"
description FindDlg = "찾기"
description FindForeBackBookmark = "앞뒤로 찾아가기 : 책갈피"
description FindForeBackCtrl = "앞뒤로 찾아가기 : 조판 부호"
description FindForeBackFind = "앞뒤로 찾아가기 : 찾기"
description FindForeBackLine = "앞뒤로 찾아가기 : 줄"
description FindForeBackPage = "앞뒤로 찾아가기 : 페이지"
description FindForeBackSection = "앞뒤로 찾아가기 : 구역"
description FindForeBackStyle = "앞뒤로 찾아가기 : 스타일"
description FindOption = "찾기 옵션 한/글 2024 부터 지원"
description ReplaceDlg = "찾아 바꾸기"
description ReplacePrivateInfoDlg = "개인 정보 찾아 숨기기(문자열 치환)"
description SearchAddress = "주소 검색"
description SearchForeign = "외래어사전검색"
description SearchPrivateInfo = "개인 정보 찾아 감추기(암호화)"

-- 총 15개 FindReplace 액션
