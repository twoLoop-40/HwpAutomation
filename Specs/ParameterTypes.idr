module Specs.ParameterTypes

import Data.String
import Data.List
import public Specs.HwpCommon

%default total

--------------------------------------------------------------------------------
-- PIT (Parameter Item Type) Type System
-- Based on Schema/parameter_table.json and HwpBooks/ParameterSetTable_2504.pdf
--------------------------------------------------------------------------------

||| PIT (Parameter Item Type) - COM ParameterSet 타입 시스템
||| 한글 COM API의 실제 타입 정의
public export
data PITType =
  -- String types
  PIT_BSTR |              -- BSTR (Basic String)

  -- Integer types (unsigned)
  PIT_UI |                -- Unsigned Integer
  PIT_UI1 |               -- 1-byte Unsigned Integer
  PIT_UI2 |               -- 2-byte Unsigned Integer
  PIT_UI4 |               -- 4-byte Unsigned Integer

  -- Integer types (signed)
  PIT_I |                 -- Signed Integer
  PIT_I1 |                -- 1-byte Signed Integer
  PIT_I2 |                -- 2-byte Signed Integer
  PIT_I4 |                -- 4-byte Signed Integer

  -- Composite types
  PIT_SET |               -- Nested ParameterSet
  PIT_ARRAY |             -- Array of values

  -- Unknown/Future types
  PIT_UNKNOWN String      -- 향후 추가될 타입

export
Show PITType where
  show PIT_BSTR = "PIT_BSTR"
  show PIT_UI = "PIT_UI"
  show PIT_UI1 = "PIT_UI1"
  show PIT_UI2 = "PIT_UI2"
  show PIT_UI4 = "PIT_UI4"
  show PIT_I = "PIT_I"
  show PIT_I1 = "PIT_I1"
  show PIT_I2 = "PIT_I2"
  show PIT_I4 = "PIT_I4"
  show PIT_SET = "PIT_SET"
  show PIT_ARRAY = "PIT_ARRAY"
  show (PIT_UNKNOWN s) = "PIT_UNKNOWN(" ++ s ++ ")"

export
Eq PITType where
  PIT_BSTR == PIT_BSTR = True
  PIT_UI == PIT_UI = True
  PIT_UI1 == PIT_UI1 = True
  PIT_UI2 == PIT_UI2 = True
  PIT_UI4 == PIT_UI4 = True
  PIT_I == PIT_I = True
  PIT_I1 == PIT_I1 = True
  PIT_I2 == PIT_I2 = True
  PIT_I4 == PIT_I4 = True
  PIT_SET == PIT_SET = True
  PIT_ARRAY == PIT_ARRAY = True
  (PIT_UNKNOWN s1) == (PIT_UNKNOWN s2) = s1 == s2
  _ == _ = False

||| 문자열에서 PITType 파싱
export
parsePITType : String -> PITType
parsePITType "PIT_BSTR" = PIT_BSTR
parsePITType "PIT_UI" = PIT_UI
parsePITType "PIT_UI1" = PIT_UI1
parsePITType "PIT_UI2" = PIT_UI2
parsePITType "PIT_UI4" = PIT_UI4
parsePITType "PIT_I" = PIT_I
parsePITType "PIT_I1" = PIT_I1
parsePITType "PIT_I2" = PIT_I2
parsePITType "PIT_I4" = PIT_I4
parsePITType "PIT_SET" = PIT_SET
parsePITType "PIT_ARRAY" = PIT_ARRAY
parsePITType other = PIT_UNKNOWN other

--------------------------------------------------------------------------------
-- Parameter Definition (From parameter_table.json)
--------------------------------------------------------------------------------

||| 파라미터 정의 (parameter_table.json의 각 항목)
public export
record ParameterDef where
  constructor MkParamDef
  paramName : String        -- 파라미터 이름 (e.g., "Text", "FaceNameHangul")
  paramType : PITType       -- PIT 타입
  subType : String          -- 서브타입 (선택사항)
  description : String      -- 설명

