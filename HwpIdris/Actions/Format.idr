-- HWP Action Table - Format
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Format

import Data.String

-- Format 액션 타입
public export
data FormatAction
    = CharShape  -- 글자 모양
    | CharShapeBold  -- 단축키: Alt+L(글자 진하게)
    | CharShapeCenterline  -- 취소선(CenterLine)
    | CharShapeDialog  -- 글자 모양 대화상자(내부 구현용)
    | CharShapeDialogWithoutBord  -- 모양 대화상자(내부 구현용, [글자 테두리]
    | CharShapeEmboss  -- 양각
    | CharShapeEngrave  -- 음각
    | CharShapeHeight
    | CharShapeHeightDecrease  -- 크기 작게 ALT+SHIFT+R
    | CharShapeHeightIncrease  -- 크기 크게 ALT+SHIFT+E
    | CharShapeItalic  -- 이탤릭 ALT + SHIFT + I
    | CharShapeLang
    | CharShapeNextFaceName  -- 다음 글꼴 ALT+SHIFT+F
    | CharShapeNormal  -- 보통모양 ALT+SHIFT+C
    | CharShapeOutline  -- 외곽선
    | CharShapePrevFaceName  -- 이전 글꼴 ALT+SHIFT+G
    | CharShapeShadow  -- 그림자
    | CharShapeSpacing
    | CharShapeSpacingDecrease  -- 자간 좁게 ALT+SHIFT+N
    | CharShapeSpacingIncrease  -- 자간 넓게 ALT+SHIFT+W
    | CharShapeSubscript  -- 아래첨자 ALT+SHIFT+S
    | CharShapeSuperscript  -- 위첨자 ALT+SHIFT+P
    | CharShapeSuperSubscript  -- 첨자 : "위첨자 -> 아래첨자 -> 보통" 반복
    | CharShapeTextColorBlack  -- 글자색을 검정
    | CharShapeTextColorBlue  -- 글자색을 파랑
    | CharShapeTextColorBluish  -- 글자색을 청록
    | CharShapeTextColorGreen  -- 글자색을 초록
    | CharShapeTextColorRed  -- 글자색을 빨강
    | CharShapeTextColorViolet  -- 글자색을 자주
    | CharShapeTextColorWhite  -- 글자색을 흰색
    | CharShapeTextColorYellow  -- 글자색을 노랑
    | CharShapeTypeFace
    | CharShapeUnderline  -- 밑줄 ALT+SHIFT+U
    | CharShapeWidth
    | CharShapeWidthDecrease  -- 장평 좁게 ALT+SHIFT+J
    | CharShapeWidthIncrease  -- 장평 넓게 ALT+SHIFT+K
    | ParaShapeDialog  -- 문단 모양 대화상자(내부 구현용)
    | Style  -- 스타일 (글2005이하버전)
    | StyleAdd  -- 스타일 추가(글2007, 스타일 대화상자를 띄움)
    | StyleChangeToCurrentShape  -- 스타일 현재 모양으로 바꾸기
    | StyleClearCharStyle  -- 글자 스타일 해제
    | StyleDelete  -- 스타일 제거
    | StyleEdit  -- 스타일 편집
    | StyleEx  -- 스타일 (글2007)
    | StyleParaNumberBullet  -- 문단번호/글머리표
    | StyleShortcut1  -- 스타일 단축키<Ctrl + 1>
    | StyleShortcut10  -- 스타일 단축키<Ctrl + 0>
    | StyleShortcut2  -- 스타일 단축키<Ctrl + 2>
    | StyleShortcut3  -- 스타일 단축키<Ctrl + 3>
    | StyleShortcut4  -- 스타일 단축키<Ctrl + 4>
    | StyleShortcut5  -- 스타일 단축키<Ctrl + 5>
    | StyleShortcut6  -- 스타일 단축키<Ctrl + 6>
    | StyleShortcut7  -- 스타일 단축키<Ctrl + 7>
    | StyleShortcut8  -- 스타일 단축키<Ctrl + 8>
    | StyleShortcut9  -- 스타일 단축키<Ctrl + 9>
    | StyleTemplate  -- 스타일 마당

-- 액션 ID 문자열로 변환
public export
toString : FormatAction -> String
toString CharShape = "CharShape"
toString CharShapeBold = "CharShapeBold"
toString CharShapeCenterline = "CharShapeCenterline"
toString CharShapeDialog = "CharShapeDialog"
toString CharShapeDialogWithoutBord = "CharShapeDialogWithoutBord"
toString CharShapeEmboss = "CharShapeEmboss"
toString CharShapeEngrave = "CharShapeEngrave"
toString CharShapeHeight = "CharShapeHeight"
toString CharShapeHeightDecrease = "CharShapeHeightDecrease"
toString CharShapeHeightIncrease = "CharShapeHeightIncrease"
toString CharShapeItalic = "CharShapeItalic"
toString CharShapeLang = "CharShapeLang"
toString CharShapeNextFaceName = "CharShapeNextFaceName"
toString CharShapeNormal = "CharShapeNormal"
toString CharShapeOutline = "CharShapeOutline"
toString CharShapePrevFaceName = "CharShapePrevFaceName"
toString CharShapeShadow = "CharShapeShadow"
toString CharShapeSpacing = "CharShapeSpacing"
toString CharShapeSpacingDecrease = "CharShapeSpacingDecrease"
toString CharShapeSpacingIncrease = "CharShapeSpacingIncrease"
toString CharShapeSubscript = "CharShapeSubscript"
toString CharShapeSuperscript = "CharShapeSuperscript"
toString CharShapeSuperSubscript = "CharShapeSuperSubscript"
toString CharShapeTextColorBlack = "CharShapeTextColorBlack"
toString CharShapeTextColorBlue = "CharShapeTextColorBlue"
toString CharShapeTextColorBluish = "CharShapeTextColorBluish"
toString CharShapeTextColorGreen = "CharShapeTextColorGreen"
toString CharShapeTextColorRed = "CharShapeTextColorRed"
toString CharShapeTextColorViolet = "CharShapeTextColorViolet"
toString CharShapeTextColorWhite = "CharShapeTextColorWhite"
toString CharShapeTextColorYellow = "CharShapeTextColorYellow"
toString CharShapeTypeFace = "CharShapeTypeFace"
toString CharShapeUnderline = "CharShapeUnderline"
toString CharShapeWidth = "CharShapeWidth"
toString CharShapeWidthDecrease = "CharShapeWidthDecrease"
toString CharShapeWidthIncrease = "CharShapeWidthIncrease"
toString ParaShapeDialog = "ParaShapeDialog"
toString Style = "Style"
toString StyleAdd = "StyleAdd"
toString StyleChangeToCurrentShape = "StyleChangeToCurrentShape"
toString StyleClearCharStyle = "StyleClearCharStyle"
toString StyleDelete = "StyleDelete"
toString StyleEdit = "StyleEdit"
toString StyleEx = "StyleEx"
toString StyleParaNumberBullet = "StyleParaNumberBullet"
toString StyleShortcut1 = "StyleShortcut1"
toString StyleShortcut10 = "StyleShortcut10"
toString StyleShortcut2 = "StyleShortcut2"
toString StyleShortcut3 = "StyleShortcut3"
toString StyleShortcut4 = "StyleShortcut4"
toString StyleShortcut5 = "StyleShortcut5"
toString StyleShortcut6 = "StyleShortcut6"
toString StyleShortcut7 = "StyleShortcut7"
toString StyleShortcut8 = "StyleShortcut8"
toString StyleShortcut9 = "StyleShortcut9"
toString StyleTemplate = "StyleTemplate"

-- ParameterSet ID
public export
paramSetID : FormatAction -> Maybe String
paramSetID CharShape = Just "CharShape"
paramSetID CharShapeBold = Nothing
paramSetID CharShapeCenterline = Nothing
paramSetID CharShapeDialog = Just "CharShape"
paramSetID CharShapeDialogWithoutBord = Just "글자"
paramSetID CharShapeEmboss = Nothing
paramSetID CharShapeEngrave = Nothing
paramSetID CharShapeHeight = Nothing
paramSetID CharShapeHeightDecrease = Nothing
paramSetID CharShapeHeightIncrease = Nothing
paramSetID CharShapeItalic = Nothing
paramSetID CharShapeLang = Nothing
paramSetID CharShapeNextFaceName = Nothing
paramSetID CharShapeNormal = Nothing
paramSetID CharShapeOutline = Nothing
paramSetID CharShapePrevFaceName = Nothing
paramSetID CharShapeShadow = Nothing
paramSetID CharShapeSpacing = Nothing
paramSetID CharShapeSpacingDecrease = Nothing
paramSetID CharShapeSpacingIncrease = Nothing
paramSetID CharShapeSubscript = Nothing
paramSetID CharShapeSuperscript = Nothing
paramSetID CharShapeSuperSubscript = Nothing
paramSetID CharShapeTextColorBlack = Nothing
paramSetID CharShapeTextColorBlue = Nothing
paramSetID CharShapeTextColorBluish = Nothing
paramSetID CharShapeTextColorGreen = Nothing
paramSetID CharShapeTextColorRed = Nothing
paramSetID CharShapeTextColorViolet = Nothing
paramSetID CharShapeTextColorWhite = Nothing
paramSetID CharShapeTextColorYellow = Nothing
paramSetID CharShapeTypeFace = Nothing
paramSetID CharShapeUnderline = Nothing
paramSetID CharShapeWidth = Nothing
paramSetID CharShapeWidthDecrease = Nothing
paramSetID CharShapeWidthIncrease = Nothing
paramSetID ParaShapeDialog = Just "ParaShape"
paramSetID Style = Just "Style"
paramSetID StyleAdd = Just "Style"
paramSetID StyleChangeToCurrentShape = Just "StyleItem"
paramSetID StyleClearCharStyle = Nothing
paramSetID StyleDelete = Just "StyleDelete"
paramSetID StyleEdit = Just "Style"
paramSetID StyleEx = Just "Style"
paramSetID StyleParaNumberBullet = Just "ParaShape"
paramSetID StyleShortcut1 = Nothing
paramSetID StyleShortcut10 = Nothing
paramSetID StyleShortcut2 = Nothing
paramSetID StyleShortcut3 = Nothing
paramSetID StyleShortcut4 = Nothing
paramSetID StyleShortcut5 = Nothing
paramSetID StyleShortcut6 = Nothing
paramSetID StyleShortcut7 = Nothing
paramSetID StyleShortcut8 = Nothing
paramSetID StyleShortcut9 = Nothing
paramSetID StyleTemplate = Just "StyleTemplate"

-- 설명
public export
description : FormatAction -> String
description CharShape = "글자 모양"
description CharShapeBold = "단축키: Alt+L(글자 진하게)"
description CharShapeCenterline = "취소선(CenterLine)"
description CharShapeDialog = "글자 모양 대화상자(내부 구현용)"
description CharShapeDialogWithoutBord = "모양 대화상자(내부 구현용, [글자 테두리]"
description CharShapeEmboss = "양각"
description CharShapeEngrave = "음각"
description CharShapeHeight = "No description"
description CharShapeHeightDecrease = "크기 작게 ALT+SHIFT+R"
description CharShapeHeightIncrease = "크기 크게 ALT+SHIFT+E"
description CharShapeItalic = "이탤릭 ALT + SHIFT + I"
description CharShapeLang = "No description"
description CharShapeNextFaceName = "다음 글꼴 ALT+SHIFT+F"
description CharShapeNormal = "보통모양 ALT+SHIFT+C"
description CharShapeOutline = "외곽선"
description CharShapePrevFaceName = "이전 글꼴 ALT+SHIFT+G"
description CharShapeShadow = "그림자"
description CharShapeSpacing = "No description"
description CharShapeSpacingDecrease = "자간 좁게 ALT+SHIFT+N"
description CharShapeSpacingIncrease = "자간 넓게 ALT+SHIFT+W"
description CharShapeSubscript = "아래첨자 ALT+SHIFT+S"
description CharShapeSuperscript = "위첨자 ALT+SHIFT+P"
description CharShapeSuperSubscript = "첨자 : \"위첨자 -> 아래첨자 -> 보통\" 반복"
description CharShapeTextColorBlack = "글자색을 검정"
description CharShapeTextColorBlue = "글자색을 파랑"
description CharShapeTextColorBluish = "글자색을 청록"
description CharShapeTextColorGreen = "글자색을 초록"
description CharShapeTextColorRed = "글자색을 빨강"
description CharShapeTextColorViolet = "글자색을 자주"
description CharShapeTextColorWhite = "글자색을 흰색"
description CharShapeTextColorYellow = "글자색을 노랑"
description CharShapeTypeFace = "No description"
description CharShapeUnderline = "밑줄 ALT+SHIFT+U"
description CharShapeWidth = "No description"
description CharShapeWidthDecrease = "장평 좁게 ALT+SHIFT+J"
description CharShapeWidthIncrease = "장평 넓게 ALT+SHIFT+K"
description ParaShapeDialog = "문단 모양 대화상자(내부 구현용)"
description Style = "스타일 (글2005이하버전)"
description StyleAdd = "스타일 추가(글2007, 스타일 대화상자를 띄움)"
description StyleChangeToCurrentShape = "스타일 현재 모양으로 바꾸기"
description StyleClearCharStyle = "글자 스타일 해제"
description StyleDelete = "스타일 제거"
description StyleEdit = "스타일 편집"
description StyleEx = "스타일 (글2007)"
description StyleParaNumberBullet = "문단번호/글머리표"
description StyleShortcut1 = "스타일 단축키<Ctrl + 1>"
description StyleShortcut10 = "스타일 단축키<Ctrl + 0>"
description StyleShortcut2 = "스타일 단축키<Ctrl + 2>"
description StyleShortcut3 = "스타일 단축키<Ctrl + 3>"
description StyleShortcut4 = "스타일 단축키<Ctrl + 4>"
description StyleShortcut5 = "스타일 단축키<Ctrl + 5>"
description StyleShortcut6 = "스타일 단축키<Ctrl + 6>"
description StyleShortcut7 = "스타일 단축키<Ctrl + 7>"
description StyleShortcut8 = "스타일 단축키<Ctrl + 8>"
description StyleShortcut9 = "스타일 단축키<Ctrl + 9>"
description StyleTemplate = "스타일 마당"

-- 총 56개 Format 액션
