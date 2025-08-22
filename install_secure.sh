#!/bin/bash

# Secure installer for File Organizer with checksum verification
# Author: William Cloutman

set -e  # Exit on any error

echo "📦 Installing File Organizer (Secure Version)..."

# Configuration
REPO="Bilhelm/fileorg"
FILE="file_organizer.py"
EXPECTED_CHECKSUM="f3df860539c90f3ccd6818c0bd8cc12a9e29df2cb3b00ac070c3dd70eb58b2c9"
INSTALL_DIR="$HOME/bin"
TEMP_FILE="/tmp/${FILE}.tmp"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create bin directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download the file
echo -e "${YELLOW}Downloading File Organizer...${NC}"
if ! curl -sL -o "$TEMP_FILE" "https://raw.githubusercontent.com/${REPO}/master/${FILE}"; then
    echo -e "${RED}❌ Download failed${NC}"
    exit 1
fi

# Verify checksum
echo -e "${YELLOW}Verifying integrity...${NC}"
ACTUAL_CHECKSUM=$(sha256sum "$TEMP_FILE" | cut -d' ' -f1)

if [ "$ACTUAL_CHECKSUM" = "$EXPECTED_CHECKSUM" ]; then
    echo -e "${GREEN}✅ Checksum verified${NC}"
    echo "   Expected: $EXPECTED_CHECKSUM"
    echo "   Actual:   $ACTUAL_CHECKSUM"
else
    echo -e "${RED}❌ Checksum verification failed!${NC}"
    echo "   Expected: $EXPECTED_CHECKSUM"
    echo "   Actual:   $ACTUAL_CHECKSUM"
    echo ""
    echo "This could mean:"
    echo "  1. The file was modified (check for updates)"
    echo "  2. Download was corrupted"
    echo "  3. Potential security issue"
    rm "$TEMP_FILE"
    exit 1
fi

# Install the file
mv "$TEMP_FILE" "$INSTALL_DIR/$FILE"
chmod +x "$INSTALL_DIR/$FILE"

# Add alias to bashrc if not already present
if ! grep -q "alias fileorg=" ~/.bashrc 2>/dev/null; then
    echo "alias fileorg='python3 $INSTALL_DIR/$FILE'" >> ~/.bashrc
    echo -e "${GREEN}✅ Added alias to ~/.bashrc${NC}"
fi

echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "🚀 Usage:"
echo "   source ~/.bashrc  # Reload shell configuration"
echo "   fileorg          # Run File Organizer"
echo ""
echo "📝 To verify installation:"
echo "   sha256sum $INSTALL_DIR/$FILE"
echo ""
echo "🔒 This installation was verified using SHA-256 checksum"