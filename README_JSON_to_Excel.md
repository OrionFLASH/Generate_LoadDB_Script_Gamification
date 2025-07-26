# Конвертер JSON в Excel для данных LeadersForAdmin

## Описание

Автономная программа для конвертации JSON файлов с данными LeadersForAdmin в Excel файлы с форматированием и статистикой.

## Возможности

- ✅ Загрузка JSON файлов с данными LeadersForAdmin
- ✅ Автоматическое парсинг и обработка данных
- ✅ Создание Excel файлов с несколькими листами:
  - **DATA** - основные данные участников
  - **SUMMARY** - сводная статистика
  - **STATISTICS** - статистика по подразделениям и бизнес-блокам
- ✅ Применение стилей и форматирования к Excel файлам
- ✅ Обработка европейского формата чисел (запятая вместо точки)
- ✅ Автоматическая настройка ширины столбцов

## Установка зависимостей

```bash
pip install pandas openpyxl
```

## Использование

### Базовое использование

```bash
python json_to_excel_converter.py input.json output.xlsx
```

### Примеры

```bash
# Конвертация файла в текущей директории
python json_to_excel_converter.py data.json result.xlsx

# Конвертация с полными путями
python json_to_excel_converter.py /path/to/input.json /path/to/output.xlsx

# Подробный вывод
python json_to_excel_converter.py input.json output.xlsx --verbose
```

### Параметры командной строки

- `input_file` - путь к входному JSON файлу (обязательный)
- `output_file` - путь к выходному Excel файлу (обязательный)
- `--verbose, -v` - подробный вывод (опциональный)
- `--help, -h` - справка

## Структура данных

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

## Выходные данные

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

## Особенности

1. **Автоматическое создание директорий** - программа создает необходимые директории для выходного файла
2. **Обработка ошибок** - подробные сообщения об ошибках
3. **Форматирование** - автоматическое применение стилей к Excel файлу
4. **Парсинг чисел** - корректная обработка европейского формата чисел

## Примеры использования

### Конвертация файла LeadersForAdmin

```bash
python json_to_excel_converter.py leadersForAdmin_SIGMA_20250726-192035.json output.xlsx
```

### Создание файла с подробным выводом

```bash
python json_to_excel_converter.py input.json output.xlsx --verbose
```

## Автор

OrionFLASH

## Версия

1.0.0 