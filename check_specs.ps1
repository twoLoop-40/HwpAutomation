# Idris2 spec compilation checker
# Run with: powershell -ExecutionPolicy Bypass -File check_specs.ps1

Write-Host "Checking Idris2 specifications..." -ForegroundColor Cyan

$specs = @(
    "Specs/HwpCommon.idr",
    "Specs/ActionTableMCP.idr",
    "Specs/AutomationMCP.idr"
)

$failed = 0

foreach ($spec in $specs) {
    Write-Host "`nChecking $spec..." -ForegroundColor Yellow

    $result = idris2 --check $spec 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $spec compiled successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ $spec failed to compile" -ForegroundColor Red
        Write-Host $result
        $failed++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($failed -eq 0) {
    Write-Host "All specs compiled successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$failed spec(s) failed to compile" -ForegroundColor Red
    exit 1
}
