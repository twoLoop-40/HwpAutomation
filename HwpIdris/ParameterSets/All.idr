-- ParameterSet 전체 목록
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.All

import Data.String

-- ParameterSet 타입
public export
data ParameterSetType
    = PS_ActionCrossRef
    | PS_AutoFill
    | PS_AutoNum
    | PS_BookMark
    | PS_BorderFill
    | PS_BorderFillExt
    | PS_BulletShape
    | PS_Caption
    | PS_CaptureEnd
    | PS_Cell
    | PS_CellBorderFill
    | PS_ChangeRome
    | PS_CharShape
    | PS_ChCompose
    | PS_ChComposeShapes
    | PS_CodeTable
    | PS_ColDef
    | PS_ConvertCase
    | PS_ConvertFullHalf
    | PS_ConvertHiraToGata
    | PS_ConvertJianFan
    | PS_ConvertToHangul
    | PS_CtrlData
    | PS_DeleteCtrls
    | PS_DocFilters
    | PS_DocFindInfo
    | PS_DocumentInfo
    | PS_DrawArcType
    | PS_DrawCoordInfo
    | PS_DrawCtrlHyperlink
    | PS_DrawEditDetail
    | PS_DrawFillAttr
    | PS_DrawImageAttr
    | PS_DrawImageScissoring
    | PS_DrawLayOut
    | PS_DrawLineAttr
    | PS_DrawRectType
    | PS_DrawResize
    | PS_DrawRotate
    | PS_DrawScAction
    | PS_DrawShadow
    | PS_DrawShear
    | PS_DrawTextart
    | PS_DropCap
    | PS_Dutmal
    | PS_EngineProperties
    | PS_EqEdit
    | PS_ExchangeFootnoteEndNote
    | PS_FieldCtrl
    | PS_FileConvert
    | PS_Other  -- 외 91개

-- ParameterSet 이름
public export
toString : ParameterSetType -> String
toString PS_ActionCrossRef = "ActionCrossRef"
toString PS_AutoFill = "AutoFill"
toString PS_AutoNum = "AutoNum"
toString PS_BookMark = "BookMark"
toString PS_BorderFill = "BorderFill"
toString PS_BorderFillExt = "BorderFillExt"
toString PS_BulletShape = "BulletShape"
toString PS_Caption = "Caption"
toString PS_CaptureEnd = "CaptureEnd"
toString PS_Cell = "Cell"
toString PS_CellBorderFill = "CellBorderFill"
toString PS_ChangeRome = "ChangeRome"
toString PS_CharShape = "CharShape"
toString PS_ChCompose = "ChCompose"
toString PS_ChComposeShapes = "ChComposeShapes"
toString PS_CodeTable = "CodeTable"
toString PS_ColDef = "ColDef"
toString PS_ConvertCase = "ConvertCase"
toString PS_ConvertFullHalf = "ConvertFullHalf"
toString PS_ConvertHiraToGata = "ConvertHiraToGata"
toString PS_ConvertJianFan = "ConvertJianFan"
toString PS_ConvertToHangul = "ConvertToHangul"
toString PS_CtrlData = "CtrlData"
toString PS_DeleteCtrls = "DeleteCtrls"
toString PS_DocFilters = "DocFilters"
toString PS_DocFindInfo = "DocFindInfo"
toString PS_DocumentInfo = "DocumentInfo"
toString PS_DrawArcType = "DrawArcType"
toString PS_DrawCoordInfo = "DrawCoordInfo"
toString PS_DrawCtrlHyperlink = "DrawCtrlHyperlink"
toString PS_DrawEditDetail = "DrawEditDetail"
toString PS_DrawFillAttr = "DrawFillAttr"
toString PS_DrawImageAttr = "DrawImageAttr"
toString PS_DrawImageScissoring = "DrawImageScissoring"
toString PS_DrawLayOut = "DrawLayOut"
toString PS_DrawLineAttr = "DrawLineAttr"
toString PS_DrawRectType = "DrawRectType"
toString PS_DrawResize = "DrawResize"
toString PS_DrawRotate = "DrawRotate"
toString PS_DrawScAction = "DrawScAction"
toString PS_DrawShadow = "DrawShadow"
toString PS_DrawShear = "DrawShear"
toString PS_DrawTextart = "DrawTextart"
toString PS_DropCap = "DropCap"
toString PS_Dutmal = "Dutmal"
toString PS_EngineProperties = "EngineProperties"
toString PS_EqEdit = "EqEdit"
toString PS_ExchangeFootnoteEndNote = "ExchangeFootnoteEndNote"
toString PS_FieldCtrl = "FieldCtrl"
toString PS_FileConvert = "FileConvert"
toString PS_Other = "Other"

