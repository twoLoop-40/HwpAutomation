-- HWP Action Table - Table
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Table

import Data.String

-- Table 액션 타입
public export
data TableAction
    = CellBorder  -- 셀 테두리
    | CellBorderFill  -- 셀 테두리
    | CellFill  -- 셀 배경
    | CellZoneBorder
    | CellZoneBorderFill
    | CellZoneFill
    | TableAppendRow  -- 줄 추가
    | TableDrawPen  -- 그리기 선 모양
    | TableAutoFill  -- 자동 채우기
    | TableAutoFillDlg  -- 자동 채우기
    | TableBreak  -- 표 쪽 경계에서(나누지 않음)
    | TableBreakCell  -- 표 쪽 경계에서(나눔)
    | TableBreakNone  -- 표 쪽 경계에서(셀 단위로 나눔)
    | TableCaptionPosBottom  -- 테이블 캡션 위치-아래
    | TableCaptionPosLeftBottom  -- 테이블 캡션 위치–윈쪽 아래
    | TableCaptionPosLeftCenter  -- 테이블 캡션 위치–왼쪽 가운데
    | TableCaptionPosLeftTop  -- 테이블 캡션 위치–왼쪽 위
    | TableCaptionPosRightBottom  -- 테이블 캡션 위치–오른쪽 아래
    | TableCaptionPosRightCenter  -- 테이블 캡션 위치–오른쪽 가운데
    | TableCaptionPosRightTop  -- 테이블 캡션 위치–오른쪽 위
    | TableCaptionPosTop  -- 테이블 캡션 위치-위
    | TableCellAlignCenterBottom
    | TableCellAlignCenterCenter
    | TableCellAlignCenterTop
    | TableCellAlignLeftBottom
    | TableCellAlignLeftCenter
    | TableCellAlignLeftTop
    | TableCellAlignRightBottom
    | TableCellAlignRightCenter
    | TableCellAlignRightTop
    | TableCellBlock  -- 셀 블록
    | TableCellBlockCol  -- 셀 블록 (칸)
    | TableCellBlockExtend  -- 셀 블록 연장(F5 + F5)
    | TableCellBlockExtendAbs  -- 셀 블록 연장(SHIFT + F5)
    | TableCellBlockRow  -- 셀 블록(줄)
    | TableCellBorderAll
    | TableCellBorderBottom
    | TableCellBorderDiagonalDow  -- 셀 테두리 toggle(있음/없음). 셀
    | TableCellBorderDiagonalUp
    | TableCellBorderInside
    | TableCellBorderInsideHorz
    | TableCellBorderInsideVert
    | TableCellBorderLeft
    | TableCellBorderNo
    | TableCellBorderOutside
    | TableCellBorderRight
    | TableCellBorderTop
    | TableCellShadeDec  -- 셀 배경의 음영을 낮춘다.(결과적으로 밝아진다)
    | TableCellShadeInc
    | TableCellTextHorz  -- 셀 문자 방향–가로 쓰기
    | TableCellTextVert  -- 셀 음영 없음
    | TableCellTextVertAll  -- 셀 문자 방향–세로 쓰기–영문 세움
    | TableCellToggleDirection  -- 표 문자 방향- toggle
    | TableColBegin  -- 셀 이동: 열 시작
    | TableColEnd  -- 셀 이동: 열 끝
    | TableColPageDown  -- 셀 이동: 페이지다운
    | TableColPageUp  -- 셀 이동: 페이지 업
    | TableCreate  -- 표 만들기
    | TableDeleteCell  -- 셀 삭제
    | TableDeleteColumn  -- 칸 지우기
    | TableDeleteComma  -- 세자리마다 자리점 빼기
    | TableDeleteRow  -- 줄-칸 지우기
    | TableDeleteRowColumn  -- 줄-칸 지우기
    | TableDistributeCellHeight  -- 셀 높이를 같게
    | TableDistributeCellWidth  -- 셀 너비를 같게
    | TableDrawPen2  -- 표 그리기
    | TableEraser  -- 표 지우개
    | TableFormula  -- 계산식
    | TableFormulaAvgAuto  -- 블록 평균
    | TableFormulaAvgHor  -- 가로 평균
    | TableFormulaAvgVer  -- 세로 평균
    | TableFormulaProAuto  -- 블록 곱
    | TableFormulaProHor  -- 가로 곱
    | TableFormulaProVer  -- 세로 곱
    | TableFormulaSumAuto  -- 블록 합계
    | TableFormulaSumHor  -- 가로 합계
    | TableFormulaSumVer  -- 세로 합계
    | TableInsertComma  -- 세자리마다 자리점 넣기
    | TableInsertLeftColumn  -- 왼쪽 칸 삽입
    | TableInsertLowerRow  -- 아래쪽 줄 삽입
    | TableInsertRightColumn  -- 오른쪽 칸 삽입
    | TableInsertRowColumn  -- 줄-칸 삽입
    | TableInsertUpperRow  -- 위쪽 줄 삽입
    | TableLeftCell  -- 셀 이동: 셀 왼쪽
    | TableLowerCell  -- 셀 이동: 셀 아래
    | TableMergeCell  -- 셀 합치기
    | TableMergeTable  -- 표 붙이기
    | TablePropertyDialog  -- 표 고치기
    | TableResizeCellDown  -- 셀 크기 변경: 셀 아래
    | TableResizeCellLeft  -- 셀 크기 변경: 셀 왼쪽
    | TableResizeCellRight  -- 셀 크기 변경: 셀 오른쪽
    | TableResizeCellUp  -- 셀 크기 변경: 셀 위
    | TableResizeDown  -- 셀 크기 변경
    | TableResizeExDown  -- TebleResizeDown과 다른 점은 셀 블록 상태가
    | TableResizeExLeft  -- TebleResizeLeft와 다른 점은 셀 블록 상태가
    | TableResizeExRight  -- TebleResizeRight와 다른 점은 셀 블록 상태가
    | TableResizeExUp  -- TebleResizeUp과 다른 점은 셀 블록 상태가 아
    | TableResizeLeft  -- 셀 크기 변경
    | TableResizeLineDown  -- 셀 크기 변경: 선아래
    | TableResizeLineLeft  -- 셀 크기 변경: 선 왼쪽
    | TableResizeLineRight  -- 셀 크기 변경: 선 오른쪽
    | TableResizeLineUp  -- 셀 크기 변경: 선 위
    | TableResizeRight  -- 셀 크기 변경
    | TableResizeUp  -- 셀 크기 변경
    | TableRightCell  -- 셀 이동: 셀 오른쪽
    | TableRightCellAppend  -- 셀 이동: 셀 오른쪽에 이어서
    | TableSplitCell  -- 셀 나누기
    | TableSplitCellCol2  -- 셀 칸 나누기
    | TableSplitCellRow2  -- 셀 줄 나누기
    | TableSplitTable  -- 표 나누기
    | TableStringToTable  -- 문자열을 표로
    | TableSubtractRow  -- 표 줄 삭제
    | TableSwap  -- 표 뒤집기
    | TableTableToString  -- 표를 문자열로
    | TableTemplate  -- 표 마당
    | TableTreatAsChar  -- 표 글자처럼 취급
    | TableUpperCell  -- 셀 이동: 셀 위
    | TableVAlignBottom  -- 셀 세로정렬 아래
    | TableVAlignCenter  -- 셀 세로정렬 가운데
    | TableVAlignTop  -- 셀 세로정렬 위
    | TableAutoFillDlg2

