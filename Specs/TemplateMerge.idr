-- TemplateMerge.idr
-- Template-based B4 2-column merging with endnote preservation
-- Based on MCP analysis: Scripts/find_column_positions.py

module Specs.TemplateMerge

import Specs.HwpCommon

%default partial

-- ============================================================================
-- Template Structure (from MCP discovery)
-- ============================================================================

||| Template file: Tests/E2ETest/[양식]mad모의고사.hwp
||| Structure:
|||   - Page 1: B4 2-column layout (expandable)
|||   - Page 2: Endnote page (auto-generated, do NOT touch)
|||
||| Column Control (cold):
|||   - Position: List=0, Para=0, Pos=8
|||
||| Column Start Positions:
|||   - First column: (0, 1, 0) - immediately after cold control
|||   - Second column: (0, 3, 0) - created via BreakColumn
|||   - Third column: (0, 5, 0) - another BreakColumn
|||   - Pattern: Para increases by 2 for each column

public export
record DocPosition where
  constructor MkDocPos
  list : Nat
  para : Nat
  pos  : Nat

||| First column starting position (verified by MCP)
public export
firstColumnStart : DocPosition
firstColumnStart = MkDocPos 0 1 0

||| Calculate Nth column position (N starts from 1)
public export
nthColumnPosition : (n : Nat) -> DocPosition
nthColumnPosition n = MkDocPos 0 (1 + 2 * (n `minus` 1)) 0

-- ============================================================================
-- Endnote Page Constraint
-- ============================================================================

||| CRITICAL: Page 2 is for endnotes (problem explanations)
||| NEVER use BreakPage - it will corrupt the endnote structure
|||
||| How endnotes work:
|||   - When problems have footnotes/explanations (미주)
|||   - They automatically accumulate on Page 2
|||   - Page 2 is managed by HWP, not by us
|||
||| Solution: Expand Page 1 horizontally (add columns)
|||          NOT vertically (add pages)

public export
data PageType : Type where
  ContentPage  : PageType  -- Page 1: Our content (expandable)
  EndnotePage  : PageType  -- Page 2: Endnotes (auto-managed)

public export
data PageConstraint : PageType -> Type where
  ||| Page 1 can be expanded with BreakColumn
  ExpandableContent : PageConstraint ContentPage

  ||| Page 2 must NOT be touched
  ReadOnlyEndnotes : PageConstraint EndnotePage

-- ============================================================================
-- Column Operation State Machine
-- ============================================================================

||| States during template-based merging
public export
data MergeState : Type where
  TemplateOpened    : MergeState  -- Template file opened
  AtColumn          : (n : Nat) -> MergeState  -- Positioned at Nth column
  ContentInserted   : (n : Nat) -> MergeState  -- Content inserted in Nth column
  ColumnCreated     : (n : Nat) -> MergeState  -- New column created (N+1)

-- ============================================================================
-- Operations
-- ============================================================================

||| Position cursor at Nth column
||| Uses SetPos(0, 1 + 2*(N-1), 0)
public export
data PositionAtColumn : (n : Nat) -> MergeState -> Type where
  PositionFirst  : PositionAtColumn 1 TemplateOpened
  PositionNext   : PositionAtColumn n (ColumnCreated (n `minus` 1))

||| Insert content via copy-paste
public export
data InsertContent : (n : Nat) -> MergeState -> Type where
  InsertAtColumn : PositionAtColumn n s -> InsertContent n (AtColumn n)

||| Create next column via BreakColumn
||| IMPORTANT: NOT MoveNextColumn (which fails in template)
public export
data CreateNextColumn : (n : Nat) -> MergeState -> Type where
  BreakToNext : InsertContent n s -> CreateNextColumn (n + 1) (ContentInserted n)

-- ============================================================================
-- Complete Workflow
-- ============================================================================

||| Merge N problems into template
||| Each problem goes into one column
||| Page 1 expands to accommodate all problems
||| Page 2 (endnotes) remains untouched
public export
data TemplateMergeWorkflow : (problems : Nat) -> MergeState -> MergeState -> Type where
  ||| Merge single problem (simplest case)
  SingleProblem :
    PositionAtColumn 1 TemplateOpened ->
    InsertContent 1 (AtColumn 1) ->
    TemplateMergeWorkflow 1 TemplateOpened (ContentInserted 1)

  ||| Merge two problems (one page, two columns)
  TwoProblems :
    PositionAtColumn 1 TemplateOpened ->
    InsertContent 1 (AtColumn 1) ->
    CreateNextColumn 2 (ContentInserted 1) ->
    InsertContent 2 (AtColumn 2) ->
    TemplateMergeWorkflow 2 TemplateOpened (ContentInserted 2)

  ||| Merge multiple problems (expand page 1 as needed)
  MultipleProblems :
    (n : Nat) ->
    (workflow : List (PositionAtColumn n TemplateOpened, InsertContent n (AtColumn n))) ->
    TemplateMergeWorkflow n TemplateOpened (ContentInserted n)

-- ============================================================================
-- Validation Rules
-- ============================================================================

||| Verify column position calculation
public export
validateColumnPosition : (n : Nat) -> DocPosition -> Bool
validateColumnPosition n (MkDocPos l p _) =
  l == 0 && p == 1 + 2 * (n `minus` 1)

||| Verify BreakPage is never used
public export
data ForbiddenOperation : Type where
  BreakPageUsed : ForbiddenOperation  -- NEVER allowed

||| Only BreakColumn is allowed for expansion
public export
data AllowedOperation : Type where
  BreakColumnUsed : AllowedOperation
  CopyPasteUsed   : AllowedOperation
  SetPosUsed      : AllowedOperation

-- ============================================================================
-- Implementation Constraints
-- ============================================================================

||| Constraint 1: Always use SetPos for positioning
||| MoveDocBegin + navigation is unreliable
public export
useSetPosForColumns : String
useSetPosForColumns = "Use SetPos(0, 1 + 2*(N-1), 0) for column positioning"

||| Constraint 2: Use BreakColumn, not MoveNextColumn
||| MoveNextColumn returns None in empty template
public export
useBreakColumnNotMoveNext : String
useBreakColumnNotMoveNext = "MoveNextColumn fails. Use BreakColumn to create next column"

||| Constraint 3: Never use BreakPage
||| Page 2 is endnote page - must preserve
public export
neverBreakPage : String
neverBreakPage = "BreakPage corrupts endnote page. Expand Page 1 with BreakColumn only"

||| Constraint 4: Template is pre-configured
||| No need for PageSetup or ColumnDef
public export
templatePreConfigured : String
templatePreConfigured = "Template has B4 2-column. Do not apply PageSetup/ColumnDef"

-- ============================================================================
-- Helper Functions
-- ============================================================================

||| Calculate how many columns needed for N problems
public export
columnsNeeded : Nat -> Nat
columnsNeeded n = n

||| Calculate how many BreakColumn operations needed
||| First column exists, so N-1 breaks needed
public export
breakColumnsNeeded : Nat -> Nat
breakColumnsNeeded Z = 0
breakColumnsNeeded (S n) = n

-- ============================================================================
-- Example Usage
-- ============================================================================

||| Example: Merge 20 problems from CSV
||| Result: 20 columns on Page 1, Page 2 has endnotes
public export
example20Problems : TemplateMergeWorkflow 20 TemplateOpened (ContentInserted 20)
example20Problems = MultipleProblems 20 []  -- Placeholder, actual implementation in Python
