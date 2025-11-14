-- HWP Action Table - Shape
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Shape

import Data.String

-- Shape 액션 타입
public export
data ShapeAction
    = ShapeObject  -- 펜 그리기
    | ShapeObject2  -- 사각형 그리기
    | ImageFindPath  -- 그림 경로 찾기
    | ShapeObject3  -- 연결선(구부러진 연결선)
    | ShapeObject4  -- 연결선 반복해서 그리기(직선 연결선)
    | ShapeObject5  -- 연결선 반복해서 그리기(꺾인 연결선)
    | ShapeObject6  -- 연결선(직선 양쪽 화살표 연결선)
    | ShapeObject7  -- 연결선(직선 연결선)
    | ShapeObject8  -- 연결선(직선 화살표 연결선)
    | ShapeObject9  -- 연결선(꺾인 양쪽 화살표 연결선)
    | ShapeObject10  -- 연결선(꺾인 연결선)
    | ShapeObject11  -- 연결선(꺾인 화살표 연결선)
    | PictureBulletDlg  -- 그림 글머리표 대화상자
    | PictureChange  -- 그림 바꾸기
    | PictureEffect1  -- 그림 그레이 스케일
    | PictureEffect2  -- 그림 흑백으로
    | PictureEffect3  -- 그림 워터마크
    | PictureEffect4  -- 그림 효과 없음
    | PictureEffect5  -- 그림 밝기 증가
    | PictureEffect6  -- 그림 밝기 감소
    | PictureEffect7  -- 그림 명암 증가
    | PictureEffect8  -- 그림 명암 감소
    | PictureInsertDialog
    | PictureLinkedToEmbedded  -- 연결된 그림을 모두 삽입그림으로
    | PictureNoBrightness  -- 그림 밝기 효과 없음
    | PictureNoContrast  -- 그림 대비 효과 없음
    | PictureNoGlow  -- 그림 네온 효과 없음
    | PictureNoReflection  -- 그림 반사 효과 없음
    | PictureNoShadow  -- 그림 그림자 효과 없음
    | PictureNoSofeEdge  -- 그림 부드러운 가장자리 효과 없음
    | PictureNoStyle  -- 그림 스타일 효과 없음
    | PictureSave  -- 그림 빼내기
    | PictureSaveAsAll  -- 삽입된 바이너리 그림 다른 형태로 저장.
    | PictureSaveAsOption
    | PictureScissor  -- 그림 자르기
    | PictureToOriginal  -- 그림 원래 그림으로
    | ShapeCopyPaste  -- 모양 복사
    | ShapeObjAlignBottom  -- 아래로 정렬
    | ShapeObjAlignCenter  -- 가운데로 정렬
    | ShapeObjAlignHeight  -- 높이 맞춤
    | ShapeObjAlignHorzSpacing  -- 왼쪽/오른쪽 일정한 비율로 정렬
    | ShapeObjAlignLeft  -- 왼쪽으로 정렬
    | ShapeObjAlignMiddle  -- 중간 정렬
    | ShapeObjAlignRight  -- 오른쪽으로 정렬
    | ShapeObjAlignSize  -- 폭/높이 맞춤
    | ShapeObjAlignTop  -- 위로 정렬
    | ShapeObjAlignVertSpacing  -- 위/아래 일정한 비율로 정렬
    | ShapeObjAlignWidth  -- 폭 맞춤
    | ShapeObjAttachCaption  -- 캡션 넣기
    | ShapeObjAttachTextBox  -- 글 상자로 만들기
    | ShapeObjAttrDialog  -- 틀 속성 환경설정
    | ShapeObjBringForward  -- 앞으로
    | ShapeObjBringInFrontOfText  -- 글 앞으로
    | ShapeObjBringToFront  -- 맨 앞으로
    | ShapeObjComment  -- 개체 설명문 수정하기
    | ShapeObjCtrlSendBehindText  -- 글 뒤로
    | ShapeObjDetachCaption  -- 캡션 없애기
    | ShapeObjDetachTextBox  -- 글상자 속성 없애기
    | ShapeObjDialog  -- 환경설정
    | ShapeObjectCopy  -- 모양 복사
    | ShapeObjectPaste  -- 모양 붙여넣기
    | ShapeObjFillProperty  -- 고치기 대화상자중 fill tab
    | ShapeObjGroup  -- 틀 묶기
    | ShapeObjGuideLine  -- 개체 안내선
    | ShapeObjHorzFlip  -- 그리기 개체 좌우 뒤집기
    | ShapeObjHorzFlipOrgState  -- 그리기 개체 좌우 뒤집기 원상태로 되돌리기
    | ShapeObjInsertCaptionNum  -- 캡션 번호 넣기
    | ShapeObjLineProperty  -- 고치기 대화상자중 line tab
    | ShapeObjLineStyleOhter  -- 다른 선 종류
    | ShapeObjLineWidthOhter  -- 다른 선 굵기
    | ShapeObjLock  -- 개체 Lock
    | ShapeObjMoveDown  -- 키로 움직이기(아래)
    | ShapeObjMoveLeft  -- 키로 움직이기(왼쪽)
    | ShapeObjMoveRight  -- 키로 움직이기(오른쪽)
    | ShapeObjMoveUp  -- 키로 움직이기(위)
    | ShapeObjNextObject  -- 이후 개채로 이동(tab키)
    | ShapeObjNorm  -- 기본 도형 설정
    | ShapeObjNoShade  -- 채우기 색 음영 없음
    | ShapeObjNoShadow  -- 그림자 없음
    | ShapeObjPrevObject  -- 이전 개체로 이동(shift + tab키)
    | ShapeObjProtectSize  -- 그리기 개체 크기 고정
    | ShapeObjRandomAngleRotater  -- 자유각 회전
    | ShapeObjResizeDown  -- 키로 크기 조절(shift + 아래)
    | ShapeObjResizeLeft  -- 키로 크기 조절(shift + 왼쪽)
    | ShapeObjResizeRight  -- 키로 크기 조절(shift + 오른쪽)
    | ShapeObjResizeUp  -- 키로 크기 조절(shift + 위)
    | ShapeObjRightAngleRotater  -- 90도 회전
    | ShapeObjRotater  -- 자유각 회전(회전중심 고정)
    | ShapeObjSaveAsPicture  -- 그리기개체를 그림으로 저장하기
    | ShapeObjSelect  -- 틀 선택 도구
    | ShapeObjSendBack  -- 뒤로
    | ShapeObjSendToBack  -- 맨 뒤로
    | ShapeObjShadowEnlarge
    | ShapeObjShadowMoveDown
    | ShapeObjShadowMoveLeft
    | ShapeObjShadowMoveOrginal  -- 그리기 개체 그림자 위치 원점으로(offset제거)
    | ShapeObjShadowMoveRight
    | ShapeObjShadowMoveUp
    | ShapeObjShadowNarrow
    | ShapeObjShadowParellelLeft  -- 개체 그림자를 원본 개체와 동일한 크기로
    | ShapeObjShadowParellelLeft2  -- 개체 그림자를 원본 개체와 동일한 크기로
    | ShapeObjShadowParellelRigh  -- 개체 그림자를 원본 개체와 동일한 크기로
    | ShapeObjShadowParellelRigh2  -- 개체 그림자를 원본 개체와 동일한 크기로
    | ShapeObjShadowShearLeftBot  -- 개체 그림자를 왼쪽 뒷부분으로 눕혀서 생
    | ShapeObjShadowShearLeftTop
    | ShapeObjShadowShearRightBo  -- 개체 그림자를 오른쪽 뒷부분으로 눕혀서
    | ShapeObjShadowShearRightTo  -- 개체 그림자를 오른쪽 앞부분으로 눕혀서
    | ShapeObjShear  -- 그리기 개체 기울이기
    | ShapeObjShowGuideLine  -- 개체 안내선
    | ShapeObjShowGuideLineBase  -- 안내선 한/글 2024 부터 지원
    | ShapeObjTableSelCell  -- 테이블 선택상태에서 첫 번째 셀 선택하기
    | ShapeObjTextBoxEdit  -- 글상자 선택상태에서 편집모드로 들어가기
    | ShapeObjToggleTextBox  -- 도형 글 상자로 만들기- Toggle
    | ShapeObjUngroup  -- 틀 풀기
    | ShapeObjUnlockAll  -- 개체 Unlock All
    | ShapeObjVertFlip  -- 그리기 개체 상하 뒤집기
    | ShapeObjVertFlipOrgState  -- 그리기 개체 상하 뒤집기 원상태로 되돌리기
    | ShapeObjWrapSquare  -- 직사각형
    | ShapeObjWrapTopAndBottom  -- 자리 차지

