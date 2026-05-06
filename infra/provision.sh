#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$SCRIPT_DIR/terraform"

echo "=== fitnessMaven Infrastructure Provisioning ==="

# Verify Azure login
echo "Checking Azure CLI authentication..."
if ! az account show > /dev/null 2>&1; then
    echo "ERROR: Not logged into Azure. Run 'az login' first."
    exit 1
fi
echo "Azure authentication verified."

# Verify terraform.tfvars exists
if [ ! -f "$TF_DIR/terraform.tfvars" ]; then
    echo "ERROR: $TF_DIR/terraform.tfvars not found."
    echo "Copy terraform.tfvars.example to terraform.tfvars and fill in your values."
    exit 1
fi

# Initialize Terraform
echo "Initializing Terraform..."
terraform -chdir="$TF_DIR" init

# Plan
echo "Planning infrastructure changes..."
terraform -chdir="$TF_DIR" plan -out=tfplan

# Confirm before applying
read -rp "Apply these changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Apply
echo "Provisioning resources..."
terraform -chdir="$TF_DIR" apply tfplan

# Show outputs
echo ""
echo "=== Provisioning Complete ==="
terraform -chdir="$TF_DIR" output
