module Specs.Common.Result

%default total

||| 공통 에러 코드 (도메인별 확장 가능)
public export
data ErrorCode
  = Unknown
  | InvalidInput
  | NotFound
  | IOError
  | ComError
  | Timeout
  | Unsupported

||| 공통 에러 타입
public export
record Error where
  constructor MkError
  code : ErrorCode
  message : String

||| 의존 타입 기반 결과: ok=True면 value가 반드시 존재, ok=False면 Error가 존재
public export
data Outcome : (ok : Bool) -> (a : Type) -> Type where
  Ok : (value : a) -> Outcome True a
  Fail : (err : Error) -> Outcome False a

public export
mapOutcome : (a -> b) -> Outcome ok a -> Outcome ok b
mapOutcome f (Ok x) = Ok (f x)
mapOutcome _ (Fail e) = Fail e

public export
toEither : Outcome ok a -> Either Error a
toEither (Ok x) = Right x
toEither (Fail e) = Left e

public export
fromEither : Either Error a -> (ok ** Outcome ok a)
fromEither (Right x) = (True ** Ok x)
fromEither (Left e) = (False ** Fail e)


