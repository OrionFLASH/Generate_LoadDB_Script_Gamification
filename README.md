# Game Script Generator - Генератор JavaScript скриптов для DevTools

## 📜 История версий

### Версия 2.1.0 (2025-07-27)
**Основные изменения:**
- ✅ **Добавлена обработка профилей наград** - новая функция `convert_reward_profiles_json_to_excel()`
- ✅ **Реализован разворот вложенных JSON объектов** - функция `flatten_reward_leader_data()`
- ✅ **Автоматическое определение типа файла** - по имени файла (profiles/leaders)
- ✅ **Обработка структуры badgeInfo.leaders** - из JSON файлов профилей наград
- ✅ **Детальная обработка тегов и наград** - разворот до 5 тегов в отдельные поля
- ✅ **Обновлена конфигурация** - добавлен новый тип `reward_profiles`
- ✅ **Расширена документация** - подробное описание новой функциональности

**Технические улучшения:**
- Добавлена функция `flatten_reward_leader_data()` для обработки лидеров наград
- Реализована функция `convert_reward_profiles_json_to_excel()` для конвертации профилей
- Обновлена функция `convert_json_to_excel()` с автоопределением типа файла
- Добавлены новые сообщения логирования для профилей наград
- Расширена конфигурация `FUNCTION_CONFIGS` новым типом `reward_profiles`

### Версия 2.0.0 (2025-07-27)
**Основные изменения:**
- ✅ **Полная переработка системы логирования** - добавлено подробное логирование INFO и DEBUG уровней
- ✅ **Исправлены синтаксические ошибки в Reward скриптах** - корректное экранирование и формат ids
- ✅ **Улучшена система конфигурации** - поддержка WORK/CONFIG директории для входных файлов
- ✅ **Добавлена поддержка пагинации** в Reward System с автоматическим подсчетом страниц
- ✅ **Расширено техническое задание** - подробное описание всех компонентов системы
- ✅ **Улучшена обработка ошибок** - автоматические повторные попытки с экспоненциальной задержкой
- ✅ **Добавлена поддержка различных структур данных API** - 4 типа структур ответов
- ✅ **Убран вывод скриптов в консоль** - скрипты сохраняются только в файлы
- ✅ **Добавлена функция copy_to_clipboard** (позже удалена по требованию)

**Технические улучшения:**
- Исправлен декоратор `@measure_time` для корректного логирования
- Добавлена поддержка экранирования в f-строках для JavaScript
- Улучшена система обработки CSV файлов с поддержкой различных кодировок
- Добавлена валидация входных данных и конфигурации

### Версия 1.5.0 (2025-07-26)
**Основные изменения:**
- ✅ **Добавлена система Reward** - полная поддержка выгрузки профилей по кодам наград
- ✅ **Реализована конвертация JSON в Excel** с форматированием и статистикой
- ✅ **Добавлена система конфигурации** с поддержкой SIGMA/ALPHA окружений
- ✅ **Создана система логирования** с ротацией файлов
- ✅ **Добавлена обработка ошибок** и retry-механизмы

**Технические улучшения:**
- Реализована функция `flatten_reward_profile_data()` для обработки профилей
- Добавлена функция `create_reward_summary_sheet()` для сводок по наградам
- Создана система конфигурации `FUNCTION_CONFIGS` с вариантами
- Добавлен декоратор `@measure_time` для измерения производительности

### Версия 1.0.0 (2025-07-25)
**Первоначальная версия:**
- ✅ **Базовая система LeadersForAdmin** - выгрузка данных лидеров турниров
- ✅ **Генерация JavaScript скриптов** для DevTools
- ✅ **Базовая структура проекта** с рабочими директориями
- ✅ **Простая система конфигурации** для API endpoints

**Основные функции:**
- `generate_leaders_for_admin_script()` - генерация скриптов для лидеров
- `convert_leaders_json_to_excel()` - конвертация JSON в Excel
- Базовая система логирования и обработки ошибок

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

## 🔧 Подробное описание переменных и конфигурации

### Основные константы

#### BASE_DIR
```python
BASE_DIR = "/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/Project_Game_Load_Script-Cursor/Generate_LoadDB_Script_Gamification/WORK"
```
**Описание:** Абсолютный путь к рабочей директории проекта
**Тип:** str
**Использование:** Базовая директория для всех операций с файлами

