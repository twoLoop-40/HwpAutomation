module Specs.Consolidator.FolderTreeView

import Data.String

%default total

-- Treeview 기반 폴더 브라우저 명세
-- Windows 탐색기 스타일 트리 구조

||| 트리 노드 타입
public export
data NodeType = DriveNode | FolderNode | LoadingNode

||| 트리 노드 상태
public export
data NodeState = Collapsed | Expanded | Loading

||| 트리 노드
public export
record TreeNode where
  constructor MkNode
  id : String           -- 노드 ID (경로)
  name : String         -- 표시 이름
  nodeType : NodeType   -- 노드 타입
  state : NodeState     -- 펼침/접힘 상태
  parent : Maybe String -- 부모 노드 ID

||| 트리뷰 액션
public export
data TreeAction : Type where
  ExpandNode : String -> TreeAction        -- 노드 펼치기
  CollapseNode : String -> TreeAction      -- 노드 접기
  LoadChildren : String -> TreeAction      -- 자식 노드 로드
  ToggleCheckbox : String -> TreeAction    -- 체크박스 토글 (☐ ↔ ☑)
  AddToSelection : String -> TreeAction    -- 선택 목록에 추가
  RemoveFromSelection : String -> TreeAction  -- 선택 목록에서 제거

||| 트리뷰 상태 전환
public export
transition : NodeState -> TreeAction -> NodeState
transition Collapsed (ExpandNode _) = Loading
transition Loading (LoadChildren _) = Expanded
transition Expanded (CollapseNode _) = Collapsed
transition s _ = s

||| 드라이브 목록 로드
|||
||| "내 PC" 노드를 펼치면 A-Z 드라이브 열거
public export
data DriveLoadResult = DriveList (List String)

||| 폴더 목록 로드
|||
||| 특정 경로의 하위 폴더 목록 반환
public export
data FolderLoadResult = FolderList String (List String)

||| 트리뷰 초기화
|||
||| 루트: "내 PC" (Collapsed 상태)
public export
initialTree : TreeNode
initialTree = MkNode "내 PC" "내 PC" DriveNode Collapsed Nothing

||| 노드 펼침 시 로딩 노드 추가
|||
||| 자식이 로드되기 전 "로딩 중..." 표시
public export
loadingNode : String -> TreeNode
loadingNode parentId = MkNode
  (parentId ++ "/loading")
  "로딩 중..."
  LoadingNode
  Collapsed
  (Just parentId)

||| 드라이브 노드 생성
|||\
||| 드라이브 노드는 체크박스(☐)와 아이콘(💾)을 포함
||| 예: "☐ 💾 C:"
public export
createDriveNode : String -> TreeNode
createDriveNode letter = MkNode
  (letter ++ ":\\")
  ("☐ 💾 " ++ letter ++ ":")
  DriveNode
  Collapsed
  (Just "내 PC")

||| 경로 결합 (Windows 경로 구분자 처리)
|||
||| 드라이브 루트(C:\) + 폴더 → C:\Folder
||| 일반 폴더(C:\Foo) + 폴더 → C:\Foo\Folder
|||
||| 주의: 실제 Python 구현 시 os.path.join 또는 pathlib.Path 사용 권장
public export
joinPath : String -> String -> String
joinPath parent child =
  if parent == "내 PC" then
    child  -- "내 PC" + "C:" → "C:"
  else if isSuffixOf "\\" parent then
    parent ++ child  -- "C:\" + "Folder" → "C:\Folder"
  else
    parent ++ "\\" ++ child  -- "C:\Foo" + "Bar" → "C:\Foo\Bar"

||| 폴더 노드 생성 (인자 2개)
|||\
||| 폴더 노드는 체크박스(☐)와 아이콘(📁)을 포함
||| 예: "☐ 📁 Documents"
||| 선택 시 체크박스가 ☑로 변경됨
public export
createFolderNode : String -> String -> TreeNode
createFolderNode parentPath folderName = MkNode
  (joinPath parentPath folderName)
  ("☐ 📁 " ++ folderName)
  FolderNode
  Collapsed
  (Just parentPath)

||| 노드가 펼쳐질 수 있는지 검증
public export
canExpand : NodeType -> Bool
canExpand DriveNode = True
canExpand FolderNode = True
canExpand LoadingNode = False

||| 노드 펼침 증명
|||
||| DriveNode와 FolderNode만 펼칠 수 있음
public export
expandableProof : (nt : NodeType) -> canExpand nt = True -> Either (nt = DriveNode) (nt = FolderNode)
expandableProof DriveNode Refl = Left Refl
expandableProof FolderNode Refl = Right Refl
expandableProof LoadingNode Refl impossible

-- 트리 구조 불변성
--
-- 1. 모든 노드의 parent는 "내 PC" 또는 실제 경로
-- 2. LoadingNode는 선택할 수 없음
-- 3. 노드 ID는 유일함

-- === 체크박스 기반 선택 모델 ===
--
-- UI 상호작용:
--   - 화살표 클릭: 노드 펼치기/접기 (선택 X)
--   - 폴더/드라이브 이름 클릭: 체크박스 토글 (☐ ↔ ☑)
--
-- 시각적 피드백:
--   - ☐: 선택되지 않음
--   - ☑: 선택됨
--
-- 양방향 동기화:
--   - 트리뷰 클릭 → 오른쪽 리스트에 추가/제거
--   - 오른쪽 리스트에서 제거 → 트리뷰 체크박스 해제
--
-- 구현 세부사항:
--   - path_to_node 매핑으로 양방향 참조 유지
--   - 텍스트 첫 문자(☐/☑) 교체로 상태 표시
--   - <ButtonRelease-1> 이벤트로 펼치기/접기 후 클릭 처리
