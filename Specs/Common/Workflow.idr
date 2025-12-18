module Specs.Common.Workflow

%default total

||| 상태 전이를 의존 타입으로 표현하기 위한 공통 Trace
||| Step : fromState -> toState -> Type 를 각 도메인에서 정의하고,
||| Trace를 통해 "가능한 전이만" 연결되도록 강제한다.
public export
data Trace : (st : Type) -> (step : st -> st -> Type) -> st -> st -> Type where
  Done : Trace st step s s
  (:::) : step s t -> Trace st step t u -> Trace st step s u

export infixr 6 :::


