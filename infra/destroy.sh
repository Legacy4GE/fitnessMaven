#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$SCRIPT_DIR/terraform"

echo "=== fitnessMaven Infrastructure Teardown ==="
echo "WARNING: This will destroy ALL fitnessMaven Azure resources."
echo ""

# Verify Azure login
if ! az account show > /dev/null 2>&1; then
    echo "ERROR: Not logged into Azure. Run 'az login' first."
    exit 1
fi

# Show what will be destroyed
echo "Resources that will be destroyed:"
terraform -chdir="$TF_DIR" plan -destroy

# Double confirm
echo ""
read -rp "Type 'destroy' to confirm teardown: " confirm
if [ "$confirm" != "destroy" ]; then
    echo "Aborted."
    exit 0
fi

# Destroy
echo "Destroying resources..."
terraform -chdir="$TF_DIR" destroy -auto-approve

echo ""
echo "=== Teardown Complete ==="