-- 액션 ID 문자열로 변환
public export
toString : ShapeAction -> String
toString ShapeObject = "ShapeObject"
toString ShapeObject2 = "ShapeObject"
toString ImageFindPath = "ImageFindPath"
toString ShapeObject3 = "ShapeObject"
toString ShapeObject4 = "ShapeObject"
toString ShapeObject5 = "ShapeObject"
toString ShapeObject6 = "ShapeObject"
toString ShapeObject7 = "ShapeObject"
toString ShapeObject8 = "ShapeObject"
toString ShapeObject9 = "ShapeObject"
toString ShapeObject10 = "ShapeObject"
toString ShapeObject11 = "ShapeObject"
toString PictureBulletDlg = "PictureBulletDlg"
toString PictureChange = "PictureChange"
toString PictureEffect1 = "PictureEffect1"
toString PictureEffect2 = "PictureEffect2"
toString PictureEffect3 = "PictureEffect3"
toString PictureEffect4 = "PictureEffect4"
toString PictureEffect5 = "PictureEffect5"
toString PictureEffect6 = "PictureEffect6"
toString PictureEffect7 = "PictureEffect7"
toString PictureEffect8 = "PictureEffect8"
toString PictureInsertDialog = "PictureInsertDialog"
toString PictureLinkedToEmbedded = "PictureLinkedToEmbedded"
toString PictureNoBrightness = "PictureNoBrightness"
toString PictureNoContrast = "PictureNoContrast"
toString PictureNoGlow = "PictureNoGlow"
toString PictureNoReflection = "PictureNoReflection"
toString PictureNoShadow = "PictureNoShadow"
toString PictureNoSofeEdge = "PictureNoSofeEdge"
toString PictureNoStyle = "PictureNoStyle"
toString PictureSave = "PictureSave"
toString PictureSaveAsAll = "PictureSaveAsAll"
toString PictureSaveAsOption = "PictureSaveAsOption"
toString PictureScissor = "PictureScissor"
toString PictureToOriginal = "PictureToOriginal"
toString ShapeCopyPaste = "ShapeCopyPaste"
toString ShapeObjAlignBottom = "ShapeObjAlignBottom"
toString ShapeObjAlignCenter = "ShapeObjAlignCenter"
toString ShapeObjAlignHeight = "ShapeObjAlignHeight"
toString ShapeObjAlignHorzSpacing = "ShapeObjAlignHorzSpacing"
toString ShapeObjAlignLeft = "ShapeObjAlignLeft"
toString ShapeObjAlignMiddle = "ShapeObjAlignMiddle"
toString ShapeObjAlignRight = "ShapeObjAlignRight"
toString ShapeObjAlignSize = "ShapeObjAlignSize"
toString ShapeObjAlignTop = "ShapeObjAlignTop"
toString ShapeObjAlignVertSpacing = "ShapeObjAlignVertSpacing"
toString ShapeObjAlignWidth = "ShapeObjAlignWidth"
toString ShapeObjAttachCaption = "ShapeObjAttachCaption"
toString ShapeObjAttachTextBox = "ShapeObjAttachTextBox"
toString ShapeObjAttrDialog = "ShapeObjAttrDialog"
toString ShapeObjBringForward = "ShapeObjBringForward"
toString ShapeObjBringInFrontOfText = "ShapeObjBringInFrontOfText"
toString ShapeObjBringToFront = "ShapeObjBringToFront"
toString ShapeObjComment = "ShapeObjComment"
toString ShapeObjCtrlSendBehindText = "ShapeObjCtrlSendBehindText"
toString ShapeObjDetachCaption = "ShapeObjDetachCaption"
toString ShapeObjDetachTextBox = "ShapeObjDetachTextBox"
toString ShapeObjDialog = "ShapeObjDialog"
toString ShapeObjectCopy = "ShapeObjectCopy"
toString ShapeObjectPaste = "ShapeObjectPaste"
toString ShapeObjFillProperty = "ShapeObjFillProperty"
toString ShapeObjGroup = "ShapeObjGroup"
toString ShapeObjGuideLine = "ShapeObjGuideLine"
toString ShapeObjHorzFlip = "ShapeObjHorzFlip"
toString ShapeObjHorzFlipOrgState = "ShapeObjHorzFlipOrgState"
toString ShapeObjInsertCaptionNum = "ShapeObjInsertCaptionNum"
toString ShapeObjLineProperty = "ShapeObjLineProperty"
toString ShapeObjLineStyleOhter = "ShapeObjLineStyleOhter"
toString ShapeObjLineWidthOhter = "ShapeObjLineWidthOhter"
toString ShapeObjLock = "ShapeObjLock"
toString ShapeObjMoveDown = "ShapeObjMoveDown"
toString ShapeObjMoveLeft = "ShapeObjMoveLeft"
toString ShapeObjMoveRight = "ShapeObjMoveRight"
toString ShapeObjMoveUp = "ShapeObjMoveUp"
toString ShapeObjNextObject = "ShapeObjNextObject"
toString ShapeObjNorm = "ShapeObjNorm"
toString ShapeObjNoShade = "ShapeObjNoShade"
toString ShapeObjNoShadow = "ShapeObjNoShadow"
toString ShapeObjPrevObject = "ShapeObjPrevObject"
toString ShapeObjProtectSize = "ShapeObjProtectSize"
toString ShapeObjRandomAngleRotater = "ShapeObjRandomAngleRotater"
toString ShapeObjResizeDown = "ShapeObjResizeDown"
toString ShapeObjResizeLeft = "ShapeObjResizeLeft"
toString ShapeObjResizeRight = "ShapeObjResizeRight"
toString ShapeObjResizeUp = "ShapeObjResizeUp"
toString ShapeObjRightAngleRotater = "ShapeObjRightAngleRotater"
toString ShapeObjRotater = "ShapeObjRotater"
toString ShapeObjSaveAsPicture = "ShapeObjSaveAsPicture"
toString ShapeObjSelect = "ShapeObjSelect"
toString ShapeObjSendBack = "ShapeObjSendBack"
toString ShapeObjSendToBack = "ShapeObjSendToBack"
toString ShapeObjShadowEnlarge = "ShapeObjShadowEnlarge"
toString ShapeObjShadowMoveDown = "ShapeObjShadowMoveDown"
toString ShapeObjShadowMoveLeft = "ShapeObjShadowMoveLeft"
toString ShapeObjShadowMoveOrginal = "ShapeObjShadowMoveOrginal"
toString ShapeObjShadowMoveRight = "ShapeObjShadowMoveRight"
toString ShapeObjShadowMoveUp = "ShapeObjShadowMoveUp"
toString ShapeObjShadowNarrow = "ShapeObjShadowNarrow"
toString ShapeObjShadowParellelLeft = "ShapeObjShadowParellelLeft"
toString ShapeObjShadowParellelLeft2 = "ShapeObjShadowParellelLeft"
toString ShapeObjShadowParellelRigh = "ShapeObjShadowParellelRigh"
toString ShapeObjShadowParellelRigh2 = "ShapeObjShadowParellelRigh"
toString ShapeObjShadowShearLeftBot = "ShapeObjShadowShearLeftBot"
toString ShapeObjShadowShearLeftTop = "ShapeObjShadowShearLeftTop"
toString ShapeObjShadowShearRightBo = "ShapeObjShadowShearRightBo"
toString ShapeObjShadowShearRightTo = "ShapeObjShadowShearRightTo"
toString ShapeObjShear = "ShapeObjShear"
toString ShapeObjShowGuideLine = "ShapeObjShowGuideLine"
toString ShapeObjShowGuideLineBase = "ShapeObjShowGuideLineBase"
toString ShapeObjTableSelCell = "ShapeObjTableSelCell"
toString ShapeObjTextBoxEdit = "ShapeObjTextBoxEdit"
toString ShapeObjToggleTextBox = "ShapeObjToggleTextBox"
toString ShapeObjUngroup = "ShapeObjUngroup"
toString ShapeObjUnlockAll = "ShapeObjUnlockAll"
toString ShapeObjVertFlip = "ShapeObjVertFlip"
toString ShapeObjVertFlipOrgState = "ShapeObjVertFlipOrgState"
toString ShapeObjWrapSquare = "ShapeObjWrapSquare"
toString ShapeObjWrapTopAndBottom = "ShapeObjWrapTopAndBottom"

