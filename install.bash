#!/bin/bash

set -e  # Exit on any error

echo "🔧 Installing Pinky..."

# --- Check Python version ---
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install it first."
    exit 1
fi

# --- Create virtual environment ---
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists."
fi

# --- Activate venv ---
source .venv/bin/activate

# --- Install dependencies ---
if [ -f "requirements.txt" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️  No requirements.txt found — skipping."
fi

# --- Optional: install system dependencies for Inky (Raspberry Pi) ---
#if grep -q "Raspberry" /proc/cpuinfo; then
#    echo "🐍 Installing Raspberry Pi-specific packages..."
#    sudo apt update
#    sudo apt install -y python3-pil python3-numpy python3-inky
#fi

echo "✅ Setup complete!"
echo "To activate your environment, run:"
echo "  source .venv/bin/activate"
echo "Then start your app with:"
echo "  python3 main.py"
