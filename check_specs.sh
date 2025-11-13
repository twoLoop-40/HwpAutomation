#!/bin/bash
# Idris2 spec compilation checker (Bash version)
# Run with: bash check_specs.sh
# Note: Idris2 is auto-loaded from ~/.bashrc

echo -e "\033[36mChecking Idris2 specifications...\033[0m"

specs=(
    "Specs/HwpCommon.idr"
    "Specs/ActionTableMCP.idr"
    "Specs/AutomationMCP.idr"
)

failed=0

for spec in "${specs[@]}"; do
    echo -e "\n\033[33mChecking $spec...\033[0m"

    if idris2.sh --check "$spec" 2>&1; then
        echo -e "\033[32m✓ $spec compiled successfully\033[0m"
    else
        echo -e "\033[31m✗ $spec failed to compile\033[0m"
        ((failed++))
    fi
done

echo -e "\n\033[36m========================================\033[0m"
if [ $failed -eq 0 ]; then
    echo -e "\033[32mAll specs compiled successfully!\033[0m"
    exit 0
else
    echo -e "\033[31m$failed spec(s) failed to compile\033[0m"
    exit 1
fi
