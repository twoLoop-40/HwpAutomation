-- PageLayoutMCP.idr
-- Page and Column Layout Settings for HWP Automation
-- Based on MCP inspection: Scripts/inspect_parameters.py

module Specs.PageLayoutMCP

import Specs.HwpCommon

%default partial

-- ============================================================================
-- Page Setup Parameters (HPageDef)
-- ============================================================================

||| Paper size in hwpunit (1mm = 100 hwpunit)
public export
data PaperSize : Type where
  A4 : PaperSize          -- 210mm × 297mm
  B4 : PaperSize          -- 257mm × 364mm
  Custom : (width : Nat) -> (height : Nat) -> PaperSize

||| Convert PaperSize to hwpunit dimensions
public export
paperDimensions : PaperSize -> (Nat, Nat)
paperDimensions A4 = (21000, 29700)
paperDimensions B4 = (25700, 36400)
paperDimensions (Custom w h) = (w, h)

||| Page margins in hwpunit
public export
record PageMargins where
  constructor MkMargins
  left   : Nat
  right  : Nat
  top    : Nat
  bottom : Nat
  header : Nat
  footer : Nat

||| Standard margin presets
public export
standardMargins : PageMargins
standardMargins = MkMargins 2000 2000 2000 2000 1000 1000  -- 20mm each, 10mm header/footer

public export
narrowMargins : PageMargins
narrowMargins = MkMargins 1500 1500 1500 1500 1000 1000  -- 15mm each

||| Page orientation
public export
data Orientation : Type where
  Portrait  : Orientation
  Landscape : Orientation

||| Complete page setup configuration
public export
record PageSetupConfig where
  constructor MkPageSetup
  paperSize   : PaperSize
  margins     : PageMargins
  orientation : Orientation

||| Standard A4 portrait setup
public export
defaultA4 : PageSetupConfig
defaultA4 = MkPageSetup A4 standardMargins Portrait

||| Standard B4 portrait setup
public export
defaultB4 : PageSetupConfig
defaultB4 = MkPageSetup B4 standardMargins Portrait

-- ============================================================================
-- Column Definition Parameters (HColDef)
-- ============================================================================

||| CRITICAL FINDING: ColumnDef requires content in document
||| Empty documents cannot apply column settings (Execute returns False)
|||
||| Constraint: ApplyColumnDef requires DocumentState = Modified
|||            (i.e., document must have content)
public export
data ColumnCount : Type where
  SingleColumn : ColumnCount
  TwoColumn    : ColumnCount
  ThreeColumn  : ColumnCount
  CustomColumn : (n : Nat) -> ColumnCount

||| Column layout type
public export
data ColumnLayout : Type where
  EqualWidth    : ColumnLayout  -- Layout = 0: Same width
  ProportionalWidth : ColumnLayout  -- Layout = 1: Different widths

||| Column configuration
public export
record ColumnConfig where
  constructor MkColumnConfig
  count      : ColumnCount
  layout     : ColumnLayout
  sameGap    : Bool             -- Same gap between columns
  -- Note: ColumnGap parameter does not exist in HColDef
  -- Gap must be managed through WidthGap array

-- ============================================================================
-- Page Layout State Machine
-- ============================================================================

||| Page layout states
||| Tracks whether page/column settings can be applied
public export
data LayoutState : Type where
  EmptyDocument   : LayoutState  -- Cannot apply ColumnDef
  HasContent      : LayoutState  -- Can apply both PageSetup and ColumnDef
  LayoutApplied   : LayoutState  -- Settings already applied

||| State transition: Adding content enables column settings
public export
addContent : LayoutState -> LayoutState
addContent EmptyDocument = HasContent
addContent s = s

||| State transition: Applying layout
public export
applyLayout : LayoutState -> LayoutState
applyLayout HasContent = LayoutApplied
applyLayout s = s

-- ============================================================================
-- Layout Operations with Preconditions
-- ============================================================================

||| Apply page setup (can be done on empty document)
public export
data ApplyPageSetup : PageSetupConfig -> LayoutState -> Type where
  SetupOnEmpty    : (cfg : PageSetupConfig) -> ApplyPageSetup cfg EmptyDocument
  SetupWithContent : (cfg : PageSetupConfig) -> ApplyPageSetup cfg HasContent

||| Apply column definition (REQUIRES content in document)
public export
data ApplyColumnDef : ColumnConfig -> LayoutState -> Type where
  DefineColumns : (cfg : ColumnConfig) -> ApplyColumnDef cfg HasContent

