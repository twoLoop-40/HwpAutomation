module Specs.HwpCommon

import Data.String

%default total

--------------------------------------------------------------------------------
-- Common Types for HWP COM Automation
--------------------------------------------------------------------------------

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

||| Document state lifecycle (shared across ActionTable and Automation)
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

||| Common error types for HWP operations
public export
data HwpError =
  InvalidParameter String |
  DocumentNotOpen |
  DocumentAlreadyOpen |
  COMError String |
  InvalidState DocumentState DocumentState |  -- current, expected
  FileNotFound String

export
Show HwpError where
  show (InvalidParameter msg) = "Invalid parameter: " ++ msg
  show DocumentNotOpen = "Document is not open"
  show DocumentAlreadyOpen = "Document is already open"
  show (COMError msg) = "COM error: " ++ msg
  show (InvalidState current expected) =
    "Invalid state: current=" ++ show current ++ ", expected=" ++ show expected
  show (FileNotFound path) = "File not found: " ++ path

||| Result type for HWP operations (monad)
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

||| Document handle for tracking state
public export
record DocumentHandle where
  constructor MkDocHandle
  path : Maybe String
  state : DocumentState

export
Show DocumentHandle where
  show (MkDocHandle path state) =
    "DocumentHandle { path = " ++ show path ++ ", state = " ++ show state ++ " }"

||| Create a new closed document handle
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
