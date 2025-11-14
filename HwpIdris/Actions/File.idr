-- HWP Action Table - File
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.File

import Data.String

-- File 액션 타입
public export
data FileAction
    = Close  -- 현재 리스트를 닫고 상위 리스트로 이동.
    | CloseEx  -- Close의 확장 액션으로 전체화면 보기일 때 Root
    | FileClose  -- 문서 닫기
    | FileNew  -- 새문서
    | FileOpen  -- 파일 열기
    | FileOpenMRU  -- 최근 작업 문서
    | FilePassword  -- 문서 암호
    | FilePasswordChange  -- 문서 암호 변경 및 해제
    | FilePreview  -- 미리 보기
    | FileQuit  -- 끝
    | FileRWPasswordChange  -- 문서 열기/쓰기 암호 설정
    | FileRWPasswordNew  -- 문서 열기/쓰기 암호 설정
    | FileSave  -- 파일 저장
    | FileSaveAs  -- 다른 이름으로 저장
    | FileSaveAsImage  -- 그림 포맷으로 저장하기
    | FileSaveAsImageOption  -- 그림 포맷으로 저장할 때 옵션 설정하기
    | FileSaveOptionDlg  -- 옵션
    | FileSetSecurity
    | FileTemplate  -- 문서마당
    | SaveBlockAction  -- 블록 저장하기
    | SaveFootnote  -- 주석 저장
    | SaveHistoryItem  -- 누르면 나타나는 대화상자에서 [새 버전 저장] 버
    | FileSetSecurity2  -- 사용한다.

-- 액션 ID 문자열로 변환
public export
toString : FileAction -> String
toString Close = "Close"
toString CloseEx = "CloseEx"
toString FileClose = "FileClose"
toString FileNew = "FileNew"
toString FileOpen = "FileOpen"
toString FileOpenMRU = "FileOpenMRU"
toString FilePassword = "FilePassword"
toString FilePasswordChange = "FilePasswordChange"
toString FilePreview = "FilePreview"
toString FileQuit = "FileQuit"
toString FileRWPasswordChange = "FileRWPasswordChange"
toString FileRWPasswordNew = "FileRWPasswordNew"
toString FileSave = "FileSave"
toString FileSaveAs = "FileSaveAs"
toString FileSaveAsImage = "FileSaveAsImage"
toString FileSaveAsImageOption = "FileSaveAsImageOption"
toString FileSaveOptionDlg = "FileSaveOptionDlg"
toString FileSetSecurity = "FileSetSecurity"
toString FileTemplate = "FileTemplate"
toString SaveBlockAction = "SaveBlockAction"
toString SaveFootnote = "SaveFootnote"
toString SaveHistoryItem = "SaveHistoryItem"
toString FileSetSecurity2 = "FileSetSecurity"

-- ParameterSet ID
public export
paramSetID : FileAction -> Maybe String
paramSetID Close = Nothing
paramSetID CloseEx = Nothing
paramSetID FileClose = Nothing
paramSetID FileNew = Nothing
paramSetID FileOpen = Nothing
paramSetID FileOpenMRU = Nothing
paramSetID FilePassword = Just "Password"
paramSetID FilePasswordChange = Just "Password"
paramSetID FilePreview = Nothing
paramSetID FileQuit = Nothing
paramSetID FileRWPasswordChange = Just "Password"
paramSetID FileRWPasswordNew = Just "Password"
paramSetID FileSave = Nothing
paramSetID FileSaveAs = Nothing
paramSetID FileSaveAsImage = Just "Print"
paramSetID FileSaveAsImageOption = Just "Print"
paramSetID FileSaveOptionDlg = Just "저장"
paramSetID FileSetSecurity = Just "FileSetSecurity*"
paramSetID FileTemplate = Just "FileOpen"
paramSetID SaveBlockAction = Just "FileSaveBlock"
paramSetID SaveFootnote = Just "SaveFootnote"
paramSetID SaveHistoryItem = Just "VersionInfo"
paramSetID FileSetSecurity2 = Just "Action을"

-- 설명
public export
description : FileAction -> String
description Close = "현재 리스트를 닫고 상위 리스트로 이동."
description CloseEx = "Close의 확장 액션으로 전체화면 보기일 때 Root"
description FileClose = "문서 닫기"
description FileNew = "새문서"
description FileOpen = "파일 열기"
description FileOpenMRU = "최근 작업 문서"
description FilePassword = "문서 암호"
description FilePasswordChange = "문서 암호 변경 및 해제"
description FilePreview = "미리 보기"
description FileQuit = "끝"
description FileRWPasswordChange = "문서 열기/쓰기 암호 설정"
description FileRWPasswordNew = "문서 열기/쓰기 암호 설정"
description FileSave = "파일 저장"
description FileSaveAs = "다른 이름으로 저장"
description FileSaveAsImage = "그림 포맷으로 저장하기"
description FileSaveAsImageOption = "그림 포맷으로 저장할 때 옵션 설정하기"
description FileSaveOptionDlg = "옵션"
description FileSetSecurity = "No description"
description FileTemplate = "문서마당"
description SaveBlockAction = "블록 저장하기"
description SaveFootnote = "주석 저장"
description SaveHistoryItem = "누르면 나타나는 대화상자에서 [새 버전 저장] 버"
description FileSetSecurity2 = "사용한다."

-- 총 23개 File 액션
