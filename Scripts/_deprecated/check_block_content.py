"""
블록 내용 확인 스크립트
"""
import sys
import codecs
sys.path.insert(0, r'c:\\Users\\joonho.lee\\Projects\\AutoHwp')

from core.hwp_extractor import open_hwp

input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"

print(f"파일 열기: {input_file}\n")

with open_hwp(input_file) as hwp:
    # 블록 7의 위치: (0, 28, 0) ~ (0, 43, 0)
    print("블록 28 ~ 43 영역 선택...")

    # Para 28로 이동
    hwp.SetPos(0, 28, 0)

    # Para 28~42까지 텍스트 읽기
    texts = []
    for para_idx in range(28, 43):
        hwp.SetPos(0, para_idx, 0)
        hwp.Run("ParagraphShapeTravel")
        text = hwp.GetTextFile("TEXT")
        texts.append(f"Para {para_idx}: {text[:100] if text else '(empty)'}")

    print("\\n".join(texts[:5]))  # 처음 5개만
    print(f"\\n총 {len(texts)}개 문단")

    # 문단 수 확인
    hwp.InitScan(Range=0x0077)  # 선택 영역만
    para_count = 0
    while True:
        state, text = hwp.GetText()
        if state in [0, 1]:  # 문단 끝 또는 마지막
            para_count += 1
            if state == 1:  # 마지막
                break

    hwp.ReleaseScan()

    print(f"문단 수: {para_count}")
