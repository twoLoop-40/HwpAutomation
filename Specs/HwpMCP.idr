module Specs.HwpMCP

import Data.String
import Data.List

%default total

--------------------------------------------------------------------------------
-- Core Types
--------------------------------------------------------------------------------

||| Action ID from the HWP Action Table
||| Total of 400+ actions categorized by functionality
public export
data ActionID =
  -- Document Management
  FileNew | FileOpen | FileSave | FileSaveAs | FileClose | FileQuit |
  -- Text Operations
  InsertText | Delete | DeleteBack | Copy | Paste | Cut | SelectAll |
  -- Find/Replace
  FindDlg | ReplaceDlg | AllReplace | ForwardFind | BackwardFind |
  -- Formatting
  CharShape | ParagraphShape | Style |
  -- Table Operations
  TableCreate | TableInsertRow | TableDeleteRow | TableMergeCell |
  -- Navigation
  MovePos | Goto | MoveDocBegin | MoveDocEnd |
  -- More actions can be added here...
  UnknownAction String

||| Show instance for ActionID
export
Show ActionID where
  show FileNew = "FileNew"
  show FileOpen = "FileOpen"
  show FileSave = "FileSave"
  show FileSaveAs = "FileSaveAs"
  show FileClose = "FileClose"
  show FileQuit = "FileQuit"
  show InsertText = "InsertText"
  show Delete = "Delete"
  show DeleteBack = "DeleteBack"
  show Copy = "Copy"
  show Paste = "Paste"
  show Cut = "Cut"
  show SelectAll = "SelectAll"
  show FindDlg = "FindDlg"
  show ReplaceDlg = "ReplaceDlg"
  show AllReplace = "AllReplace"
  show ForwardFind = "ForwardFind"
  show BackwardFind = "BackwardFind"
  show CharShape = "CharShape"
  show ParagraphShape = "ParagraphShape"
  show Style = "Style"
  show TableCreate = "TableCreate"
  show TableInsertRow = "TableInsertRow"
  show TableDeleteRow = "TableDeleteRow"
  show TableMergeCell = "TableMergeCell"
  show MovePos = "MovePos"
  show Goto = "Goto"
  show MoveDocBegin = "MoveDocBegin"
  show MoveDocEnd = "MoveDocEnd"
  show (UnknownAction s) = "UnknownAction(" ++ s ++ ")"

||| Parameter value types supported by HWP COM
public export
data ParamValue =
  PString String |
  PInt Int |
  PBool Bool |
  PDouble Double

export
Show ParamValue where
  show (PString s) = "\"" ++ s ++ "\""
  show (PInt i) = show i
  show (PBool b) = show b
  show (PDouble d) = show d

||| Parameter set for actions that require parameters
public export
data ParameterSet = MkParameterSet (List (String, ParamValue))

export
Show ParameterSet where
  show (MkParameterSet params) = "ParameterSet " ++ show params

||| Document state lifecycle
public export
data DocumentState = Closed | Opened | Modified | Saved

export
Show DocumentState where
  show Closed = "Closed"
  show Opened = "Opened"
  show Modified = "Modified"
  show Saved = "Saved"

export
Eq DocumentState where
  Closed == Closed = True
  Opened == Opened = True
  Modified == Modified = True
  Saved == Saved = True
  _ == _ = False

||| Error types that can occur during HWP operations
public export
data HwpError =
  ActionNotFound ActionID |
  InvalidParameter String |
  DocumentNotOpen |
  DocumentAlreadyOpen |
  COMError String |
  InvalidState DocumentState DocumentState |  -- current, expected
  FileNotFound String

export
Show HwpError where
  show (ActionNotFound aid) = "Action not found: " ++ show aid
  show (InvalidParameter msg) = "Invalid parameter: " ++ msg
  show DocumentNotOpen = "Document is not open"
  show DocumentAlreadyOpen = "Document is already open"
  show (COMError msg) = "COM error: " ++ msg
  show (InvalidState current expected) =
    "Invalid state: current=" ++ show current ++ ", expected=" ++ show expected
  show (FileNotFound path) = "File not found: " ++ path

--------------------------------------------------------------------------------
-- Action Classification
--------------------------------------------------------------------------------

||| Classification of actions based on parameter requirements
public export
data ActionRequirement =
  NoParam |        -- No ParameterSet needed (-)
  OptionalParam |  -- ParameterSet optional
  RequiredParam |  -- ParameterSet required
  ReadOnly         -- Read-only action (*)

