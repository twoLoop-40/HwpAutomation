"""
제 코드 vs math-collector 코드 비교
"""
import sys
import codecs

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

print("=== 코드 비교 ===\n")

print("1. 제 코드 (실패):")
print("""
def save_block(hwp, filepath: str, fmt: str = "HWP") -> bool:
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result
""")

print("\n2. math-collector 코드 (성공):")
print("""
def save_block(hwp: CDispatch, *, filepath: str | Path, fmt: str = "HWP") -> bool:
    filepath_str = str(filepath)

    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath_str
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result_bool: bool = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

    return result_bool
""")

print("\n차이점:")
print("1. filepath를 str()로 명시적 변환")
print("2. 타입 힌트 추가 (CDispatch, Path)")
print("3. result_bool: bool 명시적 타입")
print("\n하지만 실제 로직은 동일합니다!")

print("\n\n=== select_and_save 함수 ===")
print("""
def select_and_save(hwp, idx, origin_num, csv_filename):
    block = get_block(hwp, idx)

    def save_selected_block(src):
        start, end = block

        # 블록 선택
        hwp.SetPos(*start)
        hwp.Run("Select")
        hwp.SetPos(*end)

        # 파일 경로 생성
        target_path = make_hwp_path(src, origin_num, csv_filename=csv_filename)

        # 저장
        result = save_block(hwp, filepath=target_path)

        return result, target_path

    return save_selected_block
""")

print("\n핵심: math-collector는 **함수를 반환**합니다!")
print("saver = select_and_save(...) → 함수 반환")
print("saver(src) → 실제 실행")
