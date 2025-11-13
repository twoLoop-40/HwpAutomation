한글 오토메이션을 사용할 때 로컬 파일에 접근하거나 저장하려고 하면 보안 승인 메시지가 나타납니다.
첨부된 ‘보안모듈(Automation).zip’ 파일은 보안 승인 메시지가 나타나지 않도록 처리하는 모듈로 파일에 대한 유효성과 보안 확인을 처리합니다.

위 첨부 파일을 다운로드한 후 압축을 해제하시기 바랍니다.
▪ 보안모듈(FilePathCeckerModuleExample.dll)
▪ 보안모듈 등록 위치(레지스트리.JPG)

보안모듈을 특정 위치에 설치한 다음 '레지스트리.JPG'를 따라 보안모듈의 이름과 전체 경로를 레지스트리로 등록하고 사용하시기 바랍니다.
추가로 프로그램 소스 코드에서도 다음과 같이 보안모듈을 추가해야 합니다.
▪ HwpObject.RegisterModule("FilePathCheckDLL", "FilePathCheckerModuleExample");
▪ RegisterModule()의 자세한 설명은 매뉴얼을 참고하시기 바랍니다.