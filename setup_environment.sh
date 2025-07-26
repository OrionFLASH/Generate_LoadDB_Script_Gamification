#!/bin/bash

# Скрипт для настройки окружения для проекта Game Script Generator

echo "=== Настройка окружения Game Script Generator ==="

# Проверка наличия conda
if ! command -v conda &> /dev/null; then
    echo "ОШИБКА: conda не найдена. Установите Anaconda или Miniconda."
    exit 1
fi

# Создание окружения из файла environment.yml
echo "Создание conda окружения из environment.yml..."
conda env create -f environment.yml

# Активация окружения
echo "Активация окружения..."
source activate game_script_env

echo "=== Окружение настроено успешно! ==="
echo ""
echo "Для работы с программой:"
echo "1. Активируйте окружение: conda activate game_script_env"
echo "2. Запустите программу: python main.py"
echo "3. Для деактивации: conda deactivate" 