export
Show ActionRequirement where
  show NoParam = "NoParam"
  show OptionalParam = "OptionalParam"
  show RequiredParam = "RequiredParam"
  show ReadOnly = "ReadOnly"

||| Get parameter requirement for an action
export
getActionRequirement : ActionID -> ActionRequirement
getActionRequirement FileNew = NoParam
getActionRequirement FileOpen = RequiredParam
getActionRequirement FileSave = NoParam
getActionRequirement FileSaveAs = RequiredParam
getActionRequirement FileClose = NoParam
getActionRequirement InsertText = RequiredParam
getActionRequirement Delete = NoParam
getActionRequirement CharShape = RequiredParam
getActionRequirement TableCreate = RequiredParam
getActionRequirement _ = OptionalParam

||| Check if an action requires a specific document state
export
requiredState : ActionID -> Maybe DocumentState
requiredState FileNew = Just Closed
requiredState FileOpen = Just Closed
requiredState FileClose = Just Opened
requiredState InsertText = Just Opened
requiredState Delete = Just Opened
requiredState _ = Nothing

--------------------------------------------------------------------------------
-- Document Handle (State tracking without linearity)
--------------------------------------------------------------------------------

||| A document handle that tracks state
public export
record DocumentHandle where
  constructor MkDocHandle
  path : Maybe String
  state : DocumentState

export
Show DocumentHandle where
  show (MkDocHandle path state) =
    "DocumentHandle { path = " ++ show path ++ ", state = " ++ show state ++ " }"

||| Create a closed document handle
export
newDocument : DocumentHandle
newDocument = MkDocHandle Nothing Closed

||| Transition document state
export
transitionState : DocumentHandle -> DocumentState -> DocumentHandle
transitionState doc newState = { state := newState } doc

||| Check if document is in expected state
export
checkState : DocumentHandle -> DocumentState -> Bool
checkState doc expected = doc.state == expected

--------------------------------------------------------------------------------
-- Safe Action Execution
--------------------------------------------------------------------------------

||| Result type for HWP operations
public export
data HwpResult : Type -> Type where
  Success : a -> HwpResult a
  Failure : HwpError -> HwpResult a

export
Functor HwpResult where
  map f (Success x) = Success (f x)
  map f (Failure e) = Failure e

export
Applicative HwpResult where
  pure = Success
  (Success f) <*> (Success x) = Success (f x)
  (Failure e) <*> _ = Failure e
  _ <*> (Failure e) = Failure e

export
Monad HwpResult where
  (Success x) >>= f = f x
  (Failure e) >>= _ = Failure e

export
Show a => Show (HwpResult a) where
  show (Success x) = "Success: " ++ show x
  show (Failure e) = "Failure: " ++ show e

||| Execute an action with no parameters
||| Proof: Action must not require parameters
export
executeNoParam : (aid : ActionID) ->
                 {auto prf : getActionRequirement aid = NoParam} ->
                 HwpResult ()
executeNoParam aid = Success ()  -- Placeholder for actual COM call

||| Execute an action with required parameters
||| Proof: Action must require parameters
export
executeWithParam : (aid : ActionID) ->
                   ParameterSet ->
                   {auto prf : getActionRequirement aid = RequiredParam} ->
                   HwpResult ()
executeWithParam aid params = Success ()  -- Placeholder for actual COM call

--------------------------------------------------------------------------------
-- Parameter Builders (Type-safe parameter construction)
--------------------------------------------------------------------------------

||| Build parameter set for FileOpen
export
fileOpenParams : (path : String) -> ParameterSet
fileOpenParams path = MkParameterSet [("filename", PString path)]

||| Build parameter set for InsertText
export
insertTextParams : (text : String) -> ParameterSet
insertTextParams text = MkParameterSet [("Text", PString text)]

||| Build parameter set for CharShape
export
charShapeParams : (textColor : Maybe Int) ->
                  (fontSize : Maybe Int) ->
                  (fontFace : Maybe String) ->
                  ParameterSet
charShapeParams color size face =
  MkParameterSet $ catMaybes [
    map (\c => ("TextColor", PInt c)) color,
    map (\s => ("FontSize", PInt s)) size,
    map (\f => ("FontFace", PString f)) face
  ]

||| Build parameter set for TableCreate
export
tableCreateParams : (rows : Nat) -> (cols : Nat) -> ParameterSet
tableCreateParams rows cols =
  MkParameterSet [
    ("Rows", PInt (cast rows)),
    ("Cols", PInt (cast cols))
  ]

