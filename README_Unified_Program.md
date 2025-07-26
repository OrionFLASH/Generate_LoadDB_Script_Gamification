# Объединенная программа Game Script Generator

## Описание

Единая программа для генерации JavaScript скриптов и обработки JSON файлов в Excel. Все функции объединены в одном файле `main.py` с системой выбора операций через переменные.

## Возможности

### 🔧 Генерация скриптов
- ✅ Генерация JavaScript скриптов для различных сервисов
- ✅ Поддержка множественных вариантов (SIGMA, ALPHA)
- ✅ Автоматическое копирование в буфер обмена
- ✅ Настраиваемые источники данных (файлы, переменные)

### 📊 Обработка JSON в Excel
- ✅ Конвертация JSON файлов LeadersForAdmin в Excel
- ✅ Создание структурированных Excel файлов с несколькими листами
- ✅ Автоматическое форматирование и стилизация
- ✅ Статистика и сводные данные
- ✅ Обработка европейского формата чисел

## Настройка операций

### Основные настройки в `main.py`:

```python
# Выбор активных операций
ACTIVE_OPERATIONS = [
    "generate_scripts",  # Генерация скриптов
    "process_json"       # Обработка JSON файлов в Excel
]

# Выбор активных скриптов для генерации
ACTIVE_SCRIPTS = [
    "leaders_for_admin",  # Информация по участникам турнира
    # "reward",             # Информация о наградах сотрудников
    # "profile",            # Профили сотрудников
    # ... другие скрипты
]

# Настройки обработки JSON файлов
JSON_PROCESSING_CONFIG = {
    "input_directory": "INPUT",  # Директория с JSON файлами
    "output_directory": "OUTPUT",  # Директория для Excel файлов
    "file_pattern": "*.json",  # Паттерн для поиска JSON файлов
    "create_summary": True,  # Создавать лист SUMMARY
    "create_statistics": True,  # Создавать лист STATISTICS
    "apply_styling": True  # Применять стили к Excel
}
```

## Использование

### 1. Запуск программы
```bash
python main.py
```

### 2. Настройка операций

#### Только генерация скриптов:
```python
ACTIVE_OPERATIONS = ["generate_scripts"]
```

#### Только обработка JSON:
```python
ACTIVE_OPERATIONS = ["process_json"]
```

#### Обе операции:
```python
ACTIVE_OPERATIONS = ["generate_scripts", "process_json"]
```

### 3. Выбор скриптов для генерации

Раскомментируйте нужные скрипты в `ACTIVE_SCRIPTS`:
```python
ACTIVE_SCRIPTS = [
    "leaders_for_admin",  # ✅ Активен
    "reward",             # ✅ Активен
    # "profile",          # ❌ Отключен
    # "news_details",     # ❌ Отключен
]
```

### 4. Настройка обработки JSON

Измените параметры в `JSON_PROCESSING_CONFIG`:
```python
JSON_PROCESSING_CONFIG = {
    "input_directory": "INPUT",     # Директория с JSON файлами
    "output_directory": "OUTPUT",   # Директория для Excel файлов
    "create_summary": True,         # Создавать лист SUMMARY
    "create_statistics": True,      # Создавать лист STATISTICS
    "apply_styling": True           # Применять стили
}
```

## Структура проекта

```
Generate_LoadDB_Script_Gamification/
├── main.py                    # 🎯 Основная программа
├── INPUT/                     # 📁 Входные файлы
│   ├── *.csv                 # Данные для генерации скриптов
│   └── *.json                # JSON файлы для обработки
├── OUTPUT/                    # 📁 Выходные файлы
│   ├── *.xlsx                # Созданные Excel файлы
│   └── logs/                 # Логи программы
├── requirements.txt           # Зависимости Python
└── README_Unified_Program.md # Это руководство
```

## Примеры использования

### Пример 1: Только генерация скрипта LeadersForAdmin
```python
ACTIVE_OPERATIONS = ["generate_scripts"]
ACTIVE_SCRIPTS = ["leaders_for_admin"]
```

### Пример 2: Только обработка JSON файлов
```python
ACTIVE_OPERATIONS = ["process_json"]
ACTIVE_SCRIPTS = []  # Не важно для обработки JSON
```

### Пример 3: Полный цикл (генерация + обработка)
```python
ACTIVE_OPERATIONS = ["generate_scripts", "process_json"]
ACTIVE_SCRIPTS = ["leaders_for_admin"]
```

## Выходные файлы

### Excel файлы содержат:
- **DATA** - основные данные участников
- **SUMMARY** - сводная статистика
- **STATISTICS** - статистика по подразделениям и бизнес-блокам

### Логирование:
- Подробные логи всех операций
- Время выполнения функций
- Статистика обработки

## Установка зависимостей

```bash
pip install pandas openpyxl pyperclip
```

## Особенности

1. **Единый файл**: Все функции в одном `main.py`
2. **Гибкая настройка**: Выбор операций через переменные
3. **Автоматизация**: Автоматический поиск и обработка файлов
4. **Форматирование**: Красивое оформление Excel файлов
5. **Логирование**: Подробные логи всех операций
6. **Обработка ошибок**: Корректная обработка различных форматов данных

## Поддержка

Программа поддерживает:
- ✅ Различные форматы входных данных (CSV, TXT, JSON)
- ✅ Европейский формат чисел (запятая вместо точки)
- ✅ Автоматическое создание директорий
- ✅ Обработка больших файлов
- ✅ Детальное логирование
- ✅ Настраиваемые стили Excel 