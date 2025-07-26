#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный модуль для генерации JavaScript скриптов
Автор: OrionFLASH
Описание: Программа для создания JavaScript скриптов на основе входных данных
         с поддержкой логирования, измерения времени выполнения и копирования в буфер обмена
"""

import logging
import os
import time
import datetime
import csv
import re
import json
import pandas as pd
from functools import wraps

# Импорт библиотеки для работы с буфером обмена
import pyperclip

# Импорт библиотек для работы с Excel
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule

# =============================================================================
# КОНСТАНТЫ И НАСТРОЙКИ ПРОГРАММЫ
# =============================================================================

# Настройки логирования
LOG_LEVEL = "DEBUG"  # Уровень детализации логов: "INFO" - основная информация, "DEBUG" - подробная отладочная информация
LOG_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/LOGS"  # Абсолютный путь к директории для сохранения файлов логов
LOG_FILENAME_BASE = "game_script_generator"  # Базовое имя файла лога (к нему добавляется дата и время)

# Настройки входных и выходных данных
INPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"  # Абсолютный путь к директории с входными файлами (CSV, TXT)
OUTPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"  # Абсолютный путь к директории для сохранения сгенерированных файлов

# Настройки обработки данных
DATA_SOURCE = "external_file"  # Источник данных: "file" - из основного файла, "variable" - из тестовых данных, "external_file" - из конфигурации функции
INPUT_FORMAT = "CSV"  # Формат входного файла: "TXT" - текстовый файл, "CSV" - табличный файл с разделителями
INPUT_FILENAME = "input_data"  # Имя основного входного файла без расширения (расширение добавляется автоматически)
INPUT_FILE_EXTENSION = ".txt"  # Расширение по умолчанию для основного входного файла (используется как fallback)

# Расширения файлов для различных форматов
# Словарь для автоматического определения расширения файла на основе его формата
# Используется для формирования полных путей к файлам
FILE_EXTENSIONS = {
    "CSV": ".csv",    # Ключ: формат CSV файлов
    "TXT": ".txt",    # Ключ: формат текстовых файлов  
    "JSON": ".json"   # Ключ: формат JSON файлов
}

# =============================================================================
# НАСТРОЙКИ ОПЕРАЦИЙ
# =============================================================================

# Выбор активных операций
# Список операций, которые будут выполнены при запуске программы
# Доступные операции:
# - "generate_scripts" - генерация JavaScript скриптов на основе входных данных
# - "process_json" - конвертация JSON файлов в Excel с форматированием
ACTIVE_OPERATIONS = [
    "generate_scripts",  # Генерация JavaScript скриптов для различных сервисов
    "process_json"       # Обработка JSON файлов и создание Excel отчетов
]

# Выбор активных скриптов для генерации
# Список типов скриптов, которые будут сгенерированы
# Раскомментируйте нужные скрипты для генерации (уберите # в начале строки)
ACTIVE_SCRIPTS = [
    "leaders_for_admin",  # Скрипт для получения информации по участникам турнира (LeadersForAdmin)
    # "reward",             # Скрипт для получения информации о наградах сотрудников
    # "profile",            # Скрипт для получения профилей сотрудников
    # "news_details",       # Скрипт для получения детальной карточки новости
    # "address_book_tn",    # Скрипт для получения карточки сотрудника по табельному номеру
    # "address_book_dev",   # Скрипт для получения карточки подразделения
    # "orders",             # Скрипт для получения списка сотрудников с преференциями
    # "news_list",          # Скрипт для получения списка новостей
    # "rating_list"         # Скрипт для получения рейтинга участников
]

# Настройки обработки JSON файлов
# Конфигурация для конвертации JSON файлов в Excel с дополнительными возможностями
JSON_PROCESSING_CONFIG = {
    "input_directory": r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT",     # Ключ: директория для поиска JSON файлов (абсолютный путь)
    "output_directory": r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT",   # Ключ: директория для сохранения Excel файлов (абсолютный путь)
    "create_summary": True,         # Ключ: создавать лист SUMMARY с общей сводкой данных
    "create_statistics": True,      # Ключ: создавать лист STATISTICS с аналитическими данными
    "apply_styling": True           # Ключ: применять цветовое оформление и форматирование к Excel файлу
}



# Названия листов для экспорта Excel
# Словарь с названиями листов, которые будут созданы в Excel файле
EXCEL_SHEET_NAMES = {
    "data": "DATA",       # Ключ: основной лист с данными (плоская структура из JSON)
    "summary": "SUMMARY", # Ключ: лист с общей сводкой и метаданными
    "statistics": "STATISTICS"  # Ключ: лист со статистическими данными и аналитикой
}

# Цвета для оформления Excel
# Словарь с HEX-кодами цветов для оформления Excel файлов
# Используется для создания профессионального внешнего вида отчетов
EXCEL_COLORS = {
    "header": "366092",     # Ключ: темно-синий цвет для заголовков (основной)
    "subheader": "9BC2E6",  # Ключ: светло-синий цвет для подзаголовков
    "alternate": "E7E6E6",  # Ключ: светло-серый цвет для чередующихся строк
    "highlight": "FFEB9C"   # Ключ: желтый цвет для выделения важных данных
}

# Настройки для TXT файлов
# Массив всех возможных разделителей для текстовых файлов
# Программа автоматически определяет разделитель, анализируя содержимое файла
# Включает знаки препинания, пробелы, переносы строк и специальные символы
TXT_DELIMITERS = [",", ";", "\t", " ", "\n", "\r\n", "|", ":", ".", "!", "?", "@", "#", "$", "%", "^", "&", "*", "(", ")", "[", "]", "{", "}", "<", ">", "/", "\\", "=", "+", "~", "`", "'", '"']

# Настройки для CSV файлов
CSV_DELIMITER = ";"  # Разделитель колонок в CSV файлах (точка с запятой для европейского формата)
CSV_ENCODING = "utf-8"  # Кодировка CSV файлов (поддерживает кириллицу и специальные символы)
CSV_COLUMN_NAME = "data_column"  # Название столбца по умолчанию для извлечения данных (если не указан конкретный)

# Тестовые данные для работы без внешнего файла
# Список тестовых значений, используемых когда DATA_SOURCE = "variable"
# Позволяет тестировать программу без необходимости создания входных файлов
TEST_DATA_LIST = [
    "test_value_1",  # Тестовое значение 1
    "test_value_2",  # Тестовое значение 2
    "test_value_3"   # Тестовое значение 3
]

# =============================================================================
# ТЕКСТЫ ДЛЯ ЛОГИРОВАНИЯ
# =============================================================================

# Словарь с сообщениями для логирования
# Содержит все текстовые сообщения, выводимые программой
# Поддерживает форматирование с переменными в фигурных скобках {variable}
# Позволяет централизованно управлять всеми сообщениями программы
LOG_MESSAGES = {
    # Сообщения о начале и конце программы
    "program_start": "=== СТАРТ ПРОГРАММЫ - Генератор JavaScript скриптов: {time} ===",  # Ключ: сообщение о старте программы
    "program_end": "=== ФИНАЛ ПРОГРАММЫ - {time} ===",  # Ключ: сообщение о завершении программы
    "processing_start_time": "Время начала обработки: {time}",  # Ключ: время начала обработки
    "logging_level": "Уровень логирования: {level}",  # Ключ: уровень логирования
    "total_execution_time": "Итоговое время работы: {time:.4f} секунд",  # Ключ: общее время выполнения
    
    # Сообщения о выполнении функций
    "function_start": "[START] {func} {params}",  # Ключ: начало выполнения функции
    "function_completed": "[END] {func} {params} (время: {time:.4f}s)",  # Ключ: завершение функции
    "function_error": "[ERROR] {func} {params} — {error}",  # Ключ: ошибка в функции
    
    # Сообщения о данных
    "data_received": "Получено данных для обработки: {count}",  # Ключ: количество полученных данных
    "program_success": "Программа выполнена успешно",  # Ключ: успешное завершение программы
    "critical_error": "Критическая ошибка в программе: {error}",  # Ключ: критическая ошибка
    
    # Сообщения для итоговой статистики
    "summary_title": "SUMMARY - Итоговая статистика",  # Ключ: заголовок итоговой статистики
    "total_time": "Общее время: {time:.4f} сек",  # Ключ: общее время выполнения
    "actions_processed": "Действий: {count}",  # Ключ: количество обработанных действий
    "functions_executed": "Функций: {count}",  # Ключ: количество выполненных функций
    "function_time": "Функция {func}: {time:.4f} сек",  # Ключ: время выполнения конкретной функции
    "program_completed": "Программа завершена: {time}",  # Ключ: время завершения программы
    
    # Сообщения о работе с файлами
    "file_loading": "Загрузка данных из файла: {file_path}, формат: {format}",  # Ключ: загрузка файла
    "file_not_found": "Файл не найден: {file_path}",  # Ключ: файл не найден
    "file_loaded": "Файл успешно загружен: {file_path}, элементов: {count}",  # Ключ: файл загружен
    "file_load_error": "Ошибка загрузки файла: {file_path}. {error}",  # Ключ: ошибка загрузки файла
    "using_test_data": "Использование тестовых данных: {count} элементов",  # Ключ: использование тестовых данных
    
    # Сообщения о буфере обмена
    "clipboard_copied": "Текст скопирован в буфер обмена",  # Ключ: успешное копирование в буфер
    "clipboard_error": "Ошибка при копировании в буфер: {error}",  # Ключ: ошибка копирования в буфер
    
    # Сообщения о генерации скриптов
    "script_generation": "Генерация скрипта: {script_name}",  # Ключ: начало генерации скрипта
    "script_generated": "Скрипт {script_name} сгенерирован успешно (данных: {count})",  # Ключ: успешная генерация скрипта
    "script_saved": "Скрипт сохранен в файл: {file_path}",  # Ключ: скрипт сохранен в файл
    "script_save_error": "Ошибка сохранения скрипта: {error}",  # Ключ: ошибка сохранения скрипта
    
    # Сообщения для итоговой статистики
    "summary_stats": "ИТОГОВАЯ СТАТИСТИКА РАБОТЫ ПРОГРАММЫ",  # Ключ: заголовок статистики
    "total_execution": "Общее время выполнения: {time:.4f} секунд",  # Ключ: общее время выполнения
    "processed_actions": "Обработано действий: {count}",  # Ключ: количество обработанных действий
    "executed_functions": "Выполнено функций: {count}",  # Ключ: количество выполненных функций
    "execution_times": "Время выполнения функций:",  # Ключ: заголовок времени выполнения функций
    "selected_script": "Выбранный скрипт для генерации: {script_name}",  # Ключ: выбранный скрипт
    "config_loaded": "Конфигурация загружена для: {script_name}",  # Ключ: загрузка конфигурации
    
    # Сообщения о обработке файлов
    "csv_processing": "Обработка CSV: разделитель '{delimiter}', кодировка '{encoding}', столбец '{column}'",  # Ключ: обработка CSV файла
    "txt_processing": "Обработка TXT: найдено разделителей {delimiters_count}",  # Ключ: обработка TXT файла
    "data_source_selected": "Источник данных: {source} ({format})",  # Ключ: выбранный источник данных
    
    # Сообщения о обработке JSON файлов
    "json_conversion_start": "Начинаем конвертацию JSON: {input} -> {output}",  # Ключ: начало конвертации JSON
    "json_file_not_found": "JSON файл не найден: {file_path}",  # Ключ: JSON файл не найден
    "json_directory_created": "Создана директория: {directory}",  # Ключ: создана директория для JSON
    "json_data_loading": "Загружаем JSON данные...",  # Ключ: загрузка JSON данных
    "json_data_processing": "Обрабатываем JSON данные...",  # Ключ: обработка JSON данных
    "json_leaders_found": "Найдены данные лидеров в ключе: {key}, количество: {count}",  # Ключ: найдены данные лидеров
    "json_direct_leaders": "Прямой список лидеров, количество: {count}",  # Ключ: прямой список лидеров
    "json_invalid_format": "Неверный формат JSON данных",  # Ключ: неверный формат JSON
    "json_no_leaders": "Не найдены данные лидеров в JSON файле",  # Ключ: нет данных лидеров
    "json_records_processed": "Обработано {count} записей",  # Ключ: количество обработанных записей
    "json_excel_creation": "Создаем Excel файл...",  # Ключ: создание Excel файла
    "json_excel_success": "Excel файл успешно создан: {file_path}",  # Ключ: Excel файл создан
    "json_conversion_error": "Ошибка при конвертации JSON: {error}",  # Ключ: ошибка конвертации JSON
    "json_file_processing": "Обработка JSON файла: {file_name}",  # Ключ: обработка конкретного JSON файла
    "json_files_processed": "Обработано JSON файлов: {count}",  # Ключ: количество обработанных JSON файлов
    "json_no_files_found": "JSON файлы для обработки не найдены"  # Ключ: JSON файлы не найдены
}

# =============================================================================
# КОНФИГУРАЦИЯ ФУНКЦИЙ
# =============================================================================

# Словарь с конфигурацией для каждого типа скрипта
# Содержит параметры для генерации JavaScript и обработки данных
# Каждая конфигурация включает: домен, API пути, параметры запросов, настройки файлов
FUNCTION_CONFIGS = {
    "leaders_for_admin": {  # Ключ: конфигурация для скрипта LeadersForAdmin (информация по участникам турнира)
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
        "input_file": "TOURNAMENT-SCHEDULE (PROM) 2025-07-25 v6",  # Ключ: имя входного файла (без расширения)
        "json_file": "leadersForAdmin_SIGMA_20250726-192035"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "reward": {  # Ключ: конфигурация для скрипта REWARD (информация о наградах сотрудников)
        "name": "REWARD",  # Ключ: название скрипта для отображения
        "description": "Информация о сотрудниках которые уже получили награды",  # Ключ: описание назначения скрипта
        "domain": "rewards.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/rewards/list",  # Ключ: конечная точка API
            "include_details": True,  # Ключ: включать ли детали
            "status": "received",  # Ключ: статус наград
            "date_from": "2024-01-01"  # Ключ: дата начала периода
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "employee_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "reward"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "profile": {  # Ключ: конфигурация для скрипта PROFILE (профили сотрудников)
        "name": "PROFILE",  # Ключ: название скрипта для отображения
        "description": "Профили сотрудников в героях продаж",  # Ключ: описание назначения скрипта
        "domain": "profiles.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/profiles/employee",  # Ключ: конечная точка API
            "include_stats": True,  # Ключ: включать ли статистику
            "include_achievements": True,  # Ключ: включать ли достижения
            "format": "detailed"  # Ключ: формат ответа
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "TXT",  # Ключ: формат входного файла
        "csv_column": "profile_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "profile"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "news_details": {  # Ключ: конфигурация для скрипта NewsDetails (детальная карточка новости)
        "name": "NewsDetails",  # Ключ: название скрипта для отображения
        "description": "Детальная карточка новости",  # Ключ: описание назначения скрипта
        "domain": "news.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/news/details",  # Ключ: конечная точка API
            "include_content": True,  # Ключ: включать ли содержимое
            "include_attachments": True,  # Ключ: включать ли вложения
            "format": "full"  # Ключ: формат ответа
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "TXT",  # Ключ: формат входного файла
        "csv_column": "news_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "news_details"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "address_book_tn": {  # Ключ: конфигурация для скрипта AdressBookTN (карточка сотрудника по табельному номеру)
        "name": "AdressBookTN",  # Ключ: название скрипта для отображения
        "description": "Карточка сотрудника из адресной книги по табельным номерам",  # Ключ: описание назначения скрипта
        "domain": "directory.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/directory/employee",  # Ключ: конечная точка API
            "search_by": "employee_number",  # Ключ: поле для поиска
            "include_contacts": True,  # Ключ: включать ли контакты
            "include_department": True  # Ключ: включать ли отдел
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "employee_number",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "address_book_tn"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "address_book_dev": {  # Ключ: конфигурация для скрипта AdressBookDev (карточка подразделения)
        "name": "AdressBookDev",  # Ключ: название скрипта для отображения
        "description": "Карточка подразделения из адресной книги со списком сотрудников",  # Ключ: описание назначения скрипта
        "domain": "directory.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/directory/department",  # Ключ: конечная точка API
            "include_employees": True,  # Ключ: включать ли сотрудников
            "include_hierarchy": True,  # Ключ: включать ли иерархию
            "format": "detailed"  # Ключ: формат ответа
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "department_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "address_book_dev"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "orders": {  # Ключ: конфигурация для скрипта Orders (список сотрудников с преференциями)
        "name": "Orders",  # Ключ: название скрипта для отображения
        "description": "Список сотрудников выбравших преференции",  # Ключ: описание назначения скрипта
        "domain": "orders.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/orders/preferences",  # Ключ: конечная точка API
            "status": "selected",  # Ключ: статус заказов
            "include_details": True,  # Ключ: включать ли детали
            "date_from": "2024-01-01"  # Ключ: дата начала периода
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "employee_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "orders"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "news_list": {  # Ключ: конфигурация для скрипта NewsList (список новостей)
        "name": "NewsList",  # Ключ: название скрипта для отображения
        "description": "Список новостей",  # Ключ: описание назначения скрипта
        "domain": "news.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/news/list",  # Ключ: конечная точка API
            "status": "published",  # Ключ: статус новостей
            "include_preview": True,  # Ключ: включать ли превью
            "limit": 100  # Ключ: лимит записей
        },
        "data_source": "variable",  # Ключ: источник данных (использует тестовые данные)
        "input_format": "TXT",  # Ключ: формат входного файла
        "csv_column": "news_category",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "news_list"  # Ключ: имя JSON файла для обработки (без расширения)
    },
    "rating_list": {  # Ключ: конфигурация для скрипта RaitingList (рейтинг участников)
        "name": "RaitingList",  # Ключ: название скрипта для отображения
        "description": "Рейтинг участников по полученным наградам и кристаллам",  # Ключ: описание назначения скрипта
        "domain": "rating.example.com",  # Ключ: домен для API запросов
        "params": {  # Ключ: параметры API запросов
            "api_endpoint": "/api/rating/participants",  # Ключ: конечная точка API
            "sort_by": "total_points",  # Ключ: поле для сортировки
            "include_rewards": True,  # Ключ: включать ли награды
            "include_crystals": True,  # Ключ: включать ли кристаллы
            "limit": 500  # Ключ: лимит записей
        },
        "data_source": "file",  # Ключ: источник данных
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "participant_id",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "json_file": "rating_list"  # Ключ: имя JSON файла для обработки (без расширения)
    }
}

# Настройки для генерации JavaScript скриптов (глобальные по умолчанию)
# Используются как fallback значения, если не указаны в конфигурации конкретной функции
BASE_DOMAIN = "example.com"  # Базовый домен для API запросов (используется по умолчанию)
REQUEST_PARAMETERS = {  # Дополнительные параметры запросов (заглушка для будущего использования)
    "param1": "value1",  # Ключ: параметр 1 (пример)
    "param2": "value2"   # Ключ: параметр 2 (пример)
}

# =============================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# =============================================================================

logger = None  # Глобальный объект логгера (инициализируется в setup_logging())
program_start_time = None  # Время начала выполнения программы (записывается в main())
function_execution_times = {}  # Словарь для хранения времени выполнения функций (заполняется декоратором measure_time)
processed_actions_count = 0  # Счетчик обработанных действий (увеличивается в процессе работы программы)

# =============================================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# =============================================================================

def setup_logging():
    """
    Настройка системы логирования
    
    Создает логгер с двумя обработчиками:
    - FileHandler: записывает логи в файл
    - StreamHandler: выводит логи в консоль
    
    Returns:
        logging.Logger: Настроенный объект логгера
    """
    global logger
    
    # Создание директорий если не существуют
    # Используем exist_ok=True чтобы не вызывать ошибку если директория уже существует
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Формирование имени файла лога с временной меткой
    # Формат: game_script_generator_DEBUG_2024-01-15.log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    log_filename = f"{LOG_FILENAME_BASE}_{LOG_LEVEL}_{timestamp}.log"
    log_filepath = os.path.join(LOG_DIR, log_filename)
    
    # Настройка логгера
    logger = logging.getLogger('GameScriptGenerator')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Удаление существующих handlers для избежания дублирования
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Создание file handler для записи в файл
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Создание console handler для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Создание форматтера для логов
    # Включает время с миллисекундами, имя логгера, уровень и сообщение
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Применение форматтера к обработчикам
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Добавление обработчиков к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# =============================================================================
# ДЕКОРАТОРЫ ДЛЯ ИЗМЕРЕНИЯ ВРЕМЕНИ ВЫПОЛНЕНИЯ
# =============================================================================

def measure_time(func):
    """
    Декоратор для измерения времени выполнения функций
    
    Логирует начало и конец выполнения функции, а также время выполнения.
    Сохраняет время выполнения в глобальный словарь function_execution_times.
    
    Args:
        func: Функция для декорирования
        
    Returns:
        wrapper: Обернутая функция с измерением времени
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Формирование строки параметров для логирования
        # Ограничиваем количество аргументов для читаемости логов
        params_str = f"args={args[:2] if len(args) > 2 else args}, kwargs={list(kwargs.keys())}"
        logger.debug(LOG_MESSAGES['function_start'].format(func=func.__name__, params=params_str))
        
        try:
            # Выполнение функции
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Сохранение времени выполнения в глобальный словарь
            function_execution_times[func.__name__] = execution_time
            
            # Логирование успешного завершения
            logger.debug(LOG_MESSAGES['function_completed'].format(func=func.__name__, params=params_str, time=execution_time))
            return result
            
        except Exception as e:
            # Обработка ошибок
            execution_time = time.time() - start_time
            function_execution_times[func.__name__] = execution_time
            logger.error(LOG_MESSAGES['function_error'].format(func=func.__name__, params=params_str, error=str(e)))
            raise
            
    return wrapper