#### SUBDIRECTORIES
```python
SUBDIRECTORIES = {
    "INPUT": "INPUT",      # Входные CSV/TXT файлы
    "SCRIPT": "SCRIPT",    # Сгенерированные JavaScript скрипты
    "OUTPUT": "OUTPUT",    # Excel файлы результатов
    "JSON": "JSON",        # JSON файлы от API
    "LOGS": "LOGS",        # Логи выполнения
    "CONFIG": "CONFIG"     # Конфигурационные файлы
}
```
**Описание:** Словарь с названиями поддиректорий
**Тип:** dict
**Использование:** Определение структуры рабочих директорий

#### LOG_MESSAGES
```python
LOG_MESSAGES = {
    'function_start': '🚀 [START] {func} args={args}, kwargs={kwargs}',
    'function_completed': '✅ [END] {func} args={args}, kwargs={kwargs} (время: {time}s)',
    'function_error': '❌ [ERROR] {func} args={args}, kwargs={kwargs} - {error}',
    'script_generated': '📝 Скрипт {script_name} сгенерирован ({count} элементов)',
    'file_loaded': '📁 Файл загружен: {filepath}, элементов: {count}',
    'excel_created': '📊 Excel файл создан: {filepath}'
}
```
**Описание:** Шаблоны сообщений для логирования
**Тип:** dict
**Использование:** Стандартизация сообщений в логах

### Система конфигурации FUNCTION_CONFIGS

#### Структура конфигурации
```python
FUNCTION_CONFIGS = {
    "script_name": {
        "name": "Human Readable Name",
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
                "delay_between_requests": 5
            }
        },
        "input_file": "filename.csv",
        "active_operations": "scripts_only|json_only|both"
    }
}
```

#### Параметры конфигурации

**name** (str)
- **Описание:** Человекочитаемое название скрипта
- **Пример:** "Leaders For Admin", "Reward System"

**selected_variant** (str)
- **Описание:** Выбранный вариант окружения
- **Значения:** "sigma" (продакшн), "alpha" (тестовое)
- **По умолчанию:** "sigma"

**variants** (dict)
- **Описание:** Словарь с вариантами конфигурации
- **Структура:** Ключ - название окружения, значение - параметры

**domain** (str)
- **Описание:** Базовый URL API
- **Пример:** "https://salesheroes.sberbank.ru"

**params** (dict)
- **api_path** (str): Путь к API
- **service** (str): Название сервиса/эндпоинта

**timeout** (int)
- **Описание:** Таймаут запроса в миллисекундах
- **По умолчанию:** 30000 (30 секунд)

**retry_count** (int)
- **Описание:** Количество повторных попыток при ошибке
- **По умолчанию:** 3

**delay_between_requests** (int)
- **Описание:** Задержка между запросами в миллисекундах
- **По умолчанию:** 5

**input_file** (str)
- **Описание:** Имя файла с входными данными
- **Расположение:** WORK/CONFIG/
- **Формат:** CSV

**active_operations** (str)
- **Описание:** Режим работы программы
- **Значения:**
  - "scripts_only" - только генерация скриптов
  - "json_only" - только обработка JSON
  - "both" - полный цикл

### Примеры конфигураций

#### Leaders For Admin
```python
"leaders_for_admin": {
    "name": "Leaders For Admin",
    "selected_variant": "sigma",
    "variants": {
        "sigma": {
            "domain": "https://salesheroes.sberbank.ru",
            "params": {
                "api_path": "/bo/rmkib.gamification/api/v1/tournaments/",
                "service": "leadersForAdmin"
            },
            "timeout": 30000,
            "retry_count": 3,
            "delay_between_requests": 5
        }
    },
    "input_file": "TOURNAMENT-SCHEDULE (PROM) 2025-07-25 v6.csv",
    "active_operations": "both"
}
```

#### Reward System
```python
"reward": {
    "name": "Reward System",
    "selected_variant": "sigma",
    "variants": {
        "sigma": {
            "domain": "https://salesheroes.sberbank.ru",
            "params": {
                "api_path": "/bo/rmkib.gamification/api/v1/badges/",
                "service": "profiles"
            },
            "timeout": 30000,
            "retry_count": 3,
            "delay_between_requests": 5
        }
    },
    "input_file": "REWARD (PROM) 2025-07-24 v1.csv",
    "active_operations": "scripts_only"
}
```

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