||| Complete B4 2-column setup requires specific order:
||| 1. Create document (EmptyDocument)
||| 2. Apply PageSetup (optional, but recommended)
||| 3. Insert content (EmptyDocument -> HasContent)
||| 4. Apply ColumnDef (HasContent -> LayoutApplied)
public export
data B4TwoColumnWorkflow : LayoutState -> LayoutState -> Type where
  ||| Full workflow from empty document to B4 2-column
  CompleteWorkflow :
    (pageSetup : PageSetupConfig) ->
    (colConfig : ColumnConfig) ->
    B4TwoColumnWorkflow EmptyDocument LayoutApplied

-- ============================================================================
-- Validated Builders
-- ============================================================================

||| Build B4 2-column configuration
public export
b4TwoColumn : ColumnConfig
b4TwoColumn = MkColumnConfig TwoColumn EqualWidth True

||| Validated B4 2-column workflow
||| Ensures correct application order
public export
createB4TwoColumn : B4TwoColumnWorkflow EmptyDocument LayoutApplied
createB4TwoColumn = CompleteWorkflow defaultB4 b4TwoColumn

-- ============================================================================
-- Parameter Validation from MCP Inspection
-- ============================================================================

||| Known valid PageSetup parameters (from inspect_parameters.py)
public export
data HPageDefParam : Type where
  PaperWidth_   : HPageDefParam
  PaperHeight_  : HPageDefParam
  LeftMargin_   : HPageDefParam
  RightMargin_  : HPageDefParam
  TopMargin_    : HPageDefParam
  BottomMargin_ : HPageDefParam
  HeaderLen_    : HPageDefParam
  FooterLen_    : HPageDefParam
  GutterLen_    : HPageDefParam
  GutterType_   : HPageDefParam
  Landscape_    : HPageDefParam

||| Known valid ColumnDef parameters
public export
data HColDefParam : Type where
  Count_     : HColDefParam
  Layout_    : HColDefParam
  SameGap_   : HColDefParam
  SameSize_  : HColDefParam
  LineType_  : HColDefParam
  LineWidth_ : HColDefParam
  LineColor_ : HColDefParam
  WidthGap_  : HColDefParam  -- HArray type

||| Parameter set with validated fields
public export
record ValidatedPageSetup where
  constructor MkValidatedPageSetup
  paperWidth   : Nat
  paperHeight  : Nat
  leftMargin   : Nat
  rightMargin  : Nat
  topMargin    : Nat
  bottomMargin : Nat
  headerLen    : Nat
  footerLen    : Nat
  landscape    : Bool

||| Convert high-level config to validated parameter set
public export
toValidatedPageSetup : PageSetupConfig -> ValidatedPageSetup
toValidatedPageSetup (MkPageSetup size margins orient) =
  let (w, h) = paperDimensions size
      isLandscape = case orient of
                      Portrait => False
                      Landscape => True
  in MkValidatedPageSetup w h
                          margins.left margins.right
                          margins.top margins.bottom
                          margins.header margins.footer
                          isLandscape

public export
record ValidatedColumnDef where
  constructor MkValidatedColumnDef
  count    : Nat
  layout   : Nat  -- 0 = equal width, 1 = proportional
  sameGap  : Bool
  sameSize : Bool

public export
toValidatedColumnDef : ColumnConfig -> ValidatedColumnDef
toValidatedColumnDef (MkColumnConfig count layout sameGap) =
  let countVal = case count of
                   SingleColumn => 1
                   TwoColumn => 2
                   ThreeColumn => 3
                   CustomColumn n => n
      layoutVal = case layout of
                    EqualWidth => 0
                    ProportionalWidth => 1
  in MkValidatedColumnDef countVal layoutVal sameGap True

-- ============================================================================
-- Execution Preconditions
-- ============================================================================

||| PageSetup execution result
||| MCP shows: Execute returns True, but settings may not apply correctly
||| Additional verification needed after Execute
public export
data PageSetupResult : Type where
  PageSetupSuccess : ValidatedPageSetup -> PageSetupResult
  PageSetupFailed  : String -> PageSetupResult

||| ColumnDef execution result
||| MCP shows: Execute returns False on empty document
public export
data ColumnDefResult : Type where
  ColumnDefSuccess : ValidatedColumnDef -> ColumnDefResult
  ColumnDefFailed  : String -> ColumnDefResult
  ColumnDefRequiresContent : ColumnDefResult  -- Empty document error

-- ============================================================================
-- Error Messages
-- ============================================================================

public export
columnDefEmptyDocError : String
columnDefEmptyDocError = "ColumnDef requires content in document. Insert text/content before applying column settings."

public export
pageSetupNotAppliedError : String
pageSetupNotAppliedError = "PageSetup Execute returned True but settings were not applied (verification failed)."
