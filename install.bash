#!/bin/bash
set -e  # Exit on any error

# -----------------------------
# CONFIGURATION
# -----------------------------
# Determine app directory as the parent directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR"
VENV_DIR="$APP_DIR/.venv"
APP_NAME="pinky"
PYTHON_PATH="/usr/bin/python3"
LOG_DIR="/var/log/$APP_NAME"
LOGROTATE_CONF="/etc/logrotate.d/$APP_NAME"
RETENTION_WEEKS=4 # Number of weekly log rotations to keep

echo "🔧 Installing $APP_NAME..."

# --- Check Python version ---
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install it first."
    exit 1
fi

# -----------------------------
# CHECK FOR SYSTEM DEPENDENCIES
# -----------------------------
# List of required packages
packages=(
  libjpeg-dev
  zlib1g-dev
  libfreetype6-dev
  liblcms2-dev
  libwebp-dev
  libtiff-dev
  libopenblas-dev
  wkhtmltopdf
)

missing=()

echo "Checking required system packages..."

for pkg in "${packages[@]}"; do
    if dpkg -s "$pkg" >/dev/null 2>&1; then
        echo "✅ [OK] $pkg is installed"
    else
        echo "❌ [MISSING] $pkg is NOT installed"
        missing+=("$pkg")
    fi
done

if [ ${#missing[@]} -ne 0 ]; then
    echo
    echo "❌ ERROR: Missing required packages:"
    for m in "${missing[@]}"; do
        echo "  - $m"
    done
    echo
    exit 1
fi

echo "✅ All required packages are installed."


# --- Create virtual environment ---
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists."
fi

# --- Activate venv ---
source "$VENV_DIR/bin/activate"


# -----------------------------
# INSTALL DEPENDENCIES
# -----------------------------
if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "📥 Installing Python dependencies from requirements.txt..."
    pip3 install -r "$APP_DIR/requirements.txt"
else
    echo "⚠️ No requirements.txt found, skipping Python dependencies installation."
fi

deactivate

# -----------------------------
# SETUP LOG DIRECTORY
# -----------------------------
echo "Setting up log directory at $LOG_DIR..."
sudo mkdir -p "$LOG_DIR"
sudo chown pi:pi "$LOG_DIR"


# -----------------------------
# CREATE SYSTEMD SERVICE
# -----------------------------
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
echo "Creating systemd service at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=$APP_NAME service
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python -u $APP_DIR/src/main.py
StandardOutput=append:$LOG_DIR/output.log
StandardError=append:$LOG_DIR/error.log
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME.service
sudo systemctl start $APP_NAME.service

# -----------------------------
# CONFIGURE LOGROTATE
# -----------------------------
echo "Setting up logrotate for $LOG_DIR..."
sudo bash -c "cat > $LOGROTATE_CONF" <<EOF
$LOG_DIR/*.log {
    weekly
    rotate $RETENTION_WEEKS
    compress
    missingok
    notifempty
    copytruncate
}
EOF

echo "-----------------------------------------------------"
echo "🎉Installation complete!"
echo "App directory:  $APP_DIR"
echo "Virtual env:    $VENV_DIR"
echo "Logs:           $LOG_DIR"
echo "Log rotation:   Weekly, keeping $RETENTION_WEEKS weeks"
echo "Service:        $APP_NAME.service"
echo "-----------------------------------------------------"