**Назначение:** Выгрузка профилей участников по кодам наград с поддержкой пагинации и детальной обработкой данных.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/badges/{reward_code}/profiles`

### 3. Reward Profiles Processing (Обработка профилей наград)

**Назначение:** Обработка JSON файлов с данными профилей наград и конвертация в Excel с разворотом в плоскую структуру.

**Особенности:**
- ✅ Обработка структуры `badgeInfo.leaders` из JSON файлов профилей наград
- ✅ Разворот вложенных JSON объектов в плоскую структуру
- ✅ Обработка тегов, цветовых кодов, заработанных наград
- ✅ Детальная информация о каждом лидере награды
- ✅ Автоматическое определение типа файла по имени
- ✅ Создание Excel файла с форматированием и стилями

**Структура обрабатываемых данных:**
```json
{
  "REWARD_CODE": {
    "profilesCount": 0,
    "profiles": [],
    "badgeInfo": {
      "badgeId": "REWARD_CODE",
      "contestants": "65 участников по стране",
      "leaders": [
        {
          "isMarked": false,
          "employeeNumber": "00640863",
          "lastName": "Спирчагова",
          "firstName": "Ольга",
          "terDivisionName": "МБ",
          "gosbCode": "90384",
          "earnedBadges": [],
          "receivingDate": "11.10.24",
          "employeeStatus": "NON_CONTESTANT",
          "colorCode": {
            "primary": "gray-60",
            "secondary": "gray-30"
          },
          "tags": [
            {
              "tagId": "REWARD_CODE",
              "tagName": "AI-community",
              "tagColor": "purple-80"
            }
          ]
        }
      ]
    }
  }
}
```

**Поля Excel:**
- `rewardCode` - код награды
- `badgeId` - ID награды
- `contestants` - информация об участниках
- `profilesCount` - количество профилей
- `employeeNumber` - табельный номер
- `lastName`, `firstName` - ФИО
- `fullName` - полное имя
- `terDivisionName` - подразделение
- `gosbCode` - код ГОСБ
- `employeeStatus` - статус сотрудника
- `receivingDate` - дата получения
- `isMarked` - отмечен ли
- `colorPrimary`, `colorSecondary` - цветовые коды
- `earnedBadgesCount` - количество заработанных наград
- `earnedBadgesList` - список заработанных наград
- `tagsCount` - количество тегов
- `tagsList` - список тегов
- `tag1_id`, `tag1_name`, `tag1_color` - детали тегов (до 5 тегов)

**Конфигурация:**
```python
"reward_profiles": {
    "name": "Reward Profiles",
    "description": "Обработка профилей наград из JSON в Excel",
    "active_operations": "json_only",
    "json_file": "profiles_SIGMA_20250727-032838",
    "excel_file": "RewardProfiles"
}
```

**Особенности:**
- ✅ Поддержка пагинации (100 профилей на страницу)
- ✅ Автоматический подсчет страниц и участников
- ✅ Извлечение информации о наградах (badgeInfo)
- ✅ Обработка различных структур ответа API
- ✅ Поддержка двух окружений: SIGMA (продакшн) и ALPHA (тестовое)
- ✅ Автоматическое извлечение профилей из различных структур данных
- ✅ Настраиваемые таймауты и задержки между запросами
- ✅ Обработка ошибок и повторные попытки

**Поддерживаемые структуры данных API:**
1. `body.badge.profiles` - профили в структуре badge
2. `body.profiles` - прямые профили в body
3. `body.array` - массив профилей в body
4. `root.array` - массив профилей в корне

**Структура результата:**
```json
{
  "reward_code": {
    "profilesCount": 150,
    "profiles": [...],
    "badgeInfo": {
      "name": "Награда за достижения",
      "description": "Описание награды",
      "type": "achievement",
      "category": "sales"
    },
    "totalContestants": 150,
    "pages": 2
  }
}
```

**Поля профиля:**
- `rewardCode` - код награды
- `badgeName` - название награды
- `badgeDescription` - описание награды
- `badgeType` - тип награды
- `badgeCategory` - категория награды
- `employeeNumber` - табельный номер
- `lastName`, `firstName`, `middleName` - ФИО
- `fullName` - полное имя
- `email`, `phone`, `mobilePhone` - контакты
- `terDivisionName`, `divisionName`, `departmentName` - подразделения
- `positionName` - должность
- `employeeStatus` - статус сотрудника
- `businessBlock` - бизнес-блок
- `awardDate`, `awardReason`, `awardLevel`, `awardValue` - информация о награде
- `indicatorValue`, `successValue`, `rating`, `placeInRating` - показатели
- `photoUrl`, `isActive`, `lastActivityDate` - дополнительные данные

**Конфигурация параметров:**
```json
{
  "timeout": 30000,           // Таймаут запроса в миллисекундах
  "retry_count": 3,           // Количество попыток при ошибке
  "delay_between_requests": 5 // Задержка между запросами в миллисекундах
}
```

**Обработка ошибок:**
- HTTP ошибки (статус коды 4xx, 5xx)
- Таймауты (превышение времени ожидания)
- Ошибки сети (проблемы с соединением)
- Ошибки парсинга (неверная структура данных)
- Автоматические повторные попытки с экспоненциальной задержкой

### 4. Profile System (Система профилей)

**Назначение:** Выгрузка детальной информации о профилях пользователей.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/profiles/{profile_id}`

