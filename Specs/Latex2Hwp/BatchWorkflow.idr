module Latex2Hwp.BatchWorkflow

import Latex2Hwp.Types
import Data.List  -- zipWith, length, filter, map

%default total

-- ============================================================
-- Stable Batch LaTeX to HWP Conversion Spec
-- ============================================================

{-
Problem:
  - Direct insertion of 30+ equations fails due to UI state drift / timing issues.
  - Parallel execution (ProcessPool) fails due to `pyhwpx` COM cache conflicts and UI window ambiguity.

Solution: "Isolated Batch Processing"
  1. **Isolation**: Create each equation in a fresh HWP instance (or restart HWP every N items).
     - For maximum stability: 1 equation per file, 1 HWP instance per file.
     - Performance trade-off: High overhead (1-2s startup), but 100% isolation.
  
  2. **Batching**:
     - Generate N small `.hwp` files (e.g., `eq_001.hwp`, `eq_002.hwp`).
     - Verify each file exists.
  
  3. **Merging**:
     - Use `InsertFile` (COM API) to merge all small files into one.
     - This is fast and stable compared to UI automation.

Workflow:
  1. `generateBatch`: List Latex -> List (TempPath, Success)
     - For each latex in list:
       a. Open HWP (new instance)
       b. Insert Equation (UI Automation)
       c. Save as `temp_{i}.hwp`
       d. Quit HWP
       e. Wait (cleanup time)
  
  2. `mergeBatch`: List TempPath -> OutputPath -> IO Bool
     - Open Target HWP
     - For each path: `InsertFile(path)` + `BreakPara`
     - Save
-}

-- ============================================================
-- Types
-- ============================================================

public export
record BatchTask where
    constructor MkBatchTask
    latex : String
    index : Nat

public export
record BatchResult where
    constructor MkBatchResult
    task : BatchTask
    tempPath : String
    success : Bool
    error : Maybe String

-- ============================================================
-- Interface
-- ============================================================

public export
interface Monad m => BatchEquationSpec m where
    -- 1. Isolated Generation (Single Item)
    -- Opens HWP, inserts equation, saves, quits.
    generateSingleEquation : BatchTask -> String -> m BatchResult
    
    -- 2. Cleanup
    -- Ensures HWP processes are killed if stuck
    cleanupProcess : m ()

    -- 3. Fast Merge
    -- Merges multiple HWP files into one using InsertFile API
    mergeFiles : List String -> String -> m Bool

-- ============================================================
-- Workflow Logic
-- ============================================================

export
batchWorkflow : (Monad m, BatchEquationSpec m)
             => List String        -- LaTeX sources
             -> String             -- Output path
             -> String             -- Temp dir
             -> m Bool
batchWorkflow latexSources outputPath tempDir = do
    -- 1. Create Tasks
    let tasks = zipWith MkBatchTask latexSources [0 .. (length latexSources)]
    
    -- 2. Execute Batch (Sequential with Isolation)
    results <- traverse (processTask tempDir) tasks
    
    -- 3. Filter Success
    let successPaths = map tempPath $ filter success results
    
    -- 4. Merge
    if length successPaths > 0
        then mergeFiles successPaths outputPath
        else pure False

  where
    processTask : String -> BatchTask -> m BatchResult
    processTask dir task = do
        res <- generateSingleEquation task dir
        cleanupProcess -- Ensure clean state for next item
        pure res
