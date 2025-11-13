module Specs.ActionTableMCP

import Data.String
import Data.List
import public Specs.HwpCommon

%default total

--------------------------------------------------------------------------------
-- ActionTable-Specific Types
-- Based on HwpBooks/ActionTable_2504.pdf
--------------------------------------------------------------------------------

||| Action ID from the HWP Action Table (400+ actions)
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

||| Parameter set for actions
public export
data ParameterSet = MkParameterSet (List (String, ParamValue))

export
Show ParameterSet where
  show (MkParameterSet params) = "ParameterSet " ++ show params

||| ActionTable-specific error
public export
data ActionError =
  ActionNotFound ActionID |
  BaseError HwpError

export
Show ActionError where
  show (ActionNotFound aid) = "Action not found: " ++ show aid
  show (BaseError err) = show err

--------------------------------------------------------------------------------
-- Action Classification
--------------------------------------------------------------------------------

||| Parameter requirements for actions
public export
data ActionRequirement =
  NoParam |        -- No ParameterSet needed
  OptionalParam |  -- ParameterSet optional
  RequiredParam |  -- ParameterSet required
  ReadOnly         -- Read-only action

export
Show ActionRequirement where
  show NoParam = "NoParam"
  show OptionalParam = "OptionalParam"
  show RequiredParam = "RequiredParam"
  show ReadOnly = "ReadOnly"

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

export
requiredState : ActionID -> Maybe DocumentState
requiredState FileNew = Just Closed
requiredState FileOpen = Just Closed
requiredState FileClose = Just Opened
requiredState InsertText = Just Opened
requiredState Delete = Just Opened
requiredState _ = Nothing

--------------------------------------------------------------------------------
-- Safe Action Execution
--------------------------------------------------------------------------------

export
executeNoParam : (aid : ActionID) ->
                 {auto prf : getActionRequirement aid = NoParam} ->
                 HwpResult ()
executeNoParam aid = Success ()

export
executeWithParam : (aid : ActionID) ->
                   ParameterSet ->
                   {auto prf : getActionRequirement aid = RequiredParam} ->
                   HwpResult ()
executeWithParam aid params = Success ()

--------------------------------------------------------------------------------
-- Parameter Builders
--------------------------------------------------------------------------------

export
fileOpenParams : (path : String) -> ParameterSet
fileOpenParams path = MkParameterSet [("filename", PString path)]

export
insertTextParams : (text : String) -> ParameterSet
insertTextParams text = MkParameterSet [("Text", PString text)]

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

export
tableCreateParams : (rows : Nat) -> (cols : Nat) -> ParameterSet
tableCreateParams rows cols =
  MkParameterSet [
    ("Rows", PInt (cast rows)),
    ("Cols", PInt (cast cols))
  ]

--------------------------------------------------------------------------------
-- High-level Operations
--------------------------------------------------------------------------------

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

export
closeDocument : (doc : DocumentHandle) ->
                HwpResult DocumentHandle
closeDocument doc =
  if checkState doc Opened
    then case executeNoParam FileClose of
           Success () => Success (transitionState doc Closed)
           Failure err => Failure err
    else Failure (InvalidState doc.state Opened)

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
-- MCP Tool Definitions
--------------------------------------------------------------------------------

public export
record MCPTool where
  constructor MkMCPTool
  name : String
  description : String
  actionId : ActionID
  paramBuilder : List (String, ParamValue) -> ParameterSet

export
mcpTools : List MCPTool
mcpTools = [
  MkMCPTool "hwp_action_create_document" "새 한글 문서 생성" FileNew (\_ => MkParameterSet []),
  MkMCPTool "hwp_action_open_document" "한글 문서 열기" FileOpen (\params => MkParameterSet params),
  MkMCPTool "hwp_action_save_document" "문서 저장" FileSave (\_ => MkParameterSet []),
  MkMCPTool "hwp_action_insert_text" "텍스트 삽입" InsertText (\params => MkParameterSet params),
  MkMCPTool "hwp_action_create_table" "표 만들기" TableCreate (\params => MkParameterSet params)
]
