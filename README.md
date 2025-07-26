# Game Script Generator - Генератор JavaScript скриптов для DevTools

## 📋 Описание проекта

**Game Script Generator** - это Python-приложение для автоматической генерации JavaScript скриптов, предназначенных для выполнения в браузерных DevTools. Скрипты взаимодействуют с API геймификации Сбербанка для выгрузки данных о лидерах, наградах, профилях и других игровых элементах.

### 🎯 Основные возможности

- **Автоматическая генерация JavaScript скриптов** для DevTools
- **Поддержка множественных API эндпоинтов** (лидеры, награды, профили, новости)
- **Конвертация JSON в Excel** с форматированием и статистикой
- **Система конфигурации** для гибкой настройки параметров
- **Логирование и мониторинг** выполнения операций
- **Обработка ошибок и retry-механизмы**

## 🏗️ Архитектура системы

### Структура проекта
```
Generate_LoadDB_Script_Gamification/
├── main.py                 # Основной файл приложения
├── README.md              # Документация
├── WORK/                  # Рабочие директории
│   ├── INPUT/            # Входные CSV/TXT файлы
│   ├── SCRIPT/           # Сгенерированные JavaScript скрипты
│   ├── OUTPUT/           # Excel файлы результатов
│   ├── JSON/             # JSON файлы от API
│   ├── LOGS/             # Логи выполнения
│   └── CONFIG/           # Конфигурационные файлы
└── requirements.txt      # Зависимости Python
```

### Основные компоненты

1. **Генератор скриптов** - создает JavaScript код для DevTools
2. **Обработчик данных** - конвертирует JSON в Excel
3. **Система конфигурации** - управляет параметрами
4. **Логирование** - отслеживает выполнение операций

## 🔧 Техническое задание

### ТЗ-1: Система генерации JavaScript скриптов

**Цель:** Создать универсальную систему генерации JavaScript скриптов для взаимодействия с API геймификации.

**Требования:**
- Генерация скриптов для DevTools браузера
- Поддержка различных API эндпоинтов
- Встроенная обработка ошибок и retry-логика
- Конфигурируемые параметры (timeout, retry_count, delays)
- Автоматическое удаление photoData из ответов
- Скачивание результатов в JSON формате

**Функциональные требования:**
1. **removePhotoData()** - рекурсивное удаление полей photoData
2. **getTimestamp()** - генерация временных меток
3. **fetchWithRetry()** - HTTP запросы с повторными попытками
4. **extractProfiles()** - извлечение профилей из различных структур данных
5. **extractContestantsCount()** - подсчет участников из текста

**Технические требования:**
- Использование ES6+ синтаксиса
- Async/await для асинхронных операций
- AbortController для управления timeout
- Blob API для скачивания файлов
- Console.log для отладки

### ТЗ-2: Система обработки данных (JSON → Excel)

**Цель:** Создать систему конвертации JSON данных в структурированные Excel файлы с форматированием.

**Требования:**
- Поддержка различных структур JSON данных
- Автоматическое создание листов (DATA, SUMMARY, STATISTICS)
- Применение стилей и форматирования
- Обработка вложенных объектов
- Безопасное преобразование типов данных

**Функциональные требования:**
1. **flatten_leader_data()** - уплощение данных лидеров
2. **flatten_reward_profile_data()** - уплощение профилей наград
3. **parse_float_safe()** - безопасное преобразование чисел
4. **apply_excel_styling()** - применение стилей Excel
5. **create_summary_sheet()** - создание сводных листов

**Технические требования:**
- Использование pandas для обработки данных
- openpyxl для работы с Excel
- Обработка европейского формата чисел (запятая)
- Автоматическое определение типов данных
- Обработка отсутствующих значений

### ТЗ-3: Система конфигурации

**Цель:** Создать гибкую систему конфигурации для управления параметрами скриптов и обработки данных.

**Требования:**
- Централизованное хранение настроек
- Поддержка вариантов конфигурации (SIGMA/ALPHA)
- Валидация параметров
- Группировка настроек по функциональности