### 5. News System (Система новостей)

**Назначение:** Выгрузка списка новостей и их детальной информации.

**API Endpoints:**
- Список: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/news`
- Детали: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/news/{news_id}`

### 6. Address Book (Адресная книга)

**Назначение:** Выгрузка контактной информации сотрудников.

**API Endpoints:**
- TN: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/addressbook/tn`
- DEV: `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/addressbook/dev`

### 7. Orders System (Система заказов)

**Назначение:** Выгрузка информации о заказах и транзакциях.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/orders`

### 8. Rating List (Рейтинг)

**Назначение:** Выгрузка рейтинговых списков участников.

**API Endpoint:** `https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/ratings`

## 🔧 Подробное описание функций

### Система логирования

#### setup_logging()
```python
def setup_logging():
```
**Назначение:** Инициализация системы логирования
**Параметры:** Нет
**Возвращает:** logger - настроенный объект логирования
**Функциональность:**
- Создание директории для логов
- Настройка ротации файлов (5 файлов по 10MB)
- Форматирование сообщений с временными метками
- Установка уровня логирования DEBUG

#### measure_time()
```python
def measure_time(func):
```
**Назначение:** Декоратор для измерения времени выполнения функций
**Параметры:** func - функция для измерения
**Возвращает:** wrapper - обернутая функция
**Функциональность:**
- Логирование начала выполнения функции
- Измерение времени выполнения
- Логирование завершения с временем
- Обработка и логирование ошибок
- Исключение вывода содержимого скриптов в логи

### Загрузка и обработка данных

#### load_data_from_file()
```python
def load_data_from_file(filepath, file_format="TXT", csv_delimiter=None, csv_encoding=None, csv_column=None):
```
**Назначение:** Загрузка данных из файлов различных форматов
**Параметры:**
- filepath (str): Путь к файлу
- file_format (str): Формат файла ("TXT", "CSV")
- csv_delimiter (str): Разделитель для CSV (по умолчанию ";")
- csv_encoding (str): Кодировка файла (по умолчанию "utf-8")
- csv_column (str): Название столбца для извлечения данных
**Возвращает:** list - список данных
**Функциональность:**
- Поддержка TXT и CSV форматов
- Автоматическое определение кодировки
- Извлечение данных из указанного столбца
- Обработка ошибок чтения файлов

#### load_script_data()
```python
def load_script_data(config_key, data_list=None):
```
**Назначение:** Загрузка конфигурации и данных для генерации скриптов
**Параметры:**
- config_key (str): Ключ конфигурации скрипта
- data_list (list): Список данных (опционально)
**Возвращает:** tuple (config, data_list, selected_variant, variant_config)
**Функциональность:**
- Загрузка конфигурации из FUNCTION_CONFIGS
- Определение выбранного варианта (SIGMA/ALPHA)
- Загрузка данных из файла если не переданы
- Валидация конфигурации

### Генерация скриптов

#### generate_leaders_for_admin_script()
```python
def generate_leaders_for_admin_script(data_list=None):
```
**Назначение:** Генерация JavaScript скрипта для выгрузки данных лидеров турниров
**Параметры:**
- data_list (list): Список ID турниров (опционально)
**Возвращает:** str - сгенерированный JavaScript скрипт
**Функциональность:**
- Загрузка конфигурации и данных
- Генерация JavaScript кода с параметрами
- Формирование массива IDs в одну строку
- Сохранение скрипта в файл
- Подробное логирование процесса

#### generate_reward_script()
```python
def generate_reward_script(data_list=None):
```
**Назначение:** Генерация JavaScript скрипта для выгрузки профилей по кодам наград
**Параметры:**
- data_list (list): Список кодов наград (опционально)
**Возвращает:** str - сгенерированный JavaScript скрипт
**Функциональность:**
- Загрузка конфигурации и данных
- Генерация JavaScript кода с поддержкой пагинации
- Реализация функций removePhotoData, extractProfiles, fetchWithRetry
- Формирование массива IDs в одну строку
- Сохранение скрипта в файл
- Подробное логирование процесса

### Сохранение файлов

#### save_script_to_file()
```python
def save_script_to_file(script_content, script_name, config_key=None):
```
**Назначение:** Сохранение сгенерированного скрипта в файл
**Параметры:**
- script_content (str): Содержимое скрипта
- script_name (str): Название скрипта
- config_key (str): Ключ конфигурации (для определения имени файла)
**Возвращает:** str - путь к сохраненному файлу
**Функциональность:**
- Создание директории если не существует
- Генерация имени файла с временной меткой
- Включение варианта в имя файла для reward и leaders_for_admin
- Сохранение в кодировке utf-8
- Логирование результата

