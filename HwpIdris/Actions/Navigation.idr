-- HWP Action Table - Navigation
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Navigation

import Data.String

-- Navigation 액션 타입
public export
data NavigationAction
    = Goto  -- 찾아가기
    | GotoStyle  -- 찾아가기-스타일(찾기/바꾸기 대화상자에서 사용)
    | MoveColumnBegin  -- 무동작도 하지 않는다. 해당 리스트 안에서만 동작
    | MoveColumnEnd  -- 동작도 하지 않는다. 해당 리스트 안에서만 동작한
    | MoveDocBegin
    | MoveDocEnd
    | MoveDown  -- 캐럿을 (논리적 개념의) 아래로 이동시킨다.
    | MoveLeft  -- 캐럿을 (논리적 개념의) 왼쪽으로 이동시킨다.
    | MoveLineBegin  -- 현재 위치한 줄의 시작/끝으로 이동
    | MoveLineDown  -- 한 줄 아래로 이동한다.
    | MoveLineEnd  -- 현재 위치한 줄의 시작/끝으로 이동
    | MoveLineUp  -- 한 줄 위로 이동한다.
    | MoveListBegin  -- 현재 리스트의 시작으로 이동
    | MoveListEnd  -- 현재 리스트의 끝으로 이동
    | MoveNextChar
    | MoveNextColumn  -- 뒤 단으로 이동
    | MoveNextParaBegin
    | MoveNextPos
    | MoveNextPosEx  -- 있다. (머리말, 꼬리말, 각주, 미주, 글상자 포
    | MoveNextWord
    | MovePageBegin  -- 만약 캐럿의 위치가 변경되었다면 화면이 전환되어
    | MovePageDown
    | MovePageEnd  -- 만약 캐럿의 위치가 변경되었다면 화면이 전환되어
    | MovePageUp
    | MoveParaBegin  -- 현재 위치한 문단의 시작/끝으로 이동
    | MoveParaEnd  -- 현재 위치한 문단의 시작/끝으로 이동
    | MoveParentList
    | MovePrevChar
    | MovePrevColumn  -- 앞 단으로 이동
    | MovePrevParaBegin
    | MovePrevParaEnd
    | MovePrevPos
    | MovePrevPosEx  -- 있다. (머리말, 꼬리말, 각주, 미주, 글상자 포
    | MovePrevWord
    | MoveRight  -- 캐럿을 (논리적 개념의) 오른쪽으로 이동시킨다.
    | MoveRootList
    | MoveScrollDown  -- 아래 방향으로 스크롤하면서 이동
    | MoveScrollNext  -- 다음 방향으로 스크롤하면서 이동
    | MoveScrollPrev  -- 이전 방향으로 스크롤하면서 이동
    | MoveScrollUp  -- 위 방향으로 스크롤하면서 이동
    | MoveSectionDown
    | MoveSectionUp
    | MoveSelDocBegin  -- 셀렉션: 문서 처음
    | MoveSelDocEnd  -- 셀렉션: 문서 끝
    | MoveSelDown  -- 셀렉션: 캐럿을 (논리적 방향) 아래로 이동
    | MoveSelLeft  -- 셀렉션: 캐럿을 (논리적 방향) 왼쪽으로 이동
    | MoveSelLineBegin  -- 셀렉션: 줄 처음
    | MoveSelLineDown  -- 셀렉션: 한줄 아래
    | MoveSelLineEnd  -- 셀렉션: 줄 끝
    | MoveSelLineUp  -- 셀렉션: 한줄 위
    | MoveSelListBegin  -- 셀렉션: 리스트 처음
    | MoveSelListEnd  -- 셀렉션: 리스트 끝
    | MoveSelNextChar  -- 셀렉션: 다음 글자
    | MoveSelNextParaBegin  -- 셀렉션: 다음 문단 처음
    | MoveSelNextPos  -- 셀렉션: 다음 위치
    | MoveSelNextWord  -- 셀렉션: 다음 단어
    | MoveSelPageDown  -- 셀렉션: 페이지다운
    | MoveSelPageUp  -- 셀렉션: 페이지 업
    | MoveSelParaBegin  -- 셀렉션: 문단 처음
    | MoveSelParaEnd  -- 셀렉션: 문단 끝
    | MoveSelPrevChar  -- 셀렉션: 이전 글자
    | MoveSelPrevParaBegin  -- 셀렉션: 이전 문단 시작
    | MoveSelPrevParaEnd  -- 셀렉션: 이전 문단 끝
    | MoveSelPrevPos  -- 셀렉션: 이전 위치
    | MoveSelPrevWord  -- 셀렉션: 이전 단어
    | MoveSelRight  -- 셀렉션: 캐럿을 (논리적 방향) 오른쪽으로 이동
    | MoveSelTopLevelBegin  -- 셀렉션: 처음
    | MoveSelTopLevelEnd  -- 셀렉션: 끝
    | MoveSelUp  -- 셀렉션: 캐럿을 (논리적 방향) 위로 이동
    | MoveSelViewDown  -- 셀렉션: 아래
    | MoveSelViewUp  -- 셀렉션: 위
    | MoveSelWordBegin  -- 셀렉션: 단어 처음
    | MoveSelWordEnd  -- 셀렉션: 단어 끝
    | MoveTopLevelBegin  -- 탑레벨 리스트의 시작으로 이동
    | MoveTopLevelEnd  -- 탑레벨 리스트의 끝으로 이동
    | MoveTopLevelList
    | MoveUp  -- 캐럿을 (논리적 개념의) 위로 이동시킨다.
    | MoveViewBegin  -- 현재 뷰의 시작에 위치한 곳으로 이동
    | MoveViewDown
    | MoveViewEnd  -- 현재 뷰의 끝에 위치한 곳으로 이동
    | MoveViewUp
    | MoveWordBegin
    | MoveWordEnd

-- 액션 ID 문자열로 변환
public export
toString : NavigationAction -> String
toString Goto = "Goto"
toString GotoStyle = "GotoStyle"
toString MoveColumnBegin = "MoveColumnBegin"
toString MoveColumnEnd = "MoveColumnEnd"
toString MoveDocBegin = "MoveDocBegin"
toString MoveDocEnd = "MoveDocEnd"
toString MoveDown = "MoveDown"
toString MoveLeft = "MoveLeft"
toString MoveLineBegin = "MoveLineBegin"
toString MoveLineDown = "MoveLineDown"
toString MoveLineEnd = "MoveLineEnd"
toString MoveLineUp = "MoveLineUp"
toString MoveListBegin = "MoveListBegin"
toString MoveListEnd = "MoveListEnd"
toString MoveNextChar = "MoveNextChar"
toString MoveNextColumn = "MoveNextColumn"
toString MoveNextParaBegin = "MoveNextParaBegin"
toString MoveNextPos = "MoveNextPos"
toString MoveNextPosEx = "MoveNextPosEx"
toString MoveNextWord = "MoveNextWord"
toString MovePageBegin = "MovePageBegin"
toString MovePageDown = "MovePageDown"
toString MovePageEnd = "MovePageEnd"
toString MovePageUp = "MovePageUp"
toString MoveParaBegin = "MoveParaBegin"
toString MoveParaEnd = "MoveParaEnd"
toString MoveParentList = "MoveParentList"
toString MovePrevChar = "MovePrevChar"
toString MovePrevColumn = "MovePrevColumn"
toString MovePrevParaBegin = "MovePrevParaBegin"
toString MovePrevParaEnd = "MovePrevParaEnd"
toString MovePrevPos = "MovePrevPos"
toString MovePrevPosEx = "MovePrevPosEx"
toString MovePrevWord = "MovePrevWord"
toString MoveRight = "MoveRight"
toString MoveRootList = "MoveRootList"
toString MoveScrollDown = "MoveScrollDown"
toString MoveScrollNext = "MoveScrollNext"
toString MoveScrollPrev = "MoveScrollPrev"
toString MoveScrollUp = "MoveScrollUp"
toString MoveSectionDown = "MoveSectionDown"
toString MoveSectionUp = "MoveSectionUp"
toString MoveSelDocBegin = "MoveSelDocBegin"
toString MoveSelDocEnd = "MoveSelDocEnd"
toString MoveSelDown = "MoveSelDown"
toString MoveSelLeft = "MoveSelLeft"
toString MoveSelLineBegin = "MoveSelLineBegin"
toString MoveSelLineDown = "MoveSelLineDown"
toString MoveSelLineEnd = "MoveSelLineEnd"
toString MoveSelLineUp = "MoveSelLineUp"
toString MoveSelListBegin = "MoveSelListBegin"
toString MoveSelListEnd = "MoveSelListEnd"
toString MoveSelNextChar = "MoveSelNextChar"
toString MoveSelNextParaBegin = "MoveSelNextParaBegin"
toString MoveSelNextPos = "MoveSelNextPos"
toString MoveSelNextWord = "MoveSelNextWord"
toString MoveSelPageDown = "MoveSelPageDown"
toString MoveSelPageUp = "MoveSelPageUp"
toString MoveSelParaBegin = "MoveSelParaBegin"
toString MoveSelParaEnd = "MoveSelParaEnd"
toString MoveSelPrevChar = "MoveSelPrevChar"
toString MoveSelPrevParaBegin = "MoveSelPrevParaBegin"
toString MoveSelPrevParaEnd = "MoveSelPrevParaEnd"
toString MoveSelPrevPos = "MoveSelPrevPos"
toString MoveSelPrevWord = "MoveSelPrevWord"
toString MoveSelRight = "MoveSelRight"
toString MoveSelTopLevelBegin = "MoveSelTopLevelBegin"
toString MoveSelTopLevelEnd = "MoveSelTopLevelEnd"
toString MoveSelUp = "MoveSelUp"
toString MoveSelViewDown = "MoveSelViewDown"
toString MoveSelViewUp = "MoveSelViewUp"
toString MoveSelWordBegin = "MoveSelWordBegin"
toString MoveSelWordEnd = "MoveSelWordEnd"
toString MoveTopLevelBegin = "MoveTopLevelBegin"
toString MoveTopLevelEnd = "MoveTopLevelEnd"
toString MoveTopLevelList = "MoveTopLevelList"
toString MoveUp = "MoveUp"
toString MoveViewBegin = "MoveViewBegin"
toString MoveViewDown = "MoveViewDown"
toString MoveViewEnd = "MoveViewEnd"
toString MoveViewUp = "MoveViewUp"
toString MoveWordBegin = "MoveWordBegin"
toString MoveWordEnd = "MoveWordEnd"

-- ParameterSet ID
public export
paramSetID : NavigationAction -> Maybe String
paramSetID Goto = Just "GotoE"
paramSetID GotoStyle = Just "GotoE"
paramSetID MoveColumnBegin = Nothing
paramSetID MoveColumnEnd = Nothing
paramSetID MoveDocBegin = Nothing
paramSetID MoveDocEnd = Nothing
paramSetID MoveDown = Nothing
paramSetID MoveLeft = Nothing
paramSetID MoveLineBegin = Nothing
paramSetID MoveLineDown = Nothing
paramSetID MoveLineEnd = Nothing
paramSetID MoveLineUp = Nothing
paramSetID MoveListBegin = Nothing
paramSetID MoveListEnd = Nothing
paramSetID MoveNextChar = Nothing
paramSetID MoveNextColumn = Nothing
paramSetID MoveNextParaBegin = Nothing
paramSetID MoveNextPos = Nothing
paramSetID MoveNextPosEx = Nothing
paramSetID MoveNextWord = Nothing
paramSetID MovePageBegin = Nothing
paramSetID MovePageDown = Nothing
paramSetID MovePageEnd = Nothing
paramSetID MovePageUp = Nothing
paramSetID MoveParaBegin = Nothing
paramSetID MoveParaEnd = Nothing
paramSetID MoveParentList = Nothing
paramSetID MovePrevChar = Nothing
paramSetID MovePrevColumn = Nothing
paramSetID MovePrevParaBegin = Nothing
paramSetID MovePrevParaEnd = Nothing
paramSetID MovePrevPos = Nothing
paramSetID MovePrevPosEx = Nothing
paramSetID MovePrevWord = Nothing
paramSetID MoveRight = Nothing
paramSetID MoveRootList = Nothing
paramSetID MoveScrollDown = Nothing
paramSetID MoveScrollNext = Nothing
paramSetID MoveScrollPrev = Nothing
paramSetID MoveScrollUp = Nothing
paramSetID MoveSectionDown = Nothing
paramSetID MoveSectionUp = Nothing
paramSetID MoveSelDocBegin = Nothing
paramSetID MoveSelDocEnd = Nothing
paramSetID MoveSelDown = Nothing
paramSetID MoveSelLeft = Nothing
paramSetID MoveSelLineBegin = Nothing
paramSetID MoveSelLineDown = Nothing
paramSetID MoveSelLineEnd = Nothing
paramSetID MoveSelLineUp = Nothing
paramSetID MoveSelListBegin = Nothing
paramSetID MoveSelListEnd = Nothing
paramSetID MoveSelNextChar = Nothing
paramSetID MoveSelNextParaBegin = Nothing
paramSetID MoveSelNextPos = Nothing
paramSetID MoveSelNextWord = Nothing
paramSetID MoveSelPageDown = Nothing
paramSetID MoveSelPageUp = Nothing
paramSetID MoveSelParaBegin = Nothing
paramSetID MoveSelParaEnd = Nothing
paramSetID MoveSelPrevChar = Nothing
paramSetID MoveSelPrevParaBegin = Nothing
paramSetID MoveSelPrevParaEnd = Nothing
paramSetID MoveSelPrevPos = Nothing
paramSetID MoveSelPrevWord = Nothing
paramSetID MoveSelRight = Nothing
paramSetID MoveSelTopLevelBegin = Nothing
paramSetID MoveSelTopLevelEnd = Nothing
paramSetID MoveSelUp = Nothing
paramSetID MoveSelViewDown = Nothing
paramSetID MoveSelViewUp = Nothing
paramSetID MoveSelWordBegin = Nothing
paramSetID MoveSelWordEnd = Nothing
paramSetID MoveTopLevelBegin = Nothing
paramSetID MoveTopLevelEnd = Nothing
paramSetID MoveTopLevelList = Nothing
paramSetID MoveUp = Nothing
paramSetID MoveViewBegin = Nothing
paramSetID MoveViewDown = Nothing
paramSetID MoveViewEnd = Nothing
paramSetID MoveViewUp = Nothing
paramSetID MoveWordBegin = Nothing
paramSetID MoveWordEnd = Nothing

-- 설명
public export
description : NavigationAction -> String
description Goto = "찾아가기"
description GotoStyle = "찾아가기-스타일(찾기/바꾸기 대화상자에서 사용)"
description MoveColumnBegin = "무동작도 하지 않는다. 해당 리스트 안에서만 동작"
description MoveColumnEnd = "동작도 하지 않는다. 해당 리스트 안에서만 동작한"
description MoveDocBegin = "No description"
description MoveDocEnd = "No description"
description MoveDown = "캐럿을 (논리적 개념의) 아래로 이동시킨다."
description MoveLeft = "캐럿을 (논리적 개념의) 왼쪽으로 이동시킨다."
description MoveLineBegin = "현재 위치한 줄의 시작/끝으로 이동"
description MoveLineDown = "한 줄 아래로 이동한다."
description MoveLineEnd = "현재 위치한 줄의 시작/끝으로 이동"
description MoveLineUp = "한 줄 위로 이동한다."
description MoveListBegin = "현재 리스트의 시작으로 이동"
description MoveListEnd = "현재 리스트의 끝으로 이동"
description MoveNextChar = "No description"
description MoveNextColumn = "뒤 단으로 이동"
description MoveNextParaBegin = "No description"
description MoveNextPos = "No description"
description MoveNextPosEx = "있다. (머리말, 꼬리말, 각주, 미주, 글상자 포"
description MoveNextWord = "No description"
description MovePageBegin = "만약 캐럿의 위치가 변경되었다면 화면이 전환되어"
description MovePageDown = "No description"
description MovePageEnd = "만약 캐럿의 위치가 변경되었다면 화면이 전환되어"
description MovePageUp = "No description"
description MoveParaBegin = "현재 위치한 문단의 시작/끝으로 이동"
description MoveParaEnd = "현재 위치한 문단의 시작/끝으로 이동"
description MoveParentList = "No description"
description MovePrevChar = "No description"
description MovePrevColumn = "앞 단으로 이동"
description MovePrevParaBegin = "No description"
description MovePrevParaEnd = "No description"
description MovePrevPos = "No description"
description MovePrevPosEx = "있다. (머리말, 꼬리말, 각주, 미주, 글상자 포"
description MovePrevWord = "No description"
description MoveRight = "캐럿을 (논리적 개념의) 오른쪽으로 이동시킨다."
description MoveRootList = "No description"
description MoveScrollDown = "아래 방향으로 스크롤하면서 이동"
description MoveScrollNext = "다음 방향으로 스크롤하면서 이동"
description MoveScrollPrev = "이전 방향으로 스크롤하면서 이동"
description MoveScrollUp = "위 방향으로 스크롤하면서 이동"
description MoveSectionDown = "No description"
description MoveSectionUp = "No description"
description MoveSelDocBegin = "셀렉션: 문서 처음"
description MoveSelDocEnd = "셀렉션: 문서 끝"
description MoveSelDown = "셀렉션: 캐럿을 (논리적 방향) 아래로 이동"
description MoveSelLeft = "셀렉션: 캐럿을 (논리적 방향) 왼쪽으로 이동"
description MoveSelLineBegin = "셀렉션: 줄 처음"
description MoveSelLineDown = "셀렉션: 한줄 아래"
description MoveSelLineEnd = "셀렉션: 줄 끝"
description MoveSelLineUp = "셀렉션: 한줄 위"
description MoveSelListBegin = "셀렉션: 리스트 처음"
description MoveSelListEnd = "셀렉션: 리스트 끝"
description MoveSelNextChar = "셀렉션: 다음 글자"
description MoveSelNextParaBegin = "셀렉션: 다음 문단 처음"
description MoveSelNextPos = "셀렉션: 다음 위치"
description MoveSelNextWord = "셀렉션: 다음 단어"
description MoveSelPageDown = "셀렉션: 페이지다운"
description MoveSelPageUp = "셀렉션: 페이지 업"
description MoveSelParaBegin = "셀렉션: 문단 처음"
description MoveSelParaEnd = "셀렉션: 문단 끝"
description MoveSelPrevChar = "셀렉션: 이전 글자"
description MoveSelPrevParaBegin = "셀렉션: 이전 문단 시작"
description MoveSelPrevParaEnd = "셀렉션: 이전 문단 끝"
description MoveSelPrevPos = "셀렉션: 이전 위치"
description MoveSelPrevWord = "셀렉션: 이전 단어"
description MoveSelRight = "셀렉션: 캐럿을 (논리적 방향) 오른쪽으로 이동"
description MoveSelTopLevelBegin = "셀렉션: 처음"
description MoveSelTopLevelEnd = "셀렉션: 끝"
description MoveSelUp = "셀렉션: 캐럿을 (논리적 방향) 위로 이동"
description MoveSelViewDown = "셀렉션: 아래"
description MoveSelViewUp = "셀렉션: 위"
description MoveSelWordBegin = "셀렉션: 단어 처음"
description MoveSelWordEnd = "셀렉션: 단어 끝"
description MoveTopLevelBegin = "탑레벨 리스트의 시작으로 이동"
description MoveTopLevelEnd = "탑레벨 리스트의 끝으로 이동"
description MoveTopLevelList = "No description"
description MoveUp = "캐럿을 (논리적 개념의) 위로 이동시킨다."
description MoveViewBegin = "현재 뷰의 시작에 위치한 곳으로 이동"
description MoveViewDown = "No description"
description MoveViewEnd = "현재 뷰의 끝에 위치한 곳으로 이동"
description MoveViewUp = "No description"
description MoveWordBegin = "No description"
description MoveWordEnd = "No description"

-- 총 83개 Navigation 액션
