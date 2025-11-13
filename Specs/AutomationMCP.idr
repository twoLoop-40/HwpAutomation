module Specs.AutomationMCP

import Data.String
import Data.List
import public Specs.HwpCommon

%default total

--------------------------------------------------------------------------------
-- HWP Automation API (OLE Object Model)
-- Based on HwpBooks/HwpAutomation_2504.pdf
--------------------------------------------------------------------------------

||| Core object types in HWP Automation hierarchy
public export
data AutoObjectType =
  HwpObject |           -- IHwpObject (root)
  HwpDocuments |        -- IXHwpDocuments (collection)
  HwpDocument |         -- IXHwpDocument
  HwpWindows |          -- IXHwpWindows (collection)
  HwpWindow |           -- IXHwpWindow
  FormPushButton |      -- Form controls
  FormCheckButton |
  FormRadioButton |
  UnknownObject String

export
Show AutoObjectType where
  show HwpObject = "IHwpObject"
  show HwpDocuments = "IXHwpDocuments"
  show HwpDocument = "IXHwpDocument"
  show HwpWindows = "IXHwpWindows"
  show HwpWindow = "IXHwpWindow"
  show FormPushButton = "IXHwpFormPushButton"
  show FormCheckButton = "IXHwpFormCheckButton"
  show FormRadioButton = "IXHwpFormRadioButton"
  show (UnknownObject s) = "UnknownObject(" ++ s ++ ")"

--------------------------------------------------------------------------------
-- Property Definitions
--------------------------------------------------------------------------------

||| Property access mode
public export
data PropertyMode = ReadOnly | ReadWrite

export
Show PropertyMode where
  show ReadOnly = "ReadOnly"
  show ReadWrite = "ReadWrite"

||| Property definition
public export
record PropertyDef where
  constructor MkProperty
  name : String
  mode : PropertyMode

--------------------------------------------------------------------------------
-- Object Specifications
--------------------------------------------------------------------------------

||| IHwpObject properties and methods
export
hwpObjectProperties : List PropertyDef
hwpObjectProperties = [
  MkProperty "XHwpDocuments" ReadOnly,
  MkProperty "XHwpWindows" ReadOnly,
  MkProperty "Version" ReadOnly,
  MkProperty "IsEmpty" ReadOnly,
  MkProperty "EditMode" ReadWrite,
  MkProperty "Path" ReadOnly
]

||| IXHwpDocuments properties
export
hwpDocumentsProperties : List PropertyDef
hwpDocumentsProperties = [
  MkProperty "Count" ReadOnly,
  MkProperty "ActiveDocument" ReadOnly
]

||| IXHwpDocument properties
export
hwpDocumentProperties : List PropertyDef
hwpDocumentProperties = [
  MkProperty "Path" ReadOnly,
  MkProperty "IsModified" ReadOnly,
  MkProperty "DocumentName" ReadOnly,
  MkProperty "ParentWindow" ReadOnly
]

||| IXHwpWindows properties
export
hwpWindowsProperties : List PropertyDef
hwpWindowsProperties = [
  MkProperty "Count" ReadOnly,
  MkProperty "ActiveWindow" ReadOnly
]

||| IXHwpWindow properties
export
hwpWindowProperties : List PropertyDef
hwpWindowProperties = [
  MkProperty "Document" ReadOnly,
  MkProperty "Visible" ReadWrite,
  MkProperty "Left" ReadWrite,
  MkProperty "Top" ReadWrite,
  MkProperty "Width" ReadWrite,
  MkProperty "Height" ReadWrite
]

--------------------------------------------------------------------------------
-- Method Definitions
--------------------------------------------------------------------------------

||| Method names for each object type
export
hwpObjectMethods : List String
hwpObjectMethods = ["Quit", "Run", "CreateAction"]

export
hwpDocumentsMethods : List String
hwpDocumentsMethods = ["Item", "Open", "Add"]

export
hwpDocumentMethods : List String
hwpDocumentMethods = ["Save", "SaveAs", "Close", "CreateAction"]

export
hwpWindowsMethods : List String
hwpWindowsMethods = ["Item"]

export
hwpWindowMethods : List String
hwpWindowMethods = ["Activate", "Close"]

--------------------------------------------------------------------------------
-- Automation Handle
--------------------------------------------------------------------------------

||| Handle to an automation object
public export
record AutoHandle where
  constructor MkAutoHandle
  objectType : AutoObjectType
  objectId : Maybe String

export
Show AutoHandle where
  show (MkAutoHandle otype oid) =
    "AutoHandle { type = " ++ show otype ++ ", id = " ++ show oid ++ " }"

export
newHwpObject : AutoHandle
newHwpObject = MkAutoHandle HwpObject Nothing

--------------------------------------------------------------------------------
-- Automation Error Types
--------------------------------------------------------------------------------

public export
data AutoError =
  PropertyNotFound String |
  MethodNotFound String |
  InvalidPropertyType String |
  ReadOnlyProperty String |
  ObjectNotFound |
  BaseAutoError HwpError