### Обработка JSON данных

#### load_json_data()
```python
def load_json_data(input_json_path):
```
**Назначение:** Загрузка JSON данных из файла
**Параметры:**
- input_json_path (str): Путь к JSON файлу
**Возвращает:** dict - загруженные данные
**Функциональность:**
- Проверка существования файла
- Загрузка JSON с обработкой ошибок
- Логирование результата загрузки

#### convert_leaders_json_to_excel()
```python
def convert_leaders_json_to_excel(input_json_path, output_excel_path, config_key=None):
```
**Назначение:** Конвертация JSON данных лидеров в Excel
**Параметры:**
- input_json_path (str): Путь к входному JSON файлу
- output_excel_path (str): Путь к выходному Excel файлу
- config_key (str): Ключ конфигурации
**Возвращает:** str - путь к созданному Excel файлу
**Функциональность:**
- Загрузка JSON данных
- Обработка структуры данных лидеров
- Уплощение вложенных объектов
- Создание DataFrame с pandas
- Применение стилей Excel
- Создание сводных листов

#### convert_reward_json_to_excel()
```python
def convert_reward_json_to_excel(input_json_path, output_excel_path, config_key=None):
```
**Назначение:** Конвертация JSON данных наград в Excel
**Параметры:**
- input_json_path (str): Путь к входному JSON файлу
- output_excel_path (str): Путь к выходному Excel файлу
- config_key (str): Ключ конфигурации
**Возвращает:** str - путь к созданному Excel файлу
**Функциональность:**
- Загрузка JSON данных
- Обработка структуры данных наград
- Извлечение профилей из различных структур
- Уплощение вложенных объектов
- Создание DataFrame с pandas
- Применение стилей Excel
- Создание сводных листов включая REWARD_SUMMARY

#### convert_reward_profiles_json_to_excel()
```python
def convert_reward_profiles_json_to_excel(input_json_path, output_excel_path, config_key=None):
```
**Назначение:** Конвертация JSON данных профилей наград в Excel
**Параметры:**
- input_json_path (str): Путь к входному JSON файлу
- output_excel_path (str): Путь к выходному Excel файлу
- config_key (str): Ключ конфигурации
**Возвращает:** str - путь к созданному Excel файлу
**Функциональность:**
- Загрузка JSON данных профилей наград
- Обработка структуры `badgeInfo.leaders`
- Разворот вложенных JSON объектов в плоскую структуру
- Обработка тегов, цветовых кодов, заработанных наград
- Создание DataFrame с pandas
- Применение стилей Excel
- Создание сводных листов

### Вспомогательные функции

#### flatten_leader_data()
```python
def flatten_leader_data(leader_data):
```
**Назначение:** Уплощение данных лидера в плоскую структуру
**Параметры:**
- leader_data (dict): Данные лидера
**Возвращает:** dict - уплощенные данные
**Функциональность:**
- Извлечение основных полей (ФИО, должность, рейтинг)
- Обработка вложенных объектов
- Безопасное преобразование типов данных

#### flatten_reward_profile_data()
```python
def flatten_reward_profile_data(profile_data):
```
**Назначение:** Уплощение данных профиля награды в плоскую структуру
**Параметры:**
- profile_data (dict): Данные профиля
**Возвращает:** dict - уплощенные данные
**Функциональность:**
- Извлечение всех полей профиля
- Обработка вложенных объектов (подразделения, контакты)
- Безопасное преобразование типов данных
- Обработка отсутствующих значений

#### flatten_reward_leader_data()
```python
def flatten_reward_leader_data(leader_data, reward_code):
```
**Назначение:** Уплощение данных лидера награды в плоскую структуру
**Параметры:**
- leader_data (dict): Данные лидера из структуры наград
- reward_code (str): Код награды
**Возвращает:** dict - уплощенные данные лидера награды
**Функциональность:**
- Извлечение основных полей лидера (ФИО, должность, статус)
- Обработка вложенных объектов (colorCode, earnedBadges, tags)
- Разворот тегов в отдельные поля (до 5 тегов)
- Создание полного имени
- Обработка цветовых кодов
- Подсчет количества тегов и наград

