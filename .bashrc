# AutoHwp project-specific Bash configuration
# This file is automatically sourced when working in this project

# Load Idris2 environment
IDRIS2_INIT="/c/Users/joonho.lee/Projects/InstallIdris2/init.sh"
if [ -f "$IDRIS2_INIT" ]; then
    source "$IDRIS2_INIT"
fi
