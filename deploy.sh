#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Ollama Dashboard v2 — Deploy Script
# Run this on your Unraid terminal
# ═══════════════════════════════════════════════════════════════

set -e

BUILD_DIR="/mnt/user/appdata/ollama-dashboard-build"
DATA_DIR="/mnt/user/appdata/ollama-dashboard"
TEMPLATE_DIR="/boot/config/plugins/dockerMan/templates-user"

echo "═══════════════════════════════════════════════════"
echo "  OLLAMA DASHBOARD v2 — Deployment"
echo "═══════════════════════════════════════════════════"
echo ""

# Step 1: Create directories
echo "[1/5] Creating directories..."
mkdir -p "$BUILD_DIR"
mkdir -p "$BUILD_DIR/templates"
mkdir -p "$DATA_DIR"
mkdir -p "$TEMPLATE_DIR"

# Step 2: Copy build files
echo "[2/5] Copying build files..."
cp Dockerfile "$BUILD_DIR/"
cp requirements.txt "$BUILD_DIR/"
cp app.py "$BUILD_DIR/"
cp templates/dashboard.html "$BUILD_DIR/templates/"
echo "  → Files copied to $BUILD_DIR"

# Step 3: Copy Unraid template
echo "[3/5] Installing Unraid template..."
cp my-ollama-dashboard.xml "$TEMPLATE_DIR/"
echo "  → Template installed"

# Step 4: Build Docker image
echo "[4/5] Building Docker image (this may take a minute)..."
cd "$BUILD_DIR"
docker build -t ollama-dashboard .
echo "  → Image built successfully"

# Step 5: Done
echo ""
echo "═══════════════════════════════════════════════════"
echo "  BUILD COMPLETE!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Next steps:"
echo "  1. Go to Unraid Docker tab"
echo "  2. Click 'Add Container'"
echo "  3. Select 'ollama-dashboard' from Template dropdown"
echo "  4. Verify settings (Ollama URL, port 8088, etc.)"
echo "  5. Click 'Apply'"
echo ""
echo "  Dashboard will be at: http://YOUR-SERVER-IP:8088"
echo ""
echo "  Files:"
echo "    Build:    $BUILD_DIR"
echo "    Data:     $DATA_DIR"
echo "    Template: $TEMPLATE_DIR/my-ollama-dashboard.xml"
echo "═══════════════════════════════════════════════════"
