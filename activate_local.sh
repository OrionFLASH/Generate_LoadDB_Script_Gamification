#!/bin/bash
# =============================================================================
# Скрипт активации локального Conda окружения
# Автор: OrionFLASH
# Описание: Активирует локальное Conda окружение, созданное в папке проекта.
#          Локальное окружение обеспечивает портативность проекта.
# =============================================================================

echo "🚀 Активация локального окружения..."

# Проверка существования локального окружения
if [ ! -d "./local_env" ]; then
    echo "❌ Локальное окружение не найдено в папке проекта!"
    echo "📋 Создайте его командой:"
    echo "   conda create --prefix ./local_env python=3.9 --yes"
    echo "   conda activate ./local_env"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Активация локального окружения
echo "✅ Активирую локальное окружение: $(pwd)/local_env"
conda activate ./local_env

# Проверка успешности активации
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