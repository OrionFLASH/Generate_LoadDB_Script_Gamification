#!/bin/bash

# Скрипт активации локального окружения в папке проекта
# Использование: ./activate_local.sh

echo "🚀 Активация локального окружения..."

# Проверка наличия локального окружения
if [ ! -d "./local_env" ]; then
    echo "❌ Локальное окружение не найдено в папке проекта!"
    echo "📋 Создайте его командой:"
    echo "   conda create --prefix ./local_env python=3.9 --yes"
    echo "   conda activate ./local_env"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Активация окружения
echo "✅ Активирую локальное окружение: $(pwd)/local_env"
conda activate ./local_env

# Проверка активации
if [ "$CONDA_PREFIX" = "$(pwd)/local_env" ]; then
    echo "✅ Локальное окружение активно!"
    echo "📁 Путь: $CONDA_PREFIX"
    echo "🐍 Python: $(which python)"
    echo ""
    echo "🎯 Теперь можете запускать:"
    echo "   python main.py"
    echo "   python json_parsers_runner.py all"
else
    echo "❌ Ошибка активации окружения"
    exit 1
fi 