**Структура конфигурации:**
```python
FUNCTION_CONFIGS = {
    "script_name": {
        "selected_variant": "sigma|alpha",
        "variants": {
            "sigma": {
                "domain": "https://api.example.com",
                "params": {
                    "api_path": "/api/v1/",
                    "service": "endpoint"
                },
                "timeout": 30000,
                "retry_count": 3,
                "delay_between_requests": 5,
                "processing_options": {
                    "include_photo_data": False,
                    "max_profiles_per_request": 100
                }
            }
        },
        "input_file": "filename.csv",
        "active_operations": "scripts_only|json_only|both"
    }
}
```

### ТЗ-4: Система логирования

**Цель:** Создать комплексную систему логирования для отслеживания выполнения операций.

**Требования:**
- Многоуровневое логирование (DEBUG, INFO, WARNING, ERROR)
- Ротация логов по размеру и времени
- Форматирование сообщений с контекстом
- Измерение времени выполнения функций
- Статистика выполнения операций

**Функциональные требования:**
1. **setup_logging()** - инициализация системы логирования
2. **measure_time()** - декоратор для измерения времени
3. **print_summary()** - вывод итоговой статистики
4. **Логирование ошибок** с полным стектрейсом
5. **Контекстное логирование** операций

## 📊 Поддерживаемые скрипты

### 1. Leaders For Admin (Лидеры для администратора)

**Назначение:** Выгрузка данных о лидерах турниров для административных целей.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/tournaments/{tournament_id}/leadersForAdmin`

**Структура данных:**
```json
{
  "tournament_id": {
    "body": {
      "tournament": {
        "leaders": [
          {
            "employeeNumber": "string",
            "lastName": "string",
            "firstName": "string",
            "middleName": "string",
            "fullName": "string",
            "division": "string",
            "position": "string",
            "rating": "number",
            "points": "number"
          }
        ]
      }
    }
  }
}
```

**Поля Excel:**
- employeeNumber, lastName, firstName, middleName, fullName
- division, position, rating, points
- tournament_id (из ключа)

### 2. Reward System (Система наград)

**Назначение:** Выгрузка профилей участников по кодам наград с поддержкой пагинации.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/badges/{reward_code}/profiles`

**Особенности:**
- Поддержка пагинации (100 профилей на страницу)
- Автоматический подсчет страниц
- Извлечение информации о наградах
- Обработка различных структур ответа

**Структура результата:**
```json
{
  "reward_code": {
    "profilesCount": 150,
    "profiles": [...],
    "badgeInfo": {
      "name": "string",
      "description": "string",
      "type": "string",
      "category": "string"
    },
    "totalContestants": 150,
    "pages": 2
  }
}
```

**Поля профиля:**
- rewardCode, badgeName, employeeNumber
- lastName, firstName, middleName, fullName
- division, position, email, phone
- indicatorValue, divisionRatings
- awardDate, awardDescription

### 3. Profile System (Система профилей)

**Назначение:** Выгрузка детальной информации о профилях пользователей.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/profiles/{profile_id}`

### 4. News System (Система новостей)

**Назначение:** Выгрузка списка новостей и их детальной информации.

**API Endpoints:**
- Список: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/news`
- Детали: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/news/{news_id}`

### 5. Address Book (Адресная книга)

**Назначение:** Выгрузка контактной информации сотрудников.

**API Endpoints:**
- TN: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/addressbook/tn`
- DEV: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/addressbook/dev`

### 6. Orders System (Система заказов)

**Назначение:** Выгрузка информации о заказах и транзакциях.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/orders`

### 7. Rating List (Рейтинг)

**Назначение:** Выгрузка рейтинговых списков участников.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/ratings`

## ⚙️ Конфигурация

### Основные настройки

```python
# Активные скрипты для обработки
ACTIVE_SCRIPTS = ["leaders_for_admin", "reward"]

# Уровень логирования
LOG_LEVEL = "DEBUG"

# Базовая директория проекта
BASE_DIR = "/path/to/project/WORK"

# Поддиректории
SUBDIRECTORIES = {
    "INPUT": "INPUT",
    "SCRIPT": "SCRIPT", 
    "OUTPUT": "OUTPUT",
    "JSON": "JSON",
    "LOGS": "LOGS",
    "CONFIG": "CONFIG"
}
```

### Конфигурация скриптов

Каждый скрипт имеет собственную конфигурацию с параметрами:

- **domain** - базовый URL API
- **params.api_path** - путь к API
- **params.service** - конкретный сервис
- **timeout** - таймаут запросов (мс)
- **retry_count** - количество повторных попыток
- **delay_between_requests** - задержка между запросами (мс)
- **processing_options** - опции обработки данных

## 🚀 Использование

### Запуск программы

```bash
# Активация виртуального окружения
source local_env/bin/activate