-- ParameterSet ID
public export
paramSetID : ShapeAction -> Maybe String
paramSetID ShapeObject = Just "반복해서"
paramSetID ShapeObject2 = Just "반복해서"
paramSetID ImageFindPath = Nothing
paramSetID ShapeObject3 = Just "개체"
paramSetID ShapeObject4 = Just "개체"
paramSetID ShapeObject5 = Just "개체"
paramSetID ShapeObject6 = Just "개체"
paramSetID ShapeObject7 = Just "개체"
paramSetID ShapeObject8 = Just "개체"
paramSetID ShapeObject9 = Just "개체"
paramSetID ShapeObject10 = Just "개체"
paramSetID ShapeObject11 = Just "개체"
paramSetID PictureBulletDlg = Just "ParaShape"
paramSetID PictureChange = Just "PictureChange"
paramSetID PictureEffect1 = Nothing
paramSetID PictureEffect2 = Nothing
paramSetID PictureEffect3 = Nothing
paramSetID PictureEffect4 = Nothing
paramSetID PictureEffect5 = Nothing
paramSetID PictureEffect6 = Nothing
paramSetID PictureEffect7 = Nothing
paramSetID PictureEffect8 = Nothing
paramSetID PictureInsertDialog = Nothing
paramSetID PictureLinkedToEmbedded = Nothing
paramSetID PictureNoBrightness = Just "ShapeObject"
paramSetID PictureNoContrast = Just "ShapeObject"
paramSetID PictureNoGlow = Just "ShapeObject"
paramSetID PictureNoReflection = Just "ShapeObject"
paramSetID PictureNoShadow = Just "ShapeObject"
paramSetID PictureNoSofeEdge = Just "ShapeObject"
paramSetID PictureNoStyle = Just "ShapeObject"
paramSetID PictureSave = Nothing
paramSetID PictureSaveAsAll = Just "SaveAsImage"
paramSetID PictureSaveAsOption = Just "SaveAsImage"
paramSetID PictureScissor = Nothing
paramSetID PictureToOriginal = Nothing
paramSetID ShapeCopyPaste = Just "ShapeCopyPaste"
paramSetID ShapeObjAlignBottom = Nothing
paramSetID ShapeObjAlignCenter = Nothing
paramSetID ShapeObjAlignHeight = Nothing
paramSetID ShapeObjAlignHorzSpacing = Nothing
paramSetID ShapeObjAlignLeft = Nothing
paramSetID ShapeObjAlignMiddle = Nothing
paramSetID ShapeObjAlignRight = Nothing
paramSetID ShapeObjAlignSize = Nothing
paramSetID ShapeObjAlignTop = Nothing
paramSetID ShapeObjAlignVertSpacing = Nothing
paramSetID ShapeObjAlignWidth = Nothing
paramSetID ShapeObjAttachCaption = Nothing
paramSetID ShapeObjAttachTextBox = Nothing
paramSetID ShapeObjAttrDialog = Just "ShapeObject"
paramSetID ShapeObjBringForward = Nothing
paramSetID ShapeObjBringInFrontOfText = Nothing
paramSetID ShapeObjBringToFront = Nothing
paramSetID ShapeObjComment = Just "ShapeObject"
paramSetID ShapeObjCtrlSendBehindText = Nothing
paramSetID ShapeObjDetachCaption = Nothing
paramSetID ShapeObjDetachTextBox = Nothing
paramSetID ShapeObjDialog = Just "ShapeObject"
paramSetID ShapeObjectCopy = Just "그리기"
paramSetID ShapeObjectPaste = Just "그리기"
paramSetID ShapeObjFillProperty = Nothing
paramSetID ShapeObjGroup = Nothing
paramSetID ShapeObjGuideLine = Just "그리기"
paramSetID ShapeObjHorzFlip = Nothing
paramSetID ShapeObjHorzFlipOrgState = Nothing
paramSetID ShapeObjInsertCaptionNum = Nothing
paramSetID ShapeObjLineProperty = Nothing
paramSetID ShapeObjLineStyleOhter = Nothing
paramSetID ShapeObjLineWidthOhter = Nothing
paramSetID ShapeObjLock = Nothing
paramSetID ShapeObjMoveDown = Nothing
paramSetID ShapeObjMoveLeft = Nothing
paramSetID ShapeObjMoveRight = Nothing
paramSetID ShapeObjMoveUp = Nothing
paramSetID ShapeObjNextObject = Nothing
paramSetID ShapeObjNorm = Nothing
paramSetID ShapeObjNoShade = Just "ShapeObject"
paramSetID ShapeObjNoShadow = Just "ShapeObject"
paramSetID ShapeObjPrevObject = Nothing
paramSetID ShapeObjProtectSize = Just "ShapeObject"
paramSetID ShapeObjRandomAngleRotater = Just "ShapeObject"
paramSetID ShapeObjResizeDown = Nothing
paramSetID ShapeObjResizeLeft = Nothing
paramSetID ShapeObjResizeRight = Nothing
paramSetID ShapeObjResizeUp = Nothing
paramSetID ShapeObjRightAngleRotater = Nothing
paramSetID ShapeObjRotater = Nothing
paramSetID ShapeObjSaveAsPicture = Nothing
paramSetID ShapeObjSelect = Nothing
paramSetID ShapeObjSendBack = Nothing
paramSetID ShapeObjSendToBack = Nothing
paramSetID ShapeObjShadowEnlarge = Just "+"  -- Internal
paramSetID ShapeObjShadowMoveDown = Just "+"  -- Internal
paramSetID ShapeObjShadowMoveLeft = Just "+"  -- Internal
paramSetID ShapeObjShadowMoveOrginal = Just "+"  -- Internal
paramSetID ShapeObjShadowMoveRight = Just "+"  -- Internal
paramSetID ShapeObjShadowMoveUp = Just "+"  -- Internal
paramSetID ShapeObjShadowNarrow = Just "+"  -- Internal
paramSetID ShapeObjShadowParellelLeft = Just "그리기"
paramSetID ShapeObjShadowParellelLeft2 = Just "그리기"
paramSetID ShapeObjShadowParellelRigh = Just "그리기"
paramSetID ShapeObjShadowParellelRigh2 = Just "그리기"
paramSetID ShapeObjShadowShearLeftBot = Just "그리기"
paramSetID ShapeObjShadowShearLeftTop = Just "+"  -- Internal
paramSetID ShapeObjShadowShearRightBo = Just "그리기"
paramSetID ShapeObjShadowShearRightTo = Just "그리기"
paramSetID ShapeObjShear = Just "ShapeObject"
paramSetID ShapeObjShowGuideLine = Just "그리기"
paramSetID ShapeObjShowGuideLineBase = Just "그리기"
paramSetID ShapeObjTableSelCell = Nothing
paramSetID ShapeObjTextBoxEdit = Nothing
paramSetID ShapeObjToggleTextBox = Nothing
paramSetID ShapeObjUngroup = Nothing
paramSetID ShapeObjUnlockAll = Nothing
paramSetID ShapeObjVertFlip = Nothing
paramSetID ShapeObjVertFlipOrgState = Nothing
paramSetID ShapeObjWrapSquare = Nothing
paramSetID ShapeObjWrapTopAndBottom = Nothing

