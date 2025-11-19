"""
HWP Parser - HWP COM API 기반 파서

Idris2 명세: Specs/Separator/Separator/HwpParser.idr
참조: math-collector/src/tools/handle_hwp.py:iter_note_blocks
"""

import contextlib
import pythoncom
import win32com.client as win32
from typing import List, Tuple, Generator
from .types import EndNoteInfo, EndNoteNumber, ElementPosition

# list, para, pos
Pos = Tuple[int, int, int]
Block = Tuple[Pos, Pos]


class HwpParser:
    """HWP COM API 기반 파서 (iter_note_blocks 패턴)"""

    def __init__(self, file_path: str, verbose: bool = False):
        self.file_path = file_path
        self.verbose = verbose
        self.hwp = None
        self.endnotes = []

    def log(self, message: str):
        if self.verbose:
            print(f"[HwpParser] {message}")

    @contextlib.contextmanager
    def _open_hwp(self):
        """HWP 파일 열기 (컨텍스트 매니저)"""
        pythoncom.CoInitialize()
        hwp = None

        try:
            hwp = win32.DispatchEx("HwpFrame.HwpObject")
            hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

            # 읽기 전용 + 편집 락 해제 + 대화상자 생략
            arg = "lock:false;forceopen:true;readonly:true"
            hwp.Open(self.file_path, "HWP", arg)
            hwp.XHwpWindows.Item(0).Visible = False

            yield hwp

        finally:
            if hwp:
                try:
                    hwp.XHwpDocuments.Active_XHwpDocument.Close(False)
                    hwp.Quit()
                finally:
                    pythoncom.CoUninitialize()

    def parse(self) -> List[EndNoteInfo]:
        """HWP 파일에서 EndNote 위치 추출 (iter_note_blocks 패턴)

        Returns:
            EndNote 리스트 (앵커 위치 포함)
        """
        self.log(f"파싱 시작: {self.file_path}")

        with self._open_hwp() as hwp:
            self.log("EndNote 앵커 찾기...")
            endnotes = self._find_endnote_anchors(hwp)
            self.endnotes = endnotes

        self.log(f"파싱 완료: {len(self.endnotes)}개 EndNote 발견")
        return self.endnotes

    def _find_endnote_anchors(self, hwp) -> List[EndNoteInfo]:
        """EndNote 앵커 위치 찾기 (iter_note_blocks 로직)

        핵심 로직:
        - HeadCtrl로 EndNote 순회
        - GetAnchorPos(0)로 본문의 앵커 위치 얻기
        - 앵커 위치 = 문제 경계
        """
        hwp.Run("MoveDocBegin")
        ctrl = hwp.HeadCtrl

        endnotes = []
        endnote_num = 1

        while ctrl:
            if ctrl.CtrlID == 'en':  # EndNote 발견
                pset = ctrl.GetAnchorPos(0)
                lst = pset.Item("List")
                para = pset.Item("Para")
                pos = pset.Item("Pos")

                # EndNote 정보 저장
                endnote = EndNoteInfo(
                    number=EndNoteNumber(endnote_num),
                    position=ElementPosition(
                        index=self._pos_to_index(lst, para, pos),
                        xpath=None  # HWP COM에서는 xpath 불필요
                    ),
                    suffix_char='.',  # 기본값
                    inst_id='',  # HWP COM에서는 불필요
                    para_count=0,  # TODO: 필요시 계산
                    char_count=0   # TODO: 필요시 계산
                )
                endnotes.append(endnote)
                self.log(f"EndNote {endnote_num}: List={lst}, Para={para}, Pos={pos}")
                endnote_num += 1

            ctrl = ctrl.Next

        return endnotes

    def _pos_to_index(self, lst: int, para: int, pos: int) -> int:
        """HWP Position (list, para, pos)를 단일 인덱스로 변환

        간단한 해싱: list * 1000000 + para * 1000 + pos
        """
        return lst * 1000000 + para * 1000 + pos

    def get_text_between(
        self,
        start_idx: int,
        end_idx: int,
        include_endnote: bool = True
    ) -> str:
        """지정 범위의 텍스트 추출

        Args:
            start_idx: 시작 위치 (이전 EndNote 앵커)
            end_idx: 끝 위치 (현재 EndNote 앵커)
            include_endnote: EndNote 포함 여부

        Returns:
            추출된 텍스트

        Note:
            HWP COM API는 SetPos + Select + GetText 방식 사용
        """
        with self._open_hwp() as hwp:
            # Position 인덱스를 (list, para, pos)로 복원
            start_pos = self._index_to_pos(start_idx)
            end_pos = self._index_to_pos(end_idx)

            # 블록 선택
            hwp.SetPos(*start_pos)
            hwp.Run("Select")
            hwp.SetPos(*end_pos)

            # 텍스트 가져오기
            text = hwp.GetText()

            return text

    def _index_to_pos(self, index: int) -> Tuple[int, int, int]:
        """단일 인덱스를 HWP Position (list, para, pos)로 변환"""
        lst = index // 1000000
        para = (index % 1000000) // 1000
        pos = index % 1000
        return (lst, para, pos)

    def get_total_elements(self) -> int:
        """전체 요소 개수 (사용 안 함)"""
        return 0  # HWP COM에서는 불필요
