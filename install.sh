#!/bin/bash

# One-line installer for File Organizer
echo "📦 Installing File Organizer..."

# Create a bin directory if it doesn't exist
mkdir -p ~/bin

# Download the file organizer
curl -o ~/bin/file_organizer.py https://raw.githubusercontent.com/Bilhelm/fileorg/master/file_organizer.py

# Make it executable
chmod +x ~/bin/file_organizer.py

# Add alias to bashrc
if ! grep -q "alias fileorg=" ~/.bashrc; then
    echo "alias fileorg='python3 ~/bin/file_organizer.py'" >> ~/.bashrc
fi

echo "✅ Installation complete!"
echo "🚀 Run 'source ~/.bashrc' then type 'fileorg' to organize any folder!"