# =============================================================================
# ФУНКЦИИ ОБРАБОТКИ ДАННЫХ
# =============================================================================

@measure_time
def load_data_from_file(filepath, file_format="TXT", csv_delimiter=None, csv_encoding=None, csv_column=None):
    """
    Загрузка данных из файла
    
    Поддерживает форматы TXT и CSV. Для TXT файлов использует массив разделителей,
    для CSV файлов - указанный разделитель и столбец.
    
    Args:
        filepath (str): Путь к файлу для загрузки
        file_format (str): Формат файла ("TXT" или "CSV")
        csv_delimiter (str): Разделитель для CSV файлов (по умолчанию из констант)
        csv_encoding (str): Кодировка для CSV файлов (по умолчанию из констант)
        csv_column (str): Название столбца для CSV файлов (по умолчанию из констант)
        
    Returns:
        list: Список загруженных данных
    """
    global processed_actions_count
    
    # Использование переданных параметров или значений по умолчанию
    delimiter = csv_delimiter or CSV_DELIMITER
    encoding = csv_encoding or CSV_ENCODING
    column = csv_column or CSV_COLUMN_NAME
    
    logger.debug(LOG_MESSAGES['file_loading'].format(file_path=filepath, format=file_format))
    
    # Проверка существования файла
    if not os.path.exists(filepath):
        logger.error(LOG_MESSAGES['file_not_found'].format(file_path=filepath))
        return []
    
    data_list = []
    
    try:
        if file_format.upper() == "TXT":
            # Обработка текстового файла
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                delimiters_found = 0
                
                # Разделение по массиву разделителей
                # Заменяем все найденные разделители на единый разделитель
                for delimiter_char in TXT_DELIMITERS:
                    if delimiter_char in content:
                        delimiters_found += 1
                        content = content.replace(delimiter_char, '|SPLIT|')
                
                logger.debug(LOG_MESSAGES['txt_processing'].format(delimiters_count=delimiters_found))
                
                # Разделяем по единому разделителю и очищаем пустые элементы
                data_list = [item.strip() for item in content.split('|SPLIT|') 
                           if item.strip() and item.strip() != '|SPLIT|']
                
        elif file_format.upper() == "CSV":
            # Обработка CSV файла
            logger.debug(LOG_MESSAGES['csv_processing'].format(delimiter=delimiter, encoding=encoding, column=column))
            with open(filepath, 'r', encoding=encoding) as file:
                csv_reader = csv.DictReader(file, delimiter=delimiter)
                for row in csv_reader:
                    # Извлекаем данные из указанного столбца
                    if column in row and row[column].strip():
                        data_list.append(row[column].strip())
                        
        # Обновление счетчика обработанных действий
        processed_actions_count += len(data_list)
        logger.info(LOG_MESSAGES['file_loaded'].format(file_path=filepath, count=len(data_list)))
        
    except Exception as e:
        logger.error(LOG_MESSAGES['file_load_error'].format(file_path=filepath, error=str(e)))
        
    return data_list