export
Show AutoError where
  show (PropertyNotFound name) = "Property not found: " ++ name
  show (MethodNotFound name) = "Method not found: " ++ name
  show (InvalidPropertyType name) = "Invalid property type: " ++ name
  show (ReadOnlyProperty name) = "Read-only property: " ++ name
  show ObjectNotFound = "Object not found"
  show (BaseAutoError err) = show err

--------------------------------------------------------------------------------
-- Result Type
--------------------------------------------------------------------------------

public export
data AutoResult : Type -> Type where
  AutoSuccess : a -> AutoResult a
  AutoFailure : AutoError -> AutoResult a

export
Functor AutoResult where
  map f (AutoSuccess x) = AutoSuccess (f x)
  map f (AutoFailure e) = AutoFailure e

export
Applicative AutoResult where
  pure = AutoSuccess
  (AutoSuccess f) <*> (AutoSuccess x) = AutoSuccess (f x)
  (AutoFailure e) <*> _ = AutoFailure e
  _ <*> (AutoFailure e) = AutoFailure e

export
Monad AutoResult where
  (AutoSuccess x) >>= f = f x
  (AutoFailure e) >>= _ = AutoFailure e

export
Show a => Show (AutoResult a) where
  show (AutoSuccess x) = "AutoSuccess: " ++ show x
  show (AutoFailure e) = "AutoFailure: " ++ show e

--------------------------------------------------------------------------------
-- Type-Safe Operations
--------------------------------------------------------------------------------

export
getProperty : (handle : AutoHandle) ->
              (propName : String) ->
              AutoResult ParamValue
getProperty handle propName = AutoSuccess (PString "")  -- Placeholder

export
setProperty : (handle : AutoHandle) ->
              (propName : String) ->
              (value : ParamValue) ->
              AutoResult ()
setProperty handle propName value = AutoSuccess ()  -- Placeholder

export
invokeMethod : (handle : AutoHandle) ->
               (methodName : String) ->
               (args : List ParamValue) ->
               AutoResult ParamValue
invokeMethod handle methodName args = AutoSuccess (PBool True)  -- Placeholder

--------------------------------------------------------------------------------
-- High-Level Operations
--------------------------------------------------------------------------------

export
getDocuments : (hwp : AutoHandle) -> AutoResult AutoHandle
getDocuments hwp =
  if hwp.objectType == HwpObject
    then AutoSuccess (MkAutoHandle HwpDocuments (Just "XHwpDocuments"))
    else AutoFailure ObjectNotFound

export
openDocument : (docs : AutoHandle) ->
               (path : String) ->
               AutoResult AutoHandle
openDocument docs path =
  if docs.objectType == HwpDocuments
    then AutoSuccess (MkAutoHandle HwpDocument (Just path))
    else AutoFailure ObjectNotFound

export
getDocumentPath : (doc : AutoHandle) -> AutoResult String
getDocumentPath doc =
  if doc.objectType == HwpDocument
    then case getProperty doc "Path" of
              AutoSuccess (PString p) => AutoSuccess p
              _ => AutoFailure (PropertyNotFound "Path")
    else AutoFailure ObjectNotFound

export
isDocumentModified : (doc : AutoHandle) -> AutoResult Bool
isDocumentModified doc =
  if doc.objectType == HwpDocument
    then case getProperty doc "IsModified" of
              AutoSuccess (PBool b) => AutoSuccess b
              _ => AutoFailure (PropertyNotFound "IsModified")
    else AutoFailure ObjectNotFound

export
saveAutoDocument : (doc : AutoHandle) -> AutoResult Bool
saveAutoDocument doc =
  if doc.objectType == HwpDocument
    then case invokeMethod doc "Save" [] of
              AutoSuccess (PBool b) => AutoSuccess b
              _ => AutoFailure (MethodNotFound "Save")
    else AutoFailure ObjectNotFound

export
closeAutoDocument : (doc : AutoHandle) -> AutoResult Bool
closeAutoDocument doc =
  if doc.objectType == HwpDocument
    then case invokeMethod doc "Close" [] of
              AutoSuccess (PBool b) => AutoSuccess b
              _ => AutoFailure (MethodNotFound "Close")
    else AutoFailure ObjectNotFound

--------------------------------------------------------------------------------
-- MCP Tool Definitions
--------------------------------------------------------------------------------

public export
record AutoMCPTool where
  constructor MkAutoMCPTool
  name : String
  description : String
  objectType : AutoObjectType
  operation : String

export
autoMCPTools : List AutoMCPTool
autoMCPTools = [
  MkAutoMCPTool "hwp_auto_get_documents" "문서 컬렉션 가져오기" HwpObject "get_property",
  MkAutoMCPTool "hwp_auto_open_document" "문서 열기" HwpDocuments "invoke_method",
  MkAutoMCPTool "hwp_auto_get_path" "문서 경로 가져오기" HwpDocument "get_property",
  MkAutoMCPTool "hwp_auto_is_modified" "수정 여부 확인" HwpDocument "get_property",
  MkAutoMCPTool "hwp_auto_save" "문서 저장" HwpDocument "invoke_method",
  MkAutoMCPTool "hwp_auto_close" "문서 닫기" HwpDocument "invoke_method",
  MkAutoMCPTool "hwp_auto_get_windows" "창 컬렉션 가져오기" HwpObject "get_property"
]
