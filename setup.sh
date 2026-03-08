#!/bin/bash
# door : Edwin van den Oetelaar
# datum : 7 maart 2026
# Exit script when any command fails
set -e

echo "========================================="
echo " Setting up Python Environment for SimPy "
echo "========================================="

# 1. Update package lists and install prerequisites
# We need python3-venv to create virtual environments on Ubuntu
echo "[1/4] Installing necessary system packages (sudo may ask for a password)..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip python3-dev

# 2. Create the virtual environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/4] Creating Python virtual environment in './$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
else
    echo "[2/4] Virtual environment already exists in './$VENV_DIR'. Skipping creation."
fi

# 3. Activate the virtual environment
echo "[3/4] Activating virtual environment..."
# Note: In bash scripts, 'source' only affects the current shell sub-process,
# but we need it here to use the local pip for installation.
source "$VENV_DIR/bin/activate"

# 4. Install dependencies
echo "[4/4] Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Fallback if requirements.txt somehow doesn't exist
    pip install "simpy>=4.0.0" "matplotlib" "pandas"
fi

echo "========================================="
echo " Setup complete! "
echo "========================================="
echo ""
echo "To start working and activate the virtual environment, run:"
echo "    source $VENV_DIR/bin/activate"
echo ""