@measure_time 
def get_data():
    """
    Получение данных согласно настройкам
    
    В зависимости от значения DATA_SOURCE загружает данные из файла
    или возвращает тестовые данные из переменной.
    
    Returns:
        list: Список данных для обработки
    """
    if DATA_SOURCE == "file":
        # Загрузка данных из файла
        file_extension = FILE_EXTENSIONS.get(INPUT_FORMAT, INPUT_FILE_EXTENSION)
        filepath = os.path.join(INPUT_DIR, INPUT_FILENAME + file_extension)
        return load_data_from_file(filepath, INPUT_FORMAT)
    elif DATA_SOURCE == "external_file":
        # Загрузка данных из внешнего файла (для LeadersForAdmin)
        config = FUNCTION_CONFIGS["leaders_for_admin"]
        file_extension = FILE_EXTENSIONS.get(config["input_format"], ".csv")
        filepath = os.path.join(INPUT_DIR, config["input_file"] + file_extension)
        return load_data_from_file(
            filepath, 
            config["input_format"],
            config["csv_delimiter"],
            config["csv_encoding"],
            config["csv_column"]
        )
    else:
        # Использование тестовых данных
        logger.info(LOG_MESSAGES['using_test_data'].format(count=len(TEST_DATA_LIST)))
        return TEST_DATA_LIST.copy()