-- 액션 ID 문자열로 변환
public export
toString : TableAction -> String
toString CellBorder = "CellBorder"
toString CellBorderFill = "CellBorderFill"
toString CellFill = "CellFill"
toString CellZoneBorder = "CellZoneBorder"
toString CellZoneBorderFill = "CellZoneBorderFill"
toString CellZoneFill = "CellZoneFill"
toString TableAppendRow = "TableAppendRow"
toString TableDrawPen = "TableDrawPen"
toString TableAutoFill = "TableAutoFill"
toString TableAutoFillDlg = "TableAutoFillDlg"
toString TableBreak = "TableBreak"
toString TableBreakCell = "TableBreakCell"
toString TableBreakNone = "TableBreakNone"
toString TableCaptionPosBottom = "TableCaptionPosBottom"
toString TableCaptionPosLeftBottom = "TableCaptionPosLeftBottom"
toString TableCaptionPosLeftCenter = "TableCaptionPosLeftCenter"
toString TableCaptionPosLeftTop = "TableCaptionPosLeftTop"
toString TableCaptionPosRightBottom = "TableCaptionPosRightBottom"
toString TableCaptionPosRightCenter = "TableCaptionPosRightCenter"
toString TableCaptionPosRightTop = "TableCaptionPosRightTop"
toString TableCaptionPosTop = "TableCaptionPosTop"
toString TableCellAlignCenterBottom = "TableCellAlignCenterBottom"
toString TableCellAlignCenterCenter = "TableCellAlignCenterCenter"
toString TableCellAlignCenterTop = "TableCellAlignCenterTop"
toString TableCellAlignLeftBottom = "TableCellAlignLeftBottom"
toString TableCellAlignLeftCenter = "TableCellAlignLeftCenter"
toString TableCellAlignLeftTop = "TableCellAlignLeftTop"
toString TableCellAlignRightBottom = "TableCellAlignRightBottom"
toString TableCellAlignRightCenter = "TableCellAlignRightCenter"
toString TableCellAlignRightTop = "TableCellAlignRightTop"
toString TableCellBlock = "TableCellBlock"
toString TableCellBlockCol = "TableCellBlockCol"
toString TableCellBlockExtend = "TableCellBlockExtend"
toString TableCellBlockExtendAbs = "TableCellBlockExtendAbs"
toString TableCellBlockRow = "TableCellBlockRow"
toString TableCellBorderAll = "TableCellBorderAll"
toString TableCellBorderBottom = "TableCellBorderBottom"
toString TableCellBorderDiagonalDow = "TableCellBorderDiagonalDow"
toString TableCellBorderDiagonalUp = "TableCellBorderDiagonalUp"
toString TableCellBorderInside = "TableCellBorderInside"
toString TableCellBorderInsideHorz = "TableCellBorderInsideHorz"
toString TableCellBorderInsideVert = "TableCellBorderInsideVert"
toString TableCellBorderLeft = "TableCellBorderLeft"
toString TableCellBorderNo = "TableCellBorderNo"
toString TableCellBorderOutside = "TableCellBorderOutside"
toString TableCellBorderRight = "TableCellBorderRight"
toString TableCellBorderTop = "TableCellBorderTop"
toString TableCellShadeDec = "TableCellShadeDec"
toString TableCellShadeInc = "TableCellShadeInc"
toString TableCellTextHorz = "TableCellTextHorz"
toString TableCellTextVert = "TableCellTextVert"
toString TableCellTextVertAll = "TableCellTextVertAll"
toString TableCellToggleDirection = "TableCellToggleDirection"
toString TableColBegin = "TableColBegin"
toString TableColEnd = "TableColEnd"
toString TableColPageDown = "TableColPageDown"
toString TableColPageUp = "TableColPageUp"
toString TableCreate = "TableCreate"
toString TableDeleteCell = "TableDeleteCell"
toString TableDeleteColumn = "TableDeleteColumn"
toString TableDeleteComma = "TableDeleteComma"
toString TableDeleteRow = "TableDeleteRow"
toString TableDeleteRowColumn = "TableDeleteRowColumn"
toString TableDistributeCellHeight = "TableDistributeCellHeight"
toString TableDistributeCellWidth = "TableDistributeCellWidth"
toString TableDrawPen2 = "TableDrawPen"
toString TableEraser = "TableEraser"
toString TableFormula = "TableFormula"
toString TableFormulaAvgAuto = "TableFormulaAvgAuto"
toString TableFormulaAvgHor = "TableFormulaAvgHor"
toString TableFormulaAvgVer = "TableFormulaAvgVer"
toString TableFormulaProAuto = "TableFormulaProAuto"
toString TableFormulaProHor = "TableFormulaProHor"
toString TableFormulaProVer = "TableFormulaProVer"
toString TableFormulaSumAuto = "TableFormulaSumAuto"
toString TableFormulaSumHor = "TableFormulaSumHor"
toString TableFormulaSumVer = "TableFormulaSumVer"
toString TableInsertComma = "TableInsertComma"
toString TableInsertLeftColumn = "TableInsertLeftColumn"
toString TableInsertLowerRow = "TableInsertLowerRow"
toString TableInsertRightColumn = "TableInsertRightColumn"
toString TableInsertRowColumn = "TableInsertRowColumn"
toString TableInsertUpperRow = "TableInsertUpperRow"
toString TableLeftCell = "TableLeftCell"
toString TableLowerCell = "TableLowerCell"
toString TableMergeCell = "TableMergeCell"
toString TableMergeTable = "TableMergeTable"
toString TablePropertyDialog = "TablePropertyDialog"
toString TableResizeCellDown = "TableResizeCellDown"
toString TableResizeCellLeft = "TableResizeCellLeft"
toString TableResizeCellRight = "TableResizeCellRight"
toString TableResizeCellUp = "TableResizeCellUp"
toString TableResizeDown = "TableResizeDown"
toString TableResizeExDown = "TableResizeExDown"
toString TableResizeExLeft = "TableResizeExLeft"
toString TableResizeExRight = "TableResizeExRight"
toString TableResizeExUp = "TableResizeExUp"
toString TableResizeLeft = "TableResizeLeft"
toString TableResizeLineDown = "TableResizeLineDown"
toString TableResizeLineLeft = "TableResizeLineLeft"
toString TableResizeLineRight = "TableResizeLineRight"
toString TableResizeLineUp = "TableResizeLineUp"
toString TableResizeRight = "TableResizeRight"
toString TableResizeUp = "TableResizeUp"
toString TableRightCell = "TableRightCell"
toString TableRightCellAppend = "TableRightCellAppend"
toString TableSplitCell = "TableSplitCell"
toString TableSplitCellCol2 = "TableSplitCellCol2"
toString TableSplitCellRow2 = "TableSplitCellRow2"
toString TableSplitTable = "TableSplitTable"
toString TableStringToTable = "TableStringToTable"
toString TableSubtractRow = "TableSubtractRow"
toString TableSwap = "TableSwap"
toString TableTableToString = "TableTableToString"
toString TableTemplate = "TableTemplate"
toString TableTreatAsChar = "TableTreatAsChar"
toString TableUpperCell = "TableUpperCell"
toString TableVAlignBottom = "TableVAlignBottom"
toString TableVAlignCenter = "TableVAlignCenter"
toString TableVAlignTop = "TableVAlignTop"
toString TableAutoFillDlg2 = "TableAutoFillDlg와"

