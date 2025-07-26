#!/bin/bash
# =============================================================================
# Скрипт настройки глобального Conda окружения для проекта
# Автор: OrionFLASH
# Описание: Создает и настраивает глобальное Conda окружение game_script_env
#          с установкой всех необходимых зависимостей для проекта
# =============================================================================

echo "🚀 Настройка глобального Conda окружения для проекта..."

# Проверка наличия Conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda не установлена! Установите Anaconda или Miniconda."
    exit 1
fi

echo "✅ Conda найдена: $(conda --version)"

# Создание окружения если не существует
if conda env list | grep -q "game_script_env"; then
    echo "⚠️  Окружение game_script_env уже существует"
    echo "🔄 Обновление окружения..."
    conda env update -f environment.yml
else
    echo "📦 Создание нового окружения game_script_env..."
    conda env create -f environment.yml
fi

# Активация окружения
echo "🔄 Активация окружения..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate game_script_env

# Проверка активации
if [ "$CONDA_DEFAULT_ENV" = "game_script_env" ]; then
    echo "✅ Окружение успешно активировано: $CONDA_DEFAULT_ENV"
    echo "🐍 Python: $(which python)"
    echo "📦 Версия Python: $(python --version)"
else
    echo "❌ Ошибка активации окружения"
    exit 1
fi

# Установка дополнительных пакетов через pip
echo "📦 Установка дополнительных пакетов..."
pip install -r requirements.txt

echo "🎉 Настройка окружения завершена!"
echo ""
echo "📋 Для активации окружения используйте:"
echo "   conda activate game_script_env"
echo ""
echo "🚀 Для запуска программы используйте:"
echo "   python main.py" 