@measure_time
def save_script_to_file(script_content, script_name, config_key=None):
    """
    Сохранение сгенерированного скрипта в файл TXT
    
    Создает файл с именем на основе названия скрипта и временной метки
    в директории OUTPUT.
    
    Args:
        script_content (str): Содержимое скрипта для сохранения
        script_name (str): Название скрипта для формирования имени файла
        config_key (str, optional): Ключ конфигурации для дополнительной информации
        
    Returns:
        str: Путь к сохраненному файлу или None в случае ошибки
    """
    try:
        # Создание временной метки
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Формирование имени файла
        # Убираем специальные символы и заменяем пробелы на подчеркивания
        safe_name = script_name.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        
        # Добавляем информацию о варианте если есть
        if config_key == "leaders_for_admin":
            config = FUNCTION_CONFIGS[config_key]
            selected_variant = config.get("selected_variant", "sigma")
            filename = f"{safe_name}_{selected_variant.upper()}_{timestamp}.txt"
        else:
            filename = f"{safe_name}_{timestamp}.txt"
        
        # Полный путь к файлу
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Создание директории если не существует
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Сохранение скрипта в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(LOG_MESSAGES['script_saved'].format(file_path=filepath))
        return filepath
        
    except Exception as e:
        logger.error(LOG_MESSAGES['script_save_error'].format(error=str(e)))
        return None

