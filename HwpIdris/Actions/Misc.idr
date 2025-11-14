-- HWP Action Table - Misc
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.Misc

import Data.String

-- Misc 액션 타입
public export
data MiscAction
    = Action
    | ParameterSet
    | HwpCtrlRun
    | Action2  -- Action이거나, DocSummaryInfo와 같이 값을 읽어오기만 하는 Action일 경우 해담.
    | AddHanjaWord  -- 한자단어 등록
    | AllReplace  -- 모두 바꾸기
    | AQcommandMerge
    | ParameterSet2  -- 조작하여 사용함.
    | AutoChangeHangul  -- 낱자모 우선
    | AutoChangeRun  -- 동작
    | AutoSpell  -- - 맞춤법 ― 메뉴에서 맞춤법 도우미 동작 On/Off
    | AutoSpellSelect1  -- 16 -
    | Average  -- 블록 평균
    | BackwardFind  -- 뒤로 찾기
    | Bookmark  -- 책갈피
    | BulletDlg  -- 글머리표 대화상자
    | CaptionPosBottom  -- 캡션 위치-아래
    | CaptionPosLeftBottom  -- 캡션 위치-왼쪽 아래
    | CaptionPosLeftCenter  -- 캡션 위치–왼쪽 가운데
    | CaptionPosLeftTop  -- 캡션 위치–왼쪽 위
    | CaptionPosRightBottom  -- 캡션 위치–오른쪽 아래
    | CaptionPosRightCenter  -- 캡션 위치–오른쪽 가운데
    | CaptionPosRightTop  -- 캡션 위치–오른쪽 위
    | CaptionPosTop  -- 캡션 위치-위
    | CaptureDialog  -- 갈무리 끝
    | CaptureHandler  -- 갈무리 시작
    | ChangeImageFileExtension  -- 연결 그림 확장자 바꾸기
    | ChangeObject  -- 개체 변경하기
    | ChangeRome  -- + 로마자변환 - 입력받은 스트링 변환
    | ChangeRome2  -- String + 로마자 사용자 데이터 추가
    | ChangeRome3  -- + 로마자 사용자 데이터
    | ChangeRome4  -- 로마자변환
    | er  -- 제외)
    | list  -- Shift+Esc
    | Comment  -- 숨은 설명
    | CommentDelete  -- 숨은 설명 지우기
    | CommentModify  -- 숨은 설명 고치기
    | CompatibleDocument  -- 호환 문서
    | ComposeChars  -- 글자 겹침
    | ConvertBrailleSetting
    | ConvertCase  -- 대소문자 바꾸기
    | ConvertFullHalfWidth  -- 전각 반각 바꾸기
    | ConvertHiraGata  -- 일어 바꾸기
    | ConvertJianFan
    | Text  -- 상태에서만 동작
    | ConvertOptGugyulToHangul  -- 한글로 옵션 - 구결을 한글로
    | ConvertOptHanjaToHangul  -- 한글로 옵션 - 漢字를 한글로
    | ConvertToHangul  -- 옵션 - 漢字를 漢字(한글)로
    | ConvertToBraille  -- 점자 변환
    | ConvertToBrailleSelected
    | ConvertToHangul2  -- 한글로
    | Copy  -- 복사하기
    | CopyPage  -- 복사하기
    | Cut  -- 오려두기
    | DrawObjCancelOneStep  -- 다각형(곡선) 그리는 중 이전 선 지우기
    | DrawObjCreatorArc  -- 호 그리기
    | DrawObjCreatorCanvas  -- 캔버스 그리기
    | DrawObjCreatorCurve  -- 곡선 그리기
    | DrawObjCreatorEllipse  -- 원 그리기
    | DrawObjCreatorFreeDrawing  -- 펜
    | DrawObjCreatorHorzTextBox  -- 가로 글상자 만들기
    | DrawObjCreatorLine  -- 선 그리기
    | DrawObjCreatorMultiArc  -- 반복해서 호 그리기
    | DrawObjCreatorMultiCanvas  -- 반복해서 캔버스 그리기
    | DrawObjCreatorMultiCurve  -- 반복해서 곡선 그리기
    | DrawObjCreatorMultiEllipse  -- 반복해서 원 그리기
    | DrawObjCreatorMultiLine  -- 반복해서 선 그리기
    | DrawObjCreatorMultiPolygon  -- 반복해서 다각형 그리기
    | DrawObjCreatorMultiTextBox  -- 반복해서 글상자 그리기
    | DrawObjCreatorObject  -- 그리기 개체
    | DrawObjCreatorPolygon  -- 다각형 그리기
    | DrawObjCreatorRectangle  -- 사각형 그리기
    | DrawObjCreatorTextBox  -- 글상자
    | DrawObjCreatorVertTextBox  -- 세로 글상자 만들기
    | DrawObjEditDetail  -- 그리기 개체 편집
    | DrawObjOpenClosePolygon  -- 다각형 열기/닫기
    | DrawObjTemplateLoad  -- 그리기 마당에서 불러오기
    | DrawObjTemplateSave  -- 그리기 마당에 등록
    | DrawShapeObjShadow
    | DropCap  -- 문단 첫 글자 장식
    | DutmalChars  -- 덧말 넣기
    | EditFieldMemo  -- 메모 내용 편집
    | EditParaDown  -- 옮기기
    | EditParaUp  -- 옮기기
    | EndnoteEndOfDocument  -- 미주–문서의 끝
    | EndnoteEndOfSection  -- 미주–구역의 끝
    | EndnoteToFootnote  -- 미주를 각주로
    | EquationCreate  -- 수식 만들기
    | EquationModify  -- 수식 편집하기
    | EquationPropertyDialog  -- 수식 개체 속성 고치기
    | Erase  -- 지우기
    | ExchangeFootnoteEndnote  -- 변환
    | ExecReplace  -- 바꾸기(실행)
    | ExtractImagesFromDoc  -- 삽입 그림을 연결 그림으로 추출
    | FillColorShadeDec  -- 면 색 음영 비율 감소
    | FillColorShadeInc  -- 면 색 음영 비율 증가
    | FootnoteBeneathText  -- 각주–본문 아래
    | FootnoteBottomOfEachColumn  -- 다단 각주–각 단 아래
    | SecDef  -- 각주–전 단
    | SecDef2  -- 각주–오른쪽 단 아래
    | FootnoteNoBeneathText  -- 각주–꼬리말 바로 위
    | FootnoteOption  -- 각주/미주 모양
    | FootnoteToEndnote  -- 각주를 미주로
    | FormDesignMode  -- 디자인 모드 변경
    | FormObjCreatorCheckButton  -- Check버튼 넣기
    | FormObjCreatorComboBox  -- ComboBox넣기
    | FormObjCreatorEdit  -- Edit넣기
    | FormObjCreatorListBox  -- ListBox넣기
    | FormObjCreatorPushButton  -- Push버튼 넣기
    | FormObjCreatorRadioButton  -- Radio버튼 넣기
    | FormObjCreatorScrollBar  -- ScrollBar넣기
    | ForwardFind  -- 앞으로 찾기
    | FrameStatusBar  -- 상태바 보이기/숨기기
    | FtpDownload  -- FTP서버에서 파일 다운 받아 문서 오픈하기
    | FtpUpload  -- 웹 서버로 올리기
    | GetDefaultBullet  -- 글머리표 디폴트 값
    | GetDefaultParaNumber  -- 문단번호 디폴트 값
    | GetDocFilters  -- 유틸리티 액션
    | GetRome  -- ChangeRome* Run()으로 실행시키면 프로그램이 죽는다. 반드
    | GetSectionApplyString  -- 유틸리티 액션
    | GetSectionApplyTo  -- 유틸리티 액션
    | GetVersionItemInfo
    | ParameterSet3  -- Item의 Index값을 반
    | HanThDIC  -- 유의어 사전
    | HeaderFooter  -- 머리말/꼬리말
    | HeaderFooterDelete  -- 머리말 지우기
    | HeaderFooterInsField  -- 코드 넣기
    | HeaderFooterModify  -- 머리말/꼬리말 고치기
    | HeaderFooterToNext  -- 이후 머리말
    | HeaderFooterToPrev  -- 이전 머리말
    | HiddenCredits  -- 인터넷 정보
    | HideTitle
    | Him  -- - 입력기 언어별 환경설정
    | HimKbdChange  -- 바꾸기
    | HwpCtrlEquationCreate97  -- 수식 만들기(글97버전)
    | HwpCtrlFileNew  -- 새문서
    | HwpCtrlFileOpen  -- 파일 열기
    | HwpCtrlFileSave  -- 파일 저장
    | HwpCtrlFileSaveAs  -- 다른 이름으로 저장
    | HwpCtrlFileSaveAsAutoBlock  -- 만약 텍스트가 선택되지 않은 경우에는 다른 이름
    | HwpCtrlFileSaveAutoBlock  -- 만약 텍스트가 선택되지 않은 경우에는 저장하기가
    | HwpCtrlFindDlg  -- 찾기 대화상자
    | HwpCtrlReplaceDlg  -- 바꾸기 대화상자
    | HwpDic  -- 한컴 사전
    | Hyperlink
    | HyperlinkBackward  -- 하이퍼링크 뒤로
    | HyperlinkForward  -- 하이퍼링크 앞으로
    | HyperlinkJump  -- 하이퍼링크 이동
    | Idiom  -- 상용구
    | IndexMark  -- 찾아보기 표시
    | IndexMarkModify  -- 찾아보기 표시 고치기
    | InputCodeChange
    | InputCodeTable  -- 문자표
    | InputDateStyle
    | InputHanja  -- 한자 변환
    | InputHanjaBusu  -- 부수로 입력
    | InputHanjaMean  -- 새김으로 입력
    | InputPersonsNameHanja  -- 인명한자 변환
    | oth  -- 연결선)
    | oArrow  -- 연결선)
    | neWay  -- 연결선)
    | ightBoth
    | ightOneWay
    | keBoth
    | keOneWay
    | RevisionDef  -- 부호 넣기 : 줄 서로 바꿈 나눔표(내부용)
    | RevisionDef2  -- 부호 넣기 : 자리바꿈 나눔표(내부용)
    | Jajun  -- 한자 자전
    | LabelAdd  -- 라벨 새 쪽 추가하기
    | LabelTemplate  -- 라벨 문서 만들기
    | LinkDocument  -- 문서 연결([파일-문서 연결]메뉴와 동일)
    | LinkTextBox  -- 글상자가 선택되지 않았거나, 캐럿이 글상자 내부
    | MacroDefine  -- 매크로 정의
    | MacroPause  -- 매크로 실행 일시 중지 (정의/실행)
    | MacroPlay1  -- 매크로 1
    | MacroPlay10  -- 매크로 10
    | MacroPlay11  -- 매크로 11
    | MacroPlay2  -- 매크로 2
    | MacroPlay3  -- 매크로 3
    | MacroPlay4  -- 매크로 4
    | MacroPlay5  -- 매크로 5
    | MacroPlay6  -- 매크로 6
    | MacroPlay7  -- 매크로 7
    | MacroPlay8  -- 매크로 8
    | MacroPlay9  -- 매크로 9
    | MacroRepeat  -- 매크로 실행
    | MacroRepeatDlg  -- 매크로 실행
    | MacroStop  -- 매크로 실행 중지 (정의/실행)
    | MakeAllVersionDiffs
    | MakeContents  -- 차례 만들기
    | MakeIndex  -- 찾아보기 만들기
    | ManualChangeHangul  -- 현재 커서위치 또는 문단나누기 이전에 입력된 내
    | ManuScriptTemplate  -- 원고지 쓰기
    | MarkPenDelete  -- 삭제
    | MarkPenNext  -- 이동(다음)
    | MarkPenPrev  -- 이동(이전)
    | MarkPenShape  -- Run() 실행불가, 반드시 MarkpenShape
    | ParameterSet4  -- 아이템 값을 설정하고
    | MarkPrivateInfo  -- 개인 정보 즉시 감추기(텍스트 블록 상태,암호화)
    | MarkTitle  -- 차례 코드가 삽입되어 나중에 차례 만들기에서 사
    | MasterPage  -- 바탕쪽
    | MasterPageDelete  -- 바탕쪽 삭제바탕쪽 편집모드일 경우에만 동작한다.
    | MasterPageDuplicate  -- 바탕쪽 편집상태가 활성화되어 있으며 [구역 마지
    | MasterPageEntry
    | MasterPageExcept  -- 첫 쪽 제외
    | MasterPageFront
    | MasterPagePrevSection  -- 앞 구역 바탕쪽 사용
    | MasterPageToNext  -- 이후 바탕쪽
    | MasterPageToPrevious  -- 이전 바탕쪽
    | MasterPageTypeDlg  -- 바탕쪽 종류 다이얼로그 띄움
    | MemoShape  -- 메모 모양([입력-메모-메모 모양]메뉴와 동일함)
    | MemoToNext  -- 다음 메모
    | MemoToPrev  -- 이전 메모
    | MessageBox  -- 메시지 박스
    | ModifyBookmark  -- 책갈피 고치기
    | ModifyComposeChars  -- 고치기 - 글자 겹침
    | ModifyCrossReference  -- 상호 참조 고치기
    | ModifyCtrl  -- 고치기 : 컨트롤
    | ModifyDutmal  -- 고치기 - 덧말
    | ModifyFieldClickhere  -- 누름틀 정보 고치기
    | ModifyFieldDate  -- 날짜 필드 고치기
    | ModifyFieldDateTime
    | ModifyFieldPath  -- 문서 경로 필드 고치기
    | ModifyFieldSummary  -- 문서 요약 필드 고치기
    | ModifyFieldUserInfo  -- 개인 정보 필드 고치기
    | ModifyFillProperty
    | SelectCtrlReverse  -- 개체를 탐색
    | ModifyHyperlink  -- 하이퍼링크 고치기
    | ModifyLineProperty
    | SelectCtrlReverse2  -- 개체를 탐색
    | ModifyRevision  -- 가지로 정확히 교정부호(조판 부호)의 앞에 캐럿
    | ModifyRevision2  -- 정확히 교정부호
    | ModifyRevisionHyperlink
    | Run  -- 않는다.
    | ModifySecTextHorz  -- 가로 쓰기
    | ModifySecTextVert  -- 세로 쓰기(영문 눕힘)
    | ModifySecTextVertAll  -- 세로 쓰기(영문 세움)
    | ModifySection  -- 구역
    | ModifyShapeObject  -- 고치기 - 개체 속성
    | LIST_BEGINEND  -- 현재 서브 리스트
    | LIST_BEGINEND2  -- 현재 서브 리스트
    | MPBreakNewSection  -- 새 구역 만들기–바탕쪽 편집 상태에서
    | MPCopyFromOtherSection
    | MPSectionToNext  -- 이후 구역으로
    | MPSectionToPrevious  -- 이전 구역으로
    | MPShowMarginBorder  -- 여백 보기–바탕쪽 편집 상태에서
    | MultiColumn  -- 다단
    | NewNumber  -- 새 번호로 시작
    | NewNumberModify  -- 새 번호 고치기
    | NextTextBoxLinked  -- 연결된 글상자의 다음 글상자로 이동
    | NoneTextArtShadow  -- 글맵시 그림자 없음
    | NoteDelete  -- 주석 지우기
    | NoteModify  -- 주석 고치기
    | NoteNoSuperscript  -- 주석 번호 보통(윗 첨자 사용 안함)
    | NoteNumProperty  -- 주석 번호 속성
    | NoteSuperscript  -- 주석 번호 작게(윗 첨자)
    | NoteToNext  -- 주석 다음으로 이동
    | NoteToPrev  -- 주석 앞으로 이동
    | OleCreateNew  -- 개체 삽입
    | OutlineNumber  -- 개요번호
    | ParagraphShape  -- 문단 모양
    | ParagraphShapeAlignCenter  -- 가운데 정렬
    | ParagraphShapeAlignJustify  -- 양쪽 정렬
    | ParagraphShapeAlignLeft  -- 왼쪽 정렬
    | ParagraphShapeAlignRight  -- 오른쪽 정렬
    | ParagraphShapeProtect  -- 문단 보호
    | ParagraphShapeSingleRow  -- 줄로 입력
    | ParagraphShapeWithNext  -- 다음 문단과 함께
    | ParaNumberBullet  -- 문단번호/글머리표 한 수준 위로
    | ParaNumberBulletLevelDown  -- 문단번호/글머리표 한 수준 아래로
    | ParaNumberBulletLevelUp  -- 문단번호/글머리표 한 수준 위로
    | ParaNumberDlg  -- 문단번호 대화상자
    | Paste  -- 붙이기
    | PastePage  -- 쪽 붙여넣기
    | PasteSpecial  -- 골라 붙이기
    | Preference  -- 환경 설정
    | Presentation  -- 프레젠테이션
    | PresentationDelete  -- 프레젠테이션 삭제
    | PresentationRange  -- 프레젠테이션 범위 설정.
    | PresentationSetup  -- 프레젠테이션 설정
    | PrevTextBoxLinked  -- 현재 글상자가 선택되거나, 글상자 내부에 캐럿이
    | Print  -- 인쇄
    | PrintSetup  -- 인쇄옵션 - 워터 마크
    | PrintToImage  -- 그림으로 저장하기
    | PrintToPDF  -- PDF인쇄
    | PrivateInfoChangePassword  -- 개인 정보 보안 암호 변경
    | PrivateInfoSetPassword  -- 개인 정보 보안 암호 설정
    | PutBullet  -- 글머리표 달기
    | PutNewParaNumber  -- 문단번호 새 번호 시작하기
    | PutOutlineNumber  -- 개요번호 달기
    | PutParaNumber  -- 문단번호 달기
    | QuickCommand  -- - 입력 자동 명령 동작
    | QuickCorrect  -- QCorrect 빠른 교정 ―내용 편집
    | QuickCorrect2  -- - 빠른 교정 ―내용 편집
    | QuickCorrect3  -- - 빠른 교정 ― 메뉴에서 효과음 On/Off
    | QuickCorrect4  -- 빠른 교정 (실질적인 동작 Action)
    | QuickMarkInsert0  -- 9 - 쉬운 책갈피 - 삽입
    | QuickMarkMove0  -- 9 - 쉬운 책갈피 - 이동
    | RecalcPageCount  -- 현재 페이지의 쪽 번호 재계산
    | RecentCode  -- 최근에 사용한 문자표가 없을 경우에는 문자표 대
    | Redo  -- 다시 실행
    | RepeatFind  -- 다시 찾기
    | ReplyMemo  -- 메모 회신 한/글 2022 부터 지원
    | ReturnKeyInField
    | ReturnPrevPos  -- 직전위치로 돌아가기
    | ReverseFind  -- 거꾸로 찾기
    | ScanHFTFonts  -- 글꼴 검색
    | ScrMacroDefine  -- 매크로 정의 대화상자를 띄우고, 설정이 끝나면 매
    | ScrMacroPause  -- 매크로 기록 일시정지/재시작
    | ScrMacroPlay1  -- 11 - #번 매크로 실행(Alt+Shift+#)
    | ScrMacroRepeatDlg
    | ScrMacroSecurityDlg
    | ScrMacroStop  -- 매크로 기록 중지
    | SendBrowserText  -- 브라우저로 보내기
    | SendMailAttach  -- 편지 보내기 - 첨부파일로
    | SendMailText  -- 편지 보내기 - 본문으로
    | SetLineNumbers  -- 줄 번호 넣기
    | Bottom  -- 생성한다.
    | Top  -- 생성한다.
    | tBottom  -- 생성한다.
    | tTop  -- 생성한다.
    | tom
    | ttom
    | ShowLineNumbers  -- 줄 번호 넣기
    | Soft  -- - 보기
    | Sort  -- 소트
    | SpellingCheck  -- 맞춤법
    | SplitMemoOpen  -- 메모창 열기
    | Sum  -- 블록 합계
    | SuppressLineNumbers  -- 번호 넣기
    | para  -- + cell valign :테이블의 셀 내에
    | para2  -- + cell valign :테이블의 셀 내에
    | para3  -- + cell valign :테이블의 셀 내에
    | para4  -- + cell valign :테이블의 셀 내에
    | para5  -- + cell valign :테이블의 셀 내에
    | para6  -- + cell valign :테이블의 셀 내에
    | para7  -- + cell valign :테이블의 셀 내에
    | para8  -- + cell valign :테이블의 셀 내에
    | para9  -- + cell valign :테이블의 셀 내에
    | TextArtCreate  -- 글맵시
    | TextArtModify  -- 글맵시 고치기
    | TextArtShadow  -- 글맵시 그림자 넣기/빼기
    | TextArtShadowMobeToDown  -- 글맵시 그림자 위치 이동-아래로
    | TextArtShadowMobeToLeft  -- 글맵시 그림자 위치 이동-왼쪽으로
    | TextArtShadowMobeToRight  -- 글맵시 그림자 위치 이동-오른쪽으로
    | TextArtShadowMoveToUp  -- 글맵시 그림자 위치 이동-위로
    | TextBoxAlignCenterBottom  -- 글상자 정렬
    | TextBoxAlignCenterCenter  -- 글상자 정렬
    | TextBoxAlignCenterTop  -- 글상자 정렬
    | TextBoxAlignLeftBottom  -- 글상자 정렬
    | TextBoxAlignLeftCenter  -- 글상자 정렬
    | TextBoxAlignLeftTop  -- 글상자 정렬
    | TextBoxAlignRightBottom  -- 글상자 정렬
    | TextBoxAlignRightCenter  -- 글상자 정렬
    | TextBoxAlignRightTop  -- 글상자 정렬
    | TextBoxTextHorz  -- 글상자 문자 방향–가로 쓰기
    | TextBoxTextVert  -- 글상자 문자 방향–세로 쓰기–영문 눕힘
    | TextBoxTextVertAll  -- 글상자 문자 방향–세로 쓰기–영문 세움
    | TextBoxToggleDirection  -- 글상자 문자 방향–세로/가로 토글
    | TextBoxVAlignBottom  -- 글상자 세로 정렬-아래
    | TextBoxVAlignCenter  -- 글상자 세로 정렬-가운데
    | TextBoxVAlignTop  -- 글상자 세로 정렬-위
    | ToggleOverwrite  -- Toggle Overwrite
    | TrackChangeApply  -- 변경추적:변경내용 적용
    | TrackChangeApplyAll  -- 변경추적:문서에서 변경내용 모두 적용
    | TrackChangeApplyNext  -- 변경추적:적용 후 다음으로 이동
    | TrackChangeApplyPrev  -- 변경추적:적용 후 이전으로 이동
    | TrackChangeApplyViewAll  -- 변경추적:표시된 변경내용 모두 적용
    | TrackChangeAuthor  -- 변경추적:사용자 이름 변경
    | TrackChangeCancel  -- 변경추적:변경내용 취소
    | TrackChangeCancelAll  -- 변경추적:문서에서 변경내용 모두 취소
    | TrackChangeCancelNext  -- 변경추적:취소 후 다음으로 이동
    | TrackChangeCancelPrev  -- 변경추적:취소 후 이전으로 이동
    | TrackChangeCancelViewAll  -- 변경추적:표시된 변경내용 모두 취소
    | TrackChangeNext  -- 변경추적:다음 변경내용
    | TrackChangeOption  -- 변경추적:변경 내용 추적 설정
    | TrackChangePrev  -- 변경추적:이전 변경내용
    | TrackChangeProtection  -- 변경추적:변경추적 보호
    | Undo  -- 되살리기
    | UnlinkTextBox  -- 글상자 연결 끊기
    | UserAutoFill
    | VersionDelete  -- 버전정보 지우기
    | VersionDeleteAll  -- 모든 버전정보 지우기
    | VersionInfo  -- 버전 정보
    | VersionSave  -- 버전 저장하기
    | VerticalText  -- 세로쓰기
    | ViewGridOption  -- 격자
    | ViewIdiom  -- 상용구 보기
    | ViewOptionColor  -- 보기 (회색조 보기 되돌리기 액션)
    | ViewOptionColorCustom  -- 보기
    | ViewOptionCtrlMark  -- 조판 부호
    | ViewOptionGray  -- 보기
    | ViewOptionGuideLine  -- 안내선
    | ViewOptionMemo
    | ViewOptionMemoGuideline
    | ViewOptionPaper  -- 쪽 윤곽 보기
    | ViewOptionParaMark  -- 문단 부호
    | ViewOptionPicture  -- 그림 보이기/숨기기([보기-그림]메뉴와 동일)
    | ViewOptionPronounce  -- 한자/일어 발음 표시 (Toggle)
    | ViewOptionPronounceSetting  -- 한자/일어 발음 표시 설정
    | ViewOptionRevision
    | ViewOptionTrackChange  -- 변경추적 보기
    | ViewOptionTrackChangeFinal  -- 변경추적 보기:최종본 보기
    | ViewOptionTrackChangeShape  -- 변경추적 보기:서식
    | ViewOptionTrackChnageInfo  -- 변경추적 보기:변경 내용 보기
    | ViewShowGrid  -- 격자 보이기
    | ViewZoom  -- 화면 확대(Ribbon)
    | ViewZoomFitPage  -- 화면 확대: 페이지에 맞춤
    | ViewZoomFitWidth  -- 화면 확대: 폭에 맞춤
    | ViewZoomLock  -- 잠금
    | ViewZoomNormal  -- 화면 확대: 정상
    | VoiceCommand  -- - 음성 명령 설정
    | VoiceCommand2  -- - 음성 명령 레코딩 시작
    | VoiceCommand3  -- - 음성 명령 레코딩 중지
    | VoiceCommand4  -- + 음성 명령창 보이기
    | VoiceCommand5  -- 음성 명령 동작
    | function
    | var  -- = pHwpCtrl.CreateAction("FileSetSecurity");
    | var2  -- = null;
    | ifAction
    | dset  -- dact.CreateSet();
    | ifAction2  -- && dset) {
    | dsetSetItemPassword
    | dsetSetItemNoPrint
    | dsetSetItemNoCopy
    | ifAction3  -- {
    | var3  -- = "배포용 문서 만들기 실패";
    | ifAction4  -- <= 6) {
    | msg  -- "\n암호가 너무 짧습니다.";
    | var4  -- = "배포용 문서 만들기 실패";
    | ifAction5  -- & 0x10) // 배포용 문서는 0x10 flag 를 포함한다.
    | msg2  -- "\n이미 배포용 문서로 지정된 상태입니다.\n암호를 변경하기 위해서는 먼저 일반 문서로 변경하십시오."
    | elseAction  -- (pHwpCtrl.EditMode == 0)
    | msg3  -- "\n읽기 전용 문서입니다."
    | function2
    | pHwpCtrlMovePos3  -- 커서를 문서의 맨 뒤로 이동
    | var5  -- = pHwpCtrl.CreateAction("BackwardFind"); // 뒤에서부터 찾는다.
    | var6  -- = act.CreateSet();
    | setSetItemIgnoreFindString
    | var7  -- = set.CreateItemSet("FindCharShape", "CharShape");
    | subsetSetItemUnderlineType
    | var8
    | var9  -- para, pos;
    | set  -- pHwpCtrl.GetPosBySet();
    | list2  -- set.Item("List");
    | para10  -- set.Item("Para");
    | pos  -- set.Item("Pos");
    | function3
    | var10  -- = pHwpCtrl.CreateAction("CharShape");
    | var11  -- = dAct.CreateSet();
    | dSetSetItemTextColor  -- // 글자 색을 파란색으로
    | function4
    | pHwpCtrlMovePos2  -- 페이지 맨 처음으로
    | var12  -- = true;
    | while  -- {
    | OnTestApi1  -- 현재줄의 맨 처음 단어 색깔 변경
    | con  -- pHwpCtrl.MovePos(20); // 한줄 아래로 (예전 API 매뉴얼에는 21로 되어 있으나 잘못된 값임.

-- 액션 ID 문자열로 변환
public export
toString : MiscAction -> String
toString Action = "Action"
toString ParameterSet = "ParameterSet"
toString HwpCtrlRun = "HwpCtrl.Run"
toString Action2 = "Action에"
toString AddHanjaWord = "AddHanjaWord"
toString AllReplace = "AllReplace"
toString AQcommandMerge = "AQcommandMerge"
toString ParameterSet2 = "ParameterSet을"
toString AutoChangeHangul = "AutoChangeHangul"
toString AutoChangeRun = "AutoChangeRun"
toString AutoSpell = "AutoSpell"
toString AutoSpellSelect1 = "AutoSpellSelect1"
toString Average = "Average"
toString BackwardFind = "BackwardFind"
toString Bookmark = "Bookmark"
toString BulletDlg = "BulletDlg"
toString CaptionPosBottom = "CaptionPosBottom"
toString CaptionPosLeftBottom = "CaptionPosLeftBottom"
toString CaptionPosLeftCenter = "CaptionPosLeftCenter"
toString CaptionPosLeftTop = "CaptionPosLeftTop"
toString CaptionPosRightBottom = "CaptionPosRightBottom"
toString CaptionPosRightCenter = "CaptionPosRightCenter"
toString CaptionPosRightTop = "CaptionPosRightTop"
toString CaptionPosTop = "CaptionPosTop"
toString CaptureDialog = "CaptureDialog"
toString CaptureHandler = "CaptureHandler"
toString ChangeImageFileExtension = "ChangeImageFileExtension"
toString ChangeObject = "ChangeObject"
toString ChangeRome = "ChangeRome"
toString ChangeRome2 = "ChangeRome"
toString ChangeRome3 = "ChangeRome"
toString ChangeRome4 = "ChangeRome"
toString er = "er"
toString list = "list로"
toString Comment = "Comment"
toString CommentDelete = "CommentDelete"
toString CommentModify = "CommentModify"
toString CompatibleDocument = "CompatibleDocument"
toString ComposeChars = "ComposeChars"
toString ConvertBrailleSetting = "ConvertBrailleSetting"
toString ConvertCase = "ConvertCase"
toString ConvertFullHalfWidth = "ConvertFullHalfWidth"
toString ConvertHiraGata = "ConvertHiraGata"
toString ConvertJianFan = "ConvertJianFan"
toString Text = "Text가"
toString ConvertOptGugyulToHangul = "ConvertOptGugyulToHangul"
toString ConvertOptHanjaToHangul = "ConvertOptHanjaToHangul"
toString ConvertToHangul = "ConvertToHangul"
toString ConvertToBraille = "ConvertToBraille"
toString ConvertToBrailleSelected = "ConvertToBrailleSelected"
toString ConvertToHangul2 = "ConvertToHangul"
toString Copy = "Copy"
toString CopyPage = "CopyPage"
toString Cut = "Cut"
toString DrawObjCancelOneStep = "DrawObjCancelOneStep"
toString DrawObjCreatorArc = "DrawObjCreatorArc"
toString DrawObjCreatorCanvas = "DrawObjCreatorCanvas"
toString DrawObjCreatorCurve = "DrawObjCreatorCurve"
toString DrawObjCreatorEllipse = "DrawObjCreatorEllipse"
toString DrawObjCreatorFreeDrawing = "DrawObjCreatorFreeDrawing"
toString DrawObjCreatorHorzTextBox = "DrawObjCreatorHorzTextBox"
toString DrawObjCreatorLine = "DrawObjCreatorLine"
toString DrawObjCreatorMultiArc = "DrawObjCreatorMultiArc"
toString DrawObjCreatorMultiCanvas = "DrawObjCreatorMultiCanvas"
toString DrawObjCreatorMultiCurve = "DrawObjCreatorMultiCurve"
toString DrawObjCreatorMultiEllipse = "DrawObjCreatorMultiEllipse"
toString DrawObjCreatorMultiLine = "DrawObjCreatorMultiLine"
toString DrawObjCreatorMultiPolygon = "DrawObjCreatorMultiPolygon"
toString DrawObjCreatorMultiTextBox = "DrawObjCreatorMultiTextBox"
toString DrawObjCreatorObject = "DrawObjCreatorObject"
toString DrawObjCreatorPolygon = "DrawObjCreatorPolygon"
toString DrawObjCreatorRectangle = "DrawObjCreatorRectangle"
toString DrawObjCreatorTextBox = "DrawObjCreatorTextBox"
toString DrawObjCreatorVertTextBox = "DrawObjCreatorVertTextBox"
toString DrawObjEditDetail = "DrawObjEditDetail"
toString DrawObjOpenClosePolygon = "DrawObjOpenClosePolygon"
toString DrawObjTemplateLoad = "DrawObjTemplateLoad"
toString DrawObjTemplateSave = "DrawObjTemplateSave"
toString DrawShapeObjShadow = "DrawShapeObjShadow"
toString DropCap = "DropCap"
toString DutmalChars = "DutmalChars"
toString EditFieldMemo = "EditFieldMemo"
toString EditParaDown = "EditParaDown"
toString EditParaUp = "EditParaUp"
toString EndnoteEndOfDocument = "EndnoteEndOfDocument"
toString EndnoteEndOfSection = "EndnoteEndOfSection"
toString EndnoteToFootnote = "EndnoteToFootnote"
toString EquationCreate = "EquationCreate"
toString EquationModify = "EquationModify"
toString EquationPropertyDialog = "EquationPropertyDialog"
toString Erase = "Erase"
toString ExchangeFootnoteEndnote = "ExchangeFootnoteEndnote"
toString ExecReplace = "ExecReplace"
toString ExtractImagesFromDoc = "ExtractImagesFromDoc"
toString FillColorShadeDec = "FillColorShadeDec"
toString FillColorShadeInc = "FillColorShadeInc"
toString FootnoteBeneathText = "FootnoteBeneathText"
toString FootnoteBottomOfEachColumn = "FootnoteBottomOfEachColumn"
toString SecDef = "SecDef"
toString SecDef2 = "SecDef"
toString FootnoteNoBeneathText = "FootnoteNoBeneathText"
toString FootnoteOption = "FootnoteOption"
toString FootnoteToEndnote = "FootnoteToEndnote"
toString FormDesignMode = "FormDesignMode"
toString FormObjCreatorCheckButton = "FormObjCreatorCheckButton"
toString FormObjCreatorComboBox = "FormObjCreatorComboBox"
toString FormObjCreatorEdit = "FormObjCreatorEdit"
toString FormObjCreatorListBox = "FormObjCreatorListBox"
toString FormObjCreatorPushButton = "FormObjCreatorPushButton"
toString FormObjCreatorRadioButton = "FormObjCreatorRadioButton"
toString FormObjCreatorScrollBar = "FormObjCreatorScrollBar"
toString ForwardFind = "ForwardFind"
toString FrameStatusBar = "FrameStatusBar"
toString FtpDownload = "FtpDownload"
toString FtpUpload = "FtpUpload"
toString GetDefaultBullet = "GetDefaultBullet"
toString GetDefaultParaNumber = "GetDefaultParaNumber"
toString GetDocFilters = "GetDocFilters"
toString GetRome = "GetRome"
toString GetSectionApplyString = "GetSectionApplyString"
toString GetSectionApplyTo = "GetSectionApplyTo"
toString GetVersionItemInfo = "GetVersionItemInfo"
toString ParameterSet3 = "ParameterSet에"
toString HanThDIC = "HanThDIC"
toString HeaderFooter = "HeaderFooter"
toString HeaderFooterDelete = "HeaderFooterDelete"
toString HeaderFooterInsField = "HeaderFooterInsField"
toString HeaderFooterModify = "HeaderFooterModify"
toString HeaderFooterToNext = "HeaderFooterToNext"
toString HeaderFooterToPrev = "HeaderFooterToPrev"
toString HiddenCredits = "HiddenCredits"
toString HideTitle = "HideTitle"
toString Him = "Him"
toString HimKbdChange = "HimKbdChange"
toString HwpCtrlEquationCreate97 = "HwpCtrlEquationCreate97"
toString HwpCtrlFileNew = "HwpCtrlFileNew"
toString HwpCtrlFileOpen = "HwpCtrlFileOpen"
toString HwpCtrlFileSave = "HwpCtrlFileSave"
toString HwpCtrlFileSaveAs = "HwpCtrlFileSaveAs"
toString HwpCtrlFileSaveAsAutoBlock = "HwpCtrlFileSaveAsAutoBlock"
toString HwpCtrlFileSaveAutoBlock = "HwpCtrlFileSaveAutoBlock"
toString HwpCtrlFindDlg = "HwpCtrlFindDlg"
toString HwpCtrlReplaceDlg = "HwpCtrlReplaceDlg"
toString HwpDic = "HwpDic"
toString Hyperlink = "Hyperlink"
toString HyperlinkBackward = "HyperlinkBackward"
toString HyperlinkForward = "HyperlinkForward"
toString HyperlinkJump = "HyperlinkJump"
toString Idiom = "Idiom"
toString IndexMark = "IndexMark"
toString IndexMarkModify = "IndexMarkModify"
toString InputCodeChange = "InputCodeChange"
toString InputCodeTable = "InputCodeTable"
toString InputDateStyle = "InputDateStyle"
toString InputHanja = "InputHanja"
toString InputHanjaBusu = "InputHanjaBusu"
toString InputHanjaMean = "InputHanjaMean"
toString InputPersonsNameHanja = "InputPersonsNameHanja"
toString oth = "oth"
toString oArrow = "oArrow"
toString neWay = "neWay"
toString ightBoth = "ightBoth"
toString ightOneWay = "ightOneWay"
toString keBoth = "keBoth"
toString keOneWay = "keOneWay"
toString RevisionDef = "RevisionDef"
toString RevisionDef2 = "RevisionDef"
toString Jajun = "Jajun"
toString LabelAdd = "LabelAdd"
toString LabelTemplate = "LabelTemplate"
toString LinkDocument = "LinkDocument"
toString LinkTextBox = "LinkTextBox"
toString MacroDefine = "MacroDefine"
toString MacroPause = "MacroPause"
toString MacroPlay1 = "MacroPlay1"
toString MacroPlay10 = "MacroPlay10"
toString MacroPlay11 = "MacroPlay11"
toString MacroPlay2 = "MacroPlay2"
toString MacroPlay3 = "MacroPlay3"
toString MacroPlay4 = "MacroPlay4"
toString MacroPlay5 = "MacroPlay5"
toString MacroPlay6 = "MacroPlay6"
toString MacroPlay7 = "MacroPlay7"
toString MacroPlay8 = "MacroPlay8"
toString MacroPlay9 = "MacroPlay9"
toString MacroRepeat = "MacroRepeat"
toString MacroRepeatDlg = "MacroRepeatDlg"
toString MacroStop = "MacroStop"
toString MakeAllVersionDiffs = "MakeAllVersionDiffs"
toString MakeContents = "MakeContents"
toString MakeIndex = "MakeIndex"
toString ManualChangeHangul = "ManualChangeHangul"
toString ManuScriptTemplate = "ManuScriptTemplate"
toString MarkPenDelete = "MarkPenDelete"
toString MarkPenNext = "MarkPenNext"
toString MarkPenPrev = "MarkPenPrev"
toString MarkPenShape = "MarkPenShape"
toString ParameterSet4 = "ParameterSet의"
toString MarkPrivateInfo = "MarkPrivateInfo"
toString MarkTitle = "MarkTitle"
toString MasterPage = "MasterPage"
toString MasterPageDelete = "MasterPageDelete"
toString MasterPageDuplicate = "MasterPageDuplicate"
toString MasterPageEntry = "MasterPageEntry"
toString MasterPageExcept = "MasterPageExcept"
toString MasterPageFront = "MasterPageFront"
toString MasterPagePrevSection = "MasterPagePrevSection"
toString MasterPageToNext = "MasterPageToNext"
toString MasterPageToPrevious = "MasterPageToPrevious"
toString MasterPageTypeDlg = "MasterPageTypeDlg"
toString MemoShape = "MemoShape"
toString MemoToNext = "MemoToNext"
toString MemoToPrev = "MemoToPrev"
toString MessageBox = "MessageBox"
toString ModifyBookmark = "ModifyBookmark"
toString ModifyComposeChars = "ModifyComposeChars"
toString ModifyCrossReference = "ModifyCrossReference"
toString ModifyCtrl = "ModifyCtrl"
toString ModifyDutmal = "ModifyDutmal"
toString ModifyFieldClickhere = "ModifyFieldClickhere"
toString ModifyFieldDate = "ModifyFieldDate"
toString ModifyFieldDateTime = "ModifyFieldDateTime"
toString ModifyFieldPath = "ModifyFieldPath"
toString ModifyFieldSummary = "ModifyFieldSummary"
toString ModifyFieldUserInfo = "ModifyFieldUserInfo"
toString ModifyFillProperty = "ModifyFillProperty"
toString SelectCtrlReverse = "(SelectCtrlReverse)을"
toString ModifyHyperlink = "ModifyHyperlink"
toString ModifyLineProperty = "ModifyLineProperty"
toString SelectCtrlReverse2 = "(SelectCtrlReverse)을"
toString ModifyRevision = "ModifyRevision"
toString ModifyRevision2 = "ModifyRevision과"
toString ModifyRevisionHyperlink = "ModifyRevisionHyperlink"
toString Run = "Run()으로"
toString ModifySecTextHorz = "ModifySecTextHorz"
toString ModifySecTextVert = "ModifySecTextVert"
toString ModifySecTextVertAll = "ModifySecTextVertAll"
toString ModifySection = "ModifySection"
toString ModifyShapeObject = "ModifyShapeObject"
toString LIST_BEGINEND = "LIST_BEGIN/END와"
toString LIST_BEGINEND2 = "LIST_BEGIN/END와"
toString MPBreakNewSection = "MPBreakNewSection"
toString MPCopyFromOtherSection = "MPCopyFromOtherSection"
toString MPSectionToNext = "MPSectionToNext"
toString MPSectionToPrevious = "MPSectionToPrevious"
toString MPShowMarginBorder = "MPShowMarginBorder"
toString MultiColumn = "MultiColumn"
toString NewNumber = "NewNumber"
toString NewNumberModify = "NewNumberModify"
toString NextTextBoxLinked = "NextTextBoxLinked"
toString NoneTextArtShadow = "NoneTextArtShadow"
toString NoteDelete = "NoteDelete"
toString NoteModify = "NoteModify"
toString NoteNoSuperscript = "NoteNoSuperscript"
toString NoteNumProperty = "NoteNumProperty"
toString NoteSuperscript = "NoteSuperscript"
toString NoteToNext = "NoteToNext"
toString NoteToPrev = "NoteToPrev"
toString OleCreateNew = "OleCreateNew"
toString OutlineNumber = "OutlineNumber"
toString ParagraphShape = "ParagraphShape"
toString ParagraphShapeAlignCenter = "ParagraphShapeAlignCenter"
toString ParagraphShapeAlignJustify = "ParagraphShapeAlignJustify"
toString ParagraphShapeAlignLeft = "ParagraphShapeAlignLeft"
toString ParagraphShapeAlignRight = "ParagraphShapeAlignRight"
toString ParagraphShapeProtect = "ParagraphShapeProtect"
toString ParagraphShapeSingleRow = "ParagraphShapeSingleRow"
toString ParagraphShapeWithNext = "ParagraphShapeWithNext"
toString ParaNumberBullet = "ParaNumberBullet"
toString ParaNumberBulletLevelDown = "ParaNumberBulletLevelDown"
toString ParaNumberBulletLevelUp = "ParaNumberBulletLevelUp"
toString ParaNumberDlg = "ParaNumberDlg"
toString Paste = "Paste"
toString PastePage = "PastePage"
toString PasteSpecial = "PasteSpecial"
toString Preference = "Preference"
toString Presentation = "Presentation"
toString PresentationDelete = "PresentationDelete"
toString PresentationRange = "PresentationRange"
toString PresentationSetup = "PresentationSetup"
toString PrevTextBoxLinked = "PrevTextBoxLinked"
toString Print = "Print"
toString PrintSetup = "PrintSetup"
toString PrintToImage = "PrintToImage"
toString PrintToPDF = "PrintToPDF"
toString PrivateInfoChangePassword = "PrivateInfoChangePassword"
toString PrivateInfoSetPassword = "PrivateInfoSetPassword"
toString PutBullet = "PutBullet"
toString PutNewParaNumber = "PutNewParaNumber"
toString PutOutlineNumber = "PutOutlineNumber"
toString PutParaNumber = "PutParaNumber"
toString QuickCommand = "QuickCommand"
toString QuickCorrect = "QuickCorrect"
toString QuickCorrect2 = "QuickCorrect"
toString QuickCorrect3 = "QuickCorrect"
toString QuickCorrect4 = "QuickCorrect"
toString QuickMarkInsert0 = "QuickMarkInsert0"
toString QuickMarkMove0 = "QuickMarkMove0"
toString RecalcPageCount = "RecalcPageCount"
toString RecentCode = "RecentCode"
toString Redo = "Redo"
toString RepeatFind = "RepeatFind"
toString ReplyMemo = "ReplyMemo"
toString ReturnKeyInField = "ReturnKeyInField"
toString ReturnPrevPos = "ReturnPrevPos"
toString ReverseFind = "ReverseFind"
toString ScanHFTFonts = "ScanHFTFonts"
toString ScrMacroDefine = "ScrMacroDefine"
toString ScrMacroPause = "ScrMacroPause"
toString ScrMacroPlay1 = "ScrMacroPlay1"
toString ScrMacroRepeatDlg = "ScrMacroRepeatDlg"
toString ScrMacroSecurityDlg = "ScrMacroSecurityDlg"
toString ScrMacroStop = "ScrMacroStop"
toString SendBrowserText = "SendBrowserText"
toString SendMailAttach = "SendMailAttach"
toString SendMailText = "SendMailText"
toString SetLineNumbers = "SetLineNumbers"
toString Bottom = "Bottom"
toString Top = "Top"
toString tBottom = "tBottom"
toString tTop = "tTop"
toString tom = "tom"
toString ttom = "ttom"
toString ShowLineNumbers = "ShowLineNumbers"
toString Soft = "Soft"
toString Sort = "Sort"
toString SpellingCheck = "SpellingCheck"
toString SplitMemoOpen = "SplitMemoOpen"
toString Sum = "Sum"
toString SuppressLineNumbers = "SuppressLineNumbers"
toString para = "para"
toString para2 = "para"
toString para3 = "para"
toString para4 = "para"
toString para5 = "para"
toString para6 = "para"
toString para7 = "para"
toString para8 = "para"
toString para9 = "para"
toString TextArtCreate = "TextArtCreate"
toString TextArtModify = "TextArtModify"
toString TextArtShadow = "TextArtShadow"
toString TextArtShadowMobeToDown = "TextArtShadowMobeToDown"
toString TextArtShadowMobeToLeft = "TextArtShadowMobeToLeft"
toString TextArtShadowMobeToRight = "TextArtShadowMobeToRight"
toString TextArtShadowMoveToUp = "TextArtShadowMoveToUp"
toString TextBoxAlignCenterBottom = "TextBoxAlignCenterBottom"
toString TextBoxAlignCenterCenter = "TextBoxAlignCenterCenter"
toString TextBoxAlignCenterTop = "TextBoxAlignCenterTop"
toString TextBoxAlignLeftBottom = "TextBoxAlignLeftBottom"
toString TextBoxAlignLeftCenter = "TextBoxAlignLeftCenter"
toString TextBoxAlignLeftTop = "TextBoxAlignLeftTop"
toString TextBoxAlignRightBottom = "TextBoxAlignRightBottom"
toString TextBoxAlignRightCenter = "TextBoxAlignRightCenter"
toString TextBoxAlignRightTop = "TextBoxAlignRightTop"
toString TextBoxTextHorz = "TextBoxTextHorz"
toString TextBoxTextVert = "TextBoxTextVert"
toString TextBoxTextVertAll = "TextBoxTextVertAll"
toString TextBoxToggleDirection = "TextBoxToggleDirection"
toString TextBoxVAlignBottom = "TextBoxVAlignBottom"
toString TextBoxVAlignCenter = "TextBoxVAlignCenter"
toString TextBoxVAlignTop = "TextBoxVAlignTop"
toString ToggleOverwrite = "ToggleOverwrite"
toString TrackChangeApply = "TrackChangeApply"
toString TrackChangeApplyAll = "TrackChangeApplyAll"
toString TrackChangeApplyNext = "TrackChangeApplyNext"
toString TrackChangeApplyPrev = "TrackChangeApplyPrev"
toString TrackChangeApplyViewAll = "TrackChangeApplyViewAll"
toString TrackChangeAuthor = "TrackChangeAuthor"
toString TrackChangeCancel = "TrackChangeCancel"
toString TrackChangeCancelAll = "TrackChangeCancelAll"
toString TrackChangeCancelNext = "TrackChangeCancelNext"
toString TrackChangeCancelPrev = "TrackChangeCancelPrev"
toString TrackChangeCancelViewAll = "TrackChangeCancelViewAll"
toString TrackChangeNext = "TrackChangeNext"
toString TrackChangeOption = "TrackChangeOption"
toString TrackChangePrev = "TrackChangePrev"
toString TrackChangeProtection = "TrackChangeProtection"
toString Undo = "Undo"
toString UnlinkTextBox = "UnlinkTextBox"
toString UserAutoFill = "UserAutoFill"
toString VersionDelete = "VersionDelete"
toString VersionDeleteAll = "VersionDeleteAll"
toString VersionInfo = "VersionInfo"
toString VersionSave = "VersionSave"
toString VerticalText = "VerticalText"
toString ViewGridOption = "ViewGridOption"
toString ViewIdiom = "ViewIdiom"
toString ViewOptionColor = "ViewOptionColor"
toString ViewOptionColorCustom = "ViewOptionColorCustom"
toString ViewOptionCtrlMark = "ViewOptionCtrlMark"
toString ViewOptionGray = "ViewOptionGray"
toString ViewOptionGuideLine = "ViewOptionGuideLine"
toString ViewOptionMemo = "ViewOptionMemo"
toString ViewOptionMemoGuideline = "ViewOptionMemoGuideline"
toString ViewOptionPaper = "ViewOptionPaper"
toString ViewOptionParaMark = "ViewOptionParaMark"
toString ViewOptionPicture = "ViewOptionPicture"
toString ViewOptionPronounce = "ViewOptionPronounce"
toString ViewOptionPronounceSetting = "ViewOptionPronounceSetting"
toString ViewOptionRevision = "ViewOptionRevision"
toString ViewOptionTrackChange = "ViewOptionTrackChange"
toString ViewOptionTrackChangeFinal = "ViewOptionTrackChangeFinal"
toString ViewOptionTrackChangeShape = "ViewOptionTrackChangeShape"
toString ViewOptionTrackChnageInfo = "ViewOptionTrackChnageInfo"
toString ViewShowGrid = "ViewShowGrid"
toString ViewZoom = "ViewZoom"
toString ViewZoomFitPage = "ViewZoomFitPage"
toString ViewZoomFitWidth = "ViewZoomFitWidth"
toString ViewZoomLock = "ViewZoomLock"
toString ViewZoomNormal = "ViewZoomNormal"
toString VoiceCommand = "VoiceCommand"
toString VoiceCommand2 = "VoiceCommand"
toString VoiceCommand3 = "VoiceCommand"
toString VoiceCommand4 = "VoiceCommand"
toString VoiceCommand5 = "VoiceCommand"
toString function = "function"
toString var = "var"
toString var2 = "var"
toString ifAction = "if"
toString dset = "dset"
toString ifAction2 = "if"
toString dsetSetItemPassword = "dset.SetItem("Password","
toString dsetSetItemNoPrint = "dset.SetItem("NoPrint","
toString dsetSetItemNoCopy = "dset.SetItem("NoCopy","
toString ifAction3 = "if"
toString var3 = "var"
toString ifAction4 = "if"
toString msg = "msg"
toString var4 = "var"
toString ifAction5 = "if"
toString msg2 = "msg"
toString elseAction = "else"
toString msg3 = "msg"
toString function2 = "function"
toString pHwpCtrlMovePos3 = "pHwpCtrl.MovePos(3);"
toString var5 = "var"
toString var6 = "var"
toString setSetItemIgnoreFindString = "set.SetItem("IgnoreFindString","
toString var7 = "var"
toString subsetSetItemUnderlineType = "subset.SetItem("UnderlineType","
toString var8 = "var"
toString var9 = "var"
toString set = "set"
toString list2 = "list"
toString para10 = "para"
toString pos = "pos"
toString function3 = "function"
toString var10 = "var"
toString var11 = "var"
toString dSetSetItemTextColor = "dSet.SetItem("TextColor","
toString function4 = "function"
toString pHwpCtrlMovePos2 = "pHwpCtrl.MovePos(2);"
toString var12 = "var"
toString while = "while"
toString OnTestApi1 = "OnTestApi1();"
toString con = "con"

-- ParameterSet ID
public export
paramSetID : MiscAction -> Maybe String
paramSetID Action = Just "Table"
paramSetID ParameterSet = Just "없음."
paramSetID HwpCtrlRun = Just "불가능."
paramSetID Action2 = Just "종속된"
paramSetID AddHanjaWord = Just "+"  -- Internal
paramSetID AllReplace = Just "FindReplace*"
paramSetID AQcommandMerge = Just "UserQCommandFile*"
paramSetID ParameterSet2 = Just "직접"
paramSetID AutoChangeHangul = Nothing
paramSetID AutoChangeRun = Nothing
paramSetID AutoSpell = Just "Run"
paramSetID AutoSpellSelect1 = Just "~"
paramSetID Average = Just "Sum"
paramSetID BackwardFind = Just "FindReplace*"
paramSetID Bookmark = Just "BookMark"
paramSetID BulletDlg = Just "ParaShape"
paramSetID CaptionPosBottom = Just "ShapeObject"
paramSetID CaptionPosLeftBottom = Just "ShapeObject"
paramSetID CaptionPosLeftCenter = Just "ShapeObject"
paramSetID CaptionPosLeftTop = Just "ShapeObject"
paramSetID CaptionPosRightBottom = Just "ShapeObject"
paramSetID CaptionPosRightCenter = Just "ShapeObject"
paramSetID CaptionPosRightTop = Just "ShapeObject"
paramSetID CaptionPosTop = Just "ShapeObject"
paramSetID CaptureDialog = Nothing
paramSetID CaptureHandler = Nothing
paramSetID ChangeImageFileExtension = Just "SummaryInfo"
paramSetID ChangeObject = Just "ShapeObject"
paramSetID ChangeRome = Just "String"
paramSetID ChangeRome2 = Just "User"
paramSetID ChangeRome3 = Just "User"
paramSetID ChangeRome4 = Just "+"  -- Internal
paramSetID er = Just "탭"
paramSetID list = Just "빠져나온다."
paramSetID Comment = Nothing
paramSetID CommentDelete = Nothing
paramSetID CommentModify = Nothing
paramSetID CompatibleDocument = Just "CompatibleDocument"
paramSetID ComposeChars = Just "ChCompose"
paramSetID ConvertBrailleSetting = Just "BrailleConvert"
paramSetID ConvertCase = Just "ConvertCase"
paramSetID ConvertFullHalfWidth = Just "ConvertFullHalf"
paramSetID ConvertHiraGata = Just "ConvertHiraToGata"
paramSetID ConvertJianFan = Just "ConvertJianFan"
paramSetID Text = Just "선택된"
paramSetID ConvertOptGugyulToHangul = Just "ConvertToHangul"
paramSetID ConvertOptHanjaToHangul = Just "ConvertToHangul"
paramSetID ConvertToHangul = Just "한글로"
paramSetID ConvertToBraille = Just "BrailleConvert"
paramSetID ConvertToBrailleSelected = Just "BrailleConvert"
paramSetID ConvertToHangul2 = Just "ConvertToHangul"
paramSetID Copy = Nothing
paramSetID CopyPage = Just "쪽"
paramSetID Cut = Nothing
paramSetID DrawObjCancelOneStep = Nothing
paramSetID DrawObjCreatorArc = Just "ShapeObject"
paramSetID DrawObjCreatorCanvas = Just "ShapeObject"
paramSetID DrawObjCreatorCurve = Just "ShapeObject"
paramSetID DrawObjCreatorEllipse = Just "ShapeObject"
paramSetID DrawObjCreatorFreeDrawing = Just "ShapeObject"
paramSetID DrawObjCreatorHorzTextBox = Just "ShapeObject"
paramSetID DrawObjCreatorLine = Just "ShapeObject"
paramSetID DrawObjCreatorMultiArc = Just "ShapeObject"
paramSetID DrawObjCreatorMultiCanvas = Just "ShapeObject"
paramSetID DrawObjCreatorMultiCurve = Just "ShapeObject"
paramSetID DrawObjCreatorMultiEllipse = Just "ShapeObject"
paramSetID DrawObjCreatorMultiLine = Just "ShapeObject"
paramSetID DrawObjCreatorMultiPolygon = Just "ShapeObject"
paramSetID DrawObjCreatorMultiTextBox = Just "ShapeObject"
paramSetID DrawObjCreatorObject = Just "ShapeObject"
paramSetID DrawObjCreatorPolygon = Just "ShapeObject"
paramSetID DrawObjCreatorRectangle = Just "ShapeObject"
paramSetID DrawObjCreatorTextBox = Just "ShapeObject"
paramSetID DrawObjCreatorVertTextBox = Just "ShapeObject"
paramSetID DrawObjEditDetail = Nothing
paramSetID DrawObjOpenClosePolygon = Nothing
paramSetID DrawObjTemplateLoad = Just "ShapeObject"
paramSetID DrawObjTemplateSave = Nothing
paramSetID DrawShapeObjShadow = Just "ShapeObject"
paramSetID DropCap = Just "DropCap"
paramSetID DutmalChars = Just "Dutmal"
paramSetID EditFieldMemo = Nothing
paramSetID EditParaDown = Just "문단"
paramSetID EditParaUp = Just "문단"
paramSetID EndnoteEndOfDocument = Just "SecDef"
paramSetID EndnoteEndOfSection = Just "SecDef"
paramSetID EndnoteToFootnote = Just "모든"
paramSetID EquationCreate = Just "EqEdit"
paramSetID EquationModify = Just "EqEdit"
paramSetID EquationPropertyDialog = Just "ShapeObject"
paramSetID Erase = Nothing
paramSetID ExchangeFootnoteEndnote = Just "각주/미주"
paramSetID ExecReplace = Just "FindReplace*"
paramSetID ExtractImagesFromDoc = Just "SummaryInfo"
paramSetID FillColorShadeDec = Nothing
paramSetID FillColorShadeInc = Nothing
paramSetID FootnoteBeneathText = Just "SecDef"
paramSetID FootnoteBottomOfEachColumn = Just "SecDef"
paramSetID SecDef = Just "다단"
paramSetID SecDef2 = Just "다단"
paramSetID FootnoteNoBeneathText = Just "SecDef"
paramSetID FootnoteOption = Just "SecDef"
paramSetID FootnoteToEndnote = Just "모든"
paramSetID FormDesignMode = Nothing
paramSetID FormObjCreatorCheckButton = Nothing
paramSetID FormObjCreatorComboBox = Nothing
paramSetID FormObjCreatorEdit = Nothing
paramSetID FormObjCreatorListBox = Nothing
paramSetID FormObjCreatorPushButton = Nothing
paramSetID FormObjCreatorRadioButton = Nothing
paramSetID FormObjCreatorScrollBar = Nothing
paramSetID ForwardFind = Just "FindReplace*"
paramSetID FrameStatusBar = Nothing
paramSetID FtpDownload = Just "FtpDownload"
paramSetID FtpUpload = Just "FtpUpload"
paramSetID GetDefaultBullet = Just "ParaShape*"
paramSetID GetDefaultParaNumber = Just "ParaShape*"
paramSetID GetDocFilters = Just "DocFilters"
paramSetID GetRome = Just "String"
paramSetID GetSectionApplyString = Just "SectionApply"
paramSetID GetSectionApplyTo = Just "SectionApply"
paramSetID GetVersionItemInfo = Just "VersionInfo"
paramSetID ParameterSet3 = Just "얻어올"
paramSetID HanThDIC = Nothing
paramSetID HeaderFooter = Just "HeaderFooter"
paramSetID HeaderFooterDelete = Nothing
paramSetID HeaderFooterInsField = Just "HeaderFooter"
paramSetID HeaderFooterModify = Nothing
paramSetID HeaderFooterToNext = Nothing
paramSetID HeaderFooterToPrev = Nothing
paramSetID HiddenCredits = Nothing
paramSetID HideTitle = Nothing
paramSetID Him = Just "Config"
paramSetID HimKbdChange = Nothing
paramSetID HwpCtrlEquationCreate97 = Nothing
paramSetID HwpCtrlFileNew = Nothing
paramSetID HwpCtrlFileOpen = Nothing
paramSetID HwpCtrlFileSave = Nothing
paramSetID HwpCtrlFileSaveAs = Nothing
paramSetID HwpCtrlFileSaveAsAutoBlock = Nothing
paramSetID HwpCtrlFileSaveAutoBlock = Nothing
paramSetID HwpCtrlFindDlg = Nothing
paramSetID HwpCtrlReplaceDlg = Nothing
paramSetID HwpDic = Nothing
paramSetID Hyperlink = Just "HyperLink"
paramSetID HyperlinkBackward = Nothing
paramSetID HyperlinkForward = Nothing
paramSetID HyperlinkJump = Just "HyperlinkJump"
paramSetID Idiom = Just "Idiom"
paramSetID IndexMark = Just "IndexMark"
paramSetID IndexMarkModify = Just "IndexMark"
paramSetID InputCodeChange = Nothing
paramSetID InputCodeTable = Just "CodeTable"
paramSetID InputDateStyle = Just "InputDateStyle"
paramSetID InputHanja = Nothing
paramSetID InputHanjaBusu = Nothing
paramSetID InputHanjaMean = Nothing
paramSetID InputPersonsNameHanja = Just "InputHanja"
paramSetID oth = Just "표"
paramSetID oArrow = Just "표"
paramSetID neWay = Just "표"
paramSetID ightBoth = Just "결선)"
paramSetID ightOneWay = Just "선)"
paramSetID keBoth = Just "결선)"
paramSetID keOneWay = Just "선)"
paramSetID RevisionDef = Just "교정"
paramSetID RevisionDef2 = Just "교정"
paramSetID Jajun = Nothing
paramSetID LabelAdd = Nothing
paramSetID LabelTemplate = Nothing
paramSetID LinkDocument = Just "LinkDocument"
paramSetID LinkTextBox = Nothing
paramSetID MacroDefine = Just "KeyMacro"
paramSetID MacroPause = Nothing
paramSetID MacroPlay1 = Nothing
paramSetID MacroPlay10 = Nothing
paramSetID MacroPlay11 = Nothing
paramSetID MacroPlay2 = Nothing
paramSetID MacroPlay3 = Nothing
paramSetID MacroPlay4 = Nothing
paramSetID MacroPlay5 = Nothing
paramSetID MacroPlay6 = Nothing
paramSetID MacroPlay7 = Nothing
paramSetID MacroPlay8 = Nothing
paramSetID MacroPlay9 = Nothing
paramSetID MacroRepeat = Nothing
paramSetID MacroRepeatDlg = Just "KeyMacro"
paramSetID MacroStop = Nothing
paramSetID MakeAllVersionDiffs = Just "VersionInfo"
paramSetID MakeContents = Just "MakeContents"
paramSetID MakeIndex = Nothing
paramSetID ManualChangeHangul = Nothing
paramSetID ManuScriptTemplate = Just "FileOpen"
paramSetID MarkPenDelete = Just "형광팬"
paramSetID MarkPenNext = Just "형광팬"
paramSetID MarkPenPrev = Just "형광팬"
paramSetID MarkPenShape = Just "MarkpenShape*"
paramSetID ParameterSet4 = Just "Color"
paramSetID MarkPrivateInfo = Just "PrivateInfoSecurity"
paramSetID MarkTitle = Nothing
paramSetID MasterPage = Just "MasterPage"
paramSetID MasterPageDelete = Just "MasterPage*"
paramSetID MasterPageDuplicate = Nothing
paramSetID MasterPageEntry = Just "MasterPage"
paramSetID MasterPageExcept = Nothing
paramSetID MasterPageFront = Nothing
paramSetID MasterPagePrevSection = Nothing
paramSetID MasterPageToNext = Nothing
paramSetID MasterPageToPrevious = Nothing
paramSetID MasterPageTypeDlg = Just "MasterPage*"
paramSetID MemoShape = Just "SecDef"
paramSetID MemoToNext = Nothing
paramSetID MemoToPrev = Nothing
paramSetID MessageBox = Just "+"  -- Internal
paramSetID ModifyBookmark = Just "BookMark"
paramSetID ModifyComposeChars = Nothing
paramSetID ModifyCrossReference = Just "ActionCrossRef"
paramSetID ModifyCtrl = Nothing
paramSetID ModifyDutmal = Nothing
paramSetID ModifyFieldClickhere = Just "InsertFieldTemplate"
paramSetID ModifyFieldDate = Just "InsertFieldTemplate"
paramSetID ModifyFieldDateTime = Just "InputDateStyle"
paramSetID ModifyFieldPath = Just "InsertFieldTemplate"
paramSetID ModifyFieldSummary = Just "InsertFieldTemplate"
paramSetID ModifyFieldUserInfo = Just "InsertFieldTemplate"
paramSetID ModifyFillProperty = Nothing
paramSetID SelectCtrlReverse = Just "이용해서"
paramSetID ModifyHyperlink = Just "HyperLink"
paramSetID ModifyLineProperty = Nothing
paramSetID SelectCtrlReverse2 = Just "이용해서"
paramSetID ModifyRevision = Just "RevisionDef"
paramSetID ModifyRevision2 = Just "마찬가지로"
paramSetID ModifyRevisionHyperlink = Just "HyperLink*"
paramSetID Run = Just "실행되지"
paramSetID ModifySecTextHorz = Just "TextVertical"
paramSetID ModifySecTextVert = Just "TextVertical"
paramSetID ModifySecTextVertAll = Just "TextVertical"
paramSetID ModifySection = Just "SecDef"
paramSetID ModifyShapeObject = Nothing
paramSetID LIST_BEGINEND = Just "동일하다."
paramSetID LIST_BEGINEND2 = Just "동일하다."
paramSetID MPBreakNewSection = Just "MasterPage"
paramSetID MPCopyFromOtherSection = Just "Masterpage"
paramSetID MPSectionToNext = Nothing
paramSetID MPSectionToPrevious = Nothing
paramSetID MPShowMarginBorder = Nothing
paramSetID MultiColumn = Just "ColDef"
paramSetID NewNumber = Just "AutoNum"
paramSetID NewNumberModify = Just "AutoNum"
paramSetID NextTextBoxLinked = Nothing
paramSetID NoneTextArtShadow = Just "ShapeObject"
paramSetID NoteDelete = Nothing
paramSetID NoteModify = Nothing
paramSetID NoteNoSuperscript = Just "SecDef"
paramSetID NoteNumProperty = Nothing
paramSetID NoteSuperscript = Just "SecDef"
paramSetID NoteToNext = Nothing
paramSetID NoteToPrev = Nothing
paramSetID OleCreateNew = Just "OleCreation"
paramSetID OutlineNumber = Just "SecDef"
paramSetID ParagraphShape = Just "ParaShape"
paramSetID ParagraphShapeAlignCenter = Nothing
paramSetID ParagraphShapeAlignJustify = Nothing
paramSetID ParagraphShapeAlignLeft = Nothing
paramSetID ParagraphShapeAlignRight = Nothing
paramSetID ParagraphShapeProtect = Nothing
paramSetID ParagraphShapeSingleRow = Just "한"
paramSetID ParagraphShapeWithNext = Nothing
paramSetID ParaNumberBullet = Just "ParaShape"
paramSetID ParaNumberBulletLevelDown = Just "ParaShape"
paramSetID ParaNumberBulletLevelUp = Just "ParaShape"
paramSetID ParaNumberDlg = Just "ParaShape"
paramSetID Paste = Nothing
paramSetID PastePage = Nothing
paramSetID PasteSpecial = Nothing
paramSetID Preference = Just "Preference"
paramSetID Presentation = Just "Presentation"
paramSetID PresentationDelete = Just "Presentation"
paramSetID PresentationRange = Just "PresentationRange"
paramSetID PresentationSetup = Just "Presentation"
paramSetID PrevTextBoxLinked = Nothing
paramSetID Print = Just "Print"
paramSetID PrintSetup = Just "Print"
paramSetID PrintToImage = Just "PrintToImage"
paramSetID PrintToPDF = Just "Print"
paramSetID PrivateInfoChangePassword = Just "PrivateInfoSecurity"
paramSetID PrivateInfoSetPassword = Just "PrivateInfoSecurity"
paramSetID PutBullet = Just "ParaShape*"
paramSetID PutNewParaNumber = Just "ParaShape*"
paramSetID PutOutlineNumber = Just "ParaShape*"
paramSetID PutParaNumber = Just "ParaShape*"
paramSetID QuickCommand = Just "Run"
paramSetID QuickCorrect = Just "Edit"
paramSetID QuickCorrect2 = Just "Run"
paramSetID QuickCorrect3 = Just "Sound"
paramSetID QuickCorrect4 = Nothing
paramSetID QuickMarkInsert0 = Just "~"
paramSetID QuickMarkMove0 = Just "~"
paramSetID RecalcPageCount = Nothing
paramSetID RecentCode = Nothing
paramSetID Redo = Nothing
paramSetID RepeatFind = Just "FindReplace*"
paramSetID ReplyMemo = Nothing
paramSetID ReturnKeyInField = Nothing
paramSetID ReturnPrevPos = Nothing
paramSetID ReverseFind = Just "FindReplace*"
paramSetID ScanHFTFonts = Just "한/글"
paramSetID ScrMacroDefine = Just "ScriptMacro"
paramSetID ScrMacroPause = Nothing
paramSetID ScrMacroPlay1 = Just "~"
paramSetID ScrMacroRepeatDlg = Just "ScriptMacro"
paramSetID ScrMacroSecurityDlg = Just "+"  -- Internal
paramSetID ScrMacroStop = Nothing
paramSetID SendBrowserText = Nothing
paramSetID SendMailAttach = Just "FileSendMail"
paramSetID SendMailText = Just "FileSendMail"
paramSetID SetLineNumbers = Just "SecDef"
paramSetID Bottom = Just "왼쪽하단에"
paramSetID Top = Just "왼쪽상단에"
paramSetID tBottom = Just "오른쪽하단에"
paramSetID tTop = Just "오른쪽상단에"
paramSetID tom = Just "성한다."
paramSetID ttom = Just "생성한다."
paramSetID ShowLineNumbers = Just "SecDef"
paramSetID Soft = Just "Keyboard"
paramSetID Sort = Just "Sort"
paramSetID SpellingCheck = Nothing
paramSetID SplitMemoOpen = Nothing
paramSetID Sum = Just "Sum"
paramSetID SuppressLineNumbers = Just "줄"
paramSetID para = Just "align"
paramSetID para2 = Just "align"
paramSetID para3 = Just "align"
paramSetID para4 = Just "align"
paramSetID para5 = Just "align"
paramSetID para6 = Just "align"
paramSetID para7 = Just "align"
paramSetID para8 = Just "align"
paramSetID para9 = Just "align"
paramSetID TextArtCreate = Just "+"  -- Internal
paramSetID TextArtModify = Just "+"  -- Internal
paramSetID TextArtShadow = Just "+"  -- Internal
paramSetID TextArtShadowMobeToDown = Just "ShapeObject"
paramSetID TextArtShadowMobeToLeft = Just "ShapeObject"
paramSetID TextArtShadowMobeToRight = Just "ShapeObject"
paramSetID TextArtShadowMoveToUp = Just "ShapeObject"
paramSetID TextBoxAlignCenterBottom = Just "ShapeObject"
paramSetID TextBoxAlignCenterCenter = Just "ShapeObject"
paramSetID TextBoxAlignCenterTop = Just "ShapeObject"
paramSetID TextBoxAlignLeftBottom = Just "ShapeObject"
paramSetID TextBoxAlignLeftCenter = Just "ShapeObject"
paramSetID TextBoxAlignLeftTop = Just "ShapeObject"
paramSetID TextBoxAlignRightBottom = Just "ShapeObject"
paramSetID TextBoxAlignRightCenter = Just "ShapeObject"
paramSetID TextBoxAlignRightTop = Just "ShapeObject"
paramSetID TextBoxTextHorz = Just "ShpaeObject"
paramSetID TextBoxTextVert = Just "ShapeObject"
paramSetID TextBoxTextVertAll = Just "ShapeObject"
paramSetID TextBoxToggleDirection = Just "ShapeObject"
paramSetID TextBoxVAlignBottom = Just "ShapeObject"
paramSetID TextBoxVAlignCenter = Just "ShapeObject"
paramSetID TextBoxVAlignTop = Just "ShapeObject"
paramSetID ToggleOverwrite = Nothing
paramSetID TrackChangeApply = Nothing
paramSetID TrackChangeApplyAll = Nothing
paramSetID TrackChangeApplyNext = Nothing
paramSetID TrackChangeApplyPrev = Nothing
paramSetID TrackChangeApplyViewAll = Nothing
paramSetID TrackChangeAuthor = Nothing
paramSetID TrackChangeCancel = Nothing
paramSetID TrackChangeCancelAll = Nothing
paramSetID TrackChangeCancelNext = Nothing
paramSetID TrackChangeCancelPrev = Nothing
paramSetID TrackChangeCancelViewAll = Nothing
paramSetID TrackChangeNext = Nothing
paramSetID TrackChangeOption = Just "TrackChange"
paramSetID TrackChangePrev = Nothing
paramSetID TrackChangeProtection = Just "Password"
paramSetID Undo = Nothing
paramSetID UnlinkTextBox = Nothing
paramSetID UserAutoFill = Just "AutoFill*"
paramSetID VersionDelete = Just "VersionInfo*"
paramSetID VersionDeleteAll = Nothing
paramSetID VersionInfo = Just "VersionInfo"
paramSetID VersionSave = Just "VersionInfo"
paramSetID VerticalText = Just "TextVertical"
paramSetID ViewGridOption = Just "GridInfo"
paramSetID ViewIdiom = Nothing
paramSetID ViewOptionColor = Just "컬러로"
paramSetID ViewOptionColorCustom = Just "사용자색"
paramSetID ViewOptionCtrlMark = Nothing
paramSetID ViewOptionGray = Just "회색조"
paramSetID ViewOptionGuideLine = Nothing
paramSetID ViewOptionMemo = Nothing
paramSetID ViewOptionMemoGuideline = Nothing
paramSetID ViewOptionPaper = Nothing
paramSetID ViewOptionParaMark = Nothing
paramSetID ViewOptionPicture = Nothing
paramSetID ViewOptionPronounce = Just "PronounceInfo"
paramSetID ViewOptionPronounceSetting = Just "PronounceInfo"
paramSetID ViewOptionRevision = Nothing
paramSetID ViewOptionTrackChange = Nothing
paramSetID ViewOptionTrackChangeFinal = Nothing
paramSetID ViewOptionTrackChangeShape = Nothing
paramSetID ViewOptionTrackChnageInfo = Nothing
paramSetID ViewShowGrid = Just "GridInfo"
paramSetID ViewZoom = Just "ViewProperties"
paramSetID ViewZoomFitPage = Just "ViewProperties"
paramSetID ViewZoomFitWidth = Just "ViewProperties"
paramSetID ViewZoomLock = Just "화면"
paramSetID ViewZoomNormal = Just "ViewProperties"
paramSetID VoiceCommand = Just "Config"
paramSetID VoiceCommand2 = Just "Resume"
paramSetID VoiceCommand3 = Just "Stop"
paramSetID VoiceCommand4 = Just "View"
paramSetID VoiceCommand5 = Just "+"  -- Internal
paramSetID function = Just "SetDistribute()"
paramSetID var = Just "dact"
paramSetID var2 = Just "dset"
paramSetID ifAction = Just "(dact)"
paramSetID dset = Just "="
paramSetID ifAction2 = Just "(dact"
paramSetID dsetSetItemPassword = Just "HwpControl.password.value);"
paramSetID dsetSetItemNoPrint = Just "HwpControl.NoPrint.checked);"
paramSetID dsetSetItemNoCopy = Just "HwpControl.NoCopy.checked);"
paramSetID ifAction3 = Just "(!dact.Execute(dset))"
paramSetID var3 = Just "msg"
paramSetID ifAction4 = Just "(dset.Item("Password").length"
paramSetID msg = Just "+="
paramSetID var4 = Just "msg"
paramSetID ifAction5 = Just "(pHwpCtrl.EditMode"
paramSetID msg2 = Just "+="
paramSetID elseAction = Just "if"
paramSetID msg3 = Just "+="
paramSetID function2 = Just "OnTestApi1()"
paramSetID pHwpCtrlMovePos3 = Just "//"
paramSetID var5 = Just "act"
paramSetID var6 = Just "set"
paramSetID setSetItemIgnoreFindString = Just "1);"
paramSetID var7 = Just "subset"
paramSetID subsetSetItemUnderlineType = Just "1);"
paramSetID var8 = Just "set;"
paramSetID var9 = Just "list,"
paramSetID set = Just "="
paramSetID list2 = Just "="
paramSetID para10 = Just "="
paramSetID pos = Just "="
paramSetID function3 = Just "OnTestApi1()"
paramSetID var10 = Just "dAct"
paramSetID var11 = Just "dSet"
paramSetID dSetSetItemTextColor = Just "0xFF0000);"
paramSetID function4 = Just "OnTestApi2()"
paramSetID pHwpCtrlMovePos2 = Just "//"
paramSetID var12 = Just "con"
paramSetID while = Just "(con)"
paramSetID OnTestApi1 = Just "//"
paramSetID con = Just "="

-- 설명
public export
description : MiscAction -> String
description Action = "No description"
description ParameterSet = "No description"
description HwpCtrlRun = "No description"
description Action2 = "Action이거나, DocSummaryInfo와 같이 값을 읽어오기만 하는 Action일 경우 해담."
description AddHanjaWord = "한자단어 등록"
description AllReplace = "모두 바꾸기"
description AQcommandMerge = "No description"
description ParameterSet2 = "조작하여 사용함."
description AutoChangeHangul = "낱자모 우선"
description AutoChangeRun = "동작"
description AutoSpell = "- 맞춤법 ― 메뉴에서 맞춤법 도우미 동작 On/Off"
description AutoSpellSelect1 = "16 -"
description Average = "블록 평균"
description BackwardFind = "뒤로 찾기"
description Bookmark = "책갈피"
description BulletDlg = "글머리표 대화상자"
description CaptionPosBottom = "캡션 위치-아래"
description CaptionPosLeftBottom = "캡션 위치-왼쪽 아래"
description CaptionPosLeftCenter = "캡션 위치–왼쪽 가운데"
description CaptionPosLeftTop = "캡션 위치–왼쪽 위"
description CaptionPosRightBottom = "캡션 위치–오른쪽 아래"
description CaptionPosRightCenter = "캡션 위치–오른쪽 가운데"
description CaptionPosRightTop = "캡션 위치–오른쪽 위"
description CaptionPosTop = "캡션 위치-위"
description CaptureDialog = "갈무리 끝"
description CaptureHandler = "갈무리 시작"
description ChangeImageFileExtension = "연결 그림 확장자 바꾸기"
description ChangeObject = "개체 변경하기"
description ChangeRome = "+ 로마자변환 - 입력받은 스트링 변환"
description ChangeRome2 = "String + 로마자 사용자 데이터 추가"
description ChangeRome3 = "+ 로마자 사용자 데이터"
description ChangeRome4 = "로마자변환"
description er = "제외)"
description list = "Shift+Esc"
description Comment = "숨은 설명"
description CommentDelete = "숨은 설명 지우기"
description CommentModify = "숨은 설명 고치기"
description CompatibleDocument = "호환 문서"
description ComposeChars = "글자 겹침"
description ConvertBrailleSetting = "No description"
description ConvertCase = "대소문자 바꾸기"
description ConvertFullHalfWidth = "전각 반각 바꾸기"
description ConvertHiraGata = "일어 바꾸기"
description ConvertJianFan = "No description"
description Text = "상태에서만 동작"
description ConvertOptGugyulToHangul = "한글로 옵션 - 구결을 한글로"
description ConvertOptHanjaToHangul = "한글로 옵션 - 漢字를 한글로"
description ConvertToHangul = "옵션 - 漢字를 漢字(한글)로"
description ConvertToBraille = "점자 변환"
description ConvertToBrailleSelected = "No description"
description ConvertToHangul2 = "한글로"
description Copy = "복사하기"
description CopyPage = "복사하기"
description Cut = "오려두기"
description DrawObjCancelOneStep = "다각형(곡선) 그리는 중 이전 선 지우기"
description DrawObjCreatorArc = "호 그리기"
description DrawObjCreatorCanvas = "캔버스 그리기"
description DrawObjCreatorCurve = "곡선 그리기"
description DrawObjCreatorEllipse = "원 그리기"
description DrawObjCreatorFreeDrawing = "펜"
description DrawObjCreatorHorzTextBox = "가로 글상자 만들기"
description DrawObjCreatorLine = "선 그리기"
description DrawObjCreatorMultiArc = "반복해서 호 그리기"
description DrawObjCreatorMultiCanvas = "반복해서 캔버스 그리기"
description DrawObjCreatorMultiCurve = "반복해서 곡선 그리기"
description DrawObjCreatorMultiEllipse = "반복해서 원 그리기"
description DrawObjCreatorMultiLine = "반복해서 선 그리기"
description DrawObjCreatorMultiPolygon = "반복해서 다각형 그리기"
description DrawObjCreatorMultiTextBox = "반복해서 글상자 그리기"
description DrawObjCreatorObject = "그리기 개체"
description DrawObjCreatorPolygon = "다각형 그리기"
description DrawObjCreatorRectangle = "사각형 그리기"
description DrawObjCreatorTextBox = "글상자"
description DrawObjCreatorVertTextBox = "세로 글상자 만들기"
description DrawObjEditDetail = "그리기 개체 편집"
description DrawObjOpenClosePolygon = "다각형 열기/닫기"
description DrawObjTemplateLoad = "그리기 마당에서 불러오기"
description DrawObjTemplateSave = "그리기 마당에 등록"
description DrawShapeObjShadow = "No description"
description DropCap = "문단 첫 글자 장식"
description DutmalChars = "덧말 넣기"
description EditFieldMemo = "메모 내용 편집"
description EditParaDown = "옮기기"
description EditParaUp = "옮기기"
description EndnoteEndOfDocument = "미주–문서의 끝"
description EndnoteEndOfSection = "미주–구역의 끝"
description EndnoteToFootnote = "미주를 각주로"
description EquationCreate = "수식 만들기"
description EquationModify = "수식 편집하기"
description EquationPropertyDialog = "수식 개체 속성 고치기"
description Erase = "지우기"
description ExchangeFootnoteEndnote = "변환"
description ExecReplace = "바꾸기(실행)"
description ExtractImagesFromDoc = "삽입 그림을 연결 그림으로 추출"
description FillColorShadeDec = "면 색 음영 비율 감소"
description FillColorShadeInc = "면 색 음영 비율 증가"
description FootnoteBeneathText = "각주–본문 아래"
description FootnoteBottomOfEachColumn = "다단 각주–각 단 아래"
description SecDef = "각주–전 단"
description SecDef2 = "각주–오른쪽 단 아래"
description FootnoteNoBeneathText = "각주–꼬리말 바로 위"
description FootnoteOption = "각주/미주 모양"
description FootnoteToEndnote = "각주를 미주로"
description FormDesignMode = "디자인 모드 변경"
description FormObjCreatorCheckButton = "Check버튼 넣기"
description FormObjCreatorComboBox = "ComboBox넣기"
description FormObjCreatorEdit = "Edit넣기"
description FormObjCreatorListBox = "ListBox넣기"
description FormObjCreatorPushButton = "Push버튼 넣기"
description FormObjCreatorRadioButton = "Radio버튼 넣기"
description FormObjCreatorScrollBar = "ScrollBar넣기"
description ForwardFind = "앞으로 찾기"
description FrameStatusBar = "상태바 보이기/숨기기"
description FtpDownload = "FTP서버에서 파일 다운 받아 문서 오픈하기"
description FtpUpload = "웹 서버로 올리기"
description GetDefaultBullet = "글머리표 디폴트 값"
description GetDefaultParaNumber = "문단번호 디폴트 값"
description GetDocFilters = "유틸리티 액션"
description GetRome = "ChangeRome* Run()으로 실행시키면 프로그램이 죽는다. 반드"
description GetSectionApplyString = "유틸리티 액션"
description GetSectionApplyTo = "유틸리티 액션"
description GetVersionItemInfo = "No description"
description ParameterSet3 = "Item의 Index값을 반"
description HanThDIC = "유의어 사전"
description HeaderFooter = "머리말/꼬리말"
description HeaderFooterDelete = "머리말 지우기"
description HeaderFooterInsField = "코드 넣기"
description HeaderFooterModify = "머리말/꼬리말 고치기"
description HeaderFooterToNext = "이후 머리말"
description HeaderFooterToPrev = "이전 머리말"
description HiddenCredits = "인터넷 정보"
description HideTitle = "No description"
description Him = "- 입력기 언어별 환경설정"
description HimKbdChange = "바꾸기"
description HwpCtrlEquationCreate97 = "수식 만들기(글97버전)"
description HwpCtrlFileNew = "새문서"
description HwpCtrlFileOpen = "파일 열기"
description HwpCtrlFileSave = "파일 저장"
description HwpCtrlFileSaveAs = "다른 이름으로 저장"
description HwpCtrlFileSaveAsAutoBlock = "만약 텍스트가 선택되지 않은 경우에는 다른 이름"
description HwpCtrlFileSaveAutoBlock = "만약 텍스트가 선택되지 않은 경우에는 저장하기가"
description HwpCtrlFindDlg = "찾기 대화상자"
description HwpCtrlReplaceDlg = "바꾸기 대화상자"
description HwpDic = "한컴 사전"
description Hyperlink = "No description"
description HyperlinkBackward = "하이퍼링크 뒤로"
description HyperlinkForward = "하이퍼링크 앞으로"
description HyperlinkJump = "하이퍼링크 이동"
description Idiom = "상용구"
description IndexMark = "찾아보기 표시"
description IndexMarkModify = "찾아보기 표시 고치기"
description InputCodeChange = "No description"
description InputCodeTable = "문자표"
description InputDateStyle = "No description"
description InputHanja = "한자 변환"
description InputHanjaBusu = "부수로 입력"
description InputHanjaMean = "새김으로 입력"
description InputPersonsNameHanja = "인명한자 변환"
description oth = "연결선)"
description oArrow = "연결선)"
description neWay = "연결선)"
description ightBoth = "No description"
description ightOneWay = "No description"
description keBoth = "No description"
description keOneWay = "No description"
description RevisionDef = "부호 넣기 : 줄 서로 바꿈 나눔표(내부용)"
description RevisionDef2 = "부호 넣기 : 자리바꿈 나눔표(내부용)"
description Jajun = "한자 자전"
description LabelAdd = "라벨 새 쪽 추가하기"
description LabelTemplate = "라벨 문서 만들기"
description LinkDocument = "문서 연결([파일-문서 연결]메뉴와 동일)"
description LinkTextBox = "글상자가 선택되지 않았거나, 캐럿이 글상자 내부"
description MacroDefine = "매크로 정의"
description MacroPause = "매크로 실행 일시 중지 (정의/실행)"
description MacroPlay1 = "매크로 1"
description MacroPlay10 = "매크로 10"
description MacroPlay11 = "매크로 11"
description MacroPlay2 = "매크로 2"
description MacroPlay3 = "매크로 3"
description MacroPlay4 = "매크로 4"
description MacroPlay5 = "매크로 5"
description MacroPlay6 = "매크로 6"
description MacroPlay7 = "매크로 7"
description MacroPlay8 = "매크로 8"
description MacroPlay9 = "매크로 9"
description MacroRepeat = "매크로 실행"
description MacroRepeatDlg = "매크로 실행"
description MacroStop = "매크로 실행 중지 (정의/실행)"
description MakeAllVersionDiffs = "No description"
description MakeContents = "차례 만들기"
description MakeIndex = "찾아보기 만들기"
description ManualChangeHangul = "현재 커서위치 또는 문단나누기 이전에 입력된 내"
description ManuScriptTemplate = "원고지 쓰기"
description MarkPenDelete = "삭제"
description MarkPenNext = "이동(다음)"
description MarkPenPrev = "이동(이전)"
description MarkPenShape = "Run() 실행불가, 반드시 MarkpenShape"
description ParameterSet4 = "아이템 값을 설정하고"
description MarkPrivateInfo = "개인 정보 즉시 감추기(텍스트 블록 상태,암호화)"
description MarkTitle = "차례 코드가 삽입되어 나중에 차례 만들기에서 사"
description MasterPage = "바탕쪽"
description MasterPageDelete = "바탕쪽 삭제바탕쪽 편집모드일 경우에만 동작한다."
description MasterPageDuplicate = "바탕쪽 편집상태가 활성화되어 있으며 [구역 마지"
description MasterPageEntry = "No description"
description MasterPageExcept = "첫 쪽 제외"
description MasterPageFront = "No description"
description MasterPagePrevSection = "앞 구역 바탕쪽 사용"
description MasterPageToNext = "이후 바탕쪽"
description MasterPageToPrevious = "이전 바탕쪽"
description MasterPageTypeDlg = "바탕쪽 종류 다이얼로그 띄움"
description MemoShape = "메모 모양([입력-메모-메모 모양]메뉴와 동일함)"
description MemoToNext = "다음 메모"
description MemoToPrev = "이전 메모"
description MessageBox = "메시지 박스"
description ModifyBookmark = "책갈피 고치기"
description ModifyComposeChars = "고치기 - 글자 겹침"
description ModifyCrossReference = "상호 참조 고치기"
description ModifyCtrl = "고치기 : 컨트롤"
description ModifyDutmal = "고치기 - 덧말"
description ModifyFieldClickhere = "누름틀 정보 고치기"
description ModifyFieldDate = "날짜 필드 고치기"
description ModifyFieldDateTime = "No description"
description ModifyFieldPath = "문서 경로 필드 고치기"
description ModifyFieldSummary = "문서 요약 필드 고치기"
description ModifyFieldUserInfo = "개인 정보 필드 고치기"
description ModifyFillProperty = "No description"
description SelectCtrlReverse = "개체를 탐색"
description ModifyHyperlink = "하이퍼링크 고치기"
description ModifyLineProperty = "No description"
description SelectCtrlReverse2 = "개체를 탐색"
description ModifyRevision = "가지로 정확히 교정부호(조판 부호)의 앞에 캐럿"
description ModifyRevision2 = "정확히 교정부호"
description ModifyRevisionHyperlink = "No description"
description Run = "않는다."
description ModifySecTextHorz = "가로 쓰기"
description ModifySecTextVert = "세로 쓰기(영문 눕힘)"
description ModifySecTextVertAll = "세로 쓰기(영문 세움)"
description ModifySection = "구역"
description ModifyShapeObject = "고치기 - 개체 속성"
description LIST_BEGINEND = "현재 서브 리스트"
description LIST_BEGINEND2 = "현재 서브 리스트"
description MPBreakNewSection = "새 구역 만들기–바탕쪽 편집 상태에서"
description MPCopyFromOtherSection = "No description"
description MPSectionToNext = "이후 구역으로"
description MPSectionToPrevious = "이전 구역으로"
description MPShowMarginBorder = "여백 보기–바탕쪽 편집 상태에서"
description MultiColumn = "다단"
description NewNumber = "새 번호로 시작"
description NewNumberModify = "새 번호 고치기"
description NextTextBoxLinked = "연결된 글상자의 다음 글상자로 이동"
description NoneTextArtShadow = "글맵시 그림자 없음"
description NoteDelete = "주석 지우기"
description NoteModify = "주석 고치기"
description NoteNoSuperscript = "주석 번호 보통(윗 첨자 사용 안함)"
description NoteNumProperty = "주석 번호 속성"
description NoteSuperscript = "주석 번호 작게(윗 첨자)"
description NoteToNext = "주석 다음으로 이동"
description NoteToPrev = "주석 앞으로 이동"
description OleCreateNew = "개체 삽입"
description OutlineNumber = "개요번호"
description ParagraphShape = "문단 모양"
description ParagraphShapeAlignCenter = "가운데 정렬"
description ParagraphShapeAlignJustify = "양쪽 정렬"
description ParagraphShapeAlignLeft = "왼쪽 정렬"
description ParagraphShapeAlignRight = "오른쪽 정렬"
description ParagraphShapeProtect = "문단 보호"
description ParagraphShapeSingleRow = "줄로 입력"
description ParagraphShapeWithNext = "다음 문단과 함께"
description ParaNumberBullet = "문단번호/글머리표 한 수준 위로"
description ParaNumberBulletLevelDown = "문단번호/글머리표 한 수준 아래로"
description ParaNumberBulletLevelUp = "문단번호/글머리표 한 수준 위로"
description ParaNumberDlg = "문단번호 대화상자"
description Paste = "붙이기"
description PastePage = "쪽 붙여넣기"
description PasteSpecial = "골라 붙이기"
description Preference = "환경 설정"
description Presentation = "프레젠테이션"
description PresentationDelete = "프레젠테이션 삭제"
description PresentationRange = "프레젠테이션 범위 설정."
description PresentationSetup = "프레젠테이션 설정"
description PrevTextBoxLinked = "현재 글상자가 선택되거나, 글상자 내부에 캐럿이"
description Print = "인쇄"
description PrintSetup = "인쇄옵션 - 워터 마크"
description PrintToImage = "그림으로 저장하기"
description PrintToPDF = "PDF인쇄"
description PrivateInfoChangePassword = "개인 정보 보안 암호 변경"
description PrivateInfoSetPassword = "개인 정보 보안 암호 설정"
description PutBullet = "글머리표 달기"
description PutNewParaNumber = "문단번호 새 번호 시작하기"
description PutOutlineNumber = "개요번호 달기"
description PutParaNumber = "문단번호 달기"
description QuickCommand = "- 입력 자동 명령 동작"
description QuickCorrect = "QCorrect 빠른 교정 ―내용 편집"
description QuickCorrect2 = "- 빠른 교정 ―내용 편집"
description QuickCorrect3 = "- 빠른 교정 ― 메뉴에서 효과음 On/Off"
description QuickCorrect4 = "빠른 교정 (실질적인 동작 Action)"
description QuickMarkInsert0 = "9 - 쉬운 책갈피 - 삽입"
description QuickMarkMove0 = "9 - 쉬운 책갈피 - 이동"
description RecalcPageCount = "현재 페이지의 쪽 번호 재계산"
description RecentCode = "최근에 사용한 문자표가 없을 경우에는 문자표 대"
description Redo = "다시 실행"
description RepeatFind = "다시 찾기"
description ReplyMemo = "메모 회신 한/글 2022 부터 지원"
description ReturnKeyInField = "No description"
description ReturnPrevPos = "직전위치로 돌아가기"
description ReverseFind = "거꾸로 찾기"
description ScanHFTFonts = "글꼴 검색"
description ScrMacroDefine = "매크로 정의 대화상자를 띄우고, 설정이 끝나면 매"
description ScrMacroPause = "매크로 기록 일시정지/재시작"
description ScrMacroPlay1 = "11 - #번 매크로 실행(Alt+Shift+#)"
description ScrMacroRepeatDlg = "No description"
description ScrMacroSecurityDlg = "No description"
description ScrMacroStop = "매크로 기록 중지"
description SendBrowserText = "브라우저로 보내기"
description SendMailAttach = "편지 보내기 - 첨부파일로"
description SendMailText = "편지 보내기 - 본문으로"
description SetLineNumbers = "줄 번호 넣기"
description Bottom = "생성한다."
description Top = "생성한다."
description tBottom = "생성한다."
description tTop = "생성한다."
description tom = "No description"
description ttom = "No description"
description ShowLineNumbers = "줄 번호 넣기"
description Soft = "- 보기"
description Sort = "소트"
description SpellingCheck = "맞춤법"
description SplitMemoOpen = "메모창 열기"
description Sum = "블록 합계"
description SuppressLineNumbers = "번호 넣기"
description para = "+ cell valign :테이블의 셀 내에"
description para2 = "+ cell valign :테이블의 셀 내에"
description para3 = "+ cell valign :테이블의 셀 내에"
description para4 = "+ cell valign :테이블의 셀 내에"
description para5 = "+ cell valign :테이블의 셀 내에"
description para6 = "+ cell valign :테이블의 셀 내에"
description para7 = "+ cell valign :테이블의 셀 내에"
description para8 = "+ cell valign :테이블의 셀 내에"
description para9 = "+ cell valign :테이블의 셀 내에"
description TextArtCreate = "글맵시"
description TextArtModify = "글맵시 고치기"
description TextArtShadow = "글맵시 그림자 넣기/빼기"
description TextArtShadowMobeToDown = "글맵시 그림자 위치 이동-아래로"
description TextArtShadowMobeToLeft = "글맵시 그림자 위치 이동-왼쪽으로"
description TextArtShadowMobeToRight = "글맵시 그림자 위치 이동-오른쪽으로"
description TextArtShadowMoveToUp = "글맵시 그림자 위치 이동-위로"
description TextBoxAlignCenterBottom = "글상자 정렬"
description TextBoxAlignCenterCenter = "글상자 정렬"
description TextBoxAlignCenterTop = "글상자 정렬"
description TextBoxAlignLeftBottom = "글상자 정렬"
description TextBoxAlignLeftCenter = "글상자 정렬"
description TextBoxAlignLeftTop = "글상자 정렬"
description TextBoxAlignRightBottom = "글상자 정렬"
description TextBoxAlignRightCenter = "글상자 정렬"
description TextBoxAlignRightTop = "글상자 정렬"
description TextBoxTextHorz = "글상자 문자 방향–가로 쓰기"
description TextBoxTextVert = "글상자 문자 방향–세로 쓰기–영문 눕힘"
description TextBoxTextVertAll = "글상자 문자 방향–세로 쓰기–영문 세움"
description TextBoxToggleDirection = "글상자 문자 방향–세로/가로 토글"
description TextBoxVAlignBottom = "글상자 세로 정렬-아래"
description TextBoxVAlignCenter = "글상자 세로 정렬-가운데"
description TextBoxVAlignTop = "글상자 세로 정렬-위"
description ToggleOverwrite = "Toggle Overwrite"
description TrackChangeApply = "변경추적:변경내용 적용"
description TrackChangeApplyAll = "변경추적:문서에서 변경내용 모두 적용"
description TrackChangeApplyNext = "변경추적:적용 후 다음으로 이동"
description TrackChangeApplyPrev = "변경추적:적용 후 이전으로 이동"
description TrackChangeApplyViewAll = "변경추적:표시된 변경내용 모두 적용"
description TrackChangeAuthor = "변경추적:사용자 이름 변경"
description TrackChangeCancel = "변경추적:변경내용 취소"
description TrackChangeCancelAll = "변경추적:문서에서 변경내용 모두 취소"
description TrackChangeCancelNext = "변경추적:취소 후 다음으로 이동"
description TrackChangeCancelPrev = "변경추적:취소 후 이전으로 이동"
description TrackChangeCancelViewAll = "변경추적:표시된 변경내용 모두 취소"
description TrackChangeNext = "변경추적:다음 변경내용"
description TrackChangeOption = "변경추적:변경 내용 추적 설정"
description TrackChangePrev = "변경추적:이전 변경내용"
description TrackChangeProtection = "변경추적:변경추적 보호"
description Undo = "되살리기"
description UnlinkTextBox = "글상자 연결 끊기"
description UserAutoFill = "No description"
description VersionDelete = "버전정보 지우기"
description VersionDeleteAll = "모든 버전정보 지우기"
description VersionInfo = "버전 정보"
description VersionSave = "버전 저장하기"
description VerticalText = "세로쓰기"
description ViewGridOption = "격자"
description ViewIdiom = "상용구 보기"
description ViewOptionColor = "보기 (회색조 보기 되돌리기 액션)"
description ViewOptionColorCustom = "보기"
description ViewOptionCtrlMark = "조판 부호"
description ViewOptionGray = "보기"
description ViewOptionGuideLine = "안내선"
description ViewOptionMemo = "No description"
description ViewOptionMemoGuideline = "No description"
description ViewOptionPaper = "쪽 윤곽 보기"
description ViewOptionParaMark = "문단 부호"
description ViewOptionPicture = "그림 보이기/숨기기([보기-그림]메뉴와 동일)"
description ViewOptionPronounce = "한자/일어 발음 표시 (Toggle)"
description ViewOptionPronounceSetting = "한자/일어 발음 표시 설정"
description ViewOptionRevision = "No description"
description ViewOptionTrackChange = "변경추적 보기"
description ViewOptionTrackChangeFinal = "변경추적 보기:최종본 보기"
description ViewOptionTrackChangeShape = "변경추적 보기:서식"
description ViewOptionTrackChnageInfo = "변경추적 보기:변경 내용 보기"
description ViewShowGrid = "격자 보이기"
description ViewZoom = "화면 확대(Ribbon)"
description ViewZoomFitPage = "화면 확대: 페이지에 맞춤"
description ViewZoomFitWidth = "화면 확대: 폭에 맞춤"
description ViewZoomLock = "잠금"
description ViewZoomNormal = "화면 확대: 정상"
description VoiceCommand = "- 음성 명령 설정"
description VoiceCommand2 = "- 음성 명령 레코딩 시작"
description VoiceCommand3 = "- 음성 명령 레코딩 중지"
description VoiceCommand4 = "+ 음성 명령창 보이기"
description VoiceCommand5 = "음성 명령 동작"
description function = "No description"
description var = "= pHwpCtrl.CreateAction(\"FileSetSecurity\");"
description var2 = "= null;"
description ifAction = "No description"
description dset = "dact.CreateSet();"
description ifAction2 = "&& dset) {"
description dsetSetItemPassword = "No description"
description dsetSetItemNoPrint = "No description"
description dsetSetItemNoCopy = "No description"
description ifAction3 = "{"
description var3 = "= \"배포용 문서 만들기 실패\";"
description ifAction4 = "<= 6) {"
description msg = "\"\n암호가 너무 짧습니다.\";"
description var4 = "= \"배포용 문서 만들기 실패\";"
description ifAction5 = "& 0x10) // 배포용 문서는 0x10 flag 를 포함한다."
description msg2 = "\"\n이미 배포용 문서로 지정된 상태입니다.\n암호를 변경하기 위해서는 먼저 일반 문서로 변경하십시오.\""
description elseAction = "(pHwpCtrl.EditMode == 0)"
description msg3 = "\"\n읽기 전용 문서입니다.\""
description function2 = "No description"
description pHwpCtrlMovePos3 = "커서를 문서의 맨 뒤로 이동"
description var5 = "= pHwpCtrl.CreateAction(\"BackwardFind\"); // 뒤에서부터 찾는다."
description var6 = "= act.CreateSet();"
description setSetItemIgnoreFindString = "No description"
description var7 = "= set.CreateItemSet(\"FindCharShape\", \"CharShape\");"
description subsetSetItemUnderlineType = "No description"
description var8 = "No description"
description var9 = "para, pos;"
description set = "pHwpCtrl.GetPosBySet();"
description list2 = "set.Item(\"List\");"
description para10 = "set.Item(\"Para\");"
description pos = "set.Item(\"Pos\");"
description function3 = "No description"
description var10 = "= pHwpCtrl.CreateAction(\"CharShape\");"
description var11 = "= dAct.CreateSet();"
description dSetSetItemTextColor = "// 글자 색을 파란색으로"
description function4 = "No description"
description pHwpCtrlMovePos2 = "페이지 맨 처음으로"
description var12 = "= true;"
description while = "{"
description OnTestApi1 = "현재줄의 맨 처음 단어 색깔 변경"
description con = "pHwpCtrl.MovePos(20); // 한줄 아래로 (예전 API 매뉴얼에는 21로 되어 있으나 잘못된 값임."

-- 총 457개 Misc 액션
