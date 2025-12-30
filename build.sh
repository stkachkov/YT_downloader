#!/bin/bash

# Скрипт для сборки приложения yt-dlp Downloader.
# Прекращает выполнение при любой ошибке.
set -e

# 1. Установка зависимостей
echo "--- Установка зависимостей из requirements.txt ---"
pip install -r requirements.txt

# 2. Сборка приложения с помощью PyInstaller
echo "--- Сборка приложения с помощью PyInstaller ---"
pyinstaller --onefile --windowed --name yt_downloader main.py

# 3. Сообщение о завершении
echo "--- Сборка завершена! ---"
echo "Готовое приложение находится в папке 'dist'."