@measure_time
def copy_to_clipboard(text):
    """
    Копирование текста в буфер обмена
    
    Использует библиотеку pyperclip для копирования текста в системный буфер обмена.
    
    Args:
        text (str): Текст для копирования в буфер обмена
        
    Returns:
        bool: True если копирование успешно, False в случае ошибки
    """
    try:
        pyperclip.copy(text)
        logger.debug(LOG_MESSAGES['clipboard_copied'])
        return True
    except Exception as e:
        logger.error(LOG_MESSAGES['clipboard_error'].format(error=str(e)))
        return False

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ JSON И EXCEL
# =============================================================================

def parse_float_safe(val, context=None):
    """Безопасное преобразование в float с обработкой европейского формата"""
    if val is None or val == "":
        return None
    try:
        # Обработка европейского формата чисел (запятая вместо точки)
        if isinstance(val, str):
            # Удаляем пробелы и заменяем запятую на точку
            val = val.replace(' ', '').replace(',', '.')
            # Удаляем неразрывные пробелы и другие специальные символы
            val = val.replace('\u2009', '').replace('\u00a0', '')
        return float(val)
    except (ValueError, TypeError) as ex:
        if context:
            logger.warning(f"Ошибка преобразования '{val}' в float: {ex} | Context: {context}")
        return None

def flatten_leader_data(leader_data):
    """Преобразование данных лидера в плоскую структуру"""
    flattened = {}
    
    # Основные поля из структуры LeadersForAdmin
    flattened['employeeNumber'] = leader_data.get('employeeNumber', '')
    flattened['lastName'] = leader_data.get('lastName', '')
    flattened['firstName'] = leader_data.get('firstName', '')
    flattened['indicatorValue'] = leader_data.get('indicatorValue', '')
    flattened['successValue'] = leader_data.get('successValue', '')
    flattened['terDivisionName'] = leader_data.get('terDivisionName', '')
    flattened['employeeStatus'] = leader_data.get('employeeStatus', '')
    flattened['businessBlock'] = leader_data.get('businessBlock', '')
    
    # Создаем полное имя
    flattened['fullName'] = f"{leader_data.get('lastName', '')} {leader_data.get('firstName', '')}".strip()
    
    # Парсим числовые значения
    flattened['indicatorValue_parsed'] = parse_float_safe(leader_data.get('indicatorValue', 0), f"indicatorValue for {flattened['fullName']}")
    flattened['successValue_parsed'] = parse_float_safe(leader_data.get('successValue', 0), f"successValue for {flattened['fullName']}")
    
    return flattened

