-- HWP API 명세 (자동 생성)
-- Source: ActionTable_2504.pdf
-- Generated: HwpIdris/ActionTable.idr

module HwpIdris.ActionTable

import Data.String
import Data.List

-- MoveSel 명령 타입
public export
data MoveSelCommand
    = MoveSelLeft
    | MoveSelRight
    | MoveSelUp
    | MoveSelDown
    | MoveSelPageUp
    | MoveSelPageDown
    | MoveSelDocBegin
    | MoveSelDocEnd
    | MoveSelLineBegin
    | MoveSelLineEnd
    | MoveSelParaBegin
    | MoveSelParaEnd

-- 명령 설명
public export
commandDescription : MoveSelCommand -> String
commandDescription MoveSelLeft = "현재 위치에서 왼쪽으로 선택 확장 (1글자)"
commandDescription MoveSelRight = "현재 위치에서 오른쪽으로 선택 확장 (1글자)"
commandDescription MoveSelUp = "현재 위치에서 위로 선택 확장 (1줄)"
commandDescription MoveSelDown = "현재 위치에서 아래로 선택 확장 (1줄)"
commandDescription MoveSelPageUp = "현재 위치에서 위로 선택 확장 (1페이지)"
commandDescription MoveSelPageDown = "현재 위치에서 아래로 선택 확장 (1페이지)"
commandDescription MoveSelDocBegin = "현재 위치에서 문서 시작까지 선택"
commandDescription MoveSelDocEnd = "현재 위치에서 문서 끝까지 선택"
commandDescription MoveSelLineBegin = "현재 위치에서 줄 시작까지 선택"
commandDescription MoveSelLineEnd = "현재 위치에서 줄 끝까지 선택"
commandDescription MoveSelParaBegin = "현재 위치에서 Para 시작까지 선택"
commandDescription MoveSelParaEnd = "현재 위치에서 Para 끝까지 선택"

-- 명령을 문자열로 변환
public export
commandToString : MoveSelCommand -> String
commandToString MoveSelLeft = "MoveSelLeft"
commandToString MoveSelRight = "MoveSelRight"
commandToString MoveSelUp = "MoveSelUp"
commandToString MoveSelDown = "MoveSelDown"
commandToString MoveSelPageUp = "MoveSelPageUp"
commandToString MoveSelPageDown = "MoveSelPageDown"
commandToString MoveSelDocBegin = "MoveSelDocBegin"
commandToString MoveSelDocEnd = "MoveSelDocEnd"
commandToString MoveSelLineBegin = "MoveSelLineBegin"
commandToString MoveSelLineEnd = "MoveSelLineEnd"
commandToString MoveSelParaBegin = "MoveSelParaBegin"
commandToString MoveSelParaEnd = "MoveSelParaEnd"

-- 빈 Para 삭제 전략
public export
data EmptyParaStrategy
    = UseSelLeft    -- Para 시작에서 MoveSelLeft x2
    | UseSelRight   -- Para 시작에서 MoveSelRight x2
    | UseSelDown    -- Para 시작에서 MoveSelDown x1

-- 전략 설명
public export
strategyDescription : EmptyParaStrategy -> String
strategyDescription UseSelLeft = "Para 시작에서 MoveSelLeft x2 (검증됨)"
strategyDescription UseSelRight = "Para 시작에서 MoveSelRight x2"
strategyDescription UseSelDown = "Para 시작에서 MoveSelDown x1 (권장)"

-- 전략별 명령 시퀀스
public export
strategyCommands : EmptyParaStrategy -> List MoveSelCommand
strategyCommands UseSelLeft = [MoveSelLeft, MoveSelLeft]
strategyCommands UseSelRight = [MoveSelRight, MoveSelRight]
strategyCommands UseSelDown = [MoveSelDown]

-- Para 위치 타입
public export
record ParaPosition where
    constructor MkParaPosition
    list : Nat
    para : Nat
    pos : Nat

-- 빈 Para 확인
public export
isEmptyPara : ParaPosition -> ParaPosition -> Bool
isEmptyPara start end = (pos end) == 0