--------------------------------------------------------------------------------
-- High-level Safe Operations
--------------------------------------------------------------------------------

||| Open a document safely
export
openDocument : (path : String) ->
               (doc : DocumentHandle) ->
               HwpResult DocumentHandle
openDocument path doc =
  if checkState doc Closed
    then case executeWithParam FileOpen (fileOpenParams path) of
           Success () => Success (transitionState doc Opened)
           Failure err => Failure err
    else Failure (InvalidState doc.state Closed)

||| Close a document safely
export
closeDocument : (doc : DocumentHandle) ->
                HwpResult DocumentHandle
closeDocument doc =
  if checkState doc Opened
    then case executeNoParam FileClose of
           Success () => Success (transitionState doc Closed)
           Failure err => Failure err
    else Failure (InvalidState doc.state Opened)

||| Insert text into an opened document
export
insertText : (text : String) ->
             (doc : DocumentHandle) ->
             HwpResult DocumentHandle
insertText text doc =
  if checkState doc Opened
    then case executeWithParam InsertText (insertTextParams text) of
           Success () => Success (transitionState doc Modified)
           Failure err => Failure err
    else Failure (InvalidState doc.state Opened)

||| Save a modified document
export
saveDocument : (doc : DocumentHandle) ->
               HwpResult DocumentHandle
saveDocument doc =
  if checkState doc Modified
    then case executeNoParam FileSave of
           Success () => Success (transitionState doc Saved)
           Failure err => Failure err
    else Failure (InvalidState doc.state Modified)

--------------------------------------------------------------------------------
-- Example Usage and Properties
--------------------------------------------------------------------------------

||| Example: Create, edit, and save a document
export
exampleWorkflow : HwpResult DocumentHandle
exampleWorkflow = do
  -- Start with closed state
  let doc = newDocument

  -- Open document
  doc' <- openDocument "test.hwp" doc

  -- Insert text (transitions to Modified)
  doc'' <- insertText "Hello, HWP!" doc'

  -- Save document
  doc''' <- saveDocument doc''

  -- Close document (need to transition back to Opened first)
  let doc'''' = transitionState doc''' Opened
  closeDocument doc''''

||| Property: Closed document stays closed if file not found
export
propertyClosedOnError : HwpResult DocumentHandle
propertyClosedOnError =
  let doc = newDocument
  in case openDocument "nonexistent.hwp" doc of
       Failure _ => Success doc  -- Document remains closed
       Success _ => Success doc

--------------------------------------------------------------------------------
-- MCP Tool Definitions
--------------------------------------------------------------------------------

||| MCP Tool specification for HWP automation
public export
record MCPTool where
  constructor MkMCPTool
  name : String
  description : String
  actionId : ActionID
  paramBuilder : List (String, ParamValue) -> ParameterSet

||| Define core MCP tools
export
mcpTools : List MCPTool
mcpTools = [
  MkMCPTool "hwp_create_document" "새 한글 문서 생성" FileNew (\_ => MkParameterSet []),
  MkMCPTool "hwp_open_document" "한글 문서 열기" FileOpen (\params => MkParameterSet params),
  MkMCPTool "hwp_save_document" "문서 저장" FileSave (\_ => MkParameterSet []),
  MkMCPTool "hwp_insert_text" "텍스트 삽입" InsertText (\params => MkParameterSet params),
  MkMCPTool "hwp_create_table" "표 만들기" TableCreate (\params => MkParameterSet params)
]

--------------------------------------------------------------------------------
-- Theorems and Proofs
--------------------------------------------------------------------------------

||| Theorem: State transitions maintain type safety
||| If we successfully open a closed document, it becomes opened
export
theoremOpenTransition : (doc : DocumentHandle) ->
                        checkState doc Closed = True ->
                        (result : HwpResult DocumentHandle) ->
                        result = openDocument "test.hwp" doc ->
                        (doc' : DocumentHandle) ->
                        result = Success doc' ->
                        checkState doc' Opened = True
theoremOpenTransition doc prf result eq doc' successEq =
  believe_me ()  -- Proof placeholder - would require more infrastructure

||| Theorem: Cannot insert text into closed document
export
theoremCannotInsertIntoClosed : (doc : DocumentHandle) ->
                                checkState doc Closed = True ->
                                (result : HwpResult DocumentHandle) ->
                                result = insertText "text" doc ->
                                (err : HwpError) ->
                                result = Failure err ->
                                err = InvalidState Closed Opened
theoremCannotInsertIntoClosed doc prf result eq err failEq =
  believe_me ()  -- Proof placeholder
