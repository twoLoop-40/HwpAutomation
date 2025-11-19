"""
HWP API 문서(PDF)를 추출하여 Idris2 형태로 정리

Usage:
    python Scripts/extract_hwp_api.py
"""

import sys
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

try:
    import PyPDF2
except ImportError:
    print("PyPDF2가 필요합니다")
    print("설치: pip install PyPDF2")
    sys.exit(1)

try:
    import pdfplumber
except ImportError:
    print("pdfplumber 필요합니다")
    print("설치: pip install pdfplumber")
    sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF에서 텍스트 추출"""
    print(f'PDF 읽기: {pdf_path}')

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f'총 {total_pages} 페이지')

            text_parts = []
            for i, page in enumerate(pdf.pages, 1):
                if i % 10 == 0:
                    print(f'  진행: {i}/{total_pages} 페이지...')

                text = page.extract_text()
                if text:
                    text_parts.append(text)

            print(f'추출 완료!')
            return '\n\n'.join(text_parts)

    except Exception as e:
        print(f'오류: {e}')
        return ""


def extract_movesel_commands(text: str) -> list:
    """MoveSel 관련 명령 추출"""
    lines = text.split('\n')
    movesel_sections = []

    in_movesel = False
    current_section = []

    for line in lines:
        if 'MoveSel' in line:
            in_movesel = True
            current_section = [line]
        elif in_movesel:
            current_section.append(line)
            # 빈 줄 2개 연속이면 섹션 종료
            if len(current_section) > 3 and not line.strip():
                movesel_sections.append('\n'.join(current_section))
                in_movesel = False
                current_section = []

    return movesel_sections


def create_idris_spec(output_path: str, api_data: dict):
    """Idris2 형식 명세 생성"""

    idris_content = f"""-- HWP API 명세 (자동 생성)
-- Source: ActionTable_2504.pdf
-- Generated: {output_path}

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
"""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(idris_content)

    print(f'\nIdris2 명세 생성: {output_file}')


def main():
    print('=' * 70)
    print('HWP API 문서 추출 및 Idris2 정리')
    print('=' * 70)

    # ActionTable PDF 추출
    action_table_pdf = Path("HwpBooks/ActionTable_2504.pdf")

    if not action_table_pdf.exists():
        print(f'PDF 파일이 없습니다: {action_table_pdf}')
        return

    # 텍스트 추출
    print('\n[1/3] ActionTable PDF 텍스트 추출')
    full_text = extract_text_from_pdf(str(action_table_pdf))

    # 추출된 텍스트 저장
    text_output = Path("HwpIdris/ActionTable_extracted.txt")
    text_output.parent.mkdir(parents=True, exist_ok=True)

    with open(text_output, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f'텍스트 저장: {text_output}')
    print(f'텍스트 길이: {len(full_text):,} 글자')

    # MoveSel 명령 추출
    print('\n[2/3] MoveSel 명령 추출')
    movesel_sections = extract_movesel_commands(full_text)

    print(f'MoveSel 관련 섹션: {len(movesel_sections)}개')

    # MoveSel 섹션 저장
    movesel_output = Path("HwpIdris/MoveSel_commands.txt")
    with open(movesel_output, 'w', encoding='utf-8') as f:
        f.write('\n\n' + '='*70 + '\n\n'.join(movesel_sections))

    print(f'MoveSel 명령 저장: {movesel_output}')

    # Idris2 명세 생성
    print('\n[3/3] Idris2 명세 생성')

    api_data = {
        'movesel_commands': movesel_sections,
    }

    create_idris_spec("HwpIdris/ActionTable.idr", api_data)

    print('\n' + '=' * 70)
    print('완료!')
    print('생성된 파일:')
    print(f'  - {text_output}')
    print(f'  - {movesel_output}')
    print(f'  - HwpIdris/ActionTable.idr')
    print('=' * 70)


if __name__ == "__main__":
    main()
