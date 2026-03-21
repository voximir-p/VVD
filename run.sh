#!/bin/bash

echo "[1] Use Voximir's Video Downloader"
echo "[2] Update packages (Use when you encounter an error)"

read -p "Enter your choice: " choice

clear

case "$choice" in
    1)
        ./.venv/bin/python ./src/main.py
        ;;
    2)
        ./.venv/bin/python -m pip install --upgrade yt-dlp[default]
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