-- ParameterSet ID
public export
paramSetID : TableAction -> Maybe String
paramSetID CellBorder = Just "CellBorderFill"
paramSetID CellBorderFill = Just "CellBorderFill"
paramSetID CellFill = Just "CellBorderFill"
paramSetID CellZoneBorder = Just "CellBorderFill"
paramSetID CellZoneBorderFill = Just "CellBorderFill"
paramSetID CellZoneFill = Just "CellBorderFill"
paramSetID TableAppendRow = Nothing
paramSetID TableDrawPen = Just "표"
paramSetID TableAutoFill = Just "AutoFill*"
paramSetID TableAutoFillDlg = Just "AutoFill*"
paramSetID TableBreak = Just "Table"
paramSetID TableBreakCell = Just "Table"
paramSetID TableBreakNone = Just "Table"
paramSetID TableCaptionPosBottom = Just "ShapeObject"
paramSetID TableCaptionPosLeftBottom = Just "ShapeObject"
paramSetID TableCaptionPosLeftCenter = Just "ShapeObject"
paramSetID TableCaptionPosLeftTop = Just "ShapeObject"
paramSetID TableCaptionPosRightBottom = Just "ShapeObject"
paramSetID TableCaptionPosRightCenter = Just "ShapeObject"
paramSetID TableCaptionPosRightTop = Just "ShpaeObject"
paramSetID TableCaptionPosTop = Just "ShapeObject"
paramSetID TableCellAlignCenterBottom = Nothing
paramSetID TableCellAlignCenterCenter = Nothing
paramSetID TableCellAlignCenterTop = Nothing
paramSetID TableCellAlignLeftBottom = Nothing
paramSetID TableCellAlignLeftCenter = Nothing
paramSetID TableCellAlignLeftTop = Nothing
paramSetID TableCellAlignRightBottom = Nothing
paramSetID TableCellAlignRightCenter = Nothing
paramSetID TableCellAlignRightTop = Nothing
paramSetID TableCellBlock = Nothing
paramSetID TableCellBlockCol = Nothing
paramSetID TableCellBlockExtend = Nothing
paramSetID TableCellBlockExtendAbs = Nothing
paramSetID TableCellBlockRow = Nothing
paramSetID TableCellBorderAll = Nothing
paramSetID TableCellBorderBottom = Nothing
paramSetID TableCellBorderDiagonalDow = Just "대각선(⍂)"
paramSetID TableCellBorderDiagonalUp = Nothing
paramSetID TableCellBorderInside = Nothing
paramSetID TableCellBorderInsideHorz = Nothing
paramSetID TableCellBorderInsideVert = Nothing
paramSetID TableCellBorderLeft = Nothing
paramSetID TableCellBorderNo = Nothing
paramSetID TableCellBorderOutside = Nothing
paramSetID TableCellBorderRight = Nothing
paramSetID TableCellBorderTop = Nothing
paramSetID TableCellShadeDec = Just "CellBorderFill"
paramSetID TableCellShadeInc = Just "CellBorderFill"
paramSetID TableCellTextHorz = Just "CellBorderFill"
paramSetID TableCellTextVert = Just "CellBorderFill"
paramSetID TableCellTextVertAll = Just "CellBorderFill"
paramSetID TableCellToggleDirection = Just "CellBorderFill"
paramSetID TableColBegin = Nothing
paramSetID TableColEnd = Nothing
paramSetID TableColPageDown = Nothing
paramSetID TableColPageUp = Nothing
paramSetID TableCreate = Just "TableCreation"
paramSetID TableDeleteCell = Nothing
paramSetID TableDeleteColumn = Just "TableDeleteLine"
paramSetID TableDeleteComma = Nothing
paramSetID TableDeleteRow = Just "TableDeleteLine"
paramSetID TableDeleteRowColumn = Just "TableDeleteLine"
paramSetID TableDistributeCellHeight = Nothing
paramSetID TableDistributeCellWidth = Nothing
paramSetID TableDrawPen2 = Nothing
paramSetID TableEraser = Nothing
paramSetID TableFormula = Just "FieldCtrl"
paramSetID TableFormulaAvgAuto = Nothing
paramSetID TableFormulaAvgHor = Nothing
paramSetID TableFormulaAvgVer = Nothing
paramSetID TableFormulaProAuto = Nothing
paramSetID TableFormulaProHor = Nothing
paramSetID TableFormulaProVer = Nothing
paramSetID TableFormulaSumAuto = Nothing
paramSetID TableFormulaSumHor = Nothing
paramSetID TableFormulaSumVer = Nothing
paramSetID TableInsertComma = Nothing
paramSetID TableInsertLeftColumn = Just "TableInsertLine"
paramSetID TableInsertLowerRow = Just "TableInsertLine"
paramSetID TableInsertRightColumn = Just "TableInsertLine"
paramSetID TableInsertRowColumn = Just "TableInsertLine"
paramSetID TableInsertUpperRow = Just "TableInsertLine"
paramSetID TableLeftCell = Nothing
paramSetID TableLowerCell = Nothing
paramSetID TableMergeCell = Nothing
paramSetID TableMergeTable = Nothing
paramSetID TablePropertyDialog = Just "ShapeObject"
paramSetID TableResizeCellDown = Nothing
paramSetID TableResizeCellLeft = Nothing
paramSetID TableResizeCellRight = Nothing
paramSetID TableResizeCellUp = Nothing
paramSetID TableResizeDown = Nothing
paramSetID TableResizeExDown = Nothing
paramSetID TableResizeExLeft = Nothing
paramSetID TableResizeExRight = Nothing
paramSetID TableResizeExUp = Nothing
paramSetID TableResizeLeft = Nothing
paramSetID TableResizeLineDown = Nothing
paramSetID TableResizeLineLeft = Nothing
paramSetID TableResizeLineRight = Nothing
paramSetID TableResizeLineUp = Nothing
paramSetID TableResizeRight = Nothing
paramSetID TableResizeUp = Nothing
paramSetID TableRightCell = Nothing
paramSetID TableRightCellAppend = Nothing
paramSetID TableSplitCell = Just "TableSplitCell"
paramSetID TableSplitCellCol2 = Just "TableSplitCell"
paramSetID TableSplitCellRow2 = Just "TableSplitCell"
paramSetID TableSplitTable = Nothing
paramSetID TableStringToTable = Just "TableStrToTbl"
paramSetID TableSubtractRow = Just "TableDeleteLine"
paramSetID TableSwap = Just "TableSwap"
paramSetID TableTableToString = Just "TableTblToStr"
paramSetID TableTemplate = Just "TableTemplate"
paramSetID TableTreatAsChar = Just "ShapeObject"
paramSetID TableUpperCell = Nothing
paramSetID TableVAlignBottom = Nothing
paramSetID TableVAlignCenter = Nothing
paramSetID TableVAlignTop = Nothing
paramSetID TableAutoFillDlg2 = Just "동일)"

