-- HWP Action Table - Text
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Text

import Data.String

-- Text 액션 타입
public export
data TextAction
    = BreakColDef  -- 단 정의 삽입
    | BreakColumn  -- 단 나누기
    | BreakLine  -- line break
    | BreakPage  -- 쪽 나누기
    | BreakPara  -- 문단 나누기
    | BreakSection  -- 구역 나누기
    | Delete  -- Delete
    | DeleteBack  -- Backspace
    | DeleteCtrls  -- 조판 부호 지우기
    | DeleteDocumentMasterPage  -- 문서 전체 바탕쪽 삭제
    | DeleteDutmal  -- 덧말 지우기
    | DeleteField  -- 누름틀/메모 안의 내용은 지우지 않고, 단순히 누
    | DeleteFieldMemo  -- 메모 지우기
    | DeleteLine  -- CTRL-Y (한줄 지우기)
    | DeleteLineEnd  -- ALT-Y (현재 커서에서 줄 끝까지 지우기)
    | DeletePage  -- 쪽 지우기
    | DeletePrivateInfoMark  -- 개인 정보 감추기한 정보 다시보기
    | DeleteSectionMasterPage  -- 구역 바탕쪽 삭제
    | DeleteWord  -- 단어 지우기 CTRL-T
    | DeleteWordBack  -- CTRL-BS(Back Space)
    | Insert  -- Modify 하이퍼링크 액션
    | InsertAutoNum  -- 번호 다시 넣기
    | InsertCCLMark  -- CCL 넣기
    | InsertChart  -- 차트 만들기
    | InsertConnectLineArcBoth  -- 개체 연결선(구부러진 양쪽 화살표 연결선)
    | InsertConnectLineArcOneWay  -- 개체 연결선(구부러진 화살표 연결선)
    | InsertConnectLineMultiArcB  -- 연결선 반복해서 그리기(구부러진 양쪽 화살
    | InsertConnectLineMultiArcN  -- 연결선 반복해서 그리기(구부러진 양쪽 화살
    | InsertConnectLineMultiArcO  -- 연결선 반복해서 그리기(구부러진 양쪽 화살
    | InsertConnectLineMultiStra  -- 연결선 반복해서 그리기(직선 양쪽 화살표 연
    | InsertConnectLineMultiStra2  -- 연결선 반복해서 그리기(직선 화살표 연결
    | InsertConnectLineMultiStro  -- 연결선 반복해서 그리기(꺾인 양쪽 화살표 연
    | InsertConnectLineMultiStro2  -- 연결선 반복해서 그리기(꺾인 화살표 연결
    | InsertCpNo  -- 상용구 코드 넣기(현재 쪽 번호)
    | InsertCpTpNo  -- 상용구 코드 넣기(현재 쪽/전체 쪽)
    | InsertCrossReference  -- 상호 참조 만들기(삽입하기)
    | InsertDateCode  -- 상용구 코드 넣기(만든 날짜)
    | InsertDocInfo
    | InsertDocTitle  -- 상용구 코드 넣기(문서 제목)
    | InsertDocumentProperty  -- 상호 참조 넣기
    | InsertEndnote  -- 미주 입력
    | InsertFieldCitation
    | InsertFieldCtrl
    | InsertFieldDateTime
    | InsertFieldFileName
    | InsertFieldMemo  -- 메모 넣기([입력-메모-메모 넣기]메뉴와 동일)
    | InsertFieldRevisionChagne
    | InsertFieldTemplate  -- 문서마당 정보
    | InsertFile  -- 끼워 넣기
    | InsertFileName  -- 상용구 코드 넣기(파일 이름만)
    | InsertFilePath  -- 상용구 코드 넣기(파일 이름과 경로)
    | InsertFixedWidthSpace  -- 고정폭 빈칸 삽입
    | InsertFootnote  -- 각주 입력
    | InsertHyperlink  -- 하이퍼링크 만들기
    | InsertIdiom  -- 상용구 등록
    | InsertLastPrintDate  -- 상용구 코드 넣기(마지막 인쇄한 날짜)
    | InsertLastSaveBy  -- 상용구 코드 넣기(마지막 저장한 사람)
    | InsertLastSaveDate  -- 상용구 코드 넣기(마지막 저장한 날짜)
    | InsertLine  -- 선 넣기
    | InsertLinkImageToDoc  -- 연결 그림을 문서에 삽입
    | InsertMovie  -- 동영상 파일 삽입
    | InsertNonBreakingSpace  -- 묶음 빈칸 삽입
    | InsertPageNum  -- 쪽 번호 넣기
    | InsertRevision
    | InsertRevisionAttach  -- 교정 부호 넣기 : 붙임표
    | InsertRevisionClipping  -- 교정 부호 넣기 : 뺌표
    | InsertRevisionDelete  -- 교정 부호 넣기 : 지움표
    | InsertRevisionHyperlink  -- 교정 부호 넣기 : 자료연결
    | InsertRevisionInsert  -- 교정 부호 넣기 : 넣음표
    | InsertRevisionLeftMove  -- 교정 부호 넣기 : 왼자리 옮김표
    | InsertRevisionLine  -- 교정 부호 넣기 : 줄표
    | InsertRevisionLineAttach  -- 교정 부호 넣기 : 줄 붙임표
    | InsertRevisionLineInsert  -- 교정 부호 넣기 : 줄 비움표
    | InsertRevisionLineLink  -- 교정 부호 넣기 : 줄 이음표
    | InsertRevisionLineSeparate  -- 교정 부호 넣기 : 줄 바꿈표
    | InsertRevisionLineTransfer  -- 교정 부호 넣기 : 줄 서로 바꿈표
    | InsertRevisionPraise  -- 교정 부호 넣기 : 칭찬표
    | InsertRevisionRightMove  -- 교정 부호 넣기 : 오른자리 옮김표
    | InsertRevisionSawTooth  -- 교정 부호 넣기 : 톱니표
    | InsertRevisionSimpleChange  -- 교정 부호 넣기 : 고침표
    | InsertRevisionSpace  -- 교정 부호 넣기 : 띄움표
    | InsertRevisionSymbol  -- 교정 부호 넣기 : 부호 넣음표
    | InsertRevisionThinking  -- 교정 부호 넣기 : 생각표
    | InsertRevisionTransfer  -- 교정 부호 넣기 : 자리 바꿈표
    | InsertSoftHyphen  -- 하이픈 삽입
    | InsertSpace  -- 공백 삽입
    | InsertStringDateTime
    | InsertTab  -- 탭 삽입
    | InsertText  -- 텍스트 삽입
    | InsertTpNo  -- 상용구 코드 넣기(전체 쪽수)
    | InsertUserName  -- 상용구 코드 넣기(만든 사람)
    | InsertVoice  -- 음성 삽입

-- 액션 ID 문자열로 변환
public export
toString : TextAction -> String
toString BreakColDef = "BreakColDef"
toString BreakColumn = "BreakColumn"
toString BreakLine = "BreakLine"
toString BreakPage = "BreakPage"
toString BreakPara = "BreakPara"
toString BreakSection = "BreakSection"
toString Delete = "Delete"
toString DeleteBack = "DeleteBack"
toString DeleteCtrls = "DeleteCtrls"
toString DeleteDocumentMasterPage = "DeleteDocumentMasterPage"
toString DeleteDutmal = "DeleteDutmal"
toString DeleteField = "DeleteField"
toString DeleteFieldMemo = "DeleteFieldMemo"
toString DeleteLine = "DeleteLine"
toString DeleteLineEnd = "DeleteLineEnd"
toString DeletePage = "DeletePage"
toString DeletePrivateInfoMark = "DeletePrivateInfoMark"
toString DeleteSectionMasterPage = "DeleteSectionMasterPage"
toString DeleteWord = "DeleteWord"
toString DeleteWordBack = "DeleteWordBack"
toString Insert = "Insert"
toString InsertAutoNum = "InsertAutoNum"
toString InsertCCLMark = "InsertCCLMark"
toString InsertChart = "InsertChart"
toString InsertConnectLineArcBoth = "InsertConnectLineArcBoth"
toString InsertConnectLineArcOneWay = "InsertConnectLineArcOneWay"
toString InsertConnectLineMultiArcB = "InsertConnectLineMultiArcB"
toString InsertConnectLineMultiArcN = "InsertConnectLineMultiArcN"
toString InsertConnectLineMultiArcO = "InsertConnectLineMultiArcO"
toString InsertConnectLineMultiStra = "InsertConnectLineMultiStra"
toString InsertConnectLineMultiStra2 = "InsertConnectLineMultiStra"
toString InsertConnectLineMultiStro = "InsertConnectLineMultiStro"
toString InsertConnectLineMultiStro2 = "InsertConnectLineMultiStro"
toString InsertCpNo = "InsertCpNo"
toString InsertCpTpNo = "InsertCpTpNo"
toString InsertCrossReference = "InsertCrossReference"
toString InsertDateCode = "InsertDateCode"
toString InsertDocInfo = "InsertDocInfo"
toString InsertDocTitle = "InsertDocTitle"
toString InsertDocumentProperty = "InsertDocumentProperty"
toString InsertEndnote = "InsertEndnote"
toString InsertFieldCitation = "InsertFieldCitation"
toString InsertFieldCtrl = "InsertFieldCtrl"
toString InsertFieldDateTime = "InsertFieldDateTime"
toString InsertFieldFileName = "InsertFieldFileName"
toString InsertFieldMemo = "InsertFieldMemo"
toString InsertFieldRevisionChagne = "InsertFieldRevisionChagne"
toString InsertFieldTemplate = "InsertFieldTemplate"
toString InsertFile = "InsertFile"
toString InsertFileName = "InsertFileName"
toString InsertFilePath = "InsertFilePath"
toString InsertFixedWidthSpace = "InsertFixedWidthSpace"
toString InsertFootnote = "InsertFootnote"
toString InsertHyperlink = "InsertHyperlink"
toString InsertIdiom = "InsertIdiom"
toString InsertLastPrintDate = "InsertLastPrintDate"
toString InsertLastSaveBy = "InsertLastSaveBy"
toString InsertLastSaveDate = "InsertLastSaveDate"
toString InsertLine = "InsertLine"
toString InsertLinkImageToDoc = "InsertLinkImageToDoc"
toString InsertMovie = "InsertMovie"
toString InsertNonBreakingSpace = "InsertNonBreakingSpace"
toString InsertPageNum = "InsertPageNum"
toString InsertRevision = "InsertRevision"
toString InsertRevisionAttach = "InsertRevisionAttach"
toString InsertRevisionClipping = "InsertRevisionClipping"
toString InsertRevisionDelete = "InsertRevisionDelete"
toString InsertRevisionHyperlink = "InsertRevisionHyperlink"
toString InsertRevisionInsert = "InsertRevisionInsert"
toString InsertRevisionLeftMove = "InsertRevisionLeftMove"
toString InsertRevisionLine = "InsertRevisionLine"
toString InsertRevisionLineAttach = "InsertRevisionLineAttach"
toString InsertRevisionLineInsert = "InsertRevisionLineInsert"
toString InsertRevisionLineLink = "InsertRevisionLineLink"
toString InsertRevisionLineSeparate = "InsertRevisionLineSeparate"
toString InsertRevisionLineTransfer = "InsertRevisionLineTransfer"
toString InsertRevisionPraise = "InsertRevisionPraise"
toString InsertRevisionRightMove = "InsertRevisionRightMove"
toString InsertRevisionSawTooth = "InsertRevisionSawTooth"
toString InsertRevisionSimpleChange = "InsertRevisionSimpleChange"
toString InsertRevisionSpace = "InsertRevisionSpace"
toString InsertRevisionSymbol = "InsertRevisionSymbol"
toString InsertRevisionThinking = "InsertRevisionThinking"
toString InsertRevisionTransfer = "InsertRevisionTransfer"
toString InsertSoftHyphen = "InsertSoftHyphen"
toString InsertSpace = "InsertSpace"
toString InsertStringDateTime = "InsertStringDateTime"
toString InsertTab = "InsertTab"
toString InsertText = "InsertText"
toString InsertTpNo = "InsertTpNo"
toString InsertUserName = "InsertUserName"
toString InsertVoice = "InsertVoice"

-- ParameterSet ID
public export
paramSetID : TextAction -> Maybe String
paramSetID BreakColDef = Nothing
paramSetID BreakColumn = Nothing
paramSetID BreakLine = Nothing
paramSetID BreakPage = Nothing
paramSetID BreakPara = Nothing
paramSetID BreakSection = Nothing
paramSetID Delete = Nothing
paramSetID DeleteBack = Nothing
paramSetID DeleteCtrls = Just "DeleteCtrls"
paramSetID DeleteDocumentMasterPage = Nothing
paramSetID DeleteDutmal = Just "+"  -- Internal
paramSetID DeleteField = Nothing
paramSetID DeleteFieldMemo = Nothing
paramSetID DeleteLine = Nothing
paramSetID DeleteLineEnd = Nothing
paramSetID DeletePage = Just "DeletePage"
paramSetID DeletePrivateInfoMark = Nothing
paramSetID DeleteSectionMasterPage = Nothing
paramSetID DeleteWord = Nothing
paramSetID DeleteWordBack = Nothing
paramSetID Insert = Just "또는"
paramSetID InsertAutoNum = Nothing
paramSetID InsertCCLMark = Just "HyperLink"
paramSetID InsertChart = Just "OleCreation"
paramSetID InsertConnectLineArcBoth = Just "ShapeObject"
paramSetID InsertConnectLineArcOneWay = Just "ShapeObject"
paramSetID InsertConnectLineMultiArcB = Just "개체"
paramSetID InsertConnectLineMultiArcN = Just "개체"
paramSetID InsertConnectLineMultiArcO = Just "개체"
paramSetID InsertConnectLineMultiStra = Just "개체"
paramSetID InsertConnectLineMultiStra2 = Just "개체"
paramSetID InsertConnectLineMultiStro = Just "개체"
paramSetID InsertConnectLineMultiStro2 = Just "개체"
paramSetID InsertCpNo = Nothing
paramSetID InsertCpTpNo = Nothing
paramSetID InsertCrossReference = Just "ActionCrossRef"
paramSetID InsertDateCode = Nothing
paramSetID InsertDocInfo = Nothing
paramSetID InsertDocTitle = Just "InsertFieldTemplate"
paramSetID InsertDocumentProperty = Just "InsertFieldTemplate"
paramSetID InsertEndnote = Nothing
paramSetID InsertFieldCitation = Just "인용"
paramSetID InsertFieldCtrl = Just "FieldCtrl"
paramSetID InsertFieldDateTime = Nothing
paramSetID InsertFieldFileName = Just "InsertFieldTemplate"
paramSetID InsertFieldMemo = Nothing
paramSetID InsertFieldRevisionChagne = Nothing
paramSetID InsertFieldTemplate = Just "InsertFieldTemplate"
paramSetID InsertFile = Just "InsertFile"
paramSetID InsertFileName = Just "InsertFieldTemplate"
paramSetID InsertFilePath = Just "InsertFieldTemplate"
paramSetID InsertFixedWidthSpace = Nothing
paramSetID InsertFootnote = Nothing
paramSetID InsertHyperlink = Just "HyperlinkJump"
paramSetID InsertIdiom = Just "Idiom"
paramSetID InsertLastPrintDate = Nothing
paramSetID InsertLastSaveBy = Nothing
paramSetID InsertLastSaveDate = Nothing
paramSetID InsertLine = Nothing
paramSetID InsertLinkImageToDoc = Just "SummaryInfo"
paramSetID InsertMovie = Just "ShapeObject"
paramSetID InsertNonBreakingSpace = Nothing
paramSetID InsertPageNum = Nothing
paramSetID InsertRevision = Just "RevisionDef"
paramSetID InsertRevisionAttach = Just "RevisionDef"
paramSetID InsertRevisionClipping = Just "RevisionDef"
paramSetID InsertRevisionDelete = Just "RevisionDef"
paramSetID InsertRevisionHyperlink = Just "HyperLink"
paramSetID InsertRevisionInsert = Just "RevisionDef"
paramSetID InsertRevisionLeftMove = Just "RevisionDef"
paramSetID InsertRevisionLine = Just "RevisionDef"
paramSetID InsertRevisionLineAttach = Just "RevisionDef"
paramSetID InsertRevisionLineInsert = Just "RevisionDef"
paramSetID InsertRevisionLineLink = Just "RevisionDef"
paramSetID InsertRevisionLineSeparate = Just "RevisionDef"
paramSetID InsertRevisionLineTransfer = Just "RevisionDef"
paramSetID InsertRevisionPraise = Just "RevisionDef"
paramSetID InsertRevisionRightMove = Just "RevisionDef"
paramSetID InsertRevisionSawTooth = Just "RevisionDef"
paramSetID InsertRevisionSimpleChange = Just "RevisionDef"
paramSetID InsertRevisionSpace = Just "RevisionDef"
paramSetID InsertRevisionSymbol = Just "RevisionDef"
paramSetID InsertRevisionThinking = Just "RevisionDef"
paramSetID InsertRevisionTransfer = Just "RevisionDef"
paramSetID InsertSoftHyphen = Nothing
paramSetID InsertSpace = Nothing
paramSetID InsertStringDateTime = Nothing
paramSetID InsertTab = Nothing
paramSetID InsertText = Just "InsertText"
paramSetID InsertTpNo = Nothing
paramSetID InsertUserName = Just "InsertFieldTemplate"
paramSetID InsertVoice = Just "OleCreation"

-- 설명
public export
description : TextAction -> String
description BreakColDef = "단 정의 삽입"
description BreakColumn = "단 나누기"
description BreakLine = "line break"
description BreakPage = "쪽 나누기"
description BreakPara = "문단 나누기"
description BreakSection = "구역 나누기"
description Delete = "Delete"
description DeleteBack = "Backspace"
description DeleteCtrls = "조판 부호 지우기"
description DeleteDocumentMasterPage = "문서 전체 바탕쪽 삭제"
description DeleteDutmal = "덧말 지우기"
description DeleteField = "누름틀/메모 안의 내용은 지우지 않고, 단순히 누"
description DeleteFieldMemo = "메모 지우기"
description DeleteLine = "CTRL-Y (한줄 지우기)"
description DeleteLineEnd = "ALT-Y (현재 커서에서 줄 끝까지 지우기)"
description DeletePage = "쪽 지우기"
description DeletePrivateInfoMark = "개인 정보 감추기한 정보 다시보기"
description DeleteSectionMasterPage = "구역 바탕쪽 삭제"
description DeleteWord = "단어 지우기 CTRL-T"
description DeleteWordBack = "CTRL-BS(Back Space)"
description Insert = "Modify 하이퍼링크 액션"
description InsertAutoNum = "번호 다시 넣기"
description InsertCCLMark = "CCL 넣기"
description InsertChart = "차트 만들기"
description InsertConnectLineArcBoth = "개체 연결선(구부러진 양쪽 화살표 연결선)"
description InsertConnectLineArcOneWay = "개체 연결선(구부러진 화살표 연결선)"
description InsertConnectLineMultiArcB = "연결선 반복해서 그리기(구부러진 양쪽 화살"
description InsertConnectLineMultiArcN = "연결선 반복해서 그리기(구부러진 양쪽 화살"
description InsertConnectLineMultiArcO = "연결선 반복해서 그리기(구부러진 양쪽 화살"
description InsertConnectLineMultiStra = "연결선 반복해서 그리기(직선 양쪽 화살표 연"
description InsertConnectLineMultiStra2 = "연결선 반복해서 그리기(직선 화살표 연결"
description InsertConnectLineMultiStro = "연결선 반복해서 그리기(꺾인 양쪽 화살표 연"
description InsertConnectLineMultiStro2 = "연결선 반복해서 그리기(꺾인 화살표 연결"
description InsertCpNo = "상용구 코드 넣기(현재 쪽 번호)"
description InsertCpTpNo = "상용구 코드 넣기(현재 쪽/전체 쪽)"
description InsertCrossReference = "상호 참조 만들기(삽입하기)"
description InsertDateCode = "상용구 코드 넣기(만든 날짜)"
description InsertDocInfo = "No description"
description InsertDocTitle = "상용구 코드 넣기(문서 제목)"
description InsertDocumentProperty = "상호 참조 넣기"
description InsertEndnote = "미주 입력"
description InsertFieldCitation = "No description"
description InsertFieldCtrl = "No description"
description InsertFieldDateTime = "No description"
description InsertFieldFileName = "No description"
description InsertFieldMemo = "메모 넣기([입력-메모-메모 넣기]메뉴와 동일)"
description InsertFieldRevisionChagne = "No description"
description InsertFieldTemplate = "문서마당 정보"
description InsertFile = "끼워 넣기"
description InsertFileName = "상용구 코드 넣기(파일 이름만)"
description InsertFilePath = "상용구 코드 넣기(파일 이름과 경로)"
description InsertFixedWidthSpace = "고정폭 빈칸 삽입"
description InsertFootnote = "각주 입력"
description InsertHyperlink = "하이퍼링크 만들기"
description InsertIdiom = "상용구 등록"
description InsertLastPrintDate = "상용구 코드 넣기(마지막 인쇄한 날짜)"
description InsertLastSaveBy = "상용구 코드 넣기(마지막 저장한 사람)"
description InsertLastSaveDate = "상용구 코드 넣기(마지막 저장한 날짜)"
description InsertLine = "선 넣기"
description InsertLinkImageToDoc = "연결 그림을 문서에 삽입"
description InsertMovie = "동영상 파일 삽입"
description InsertNonBreakingSpace = "묶음 빈칸 삽입"
description InsertPageNum = "쪽 번호 넣기"
description InsertRevision = "No description"
description InsertRevisionAttach = "교정 부호 넣기 : 붙임표"
description InsertRevisionClipping = "교정 부호 넣기 : 뺌표"
description InsertRevisionDelete = "교정 부호 넣기 : 지움표"
description InsertRevisionHyperlink = "교정 부호 넣기 : 자료연결"
description InsertRevisionInsert = "교정 부호 넣기 : 넣음표"
description InsertRevisionLeftMove = "교정 부호 넣기 : 왼자리 옮김표"
description InsertRevisionLine = "교정 부호 넣기 : 줄표"
description InsertRevisionLineAttach = "교정 부호 넣기 : 줄 붙임표"
description InsertRevisionLineInsert = "교정 부호 넣기 : 줄 비움표"
description InsertRevisionLineLink = "교정 부호 넣기 : 줄 이음표"
description InsertRevisionLineSeparate = "교정 부호 넣기 : 줄 바꿈표"
description InsertRevisionLineTransfer = "교정 부호 넣기 : 줄 서로 바꿈표"
description InsertRevisionPraise = "교정 부호 넣기 : 칭찬표"
description InsertRevisionRightMove = "교정 부호 넣기 : 오른자리 옮김표"
description InsertRevisionSawTooth = "교정 부호 넣기 : 톱니표"
description InsertRevisionSimpleChange = "교정 부호 넣기 : 고침표"
description InsertRevisionSpace = "교정 부호 넣기 : 띄움표"
description InsertRevisionSymbol = "교정 부호 넣기 : 부호 넣음표"
description InsertRevisionThinking = "교정 부호 넣기 : 생각표"
description InsertRevisionTransfer = "교정 부호 넣기 : 자리 바꿈표"
description InsertSoftHyphen = "하이픈 삽입"
description InsertSpace = "공백 삽입"
description InsertStringDateTime = "No description"
description InsertTab = "탭 삽입"
description InsertText = "텍스트 삽입"
description InsertTpNo = "상용구 코드 넣기(전체 쪽수)"
description InsertUserName = "상용구 코드 넣기(만든 사람)"
description InsertVoice = "음성 삽입"

-- 총 92개 Text 액션