#### parse_float_safe()
```python
def parse_float_safe(val, context=None):
```
**Назначение:** Безопасное преобразование значений в float
**Параметры:**
- val: Значение для преобразования
- context (str): Контекст для логирования ошибок
**Возвращает:** float или None
**Функциональность:**
- Обработка различных форматов чисел
- Поддержка европейского формата (запятая)
- Обработка отсутствующих значений
- Логирование ошибок преобразования

### Excel функции

#### apply_excel_styling()
```python
def apply_excel_styling(workbook, freeze_cell="B2"):
```
**Назначение:** Применение стилей к Excel файлу
**Параметры:**
- workbook: Объект рабочей книги Excel
- freeze_cell (str): Ячейка для закрепления панелей
**Возвращает:** None
**Функциональность:**
- Настройка ширины столбцов
- Закрепление панелей
- Применение стилей к заголовкам
- Настройка фильтров

#### create_summary_sheet()
```python
def create_summary_sheet(workbook, data_df):
```
**Назначение:** Создание сводного листа
**Параметры:**
- workbook: Объект рабочей книги Excel
- data_df: DataFrame с данными
**Возвращает:** None
**Функциональность:**
- Создание листа SUMMARY
- Добавление статистики по данным
- Применение стилей

#### create_reward_summary_sheet()
```python
def create_reward_summary_sheet(workbook, data_df):
```
**Назначение:** Создание сводного листа для наград
**Параметры:**
- workbook: Объект рабочей книги Excel
- data_df: DataFrame с данными наград
**Возвращает:** None
**Функциональность:**
- Создание листа REWARD_SUMMARY
- Группировка по кодам наград
- Статистика по наградам
- Применение стилей

### Основные функции управления

#### main()
```python
def main():
```
**Назначение:** Основная функция управления программой
**Параметры:** Нет
**Возвращает:** None
**Функциональность:**
- Инициализация логирования
- Определение активных скриптов
- ЭТАП 1: Генерация всех скриптов
- ЭТАП 2: Обработка всех JSON файлов
- Вывод итоговой статистики
- Обработка аргументов командной строки

#### print_summary()
```python
def print_summary():
```
**Назначение:** Вывод итоговой статистики выполнения
**Параметры:** Нет
**Возвращает:** None
**Функциональность:**
- Вывод общего времени выполнения
- Статистика по функциям
- Количество обработанных действий
- Форматированный вывод результатов

## 📊 Примеры данных и работы функций

### Примеры входных данных

#### CSV файл для Leaders For Admin
```csv
TOURNAMENT_ID
TOURNAMENT_001
TOURNAMENT_002
TOURNAMENT_003
```

#### CSV файл для Reward System
```csv
REWARD_CODE
REWARD_001
REWARD_002
REWARD_003
```

### Примеры JSON ответов API

#### Leaders For Admin Response
```json
{
  "TOURNAMENT_001": {
    "body": {
      "tournament": {
        "leaders": [
          {
            "employeeNumber": "12345",
            "lastName": "Иванов",
            "firstName": "Иван",
            "middleName": "Иванович",
            "fullName": "Иванов Иван Иванович",
            "division": "Центральный банк",
            "position": "Менеджер",
            "rating": 95.5,
            "points": 1500
          }
        ]
      }
    }
  }
}
```

#### Reward System Response
```json
{
  "REWARD_001": {
    "profilesCount": 150,
    "profiles": [
      {
        "employeeNumber": "12345",
        "lastName": "Петров",
        "firstName": "Петр",
        "middleName": "Петрович",
        "fullName": "Петров Петр Петрович",
        "email": "petrov@sberbank.ru",
        "phone": "+7-999-123-45-67",
        "terDivisionName": "Центральный банк",
        "divisionName": "Отдел продаж",
        "departmentName": "Департамент розничного бизнеса",
        "positionName": "Менеджер по продажам",
        "employeeStatus": "Активный",
        "businessBlock": "Розничный бизнес",
        "awardDate": "2025-01-15",
        "awardReason": "Высокие показатели продаж",
        "awardLevel": "Золото",
        "awardValue": 50000,
        "indicatorValue": 125.5,
        "successValue": 98.2,
        "rating": 95.5,
        "placeInRating": 1,
        "photoUrl": "https://example.com/photo.jpg",
        "isActive": true,
        "lastActivityDate": "2025-01-20"
      }
    ],
    "badgeInfo": {
      "name": "Награда за достижения",
      "description": "Награда за высокие показатели в продажах",
      "type": "achievement",
      "category": "sales"
    },
    "totalContestants": 150,
    "pages": 2
  }
}
```

### Примеры работы функций

