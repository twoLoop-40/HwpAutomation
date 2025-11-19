"""[정답] 패턴 기반 문제 분리 테스트"""
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

# HWPX 파일에서 텍스트 추출
hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

with zipfile.ZipFile(hwpx_file, 'r') as zf:
    xml_content = zf.read('Contents/section0.xml')
    root = ET.fromstring(xml_content)
    
    ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
    text_elements = root.findall('.//hh:t', ns)
    
    full_text = ''.join(t.text if t.text else '' for t in text_elements)

print(f"전체 텍스트 길이: {len(full_text):,} 문자\n")

# [정답] 패턴으로 분리
answer_pattern = r'\[정답\]\s*[➀-➄]'
matches = list(re.finditer(answer_pattern, full_text))

print(f"[정답] 개수: {len(matches)}개\n")

# 문제 분리
problems = []

# 첫 문제: 시작 ~ 첫 번째 [정답]
if matches:
    first_problem = full_text[:matches[0].start()]
    problems.append(("문제 1", first_problem))
    
    # 나머지 문제: [정답] i-1 이후 ~ [정답] i
    for i in range(len(matches) - 1):
        problem_start = matches[i].end()  # 이전 [정답] 직후
        problem_end = matches[i+1].start()  # 다음 [정답] 직전
        problem_text = full_text[problem_start:problem_end]
        problems.append((f"문제 {i+2}", problem_text))
    
    # 마지막: 마지막 [정답] 이후 (있다면)
    if matches:
        last_text = full_text[matches[-1].end():]
        if last_text.strip():
            problems.append((f"문제 {len(matches)+1}", last_text))

print(f"총 {len(problems)}개 문제 추출\n")
print("="*60)

# 처음 5개 문제 출력
for i, (title, text) in enumerate(problems[:5]):
    print(f"\n{title}")
    print("="*60)
    # 처음 500자만
    preview = text[:500].strip()
    print(preview)
    print(f"\n... (총 {len(text)} 문자)")

# TXT 파일로 저장
output_dir = Path(r"Tests\seperation\output_text_test")
output_dir.mkdir(parents=True, exist_ok=True)

for i, (title, text) in enumerate(problems[:10], 1):
    output_file = output_dir / f"문제_{i:03d}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text.strip())
    print(f"\n저장: {output_file.name} ({len(text)} 문자)")

print(f"\n\n완료: {output_dir}")