def apply_excel_styling(workbook):
    """Применение стилей к Excel файлу"""
    for sheet_name in workbook.sheetnames:
        worksheet = workbook[sheet_name]
        
        # Стили для заголовков
        header_fill = PatternFill(start_color=EXCEL_COLORS["header"], end_color=EXCEL_COLORS["header"], fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Стили для подзаголовков
        subheader_fill = PatternFill(start_color=EXCEL_COLORS["subheader"], end_color=EXCEL_COLORS["subheader"], fill_type="solid")
        subheader_font = Font(bold=True)
        
        # Применение стилей к заголовкам
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
        
        # Автоматическая ширина столбцов
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

def create_summary_sheet(workbook, data_df):
    """Создание листа с сводной информацией"""
    if 'DATA' not in workbook.sheetnames:
        return
    
    # Создаем лист SUMMARY
    if 'SUMMARY' in workbook.sheetnames:
        workbook.remove(workbook['SUMMARY'])
    summary_sheet = workbook.create_sheet('SUMMARY')
    
    # Основная статистика
    summary_data = [
        ['Параметр', 'Значение'],
        ['Общее количество участников', len(data_df)],
        ['Участники с номером сотрудника', len(data_df[data_df['employeeNumber'].notna() & (data_df['employeeNumber'] != '')])],
        ['Участники со статусом CONTESTANT', len(data_df[data_df['employeeStatus'] == 'CONTESTANT'])],
        ['Среднее значение показателя', round(data_df['indicatorValue_parsed'].mean(), 2) if 'indicatorValue_parsed' in data_df.columns else 'N/A'],
        ['Максимальное значение показателя', data_df['indicatorValue_parsed'].max() if 'indicatorValue_parsed' in data_df.columns else 'N/A'],
        ['Минимальное значение показателя', data_df['indicatorValue_parsed'].min() if 'indicatorValue_parsed' in data_df.columns else 'N/A'],
    ]
    
    # Добавляем данные в лист
    for row_idx, row_data in enumerate(summary_data, 1):
        for col_idx, value in enumerate(row_data, 1):
            summary_sheet.cell(row=row_idx, column=col_idx, value=value)
    
    # Применяем стили
    header_fill = PatternFill(start_color=EXCEL_COLORS["header"], end_color=EXCEL_COLORS["header"], fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    for cell in summary_sheet[1]:
        cell.fill = header_fill
        cell.font = header_font

def create_statistics_sheet(workbook, data_df):
    """Создание листа со статистикой"""
    if 'DATA' not in workbook.sheetnames:
        return
    
    # Создаем лист STATISTICS
    if 'STATISTICS' in workbook.sheetnames:
        workbook.remove(workbook['STATISTICS'])
    stats_sheet = workbook.create_sheet('STATISTICS')
    
    # Статистика по департаментам
    if 'terDivisionName' in data_df.columns:
        dept_stats = data_df['terDivisionName'].value_counts().reset_index()
        dept_stats.columns = ['Территориальное подразделение', 'Количество участников']
        
        # Добавляем заголовок
        stats_sheet.cell(row=1, column=1, value='Статистика по территориальным подразделениям')
        stats_sheet.cell(row=1, column=1).font = Font(bold=True, size=14)
        
        # Добавляем данные
        for row_idx, (_, row_data) in enumerate(dept_stats.iterrows(), 3):
            stats_sheet.cell(row=row_idx, column=1, value=row_data['Территориальное подразделение'])
            stats_sheet.cell(row=row_idx, column=2, value=row_data['Количество участников'])
    
    # Статистика по бизнес-блокам
    if 'businessBlock' in data_df.columns:
        block_stats = data_df['businessBlock'].value_counts().reset_index()
        block_stats.columns = ['Бизнес-блок', 'Количество участников']
        
        # Добавляем заголовок
        stats_sheet.cell(row=1, column=4, value='Статистика по бизнес-блокам')
        stats_sheet.cell(row=1, column=4).font = Font(bold=True, size=14)
        
        # Добавляем данные
        for row_idx, (_, row_data) in enumerate(block_stats.iterrows(), 3):
            stats_sheet.cell(row=row_idx, column=4, value=row_data['Бизнес-блок'])
            stats_sheet.cell(row=row_idx, column=5, value=row_data['Количество участников'])
    
    # Применяем стили
    header_fill = PatternFill(start_color=EXCEL_COLORS["subheader"], end_color=EXCEL_COLORS["subheader"], fill_type="solid")
    header_font = Font(bold=True)
    
    for cell in stats_sheet[3]:
        cell.fill = header_fill
        cell.font = header_font

# =============================================================================
# ФУНКЦИИ ГЕНЕРАЦИИ СКРИПТОВ
# =============================================================================

@measure_time
def generate_script_universal(config_key, data_list=None):
    """
    Универсальная функция для генерации скриптов
    
    Генерирует JavaScript скрипт на основе конфигурации и данных.
    Выводит скрипт в консоль и копирует в буфер обмена.
    
    Args:
        config_key (str): Ключ конфигурации из FUNCTION_CONFIGS
        data_list (list, optional): Список данных для обработки
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    config = FUNCTION_CONFIGS[config_key]
    
    # Получение данных согласно конфигурации
    if data_list is None:
        if config["data_source"] == "file":
            # Загрузка данных из файла
            file_extension = FILE_EXTENSIONS.get(config["input_format"], ".txt")
            filename = f"{config_key}_data{file_extension}"
            filepath = os.path.join(INPUT_DIR, filename)
            data_list = load_data_from_file(
                filepath, 
                config["input_format"],
                config["csv_delimiter"],
                config["csv_encoding"],
                config["csv_column"]
            )
        else:
            # Использование тестовых данных
            data_list = TEST_DATA_LIST.copy()
    
    # Логирование процесса генерации
    if config_key == "leaders_for_admin":
        selected_variant = config.get("selected_variant", "sigma")
        variant_config = config["variants"][selected_variant]
        logger.debug(LOG_MESSAGES['script_generation'].format(script_name=f"{config['name']} ({selected_variant.upper()})"))
        logger.debug(LOG_MESSAGES['config_loaded'].format(script_name=f"{config['name']} ({selected_variant.upper()})"))
        logger.debug(f"Выбранный вариант: {selected_variant.upper()}")
    else:
        logger.debug(LOG_MESSAGES['script_generation'].format(script_name=config['name']))
        logger.debug(LOG_MESSAGES['config_loaded'].format(script_name=config['name']))
    
    logger.debug(LOG_MESSAGES['data_source_selected'].format(
        source=config['data_source'], 
        format=config['input_format']
    ))
    
    # Генерация JavaScript скрипта на основе типа
    if config_key == "leaders_for_admin":
        # Получение выбранного варианта
        selected_variant = config.get("selected_variant", "sigma")
        variant_config = config["variants"][selected_variant]
        
        # Специальная генерация для LeadersForAdmin
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        script = f"""// ==UserScript==
// Скрипт для DevTools. Выгрузка лидеров для всех Tournament ID (одна страница на турнир)
// Вариант: {selected_variant.upper()}
// Сгенерировано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Количество турниров: {len(data_list)}
(async () => {{
  // === Удаление photoData рекурсивно ===
  function removePhotoData(obj) {{
    if (Array.isArray(obj)) {{
      obj.forEach(removePhotoData);
    }} else if (obj && typeof obj === 'object') {{
      Object.keys(obj).forEach(key => {{
        if (key === 'photoData') {{
          delete obj[key];
        }} else {{
          removePhotoData(obj[key]);
        }}
      }});
    }}
  }}

  // === Генерация timestamp ===
  function getTimestamp() {{
    const d = new Date();
    const pad = n => n.toString().padStart(2, '0');
    return d.getFullYear().toString()
      + pad(d.getMonth() + 1)
      + pad(d.getDate())
      + '-' + pad(d.getHours())
      + pad(d.getMinutes())
      + pad(d.getSeconds());
  }}

  const ids = {json.dumps(data_list, indent=2)};
  const service = 'leadersForAdmin';
  const BASE_URL = '{variant_config['domain']}{variant_config['params']['api_path']}';
  const results = {{}};
  let processed = 0, skipped = 0, errors = 0;
  console.log('▶️ Всего к обработке:', ids.length, 'код(ов)');
  console.log('🎯 Вариант:', '{selected_variant.upper()}');

  for (let i = 0; i < ids.length; ++i) {{
    const tid = ids[i];
    const url = BASE_URL + tid + '/' + service + '?pageNum=1';
    console.log(`⏳ [${{i+1}}/${{ids.length}}] Обрабатываем код: ${{tid}}`);
    let resp, data;
    try {{
      resp = await fetch(url, {{
        headers: {{ 'Accept': 'application/json', 'Cookie': document.cookie }}, credentials: 'include'
      }});
      if (!resp.ok) {{
        console.warn(`❌ [${{i+1}}/${{ids.length}}] Код ${{tid}}: HTTP статус ${{resp.status}}`);
        errors++;
        continue;
      }}
      data = await resp.json();
      // Число участников
      let leadersCount = 0;
      try {{
        const leadersArr = data?.body?.tournament?.leaders || data?.body?.badge?.leaders;
        if (Array.isArray(leadersArr)) {{
          leadersCount = leadersArr.length;
        }}
      }} catch {{}}
      if (leadersCount === 0) {{
        console.log(`ℹ️ [${{i+1}}/${{ids.length}}] Код ${{tid}} пропущен: участников = 0`);
        skipped++;
        continue;
      }}
      console.log(`✅ [${{i+1}}/${{ids.length}}] Код ${{tid}}: успешно, участников: ${{leadersCount}}`);
      results[tid] = [data];
      processed++;
      await new Promise(r => setTimeout(r, 5));
    }} catch (e) {{
      console.error(`❌ [${{i+1}}/${{ids.length}}] Код ${{tid}}: Ошибка запроса:`, e);
      errors++;
    }}
  }}

  console.log('🧹 Удаляем все поля photoData');
  removePhotoData(results);

  console.log('💾 Сохраняем файл ...');
  const ts = getTimestamp();
  const blob = new Blob([JSON.stringify(results, null, 2)], {{type: 'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = service + '_{selected_variant.upper()}_' + ts + '.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  console.log(`🏁 Обработка завершена. Всего: ${{ids.length}}. Успешно: ${{processed}}. Пропущено: ${{skipped}}. Ошибок: ${{errors}}. Файл скачан.`);
}})();"""
    else:
        # Заглушка для остальных типов
        script = f"""
// JavaScript скрипт для {config['name']}
// Описание: {config['description']}
// Домен: {config['domain']}
// Параметры: {config['params']}
// Данные: {len(data_list)} элементов

console.log('Скрипт {config['name']} запущен');
// Здесь будет реальная логика генерации скрипта
console.log('Обработка данных:', {data_list[:3] if len(data_list) > 3 else data_list});
"""
    
    # Вывод скрипта в консоль
    print(f"=== GENERATED SCRIPT: {config['name']} ===")
    print(script)
    
    # Сохранение скрипта в файл
    saved_filepath = save_script_to_file(script, config['name'], config_key)
    
    # Копирование в буфер обмена
    copy_to_clipboard(script)
    
    logger.info(LOG_MESSAGES['script_generated'].format(script_name=config['name'], count=len(data_list)))
    
    return script

# =============================================================================
# ФУНКЦИИ ГЕНЕРАЦИИ JAVASCRIPT СКРИПТОВ (ЗАГЛУШКИ)
# =============================================================================

def generate_leaders_for_admin_script(data_list=None):
    """
    Генерация скрипта для получения информации по участникам турнира
    
    Args:
        data_list (list, optional): Список ID участников
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("leaders_for_admin", data_list)

def generate_reward_script(data_list=None):
    """
    Генерация скрипта для получения информации о наградах
    
    Args:
        data_list (list, optional): Список ID сотрудников
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("reward", data_list)

def generate_profile_script(data_list=None):
    """
    Генерация скрипта для получения профилей сотрудников
    
    Args:
        data_list (list, optional): Список ID профилей
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("profile", data_list)

def generate_news_details_script(data_list=None):
    """
    Генерация скрипта для получения детальной карточки новости
    
    Args:
        data_list (list, optional): Список ID новостей
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("news_details", data_list)

def generate_address_book_tn_script(data_list=None):
    """
    Генерация скрипта для получения карточки сотрудника по табельному номеру
    
    Args:
        data_list (list, optional): Список табельных номеров
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("address_book_tn", data_list)

def generate_address_book_dev_script(data_list=None):
    """
    Генерация скрипта для получения карточки подразделения
    
    Args:
        data_list (list, optional): Список ID подразделений
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("address_book_dev", data_list)

def generate_orders_script(data_list=None):
    """
    Генерация скрипта для получения списка сотрудников с преференциями
    
    Args:
        data_list (list, optional): Список ID сотрудников
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("orders", data_list)

def generate_news_list_script(data_list=None):
    """
    Генерация скрипта для получения списка новостей
    
    Args:
        data_list (list, optional): Список категорий новостей
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("news_list", data_list)

def generate_rating_list_script(data_list=None):
    """
    Генерация скрипта для получения рейтинга участников
    
    Args:
        data_list (list, optional): Список ID участников
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    return generate_script_universal("rating_list", data_list)

# =============================================================================
# ФУНКЦИИ ОБРАБОТКИ JSON В EXCEL
# =============================================================================

@measure_time
def convert_json_to_excel(input_json_path, output_excel_path):
    """
    Конвертация JSON файла в Excel
    
    Args:
        input_json_path (str): Путь к входному JSON файлу
        output_excel_path (str): Путь к выходному Excel файлу
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        logger.info(LOG_MESSAGES['json_conversion_start'].format(input=input_json_path, output=output_excel_path))
        
        # Проверка существования входного файла
        if not os.path.exists(input_json_path):
            logger.error(LOG_MESSAGES['json_file_not_found'].format(file_path=input_json_path))
            return False
        
        # Создание директории для выходного файла если не существует
        output_dir = os.path.dirname(output_excel_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(LOG_MESSAGES['json_directory_created'].format(directory=output_dir))
        
        # Загрузка JSON данных
        logger.info(LOG_MESSAGES['json_data_loading'])
        with open(input_json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Обработка данных
        logger.info(LOG_MESSAGES['json_data_processing'])
        leaders_data = []
        
        if isinstance(json_data, dict):
            # Ищем данные в структуре LeadersForAdmin
            for key, value in json_data.items():
                if isinstance(value, list) and len(value) > 0:
                    # Проверяем, содержит ли первый элемент данные о турнире
                    first_item = value[0]
                    if isinstance(first_item, dict) and 'body' in first_item:
                        body = first_item['body']
                        if 'tournament' in body:
                            tournament = body['tournament']
                            if 'leaders' in tournament:
                                leaders_data = tournament['leaders']
                                logger.info(LOG_MESSAGES['json_leaders_found'].format(key=key, count=len(leaders_data)))
                                break
        elif isinstance(json_data, list):
            # Прямой список лидеров
            leaders_data = json_data
            logger.info(LOG_MESSAGES['json_direct_leaders'].format(count=len(leaders_data)))
        else:
            logger.error(LOG_MESSAGES['json_invalid_format'])
            return False
        
        if not leaders_data:
            logger.error(LOG_MESSAGES['json_no_leaders'])
            return False
        
        # Преобразование данных в плоскую структуру
        flattened_data = []
        for leader in leaders_data:
            flattened_leader = flatten_leader_data(leader)
            flattened_data.append(flattened_leader)
        
        # Создание DataFrame
        df = pd.DataFrame(flattened_data)
        
        if df.empty:
            logger.warning("Нет данных для обработки")
            return False
        
        logger.info(LOG_MESSAGES['json_records_processed'].format(count=len(df)))
        
        # Создание Excel файла
        logger.info(LOG_MESSAGES['json_excel_creation'])
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            # Основной лист с данными
            df.to_excel(writer, sheet_name='DATA', index=False)
            
            # Получаем workbook для применения стилей
            workbook = writer.book
            
            # Применяем стили
            if JSON_PROCESSING_CONFIG["apply_styling"]:
                apply_excel_styling(workbook)
            
            # Создаем дополнительные листы
            if JSON_PROCESSING_CONFIG["create_summary"]:
                create_summary_sheet(workbook, df)
            if JSON_PROCESSING_CONFIG["create_statistics"]:
                create_statistics_sheet(workbook, df)
        
        logger.info(LOG_MESSAGES['json_excel_success'].format(file_path=output_excel_path))
        return True
        
    except Exception as e:
        logger.error(LOG_MESSAGES['json_conversion_error'].format(error=str(e)))
        return False

@measure_time
def convert_specific_json_file(file_name_without_extension):
    """
    Конвертирует конкретный JSON файл в Excel
    
    Args:
        file_name_without_extension (str): Имя файла без расширения
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        # Формируем пути к файлам
        input_json_path = os.path.join(JSON_PROCESSING_CONFIG["input_directory"], f"{file_name_without_extension}.json")
        output_excel_path = os.path.join(JSON_PROCESSING_CONFIG["output_directory"], f"{file_name_without_extension}.xlsx")
        
        logger.info(LOG_MESSAGES['json_file_processing'].format(file_name=file_name_without_extension))
        
        # Конвертируем файл
        if convert_json_to_excel(input_json_path, output_excel_path):
            logger.info(LOG_MESSAGES['json_excel_success'].format(file_path=output_excel_path))
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(LOG_MESSAGES['json_conversion_error'].format(error=str(e)))
        return False

# =============================================================================
# ФУНКЦИИ ВЫВОДА СТАТИСТИКИ
# =============================================================================

def print_summary():
    """
    Вывод итоговой статистики работы программы
    
    Формирует и выводит в консоль и лог подробную статистику выполнения:
    - Общее время работы
    - Количество обработанных действий
    - Количество выполненных функций
    - Время выполнения каждой функции
    """
    total_time = time.time() - program_start_time
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    # Формирование строк статистики
    summary_lines = [
        "=" * 70,
        f"SUMMARY - {LOG_MESSAGES['summary_stats']}",
        "=" * 70,
        LOG_MESSAGES['total_execution'].format(time=total_time),
        LOG_MESSAGES['processed_actions'].format(count=processed_actions_count),
        LOG_MESSAGES['executed_functions'].format(count=len(function_execution_times)),
        "",
        LOG_MESSAGES['execution_times'],
    ]
    
    # Добавление времени выполнения каждой функции
    for func_name, exec_time in function_execution_times.items():
        summary_lines.append(f"  - {func_name}: {exec_time:.4f} сек")
    
    # Завершающие строки
    summary_lines.extend([
        "",
        LOG_MESSAGES['program_completed'].format(time=current_time),
        "=" * 70
    ])
    
    # Объединение в одну строку
    summary_text = "\n".join(summary_lines)
    
    # Вывод в консоль и лог
    print(summary_text)
    logger.info(LOG_MESSAGES['summary_title'])
    logger.info(LOG_MESSAGES['total_time'].format(time=total_time) + f", {LOG_MESSAGES['actions_processed'].format(count=processed_actions_count)}, {LOG_MESSAGES['functions_executed'].format(count=len(function_execution_times))}")
    
    # Логирование времени каждой функции
    for func_name, exec_time in function_execution_times.items():
        logger.info(LOG_MESSAGES['function_time'].format(func=func_name, time=exec_time))

# =============================================================================
# ОСНОВНАЯ ПРОГРАММА
# =============================================================================

def main():
    """
    Основная функция программы
    
    Координирует выполнение всех этапов:
    1. Инициализация логирования
    2. Получение данных
    3. Генерация скриптов согласно настройкам
    4. Вывод статистики
    """
    global program_start_time
    
    # Инициализация времени начала программы
    program_start_time = time.time()
    
    # Настройка логирования
    setup_logging()
    
    # Стартовое сообщение с разделителями для читаемости
    start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    logger.info("=" * 70)
    logger.info(LOG_MESSAGES['program_start'].format(time=start_time_str))
    logger.info(LOG_MESSAGES['processing_start_time'].format(time=start_time_str))
    logger.info(LOG_MESSAGES['logging_level'].format(level=LOG_LEVEL))
    logger.info("=" * 70)
    
    try:
        # Выполнение операций согласно настройкам ACTIVE_OPERATIONS
        logger.info(f"Активные операции: {', '.join(ACTIVE_OPERATIONS)}")
        
        # Операция: Генерация скриптов
        if "generate_scripts" in ACTIVE_OPERATIONS:
            logger.info("=== ВЫПОЛНЕНИЕ ОПЕРАЦИИ: ГЕНЕРАЦИЯ СКРИПТОВ ===")
            
            # Получение данных (для генерации скриптов)
            data_list = get_data()
            logger.info(LOG_MESSAGES['data_received'].format(count=len(data_list)))
            
            # Генерация скриптов согласно настройкам ACTIVE_SCRIPTS
            if ACTIVE_SCRIPTS:
                logger.info(f"Активные скрипты для генерации: {', '.join(ACTIVE_SCRIPTS)}")
                for script_name in ACTIVE_SCRIPTS:
                    if script_name == "leaders_for_admin":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_leaders_for_admin_script(data_list)
                    elif script_name == "reward":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_reward_script(data_list)
                    elif script_name == "profile":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_profile_script(data_list)
                    elif script_name == "news_details":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_news_details_script(data_list)
                    elif script_name == "address_book_tn":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_address_book_tn_script(data_list)
                    elif script_name == "address_book_dev":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_address_book_dev_script(data_list)
                    elif script_name == "orders":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_orders_script(data_list)
                    elif script_name == "news_list":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_news_list_script(data_list)
                    elif script_name == "rating_list":
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_rating_list_script(data_list)
                    elif script_name in FUNCTION_CONFIGS:
                        logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                        generate_script_universal(script_name, data_list)
                    else:
                        logger.error(f"Неизвестный скрипт: {script_name}")
            else:
                logger.info("Нет активных скриптов для генерации. Настройте ACTIVE_SCRIPTS.")
        else:
            logger.info("Генерация скриптов отключена (не включена в ACTIVE_OPERATIONS)")
        
        # Операция: Обработка JSON файлов в Excel
        if "process_json" in ACTIVE_OPERATIONS:
            logger.info("=== ВЫПОЛНЕНИЕ ОПЕРАЦИИ: ОБРАБОТКА JSON В EXCEL ===")
            
            # Собираем JSON файлы из конфигураций активных скриптов
            json_files_to_process = []
            for script_name in ACTIVE_SCRIPTS:
                if script_name in FUNCTION_CONFIGS and "json_file" in FUNCTION_CONFIGS[script_name]:
                    json_file = FUNCTION_CONFIGS[script_name]["json_file"]
                    if json_file not in json_files_to_process:
                        json_files_to_process.append(json_file)
            
            if json_files_to_process:
                logger.info(f"JSON файлы для обработки: {', '.join(json_files_to_process)}")
                processed_count = 0
                
                for file_name in json_files_to_process:
                    if convert_specific_json_file(file_name):
                        processed_count += 1
                
                if processed_count > 0:
                    logger.info(LOG_MESSAGES['json_files_processed'].format(count=processed_count))
                else:
                    logger.info(LOG_MESSAGES['json_no_files_found'])
            else:
                logger.info(LOG_MESSAGES['json_no_files_found'])
        else:
            logger.info("Обработка JSON файлов отключена (не включена в ACTIVE_OPERATIONS)")
            
        # Альтернативный способ - ручной вызов конкретных функций
        # Раскомментируйте нужные строки для тестирования
        # generate_leaders_for_admin_script()  # CSV с разделителем ;
        # generate_profile_script()  # TXT с различными разделителями
        # generate_news_list_script()  # использует переменную согласно конфигурации
        
        logger.info(LOG_MESSAGES['program_success'])
        
    except Exception as e:
        # Обработка критических ошибок
        logger.error(LOG_MESSAGES['critical_error'].format(error=str(e)))
        
    finally:
        # Вывод итоговой статистики (всегда выполняется)
        print_summary()
        
        # Финальное сообщение
        end_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        total_time = time.time() - program_start_time
        logger.info("=" * 70)
        logger.info(LOG_MESSAGES['program_end'].format(time=end_time_str))
        logger.info(LOG_MESSAGES['total_execution_time'].format(time=total_time))
        logger.info("=" * 70)

# Точка входа в программу
if __name__ == "__main__":
    main() 