# Генератор JavaScript Скриптов для Геймификации

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

## Структура проекта

```
Generate_LoadDB_Script_Gamification/
├── main.py                    # 🎯 Основная программа (все функции)
├── README.md                  # 📖 Документация
├── requirements.txt           # 📦 Python зависимости
├── environment.yml           # 🐍 Conda окружение (глобальное)
├── setup_environment.sh      # ⚙️ Скрипт настройки глобального окружения
├── activate_local.sh         # 🔧 Скрипт активации локального окружения
├── .gitignore                # 🚫 Git настройки исключений
├── local_env/                # 🏠 Локальное окружение (не в git)
├── INPUT/                    # 📁 Входные файлы
│   ├── *.csv                # Данные для генерации скриптов
│   └── *.json               # JSON файлы для обработки
└── OUTPUT/                   # 📁 Выходные файлы
    ├── *.xlsx               # Созданные Excel файлы
    └── logs/                # Логи программы
```

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
    # "news_details",       # Детальная карточка новости
    # "address_book_tn",    # Карточка сотрудника по табельному номеру
    # "address_book_dev",   # Карточка подразделения
    # "orders",             # Список сотрудников с преференциями
    # "news_list",          # Список новостей
    # "rating_list"         # Рейтинг участников
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

## Начальные настройки и константы

### Настройки логирования

- **LOG_LEVEL**: Уровень логирования (`"INFO"` или `"DEBUG"`)
  - `INFO`: Базовые сообщения о старте, остановке и общей сводке
  - `DEBUG`: Подробная информация о выполнении каждой функции

- **LOG_DIR**: Путь до каталога логов (сырая строка)
  ```python
  LOG_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/LOGS"
  ```

- **LOG_FILENAME_BASE**: Базовое имя файла лога без расширения
  ```python
  LOG_FILENAME_BASE = "game_script_generator"
  ```

### Формат имени файла лога

Файл лога создается по шаблону:
```
{LOG_FILENAME_BASE}_{LOG_LEVEL}_{YYYY-MM-DD}.log
```

Пример: `game_script_generator_DEBUG_2024-01-15.log`

### Настройки каталогов

- **INPUT_DIR**: Каталог входных данных
  ```python
  INPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"
  ```

- **OUTPUT_DIR**: Каталог создаваемых файлов
  ```python
  OUTPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"
  ```

### Настройки обработки данных

- **DATA_SOURCE**: Источник данных (`"file"`, `"variable"` или `"external_file"`)
- **INPUT_FORMAT**: Формат входного файла (`"TXT"`, `"CSV"` или `"JSON"`)
- **INPUT_FILENAME**: Имя входного файла (без расширения)
- **INPUT_FILE_EXTENSION**: Расширение входного файла

### Расширения файлов

```python
FILE_EXTENSIONS = {
    "CSV": ".csv",    # Ключ: формат CSV файлов
    "TXT": ".txt",    # Ключ: формат текстовых файлов  
    "JSON": ".json"   # Ключ: формат JSON файлов
}
```

### Настройки для TXT файлов

- **TXT_DELIMITERS**: Массив разделителей для TXT файлов
- Поддерживаемые разделители: `,`, `;`, `\t`, ` `, `\n`, `\r\n`, `|`, `:`, `.`, `!`, `?`, `@`, `#`, `$`, `%`, `^`, `&`, `*`, `(`, `)`, `[`, `]`, `{`, `}`, `<`, `>`, `/`, `\\`, `=`, `+`, `~`, `` ` ``, `'`, `"`
- Программа автоматически обрабатывает все разделители из массива, кроме "_" и "-"

### Настройки для CSV файлов

- **CSV_DELIMITER**: Разделитель колонок в CSV (по умолчанию `;`)
- **CSV_ENCODING**: Кодировка CSV файла (`"utf-8"`)
- **CSV_COLUMN_NAME**: Название столбца для извлечения данных

### Тексты для логирования