-- 설명
public export
description : ShapeAction -> String
description ShapeObject = "펜 그리기"
description ShapeObject2 = "사각형 그리기"
description ImageFindPath = "그림 경로 찾기"
description ShapeObject3 = "연결선(구부러진 연결선)"
description ShapeObject4 = "연결선 반복해서 그리기(직선 연결선)"
description ShapeObject5 = "연결선 반복해서 그리기(꺾인 연결선)"
description ShapeObject6 = "연결선(직선 양쪽 화살표 연결선)"
description ShapeObject7 = "연결선(직선 연결선)"
description ShapeObject8 = "연결선(직선 화살표 연결선)"
description ShapeObject9 = "연결선(꺾인 양쪽 화살표 연결선)"
description ShapeObject10 = "연결선(꺾인 연결선)"
description ShapeObject11 = "연결선(꺾인 화살표 연결선)"
description PictureBulletDlg = "그림 글머리표 대화상자"
description PictureChange = "그림 바꾸기"
description PictureEffect1 = "그림 그레이 스케일"
description PictureEffect2 = "그림 흑백으로"
description PictureEffect3 = "그림 워터마크"
description PictureEffect4 = "그림 효과 없음"
description PictureEffect5 = "그림 밝기 증가"
description PictureEffect6 = "그림 밝기 감소"
description PictureEffect7 = "그림 명암 증가"
description PictureEffect8 = "그림 명암 감소"
description PictureInsertDialog = "No description"
description PictureLinkedToEmbedded = "연결된 그림을 모두 삽입그림으로"
description PictureNoBrightness = "그림 밝기 효과 없음"
description PictureNoContrast = "그림 대비 효과 없음"
description PictureNoGlow = "그림 네온 효과 없음"
description PictureNoReflection = "그림 반사 효과 없음"
description PictureNoShadow = "그림 그림자 효과 없음"
description PictureNoSofeEdge = "그림 부드러운 가장자리 효과 없음"
description PictureNoStyle = "그림 스타일 효과 없음"
description PictureSave = "그림 빼내기"
description PictureSaveAsAll = "삽입된 바이너리 그림 다른 형태로 저장."
description PictureSaveAsOption = "No description"
description PictureScissor = "그림 자르기"
description PictureToOriginal = "그림 원래 그림으로"
description ShapeCopyPaste = "모양 복사"
description ShapeObjAlignBottom = "아래로 정렬"
description ShapeObjAlignCenter = "가운데로 정렬"
description ShapeObjAlignHeight = "높이 맞춤"
description ShapeObjAlignHorzSpacing = "왼쪽/오른쪽 일정한 비율로 정렬"
description ShapeObjAlignLeft = "왼쪽으로 정렬"
description ShapeObjAlignMiddle = "중간 정렬"
description ShapeObjAlignRight = "오른쪽으로 정렬"
description ShapeObjAlignSize = "폭/높이 맞춤"
description ShapeObjAlignTop = "위로 정렬"
description ShapeObjAlignVertSpacing = "위/아래 일정한 비율로 정렬"
description ShapeObjAlignWidth = "폭 맞춤"
description ShapeObjAttachCaption = "캡션 넣기"
description ShapeObjAttachTextBox = "글 상자로 만들기"
description ShapeObjAttrDialog = "틀 속성 환경설정"
description ShapeObjBringForward = "앞으로"
description ShapeObjBringInFrontOfText = "글 앞으로"
description ShapeObjBringToFront = "맨 앞으로"
description ShapeObjComment = "개체 설명문 수정하기"
description ShapeObjCtrlSendBehindText = "글 뒤로"
description ShapeObjDetachCaption = "캡션 없애기"
description ShapeObjDetachTextBox = "글상자 속성 없애기"
description ShapeObjDialog = "환경설정"
description ShapeObjectCopy = "모양 복사"
description ShapeObjectPaste = "모양 붙여넣기"
description ShapeObjFillProperty = "고치기 대화상자중 fill tab"
description ShapeObjGroup = "틀 묶기"
description ShapeObjGuideLine = "개체 안내선"
description ShapeObjHorzFlip = "그리기 개체 좌우 뒤집기"
description ShapeObjHorzFlipOrgState = "그리기 개체 좌우 뒤집기 원상태로 되돌리기"
description ShapeObjInsertCaptionNum = "캡션 번호 넣기"
description ShapeObjLineProperty = "고치기 대화상자중 line tab"
description ShapeObjLineStyleOhter = "다른 선 종류"
description ShapeObjLineWidthOhter = "다른 선 굵기"
description ShapeObjLock = "개체 Lock"
description ShapeObjMoveDown = "키로 움직이기(아래)"
description ShapeObjMoveLeft = "키로 움직이기(왼쪽)"
description ShapeObjMoveRight = "키로 움직이기(오른쪽)"
description ShapeObjMoveUp = "키로 움직이기(위)"
description ShapeObjNextObject = "이후 개채로 이동(tab키)"
description ShapeObjNorm = "기본 도형 설정"
description ShapeObjNoShade = "채우기 색 음영 없음"
description ShapeObjNoShadow = "그림자 없음"
description ShapeObjPrevObject = "이전 개체로 이동(shift + tab키)"
description ShapeObjProtectSize = "그리기 개체 크기 고정"
description ShapeObjRandomAngleRotater = "자유각 회전"
description ShapeObjResizeDown = "키로 크기 조절(shift + 아래)"
description ShapeObjResizeLeft = "키로 크기 조절(shift + 왼쪽)"
description ShapeObjResizeRight = "키로 크기 조절(shift + 오른쪽)"
description ShapeObjResizeUp = "키로 크기 조절(shift + 위)"
description ShapeObjRightAngleRotater = "90도 회전"
description ShapeObjRotater = "자유각 회전(회전중심 고정)"
description ShapeObjSaveAsPicture = "그리기개체를 그림으로 저장하기"
description ShapeObjSelect = "틀 선택 도구"
description ShapeObjSendBack = "뒤로"
description ShapeObjSendToBack = "맨 뒤로"
description ShapeObjShadowEnlarge = "No description"
description ShapeObjShadowMoveDown = "No description"
description ShapeObjShadowMoveLeft = "No description"
description ShapeObjShadowMoveOrginal = "그리기 개체 그림자 위치 원점으로(offset제거)"
description ShapeObjShadowMoveRight = "No description"
description ShapeObjShadowMoveUp = "No description"
description ShapeObjShadowNarrow = "No description"
description ShapeObjShadowParellelLeft = "개체 그림자를 원본 개체와 동일한 크기로"
description ShapeObjShadowParellelLeft2 = "개체 그림자를 원본 개체와 동일한 크기로"
description ShapeObjShadowParellelRigh = "개체 그림자를 원본 개체와 동일한 크기로"
description ShapeObjShadowParellelRigh2 = "개체 그림자를 원본 개체와 동일한 크기로"
description ShapeObjShadowShearLeftBot = "개체 그림자를 왼쪽 뒷부분으로 눕혀서 생"
description ShapeObjShadowShearLeftTop = "No description"
description ShapeObjShadowShearRightBo = "개체 그림자를 오른쪽 뒷부분으로 눕혀서"
description ShapeObjShadowShearRightTo = "개체 그림자를 오른쪽 앞부분으로 눕혀서"
description ShapeObjShear = "그리기 개체 기울이기"
description ShapeObjShowGuideLine = "개체 안내선"
description ShapeObjShowGuideLineBase = "안내선 한/글 2024 부터 지원"
description ShapeObjTableSelCell = "테이블 선택상태에서 첫 번째 셀 선택하기"
description ShapeObjTextBoxEdit = "글상자 선택상태에서 편집모드로 들어가기"
description ShapeObjToggleTextBox = "도형 글 상자로 만들기- Toggle"
description ShapeObjUngroup = "틀 풀기"
description ShapeObjUnlockAll = "개체 Unlock All"
description ShapeObjVertFlip = "그리기 개체 상하 뒤집기"
description ShapeObjVertFlipOrgState = "그리기 개체 상하 뒤집기 원상태로 되돌리기"
description ShapeObjWrapSquare = "직사각형"
description ShapeObjWrapTopAndBottom = "자리 차지"

-- 총 119개 Shape 액션