-- 설명
public export
description : TableAction -> String
description CellBorder = "셀 테두리"
description CellBorderFill = "셀 테두리"
description CellFill = "셀 배경"
description CellZoneBorder = "No description"
description CellZoneBorderFill = "No description"
description CellZoneFill = "No description"
description TableAppendRow = "줄 추가"
description TableDrawPen = "그리기 선 모양"
description TableAutoFill = "자동 채우기"
description TableAutoFillDlg = "자동 채우기"
description TableBreak = "표 쪽 경계에서(나누지 않음)"
description TableBreakCell = "표 쪽 경계에서(나눔)"
description TableBreakNone = "표 쪽 경계에서(셀 단위로 나눔)"
description TableCaptionPosBottom = "테이블 캡션 위치-아래"
description TableCaptionPosLeftBottom = "테이블 캡션 위치–윈쪽 아래"
description TableCaptionPosLeftCenter = "테이블 캡션 위치–왼쪽 가운데"
description TableCaptionPosLeftTop = "테이블 캡션 위치–왼쪽 위"
description TableCaptionPosRightBottom = "테이블 캡션 위치–오른쪽 아래"
description TableCaptionPosRightCenter = "테이블 캡션 위치–오른쪽 가운데"
description TableCaptionPosRightTop = "테이블 캡션 위치–오른쪽 위"
description TableCaptionPosTop = "테이블 캡션 위치-위"
description TableCellAlignCenterBottom = "No description"
description TableCellAlignCenterCenter = "No description"
description TableCellAlignCenterTop = "No description"
description TableCellAlignLeftBottom = "No description"
description TableCellAlignLeftCenter = "No description"
description TableCellAlignLeftTop = "No description"
description TableCellAlignRightBottom = "No description"
description TableCellAlignRightCenter = "No description"
description TableCellAlignRightTop = "No description"
description TableCellBlock = "셀 블록"
description TableCellBlockCol = "셀 블록 (칸)"
description TableCellBlockExtend = "셀 블록 연장(F5 + F5)"
description TableCellBlockExtendAbs = "셀 블록 연장(SHIFT + F5)"
description TableCellBlockRow = "셀 블록(줄)"
description TableCellBorderAll = "No description"
description TableCellBorderBottom = "No description"
description TableCellBorderDiagonalDow = "셀 테두리 toggle(있음/없음). 셀"
description TableCellBorderDiagonalUp = "No description"
description TableCellBorderInside = "No description"
description TableCellBorderInsideHorz = "No description"
description TableCellBorderInsideVert = "No description"
description TableCellBorderLeft = "No description"
description TableCellBorderNo = "No description"
description TableCellBorderOutside = "No description"
description TableCellBorderRight = "No description"
description TableCellBorderTop = "No description"
description TableCellShadeDec = "셀 배경의 음영을 낮춘다.(결과적으로 밝아진다)"
description TableCellShadeInc = "No description"
description TableCellTextHorz = "셀 문자 방향–가로 쓰기"
description TableCellTextVert = "셀 음영 없음"
description TableCellTextVertAll = "셀 문자 방향–세로 쓰기–영문 세움"
description TableCellToggleDirection = "표 문자 방향- toggle"
description TableColBegin = "셀 이동: 열 시작"
description TableColEnd = "셀 이동: 열 끝"
description TableColPageDown = "셀 이동: 페이지다운"
description TableColPageUp = "셀 이동: 페이지 업"
description TableCreate = "표 만들기"
description TableDeleteCell = "셀 삭제"
description TableDeleteColumn = "칸 지우기"
description TableDeleteComma = "세자리마다 자리점 빼기"
description TableDeleteRow = "줄-칸 지우기"
description TableDeleteRowColumn = "줄-칸 지우기"
description TableDistributeCellHeight = "셀 높이를 같게"
description TableDistributeCellWidth = "셀 너비를 같게"
description TableDrawPen2 = "표 그리기"
description TableEraser = "표 지우개"
description TableFormula = "계산식"
description TableFormulaAvgAuto = "블록 평균"
description TableFormulaAvgHor = "가로 평균"
description TableFormulaAvgVer = "세로 평균"
description TableFormulaProAuto = "블록 곱"
description TableFormulaProHor = "가로 곱"
description TableFormulaProVer = "세로 곱"
description TableFormulaSumAuto = "블록 합계"
description TableFormulaSumHor = "가로 합계"
description TableFormulaSumVer = "세로 합계"
description TableInsertComma = "세자리마다 자리점 넣기"
description TableInsertLeftColumn = "왼쪽 칸 삽입"
description TableInsertLowerRow = "아래쪽 줄 삽입"
description TableInsertRightColumn = "오른쪽 칸 삽입"
description TableInsertRowColumn = "줄-칸 삽입"
description TableInsertUpperRow = "위쪽 줄 삽입"
description TableLeftCell = "셀 이동: 셀 왼쪽"
description TableLowerCell = "셀 이동: 셀 아래"
description TableMergeCell = "셀 합치기"
description TableMergeTable = "표 붙이기"
description TablePropertyDialog = "표 고치기"
description TableResizeCellDown = "셀 크기 변경: 셀 아래"
description TableResizeCellLeft = "셀 크기 변경: 셀 왼쪽"
description TableResizeCellRight = "셀 크기 변경: 셀 오른쪽"
description TableResizeCellUp = "셀 크기 변경: 셀 위"
description TableResizeDown = "셀 크기 변경"
description TableResizeExDown = "TebleResizeDown과 다른 점은 셀 블록 상태가"
description TableResizeExLeft = "TebleResizeLeft와 다른 점은 셀 블록 상태가"
description TableResizeExRight = "TebleResizeRight와 다른 점은 셀 블록 상태가"
description TableResizeExUp = "TebleResizeUp과 다른 점은 셀 블록 상태가 아"
description TableResizeLeft = "셀 크기 변경"
description TableResizeLineDown = "셀 크기 변경: 선아래"
description TableResizeLineLeft = "셀 크기 변경: 선 왼쪽"
description TableResizeLineRight = "셀 크기 변경: 선 오른쪽"
description TableResizeLineUp = "셀 크기 변경: 선 위"
description TableResizeRight = "셀 크기 변경"
description TableResizeUp = "셀 크기 변경"
description TableRightCell = "셀 이동: 셀 오른쪽"
description TableRightCellAppend = "셀 이동: 셀 오른쪽에 이어서"
description TableSplitCell = "셀 나누기"
description TableSplitCellCol2 = "셀 칸 나누기"
description TableSplitCellRow2 = "셀 줄 나누기"
description TableSplitTable = "표 나누기"
description TableStringToTable = "문자열을 표로"
description TableSubtractRow = "표 줄 삭제"
description TableSwap = "표 뒤집기"
description TableTableToString = "표를 문자열로"
description TableTemplate = "표 마당"
description TableTreatAsChar = "표 글자처럼 취급"
description TableUpperCell = "셀 이동: 셀 위"
description TableVAlignBottom = "셀 세로정렬 아래"
description TableVAlignCenter = "셀 세로정렬 가운데"
description TableVAlignTop = "셀 세로정렬 위"
description TableAutoFillDlg2 = "No description"

-- 총 121개 Table 액션
