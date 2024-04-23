#!/bin/bash

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment (Windows)
if [ "$OS" = "Windows_NT" ]; then
    source venv/Scripts/activate
# Activate virtual environment (Unix)
else
    source venv/bin/activate
fi

# Install required packages
pip install -r requirements.txt

# Run the audio browser
python audio_browser.py

# Deactivate virtual environment
deactivate