-- ParameterSet 설명
public export
description : ParameterSetType -> String
description PS_ActionCrossRef = "상호참조 삽입"
description PS_AutoFill = "자동 채우기"
description PS_AutoNum = "번호 넣기"
description PS_BookMark = "책갈피"
description PS_BorderFill = "테두리/배경의 일반 속성"
description PS_BorderFillExt = "UI 구현을 위한 BorderFill 확장"
description PS_BulletShape = "불릿 모양(글머리표 모양)"
description PS_Caption = "캡션 속성"
description PS_CaptureEnd = "갈무리 끝"
description PS_Cell = "셀"
description PS_CellBorderFill = "셀 테두리/배경"
description PS_ChangeRome = "로마자 변환"
description PS_CharShape = "글자 모양"
description PS_ChCompose = "글자 겹침"
description PS_ChComposeShapes = "글자 겹치기 글자 속성셋"
description PS_CodeTable = "문자표"
description PS_ColDef = "단 정의 속성"
description PS_ConvertCase = "대/소문자 변환"
description PS_ConvertFullHalf = "전/반각 변환"
description PS_ConvertHiraToGata = "히라가나/가타가나 변환"
description PS_ConvertJianFan = "간/번체 변환"
description PS_ConvertToHangul = "한자, 일어, 구결을 한글로"
description PS_CtrlData = "컨트롤 데이터"
description PS_DeleteCtrls = "조판 부호 컨트롤 지우기"
description PS_DocFilters = "Document 필터 리스트"
description PS_DocFindInfo = "문서 찾기"
description PS_DocumentInfo = "문서에 대한 정보"
description PS_DrawArcType = "그리기 개체의 부채꼴 테두리 모양"
description PS_DrawCoordInfo = "그리기 개체의 좌표 정보"
description PS_DrawCtrlHyperlink = "그리기 개체의 Hyperlink 정보"
description PS_DrawEditDetail = "그리기 개체의 다각형 편집"
description PS_DrawFillAttr = "그리기 개체의 채우기 속성"
description PS_DrawImageAttr = "그림 개체 속성"
description PS_DrawImageScissoring = "그림 개체의 자르기 정보"
description PS_DrawLayOut = "그리기 개체의 Layout"
description PS_DrawLineAttr = "그리기 개체의 선 속성"
description PS_DrawRectType = "사각형 모서리 모양"
description PS_DrawResize = "그리기 개체 Resizing 정보"
description PS_DrawRotate = "그리기 개체 회전 정보"
description PS_DrawScAction = "그리기 개체 90도 회전 및 좌우/상하 뒤집기"
description PS_DrawShadow = "그리기 개체 그림자 정보"
description PS_DrawShear = "그리기 개체 기울이기 정보"
description PS_DrawTextart = "글맵시 속성"
description PS_DropCap = "문단 첫 글자 장식"
description PS_Dutmal = "덧말"
description PS_EngineProperties = "환경 설정 옵션"
description PS_EqEdit = "수식"
description PS_ExchangeFootnoteEndNote = "각주/미주 변환"
description PS_FieldCtrl = "필드 컨트롤의 공통 데이터"
description PS_FileConvert = "여러 파일을 동시에 특정 포맷으로 변환하여 저장 (관련 Action/API 존재하지 않음)"
description PS_Other = "기타 ParameterSet"

-- 총 141개 ParameterSet