#### Генерация скрипта Leaders For Admin
```python
# Вызов функции
script = generate_leaders_for_admin_script(["TOURNAMENT_001", "TOURNAMENT_002"])

# Результат - JavaScript скрипт
const ids = ["TOURNAMENT_001", "TOURNAMENT_002"];
const BASE_URL = "https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/tournaments/";
// ... остальной код скрипта
```

#### Генерация скрипта Reward System
```python
# Вызов функции
script = generate_reward_script(["REWARD_001", "REWARD_002"])

# Результат - JavaScript скрипт с пагинацией
const ids = ["REWARD_001", "REWARD_002"];
const BASE_URL = "https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/badges/";
// ... код с поддержкой пагинации и обработки ошибок
```

#### Конвертация JSON в Excel
```python
# Вызов функции
excel_path = convert_reward_json_to_excel(
    "profiles_SIGMA_20250101-120000.json",
    "reward_data.xlsx",
    "reward"
)

# Результат - Excel файл с листами:
# - DATA: основные данные профилей
# - SUMMARY: общая статистика
# - STATISTICS: статистика по подразделениям
# - REWARD_SUMMARY: сводка по наградам
```

#### Обработка данных профиля
```python
# Входные данные
profile_data = {
    "employeeNumber": "12345",
    "lastName": "Петров",
    "firstName": "Петр",
    "division": {
        "name": "Центральный банк",
        "code": "CB001"
    },
    "contacts": {
        "email": "petrov@sberbank.ru",
        "phone": "+7-999-123-45-67"
    }
}

# Результат flatten_reward_profile_data()
flattened_data = {
    "employeeNumber": "12345",
    "lastName": "Петров",
    "firstName": "Петр",
    "divisionName": "Центральный банк",
    "divisionCode": "CB001",
    "email": "petrov@sberbank.ru",
    "phone": "+7-999-123-45-67"
}
```

### Примеры логов

#### Логирование функции
```
🚀 [START] generate_reward_script args=(), kwargs=[]
📁 Файл загружен: WORK/CONFIG/REWARD (PROM) 2025-07-24 v1.csv, элементов: 5
📝 Скрипт Reward System сгенерирован (5 элементов)
✅ [END] generate_reward_script args=(), kwargs=[] (время: 0.15s)
```

#### Логирование ошибок
```
❌ [ERROR] load_data_from_file args=('invalid_file.csv',), kwargs={} - [Errno 2] No such file or directory: 'invalid_file.csv'
```

#### Статистика выполнения
```
📊 ИТОГОВАЯ СТАТИСТИКА:
⏱️ Общее время выполнения: 45.23 секунды
📝 Сгенерировано скриптов: 2
📊 Обработано JSON файлов: 3
✅ Успешных операций: 5
❌ Ошибок: 0
```

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

## 🎮 Управление программой

### Режимы работы

#### 1. Полный цикл (по умолчанию)
```bash
python main.py
```
**Действия:**
- Генерация всех активных скриптов
- Обработка всех JSON файлов в WORK/JSON/
- Создание Excel файлов с результатами

#### 2. Конкретный скрипт
```bash
python main.py reward
python main.py leaders_for_admin
```
**Действия:**
- Генерация только указанного скрипта
- Обработка JSON файлов для этого скрипта

#### 3. Только генерация скриптов
```python
# В конфигурации установить:
"active_operations": "scripts_only"
```
**Действия:**
- Генерация скриптов без обработки JSON

#### 4. Только обработка JSON
```python
# В конфигурации установить:
"active_operations": "json_only"
```
**Действия:**
- Обработка существующих JSON файлов
- Создание Excel файлов

### Управление конфигурацией

#### Изменение активных скриптов
```python
# В main.py изменить:
ACTIVE_SCRIPTS = ["reward"]  # Только reward
ACTIVE_SCRIPTS = ["leaders_for_admin", "reward"]  # Оба скрипта
```

#### Изменение окружения
```python
# Для SIGMA (продакшн)
FUNCTION_CONFIGS["reward"]["selected_variant"] = "sigma"

# Для ALPHA (тестовое)
FUNCTION_CONFIGS["reward"]["selected_variant"] = "alpha"
```

#### Настройка параметров API
```python
# Изменение таймаута
FUNCTION_CONFIGS["reward"]["variants"]["sigma"]["timeout"] = 60000

# Изменение количества попыток
FUNCTION_CONFIGS["reward"]["variants"]["sigma"]["retry_count"] = 5

# Изменение задержки
FUNCTION_CONFIGS["reward"]["variants"]["sigma"]["delay_between_requests"] = 10
```

### Управление файлами

