"""
본문과 미주 영역 분리

본문: 문제 본문 (선택지 포함)
미주: 정답 해설
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import re

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def separate_body_and_endnotes(hwpx_path: str):
    """본문과 미주 분리"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        xml_content = zf.read('Contents/section0.xml')
        root = ET.fromstring(xml_content)

        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        print("=== 본문과 미주 분리 ===\n")

        # 1. 전체 문단 수
        all_paras = root.findall('.//hh:p', namespaces)
        print(f"1. 전체 문단 수: {len(all_paras)}개\n")

        # 2. 미주 요소
        endnotes = root.findall('.//hh:endNote', namespaces)
        if not endnotes:
            endnotes = root.findall('.//endNote')

        print(f"2. 미주(endNote) 태그: {len(endnotes)}개\n")

        # 3. 미주 내부 문단
        endnote_paras = []
        for endnote in endnotes:
            paras_in_endnote = endnote.findall('.//hh:p', namespaces)
            if not paras_in_endnote:
                paras_in_endnote = endnote.findall('.//p')
            endnote_paras.extend(paras_in_endnote)

        print(f"3. 미주 내부 문단: {len(endnote_paras)}개\n")

        # 4. 본문 문단 (전체 - 미주)
        body_para_count = len(all_paras) - len(endnote_paras)
        print(f"4. 본문 문단 (추정): {body_para_count}개\n")

        # 5. 미주별 [정답] 개수
        print(f"5. 미주 내용 분석:\n")

        answer_count = 0
        for i, endnote in enumerate(endnotes[:20]):  # 처음 20개만
            texts = endnote.findall('.//hh:t', namespaces)
            if not texts:
                texts = endnote.findall('.//t')

            endnote_text = ''.join(t.text for t in texts if t.text)

            # [정답] 포함 여부
            has_answer = '[정답]' in endnote_text
            if has_answer:
                answer_count += 1

            print(f"   [미주 {i+1:3d}] {len(endnote_text):4d}자, [정답]: {'O' if has_answer else 'X'} | {endnote_text[:80]}")

        # 전체 미주에서 [정답] 개수
        total_answers = 0
        for endnote in endnotes:
            texts = endnote.findall('.//hh:t', namespaces)
            if not texts:
                texts = endnote.findall('.//t')
            endnote_text = ''.join(t.text for t in texts if t.text)
            if '[정답]' in endnote_text:
                total_answers += 1

        print(f"\n   총 [정답] 포함 미주: {total_answers}개 / {len(endnotes)}개\n")

        # 6. 본문 영역 텍스트 분석
        print(f"6. 본문 영역 분석:\n")

        # 본문 영역의 텍스트 (미주 제외)
        # 방법: 전체 문단 - 미주 내 문단

        # 전체 텍스트
        all_texts = root.findall('.//hh:t', namespaces)
        full_text = ''.join(t.text for t in all_texts if t.text)

        # 미주 텍스트
        endnote_texts_combined = []
        for endnote in endnotes:
            texts = endnote.findall('.//hh:t', namespaces)
            if not texts:
                texts = endnote.findall('.//t')
            endnote_texts_combined.append(''.join(t.text for t in texts if t.text))

        total_endnote_chars = sum(len(t) for t in endnote_texts_combined)

        print(f"   전체 텍스트: {len(full_text):,} 문자")
        print(f"   미주 텍스트: {total_endnote_chars:,} 문자")
        print(f"   본문 텍스트 (추정): {len(full_text) - total_endnote_chars:,} 문자\n")

        # 7. 본문의 선택지 기호 개수
        choice_pattern = r'[➀-➄]'
        choices_in_full = len(re.findall(choice_pattern, full_text))

        endnote_full_text = ''.join(endnote_texts_combined)
        choices_in_endnotes = len(re.findall(choice_pattern, endnote_full_text))

        choices_in_body = choices_in_full - choices_in_endnotes

        print(f"7. 선택지 기호 분석:\n")
        print(f"   전체 선택지: {choices_in_full}개")
        print(f"   미주 내 선택지: {choices_in_endnotes}개")
        print(f"   본문 선택지: {choices_in_body}개")
        print(f"   추정 문제 수 (본문 기준): {choices_in_body // 5}개\n")

        print(f"\n=== 최종 결과 ===\n")
        print(f"총 미주: {len(endnotes)}개")
        print(f"[정답] 포함 미주: {total_answers}개")
        print(f"추정 문제 수: {choices_in_body // 5}개")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    separate_body_and_endnotes(hwpx_file)