# Запуск с генерацией скриптов
python main.py

# Запуск конкретного скрипта
python main.py reward
```

### Порядок выполнения

1. **ЭТАП 1: Генерация скриптов**
   - Загрузка данных из CSV/TXT файлов
   - Генерация JavaScript скриптов для DevTools
   - Сохранение скриптов в WORK/SCRIPT/

2. **ЭТАП 2: Обработка JSON файлов**
   - Поиск JSON файлов в WORK/JSON/
   - Конвертация в Excel с форматированием
   - Создание сводных листов и статистики
   - Сохранение в WORK/OUTPUT/

### Использование сгенерированных скриптов

1. Откройте DevTools в браузере (F12)
2. Перейдите на страницу `https://salesheroes.sberbank.ru`
3. Авторизуйтесь в системе
4. Скопируйте содержимое сгенерированного скрипта
5. Вставьте в консоль DevTools и нажмите Enter
6. Дождитесь завершения выполнения
7. JSON файл автоматически скачается

## 📈 Мониторинг и логирование

### Уровни логирования

- **DEBUG** - детальная отладочная информация
- **INFO** - общая информация о выполнении
- **WARNING** - предупреждения
- **ERROR** - ошибки выполнения

### Статистика выполнения

Программа ведет подробную статистику:
- Время выполнения каждой функции
- Количество обработанных записей
- Количество ошибок и предупреждений
- Общее время работы программы

### Логи

Логи сохраняются в `WORK/LOGS/` с ротацией:
- Максимальный размер файла: 10MB
- Количество файлов: 5
- Формат: `game_script_generator_YYYY-MM-DD.log`

## 🔧 Разработка и расширение

### Добавление нового скрипта

1. **Создать функцию генерации:**
```python
@measure_time
def generate_new_script(data_list=None):
    """Генерация скрипта для нового API"""
    config, data_list, selected_variant, variant_config = load_script_data("new_script", data_list)
    # Логика генерации
```

2. **Добавить конфигурацию:**
```python
"new_script": {
    "selected_variant": "sigma",
    "variants": {
        "sigma": {
            "domain": "https://api.example.com",
            "params": {
                "api_path": "/api/v1/",
                "service": "new_endpoint"
            }
        }
    },
    "input_file": "new_data.csv",
    "active_operations": "both"
}
```

3. **Добавить в main():**
```python
elif script_name == "new_script":
    generate_new_script()
```

### Добавление обработчика JSON

1. **Создать функцию конвертации:**
```python
@measure_time
def convert_new_json_to_excel(input_json_path, output_excel_path, config_key=None):
    """Конвертация JSON в Excel для нового типа данных"""
    # Логика конвертации
```

2. **Добавить в convert_json_to_excel():**
```python
if config_key == "new_script":
    return convert_new_json_to_excel(input_json_path, output_excel_path, config_key)
```

## 🐛 Отладка и устранение неполадок

### Частые проблемы

1. **Ошибка "Файл не найден"**
   - Проверьте наличие файлов в WORK/INPUT/
   - Убедитесь в правильности путей в конфигурации

2. **Ошибки API запросов**
   - Проверьте авторизацию в браузере
   - Убедитесь в корректности URL в конфигурации
   - Проверьте сетевые настройки

3. **Проблемы с Excel**
   - Убедитесь в установке openpyxl
   - Проверьте права доступа к папке OUTPUT

### Отладочные режимы

```python
# Включение детального логирования
LOG_LEVEL = "DEBUG"

# Тестирование конкретного скрипта
ACTIVE_SCRIPTS = ["reward"]

# Только генерация скриптов
"active_operations": "scripts_only"
```

## 📋 Требования к системе

### Python зависимости

```
pandas>=1.5.0
openpyxl>=3.0.0
pyperclip>=1.8.0
```

### Системные требования

- Python 3.8+
- Доступ к интернету
- Браузер с DevTools
- Права на запись в рабочую директорию

## 📄 Лицензия

Проект разработан для внутреннего использования в Сбербанке.

## 👥 Авторы

- **OrionFLASH** - основной разработчик
- Команда геймификации Сбербанка

---

*Документация обновлена: 2025-07-27* 