- **LOG_MESSAGES**: Словарь с шаблонами сообщений для логирования
- Все тексты используют форматирование с переменными: `{time}`, `{file_path}`, `{error}` и т.д.
- Примеры:
  ```python
  "start": "=== Старт работы программы: {time} ===",
  "reading_file": "Загрузка файла: {file_path}",
  "read_ok": "Файл успешно загружен: {file_path}, строк: {rows}",
  "func_start": "[START] {func} {params}",
  "func_end": "[END] {func} (время: {time:.3f}s)"
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

## Конфигурация скриптов

### FUNCTION_CONFIGS

Каждый скрипт имеет свою конфигурацию в словаре `FUNCTION_CONFIGS`:

```python
FUNCTION_CONFIGS = {
    "leaders_for_admin": {  # Ключ: конфигурация для скрипта LeadersForAdmin
        "name": "LeadersForAdmin",  # Ключ: название скрипта для отображения
        "description": "Информация по загруженным в турнир данным об участниках",  # Ключ: описание назначения скрипта
        "variants": {  # Ключ: варианты конфигурации (SIGMA/ALPHA)
            "sigma": {  # Ключ: вариант SIGMA (продакшн окружение)
                "name": "LeadersForAdmin (SIGMA)",  # Ключ: название варианта
                "description": "Информация по загруженным в турнир данным об участниках - SIGMA",  # Ключ: описание варианта
                "domain": "https://salesheroes.sberbank.ru",  # Ключ: домен для SIGMA
                "params": {  # Ключ: параметры API запросов
                    "api_path": "/bo/rmkib.gamification/api/v1/tournaments/",  # Ключ: путь к API
                    "service": "leadersForAdmin",  # Ключ: название сервиса
                    "page_param": "pageNum=1"  # Ключ: параметр пагинации
                }
            },
            "alpha": {  # Ключ: вариант ALPHA (тестовое окружение)
                "name": "LeadersForAdmin (ALPHA)",  # Ключ: название варианта
                "description": "Информация по загруженным в турнир данным об участниках - ALPHA",  # Ключ: описание варианта
                "domain": "https://efs-our-business-prom.omega.sbrf.ru",  # Ключ: домен для ALPHA
                "params": {  # Ключ: параметры API запросов
                    "api_path": "/bo/rmkib.gamification/api/v1/tournaments/",  # Ключ: путь к API
                    "service": "leadersForAdmin",  # Ключ: название сервиса
                    "page_param": "pageNum=1"  # Ключ: параметр пагинации
                }
            }
        },
        "selected_variant": "sigma",  # Ключ: выбранный вариант (sigma/alpha)
        "data_source": "external_file",  # Ключ: источник данных (file/variable/external_file)
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "TOURNAMENT_CODE",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "input_file": "TOURNAMENT-SCHEDULE (PROM) 2025-07-25 v6"  # Ключ: имя входного файла (без расширения)
    }
}
```

## Структура JSON данных

Программа ожидает JSON файл со следующей структурой:

```json
{
  "tournament_key": [
    {
      "success": true,
      "body": {
        "tournament": {
          "tournamentId": "...",
          "leaders": [
            {
              "employeeNumber": "...",
              "lastName": "...",
              "firstName": "...",
              "indicatorValue": "...",
              "successValue": "...",
              "terDivisionName": "...",
              "employeeStatus": "...",
              "businessBlock": "..."
            }
          ]
        }
      }
    }
  ]
}
```

## Выходные данные Excel

### Лист DATA
Содержит основные данные участников:
- employeeNumber - номер сотрудника
- lastName, firstName - фамилия и имя
- fullName - полное имя
- indicatorValue - значение показателя
- successValue - целевое значение
- terDivisionName - территориальное подразделение
- employeeStatus - статус сотрудника
- businessBlock - бизнес-блок
- indicatorValue_parsed, successValue_parsed - числовые значения

### Лист SUMMARY
Сводная статистика:
- Общее количество участников
- Участники с номером сотрудника
- Участники со статусом CONTESTANT
- Среднее/максимальное/минимальное значение показателя

### Лист STATISTICS
Статистика по:
- Территориальным подразделениям
- Бизнес-блокам

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

### Пример 4: Конвертация файла LeadersForAdmin
```bash
# Разместите JSON файл в INPUT/ директории
# Настройте ACTIVE_OPERATIONS = ["process_json"]
python main.py
```

## Полный рабочий процесс

### 1. Генерация JavaScript скриптов

```bash
# Настройте ACTIVE_SCRIPTS в main.py
ACTIVE_SCRIPTS = ["leaders_for_admin", "reward"]

# Запустите генерацию
python main.py
```

### 2. Получение JSON данных

Выполните сгенерированные скрипты в браузере (DevTools Console) для получения JSON ответов.

### 3. Обработка JSON в Excel

```bash
# Разместите JSON файлы в INPUT/ папке
# Настройте ACTIVE_OPERATIONS = ["process_json"]
python main.py
```

### 4. Результат

Excel файлы с обработанными данными появятся в папке OUTPUT/.

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
7. **Автоматическое создание директорий** - программа создает необходимые директории для выходного файла
8. **Обработка европейского формата чисел** - корректная обработка европейского формата чисел (запятая вместо точки)
9. **Автоматическая настройка ширины столбцов** в Excel файлах

## Структура SUMMARY

В конце выполнения программа выводит статистику:
- Общее время выполнения
- Количество обработанных действий  
- Время выполнения каждой функции
- Дата и время завершения

Пример:
```
======================================================================
SUMMARY - ИТОГОВАЯ СТАТИСТИКА РАБОТЫ ПРОГРАММЫ
======================================================================
Общее время выполнения: 0.0097 секунд
Обработано действий: 5
Выполнено функций: 4

Время выполнения функций:
  - load_data_from_file: 0.0002 сек
  - generate_script_universal: 0.0091 сек
  - copy_to_clipboard: 0.0088 сек

Программа завершена: 2025-07-26 16:45:58.710
======================================================================
```

## Поддержка

Программа поддерживает:
- ✅ Различные форматы входных данных (CSV, TXT, JSON)
- ✅ Европейский формат чисел (запятая вместо точки)
- ✅ Автоматическое создание директорий
- ✅ Обработка больших файлов
- ✅ Детальное логирование
- ✅ Настраиваемые стили Excel
- ✅ Множественные варианты конфигурации (SIGMA/ALPHA)
- ✅ Автоматическое копирование в буфер обмена

## Автор

OrionFLASH

## Версия

2.0.0 - Объединенная версия с поддержкой генерации скриптов и обработки JSON 