#### Структура директорий
```
WORK/
├── CONFIG/          # Входные CSV файлы
│   ├── TOURNAMENT-SCHEDULE (PROM) 2025-07-25 v6.csv
│   └── REWARD (PROM) 2025-07-24 v1.csv
├── SCRIPT/          # Сгенерированные JavaScript скрипты
│   ├── LeadersForAdmin_SIGMA_20250727_123456.txt
│   └── Reward_SIGMA_20250727_123456.txt
├── JSON/            # JSON файлы от API (создаются вручную)
│   ├── leaders_SIGMA_20250727_123456.json
│   └── profiles_SIGMA_20250727_123456.json
├── OUTPUT/          # Excel файлы результатов
│   ├── leaders_SIGMA_20250727_123456.xlsx
│   └── reward_SIGMA_20250727_123456.xlsx
└── LOGS/            # Логи выполнения
    └── game_script_generator_2025-07-27.log
```

#### Управление входными данными
- **Формат:** CSV файлы с заголовком
- **Разделитель:** точка с запятой (;)
- **Кодировка:** UTF-8
- **Расположение:** WORK/CONFIG/

#### Управление выходными данными
- **Скрипты:** WORK/SCRIPT/ с временными метками
- **Excel:** WORK/OUTPUT/ с форматированием
- **Логи:** WORK/LOGS/ с ротацией

### Мониторинг и отладка

#### Уровни логирования
```python
# Детальное логирование
LOG_LEVEL = "DEBUG"

# Только важная информация
LOG_LEVEL = "INFO"

# Только ошибки
LOG_LEVEL = "ERROR"
```

#### Просмотр логов
```bash
# Последние записи
tail -f WORK/LOGS/game_script_generator_2025-07-27.log

# Поиск ошибок
grep "ERROR" WORK/LOGS/game_script_generator_2025-07-27.log

# Поиск конкретной функции
grep "generate_reward_script" WORK/LOGS/game_script_generator_2025-07-27.log
```

#### Статистика выполнения
Программа выводит подробную статистику:
- Общее время выполнения
- Время каждой функции
- Количество обработанных элементов
- Количество ошибок
- Пути к созданным файлам

### Обработка ошибок

#### Типичные ошибки и решения

**1. Файл не найден**
```
❌ [ERROR] load_data_from_file - [Errno 2] No such file or directory
```
**Решение:** Проверить наличие файла в WORK/CONFIG/

**2. Ошибка API**
```
❌ [ERROR] fetchWithRetry - HTTP 401 Unauthorized
```
**Решение:** Проверить авторизацию в браузере

**3. Ошибка синтаксиса JavaScript**
```
SyntaxError: Unexpected EOF
```
**Решение:** Проверить экранирование в generate_reward_script

**4. Ошибка Excel**
```
❌ [ERROR] convert_reward_json_to_excel - Permission denied
```
**Решение:** Проверить права доступа к WORK/OUTPUT/

### Автоматизация

#### Планировщик задач (cron)
```bash
# Ежедневный запуск в 9:00
0 9 * * * cd /path/to/project && python main.py

# Запуск каждые 2 часа
0 */2 * * * cd /path/to/project && python main.py reward
```

#### Скрипт запуска
```bash
#!/bin/bash
# run_scripts.sh
cd /path/to/project
source local_env/bin/activate
python main.py >> WORK/LOGS/run_$(date +%Y%m%d).log 2>&1
```

### Резервное копирование

#### Автоматическое резервное копирование
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_${DATE}.tar.gz WORK/
```

#### Восстановление из резервной копии
```bash
tar -xzf backup_20250727_120000.tar.gz
```
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

### Примеры использования Reward System

#### Базовый пример
```python
# Генерация скрипта для SIGMA
python main.py reward

# Конвертация результатов
convert_reward_json_to_excel("profiles_SIGMA_20250101-120000.json", "reward_data.xlsx", "reward")
```

#### Настройка параметров
```python
# Изменение конфигурации для ALPHA
FUNCTION_CONFIGS["reward"]["selected_variant"] = "alpha"
FUNCTION_CONFIGS["reward"]["variants"]["alpha"]["timeout"] = 60000
FUNCTION_CONFIGS["reward"]["variants"]["alpha"]["retry_count"] = 5
```

#### Подготовка данных
Создайте CSV файл с кодами наград в формате:
```csv
REWARD_CODE
REWARD_001
REWARD_002
REWARD_003
```

#### Выполнение скрипта
1. Откройте DevTools в браузере
2. Вставьте сгенерированный скрипт в консоль
3. Нажмите Enter для выполнения
4. Дождитесь скачивания JSON файла

#### Мониторинг выполнения
- Подробные логи всех операций
- Статистика обработки (общее количество, успешно, пропущено, ошибки)
- Информация об ошибках с деталями

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