export
Show ParameterDef where
  show (MkParamDef name ptype sub desc) =
    name ++ " : " ++ show ptype ++
    (if sub /= "" then " (" ++ sub ++ ")" else "") ++
    " - " ++ desc

||| 액션 파라미터 스키마 (액션별 파라미터 정의 목록)
public export
record ActionSchema where
  constructor MkActionSchema
  actionName : String                -- 액션 이름 (e.g., "InsertText", "CharShape")
  paramDefs : List ParameterDef      -- 파라미터 정의 목록

export
Show ActionSchema where
  show (MkActionSchema name params) =
    "Action: " ++ name ++ "\n" ++
    "Parameters (" ++ show (length params) ++ "):\n" ++
    unlines (map (("  - " ++) . show) params)

--------------------------------------------------------------------------------
-- Type Validation
--------------------------------------------------------------------------------

||| 파라미터 타입 검증 에러
public export
data ValidationError =
  TypeMismatch PITType PITType |     -- expected, actual
  ValueOutOfRange PITType Int Int Int | -- type, value, min, max
  InvalidStringValue String |
  MissingRequiredParameter String |
  UnknownParameter String

export
Show ValidationError where
  show (TypeMismatch expected actual) =
    "Type mismatch: expected " ++ show expected ++ ", got " ++ show actual
  show (ValueOutOfRange ptype val minVal maxVal) =
    "Value " ++ show val ++ " out of range for " ++ show ptype ++
    " (valid: " ++ show minVal ++ " to " ++ show maxVal ++ ")"
  show (InvalidStringValue s) = "Invalid string value: " ++ s
  show (MissingRequiredParameter name) = "Missing required parameter: " ++ name
  show (UnknownParameter name) = "Unknown parameter: " ++ name

||| ParamValue가 PITType과 호환되는지 검증
export
validateType : PITType -> ParamValue -> Either ValidationError ()
validateType PIT_BSTR (PString _) = Right ()
validateType PIT_BSTR other = Left (TypeMismatch PIT_BSTR PIT_BSTR) -- simplified

validateType PIT_UI (PInt n) =
  if n >= 0 then Right ()
  else Left (ValueOutOfRange PIT_UI n 0 4294967295) -- 2^32 - 1

validateType PIT_UI1 (PInt n) =
  if n >= 0 && n <= 255 then Right ()
  else Left (ValueOutOfRange PIT_UI1 n 0 255)

validateType PIT_UI2 (PInt n) =
  if n >= 0 && n <= 65535 then Right ()
  else Left (ValueOutOfRange PIT_UI2 n 0 65535)

validateType PIT_UI4 (PInt n) =
  if n >= 0 then Right ()
  else Left (ValueOutOfRange PIT_UI4 n 0 4294967295) -- 2^32 - 1

validateType PIT_I (PInt _) = Right ()

validateType PIT_I1 (PInt n) =
  if n >= -128 && n <= 127 then Right ()
  else Left (ValueOutOfRange PIT_I1 n (-128) 127)

validateType PIT_I2 (PInt n) =
  if n >= -32768 && n <= 32767 then Right ()
  else Left (ValueOutOfRange PIT_I2 n (-32768) 32767)

validateType PIT_I4 (PInt n) =
  if n >= -2147483648 && n < 2147483647 then Right ()
  else Left (ValueOutOfRange PIT_I4 n (-2147483648) 2147483647)

validateType expected actual = Left (TypeMismatch expected expected) -- simplified

||| 파라미터 정의와 값 검증
export
validateParameter : ParameterDef -> ParamValue -> Either ValidationError ()
validateParameter (MkParamDef _ ptype _ _) value = validateType ptype value

--------------------------------------------------------------------------------
-- Parameter Set Construction and Validation
--------------------------------------------------------------------------------

||| 타입 안전한 파라미터 생성
export
makeParameter : String -> PITType -> ParamValue -> Either ValidationError (String, ParamValue)
makeParameter name ptype value =
  case validateType ptype value of
    Left err => Left err
    Right () => Right (name, value)

||| 파라미터 리스트를 ActionSchema로 검증
export
validateParameters : ActionSchema -> List (String, ParamValue) -> Either ValidationError ()
validateParameters schema params = Right () -- simplified for now

--------------------------------------------------------------------------------
-- Sample Action Schemas (From parameter_table.json)
--------------------------------------------------------------------------------

||| InsertText 액션 스키마
export
insertTextSchema : ActionSchema
insertTextSchema = MkActionSchema "InsertText"
  [ MkParamDef "Text" PIT_BSTR "" "삽입할 텍스트" ]

||| FileOpen 액션 스키마
export
fileOpenSchema : ActionSchema
fileOpenSchema = MkActionSchema "FileOpen"
  [ MkParamDef "OpenReadOnly" PIT_UI1 "" "읽기 전용으로 열기"
  , MkParamDef "OpenFlag" PIT_UI1 "" "열기 플래그"
  , MkParamDef "SaveOverWrite" PIT_UI1 "" "덮어쓰기 저장"
  , MkParamDef "ModifiedFlag" PIT_UI1 "" "수정 플래그"
  , MkParamDef "Argument" PIT_BSTR "" "파일 경로"
  , MkParamDef "SaveCMFDoc30" PIT_UI1 "" "CMF 3.0 문서로 저장"
  , MkParamDef "SaveHwp97" PIT_UI1 "" "한글 97 형식으로 저장"
  , MkParamDef "SaveDistribute" PIT_UI1 "" "배포용으로 저장"
  , MkParamDef "SaveDRMDoc" PIT_UI1 "" "DRM 문서로 저장"
  ]

||| TableCreate 액션 스키마
export
tableCreateSchema : ActionSchema
tableCreateSchema = MkActionSchema "TableCreate"
  [ MkParamDef "Rows" PIT_UI "" "행 개수"
  , MkParamDef "Cols" PIT_UI "" "열 개수"
  ]

||| BorderFill 액션 스키마 (샘플 - 28개 파라미터 중 일부)
export
borderFillSchema : ActionSchema
borderFillSchema = MkActionSchema "BorderFill"
  [ MkParamDef "BorderTypeLeft" PIT_UI2 "" "왼쪽 테두리 종류"
  , MkParamDef "BorderTypeRight" PIT_UI2 "" "오른쪽 테두리 종류"
  , MkParamDef "BorderTypeTop" PIT_UI2 "" "위 테두리 종류"
  , MkParamDef "BorderTypeBottom" PIT_UI2 "" "아래 테두리 종류"
  , MkParamDef "BorderWidthLeft" PIT_UI1 "" "왼쪽 테두리 두께"
  , MkParamDef "BorderWidthRight" PIT_UI1 "" "오른쪽 테두리 두께"
  , MkParamDef "BorderWidthTop" PIT_UI1 "" "위 테두리 두께"
  , MkParamDef "BorderWidthBottom" PIT_UI1 "" "아래 테두리 두께"
  -- ... 나머지 20개 파라미터 생략
  ]

--------------------------------------------------------------------------------
-- Schema Registry (런타임에 parameter_table.json에서 로드)
--------------------------------------------------------------------------------

||| 액션 이름으로 스키마 조회
export
lookupSchema : String -> Maybe ActionSchema
lookupSchema "InsertText" = Just insertTextSchema
lookupSchema "FileOpen" = Just fileOpenSchema
lookupSchema "TableCreate" = Just tableCreateSchema
lookupSchema "BorderFill" = Just borderFillSchema
lookupSchema _ = Nothing

||| 모든 정의된 스키마
export
allSchemas : List ActionSchema
allSchemas =
  [ insertTextSchema
  , fileOpenSchema
  , tableCreateSchema
  , borderFillSchema
  ]
