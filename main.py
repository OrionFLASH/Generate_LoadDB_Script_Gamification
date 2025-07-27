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
# ГЛОБАЛЬНЫЕ НАСТРОЙКИ ПРОГРАММЫ
# =============================================================================

# Базовая папка проекта
BASE_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/WORK"

# Настройки логирования
LOG_LEVEL = "DEBUG"  # Уровень детализации логов: "INFO" - основная информация, "DEBUG" - подробная отладочная информация
LOG_FILENAME_BASE = "LOG"  # Базовое имя файла лога (к нему добавляется дата и время)

# Имена подпапок (глобально)
SUBDIRECTORIES = {
    "LOGS": "LOGS",           # Папка для логов
    "INPUT": "INPUT",         # Папка для входных файлов
    "OUTPUT": "OUTPUT",       # Папка для выходных файлов
    "SCRIPT": "SCRIPT",       # Папка для сгенерированных скриптов
    "CONFIG": "CONFIG",       # Папка для конфигурационных файлов
    "JSON": "JSON"            # Папка для JSON файлов
}

# Расширения файлов для различных форматов (глобально)
FILE_EXTENSIONS = {
    "CSV": ".csv",    # Ключ: формат CSV файлов
    "TXT": ".txt",    # Ключ: формат текстовых файлов  
    "JSON": ".json",  # Ключ: формат JSON файлов
    "EXCEL": ".xlsx"  # Ключ: формат Excel файлов
}

# Выбор активных скриптов для генерации (глобально)
ACTIVE_SCRIPTS = [
    "leaders_for_admin",  # Скрипт для получения информации по участникам турнира (LeadersForAdmin)
    "reward",  # Скрипт для выгрузки профилей участников по кодам наград (Reward)
    # "reward",             # Скрипт для получения информации о наградах сотрудников
    # "profile",            # Скрипт для получения профилей сотрудников
    # "news_details",       # Скрипт для получения детальной карточки новости
    # "address_book_tn",    # Скрипт для получения карточки сотрудника по табельному номеру
    # "address_book_dev",   # Скрипт для получения карточки подразделения
    # "orders",             # Скрипт для получения списка сотрудников с преференциями
    # "news_list",          # Скрипт для получения списка новостей
    # "rating_list"         # Скрипт для получения рейтинга участников
]



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
CSV_ENCODING = "utf-8"  # Кодировка для CSV файлов (поддерживает кириллицу и специальные символы)
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
    "json_reward_found": "Найдены данные участников в коде: {key}, количество: {count}",  # Ключ: найдены данные участников наград
    "json_direct_leaders": "Прямой список лидеров, количество: {count}",  # Ключ: прямой список лидеров
    "json_invalid_format": "Неверный формат JSON данных",  # Ключ: неверный формат JSON
    "json_no_leaders": "Не найдены данные лидеров в JSON файле",  # Ключ: нет данных лидеров
    "json_records_processed": "Обработано {count} записей",  # Ключ: количество обработанных записей
    "json_excel_creation": "Создаем Excel файл...",  # Ключ: создание Excel файла
    "json_excel_success": "Excel файл успешно создан: {file_path}",  # Ключ: Excel файл создан
    "json_conversion_error": "Ошибка при конвертации JSON: {error}",  # Ключ: ошибка конвертации JSON
    "json_file_processing": "Обработка JSON файла: {file_name}",  # Ключ: обработка конкретного JSON файла
    "json_files_processed": "Обработано JSON файлов: {count}",  # Ключ: количество обработанных JSON файлов
    "json_no_files_found": "JSON файлы для обработки не найдены",  # Ключ: JSON файлы не найдены
    
    # Сообщения для обработки данных
    "float_conversion_error": "Ошибка преобразования '{val}' в float: {ex} | Context: {context}",  # Ключ: ошибка преобразования в float
    "reward_summary_sheet_created": "Лист REWARD_SUMMARY создан успешно",  # Ключ: лист наград создан
    "variant_selected": "Выбранный вариант: {variant}",  # Ключ: выбранный вариант
    "script_generation_start": "=== ГЕНЕРАЦИЯ СКРИПТА: {script_name} ===",  # Ключ: начало генерации скрипта
    "data_loading": "Загрузка данных и конфигурации...",  # Ключ: загрузка данных
    "config_loaded_count": "Конфигурация загружена: {count} элементов",  # Ключ: конфигурация загружена с количеством
    "domain_info": "Домен: {domain}",  # Ключ: информация о домене
    "api_path_info": "API путь: {api_path}",  # Ключ: информация о пути API
    "request_params": "Параметры запросов: delay={delay}, max_retries={max_retries}, timeout={timeout}",  # Ключ: параметры запросов
    "base_url_info": "Базовый URL: {base_url}",  # Ключ: базовый URL
    "ids_generated": "Строка IDs сгенерирована: {count} элементов",  # Ключ: IDs сгенерированы
    "script_saving": "Сохранение скрипта в файл...",  # Ключ: сохранение скрипта
    "script_generated_success": "Скрипт {script_name} сгенерирован успешно (данных: {count})",  # Ключ: скрипт сгенерирован успешно
    "json_load_error": "Ошибка при загрузке JSON файла {file_path}: {error}",  # Ключ: ошибка загрузки JSON
    "excel_creation_error": "Ошибка при создании Excel файла: {error}",  # Ключ: ошибка создания Excel
    "tournaments_processed": "Обработано турниров: {tournaments}, общее количество лидеров: {leaders}",  # Ключ: турниры обработаны
    "no_data_warning": "Нет данных для обработки",  # Ключ: нет данных
    "json_leaders_conversion_error": "Ошибка при конвертации JSON лидеров в Excel: {error}",  # Ключ: ошибка конвертации лидеров
    "profile_extraction_error": "Ошибка при извлечении профилей из данных: {error}",  # Ключ: ошибка извлечения профилей
    "reward_profiles_found": "Найдено профилей для кода награды {code}: {count} (структура: {structure})",  # Ключ: найдены профили наград
    "reward_profiles_found_old": "Найдено профилей для кода награды {code}: {count} (старая структура)",  # Ключ: найдены профили наград (старая структура)
    "rewards_processed": "Обработано кодов наград: {rewards}, общее количество профилей: {profiles}",  # Ключ: награды обработаны
    "direct_profiles_list": "Прямой список профилей: {count}",  # Ключ: прямой список профилей
    "no_profiles_error": "Не найдено данных профилей",  # Ключ: нет профилей
    "json_reward_conversion_error": "Ошибка при конвертации JSON наград в Excel: {error}",  # Ключ: ошибка конвертации наград
    "excel_file_creation": "Создаем Excel файл: {filename}",  # Ключ: создание Excel файла
    "separator_line": "=" * 70,  # Ключ: разделительная линия
    "active_scripts_info": "Активные скрипты: {scripts}",  # Ключ: активные скрипты
    "stage1_title": "=== ЭТАП 1: ГЕНЕРАЦИЯ СКРИПТОВ ===",  # Ключ: заголовок этапа 1
    "script_processing": "--- ОБРАБОТКА СКРИПТА: {script_name} ---",  # Ключ: обработка скрипта
    "active_operations_info": "Активные операции для {script_name}: {operations}",  # Ключ: активные операции
    "script_generation_info": "Генерация скрипта: {script_name}",  # Ключ: генерация скрипта
    "script_generation_skipped": "Пропуск генерации скрипта для {script_name} (режим: {operations})",  # Ключ: пропуск генерации
    "unknown_script_error": "Неизвестный скрипт: {script_name}",  # Ключ: неизвестный скрипт
    "stage2_title": "=== ЭТАП 2: ОБРАБОТКА JSON ФАЙЛОВ ===",  # Ключ: заголовок этапа 2
    "json_file_processing_info": "Обработка JSON файла: {json_file}",  # Ключ: обработка JSON файла
    "no_json_file_warning": "Для скрипта {script_name} не указан json_file",  # Ключ: нет JSON файла
    "json_processing_skipped": "Пропуск обработки JSON для {script_name} (режим: {operations})",  # Ключ: пропуск обработки JSON
    "no_active_scripts": "Нет активных скриптов для обработки. Настройте ACTIVE_SCRIPTS.",  # Ключ: нет активных скриптов
    "summary_output": "Итоговая статистика работы программы:\n{summary}"  # Ключ: итоговая статистика
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
        "active_operations": "both",  # Ключ: активные операции ("scripts_only", "json_only", "both")
        "excel_freeze_row": 1,  # Ключ: номер строки для закрепления в Excel (1 = заголовок)
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
        "json_file": "leadersForAdmin_SIGMA_20250726-192035",  # Ключ: имя JSON файла для обработки (без расширения)
        "excel_file": "LeadersForAdmin",  # Ключ: имя Excel файла для создания (без расширения)
        "excel_freeze_cell": "B2"  # Ключ: ячейка для закрепления в Excel (B2 = первая строка и первая колонка)
    },
    "reward": {  # Ключ: конфигурация для скрипта REWARD (выгрузка профилей участников по кодам наград)
        "name": "Reward",  # Ключ: название скрипта для отображения
        "description": "Выгрузка профилей участников по кодам наград",  # Ключ: описание назначения скрипта
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
        "variants": {  # Ключ: варианты конфигурации (SIGMA/ALPHA)
            "sigma": {  # Ключ: вариант SIGMA (продакшн окружение)
                "name": "Reward (SIGMA)",  # Ключ: название варианта
                "description": "Выгрузка профилей участников по кодам наград - SIGMA",  # Ключ: описание варианта
                "domain": "https://salesheroes.sberbank.ru",  # Ключ: домен для SIGMA
                "params": {
                    "api_path": "/bo/rmkib.gamification/api/v1/badges/",  # Ключ: путь к API
                    "service": "profiles"  # Ключ: название сервиса
                },
                "timeout": 30000,  # Ключ: таймаут запроса в миллисекундах
                "retry_count": 3,  # Ключ: количество попыток при ошибке
                "delay_between_requests": 5  # Ключ: задержка между запросами в миллисекундах
            },
            "alpha": {  # Ключ: вариант ALPHA (тестовое окружение)
                "name": "Reward (ALPHA)",  # Ключ: название варианта
                "description": "Выгрузка профилей участников по кодам наград - ALPHA",  # Ключ: описание варианта
                "domain": "https://efs-our-business-prom.omega.sbrf.ru",  # Ключ: домен для ALPHA
                "params": {
                    "api_path": "/bo/rmkib.gamification/api/v1/badges/",  # Ключ: путь к API
                    "service": "profiles"  # Ключ: название сервиса
                },
                "timeout": 30000,  # Ключ: таймаут запроса в миллисекундах
                "retry_count": 3,  # Ключ: количество попыток при ошибке
                "delay_between_requests": 10  # Ключ: задержка между запросами в миллисекундах
            }
        },
        "selected_variant": "sigma",  # Ключ: выбранный вариант (sigma/alpha)
        "data_source": "external_file",  # Ключ: источник данных (file/variable/external_file)
        "input_format": "CSV",  # Ключ: формат входного файла
        "csv_column": "REWARD_CODE",  # Ключ: название столбца для извлечения данных
        "csv_delimiter": ";",  # Ключ: разделитель в CSV файле
        "csv_encoding": "utf-8",  # Ключ: кодировка CSV файла
        "input_file": "REWARD (PROM) 2025-07-24 v1",  # Ключ: имя входного файла (без расширения)
        "processing_options": {  # Ключ: опции обработки данных
            "include_photo_data": False,  # Ключ: включать ли данные фотографий
            "include_division_ratings": True,  # Ключ: включать ли рейтинги подразделений
            "include_badge_info": True,  # Ключ: включать ли информацию о наградах
            "max_profiles_per_request": 1000,  # Ключ: максимальное количество профилей на запрос
            "skip_empty_profiles": True  # Ключ: пропускать ли пустые профили
        }
    },
    "profile": {  # Ключ: конфигурация для скрипта PROFILE (профили сотрудников)
        "name": "PROFILE",  # Ключ: название скрипта для отображения
        "description": "Профили сотрудников в героях продаж",  # Ключ: описание назначения скрипта
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
        "active_operations": "scripts_only",  # Ключ: активные операции ("scripts_only", "json_only", "both")
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
    log_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["LOGS"])
    input_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["INPUT"])
    output_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["OUTPUT"])
    script_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["SCRIPT"])
    config_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["CONFIG"])
    json_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["JSON"])
    
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Формирование имени файла лога с временной меткой
    # Формат: LOG_DEBUG_2024-01-15.log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    log_filename = f"{LOG_FILENAME_BASE}_{LOG_LEVEL}_{timestamp}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
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
        # Исключаем вывод содержимого скриптов
        if func.__name__ in ['generate_leaders_for_admin_script', 'generate_reward_script']:
            params_str = f"args=(), kwargs={list(kwargs.keys())}"
        else:
            params_str = f"args={args[:2] if len(args) > 2 else args}, kwargs={list(kwargs.keys())}"
        logger.debug(LOG_MESSAGES['function_start'].format(func=func.__name__, params=params_str))
        
        try:
            # Выполнение функции
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Сохранение времени выполнения в глобальный словарь
            function_execution_times[func.__name__] = execution_time
            
            # Логирование успешного завершения
            # Исключаем вывод содержимого скриптов
            if func.__name__ in ['generate_leaders_for_admin_script', 'generate_reward_script']:
                logger.debug(LOG_MESSAGES['function_completed'].format(func=func.__name__, params="args=(), kwargs=[]", time=execution_time))
            else:
                logger.debug(LOG_MESSAGES['function_completed'].format(func=func.__name__, params=params_str, time=execution_time))
            return result
            
        except Exception as e:
            # Обработка ошибок
            execution_time = time.time() - start_time
            function_execution_times[func.__name__] = execution_time
            # Исключаем вывод содержимого скриптов при ошибках
            if func.__name__ in ['generate_leaders_for_admin_script', 'generate_reward_script']:
                logger.error(LOG_MESSAGES['function_error'].format(func=func.__name__, params="args=(), kwargs=[]", error=str(e)))
            else:
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
    # Эта функция теперь используется только для тестовых данных
    # Для каждого скрипта данные загружаются индивидуально в generate_script_universal
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
        if config_key in ["leaders_for_admin", "reward"]:
            config = FUNCTION_CONFIGS[config_key]
            selected_variant = config.get("selected_variant", "sigma")
            filename = f"{safe_name}_{selected_variant.upper()}_{timestamp}.txt"
        else:
            filename = f"{safe_name}_{timestamp}.txt"
        
        # Полный путь к файлу (используем папку SCRIPT)
        script_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["SCRIPT"])
        filepath = os.path.join(script_dir, filename)
        
        # Создание директории если не существует
        os.makedirs(script_dir, exist_ok=True)
        
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
            logger.warning(LOG_MESSAGES['float_conversion_error'].format(val=val, ex=ex, context=context))
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
    
    # Поля турнира (добавлены при обработке всех турниров)
    flattened['tournamentId'] = leader_data.get('tournamentId', '')
    flattened['tournamentIndicator'] = leader_data.get('tournamentIndicator', '')
    flattened['tournamentStatus'] = leader_data.get('tournamentStatus', '')
    flattened['contestants'] = leader_data.get('contestants', '')
    
    # Создаем полное имя
    flattened['fullName'] = f"{leader_data.get('lastName', '')} {leader_data.get('firstName', '')}".strip()
    
    # Парсим числовые значения
    flattened['indicatorValue_parsed'] = parse_float_safe(leader_data.get('indicatorValue', 0), f"indicatorValue for {flattened['fullName']}")
    flattened['successValue_parsed'] = parse_float_safe(leader_data.get('successValue', 0), f"successValue for {flattened['fullName']}")
    
    # Обработка вложенной структуры divisionRatings
    division_ratings = leader_data.get('divisionRatings', [])
    
    # Инициализируем колонки для каждой категории (BANK, TB, GOSB)
    categories = ['BANK', 'TB', 'GOSB']
    for category in categories:
        flattened[f'{category}_groupId'] = ''
        flattened[f'{category}_placeInRating'] = ''
        flattened[f'{category}_ratingCategoryName'] = ''
    
    # Заполняем данные из divisionRatings
    for rating in division_ratings:
        group_code = rating.get('groupCode', '')
        if group_code in categories:
            # Преобразуем groupId в целое число
            group_id_raw = rating.get('groupId', '')
            try:
                flattened[f'{group_code}_groupId'] = int(float(group_id_raw)) if group_id_raw else ''
            except (ValueError, TypeError):
                flattened[f'{group_code}_groupId'] = ''
            
            # Преобразуем placeInRating в целое число
            place_in_rating_raw = rating.get('placeInRating', '')
            try:
                flattened[f'{group_code}_placeInRating'] = int(float(place_in_rating_raw)) if place_in_rating_raw else ''
            except (ValueError, TypeError):
                flattened[f'{group_code}_placeInRating'] = ''
            
            flattened[f'{group_code}_ratingCategoryName'] = rating.get('ratingCategoryName', '')
    
    return flattened

def flatten_reward_profile_data(profile_data):
    """
    Преобразование данных профиля награды в плоскую структуру
    
    Args:
        profile_data (dict): Данные профиля из API наград
        
    Returns:
        dict: Плоская структура данных профиля
    """
    flattened = {}
    
    # Основные поля профиля
    flattened['rewardCode'] = profile_data.get('rewardCode', '')
    flattened['badgeName'] = profile_data.get('badgeName', '')
    flattened['badgeDescription'] = profile_data.get('badgeDescription', '')
    flattened['badgeType'] = profile_data.get('badgeType', '')
    flattened['badgeCategory'] = profile_data.get('badgeCategory', '')
    
    # Поля профиля сотрудника
    flattened['employeeNumber'] = profile_data.get('employeeNumber', '')
    flattened['lastName'] = profile_data.get('lastName', '')
    flattened['firstName'] = profile_data.get('firstName', '')
    flattened['middleName'] = profile_data.get('middleName', '')
    flattened['fullName'] = profile_data.get('fullName', '')
    
    # Контактная информация
    flattened['email'] = profile_data.get('email', '')
    flattened['phone'] = profile_data.get('phone', '')
    flattened['mobilePhone'] = profile_data.get('mobilePhone', '')
    
    # Организационная информация
    flattened['terDivisionName'] = profile_data.get('terDivisionName', '')
    flattened['divisionName'] = profile_data.get('divisionName', '')
    flattened['departmentName'] = profile_data.get('departmentName', '')
    flattened['positionName'] = profile_data.get('positionName', '')
    flattened['employeeStatus'] = profile_data.get('employeeStatus', '')
    flattened['businessBlock'] = profile_data.get('businessBlock', '')
    
    # Информация о награде
    flattened['awardDate'] = profile_data.get('awardDate', '')
    flattened['awardReason'] = profile_data.get('awardReason', '')
    flattened['awardLevel'] = profile_data.get('awardLevel', '')
    flattened['awardValue'] = profile_data.get('awardValue', '')
    
    # Статистика и показатели
    flattened['indicatorValue'] = profile_data.get('indicatorValue', '')
    flattened['successValue'] = profile_data.get('successValue', '')
    flattened['rating'] = profile_data.get('rating', '')
    flattened['placeInRating'] = profile_data.get('placeInRating', '')
    
    # Дополнительные поля
    flattened['photoUrl'] = profile_data.get('photoUrl', '')
    flattened['isActive'] = profile_data.get('isActive', '')
    flattened['lastActivityDate'] = profile_data.get('lastActivityDate', '')
    
    # Создаем полное имя, если его нет
    if not flattened['fullName']:
        name_parts = [flattened['lastName'], flattened['firstName'], flattened['middleName']]
        flattened['fullName'] = ' '.join([part for part in name_parts if part]).strip()
    
    # Парсим числовые значения
    flattened['indicatorValue_parsed'] = parse_float_safe(profile_data.get('indicatorValue', 0), f"indicatorValue for {flattened['fullName']}")
    flattened['successValue_parsed'] = parse_float_safe(profile_data.get('successValue', 0), f"successValue for {flattened['fullName']}")
    flattened['awardValue_parsed'] = parse_float_safe(profile_data.get('awardValue', 0), f"awardValue for {flattened['fullName']}")
    
    # Обработка вложенных структур (если есть)
    if 'divisionRatings' in profile_data:
        division_ratings = profile_data['divisionRatings']
        categories = ['BANK', 'TB', 'GOSB']
        for category in categories:
            flattened[f'{category}_groupId'] = ''
            flattened[f'{category}_placeInRating'] = ''
            flattened[f'{category}_ratingCategoryName'] = ''
        
        for rating in division_ratings:
            if isinstance(rating, dict):
                group_code = rating.get('groupCode', '')
                if group_code in categories:
                    group_id_raw = rating.get('groupId', '')
                    try:
                        flattened[f'{group_code}_groupId'] = int(float(group_id_raw)) if group_id_raw else ''
                    except (ValueError, TypeError):
                        flattened[f'{group_code}_groupId'] = ''
                    
                    place_in_rating_raw = rating.get('placeInRating', '')
                    try:
                        flattened[f'{group_code}_placeInRating'] = int(float(place_in_rating_raw)) if place_in_rating_raw else ''
                    except (ValueError, TypeError):
                        flattened[f'{group_code}_placeInRating'] = ''
                    
                    flattened[f'{group_code}_ratingCategoryName'] = rating.get('ratingCategoryName', '')
    
    return flattened

def apply_excel_styling(workbook, freeze_cell="B2"):
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
        
        # Закрепление строк и столбцов (если есть данные)
        if worksheet.max_row > 1:
            worksheet.freeze_panes = freeze_cell
        
        # Автофильтр для листа DATA
        if sheet_name == 'DATA' and worksheet.max_row > 1:
            # Получаем диапазон данных для автофильтра
            max_col = worksheet.max_column
            max_row = worksheet.max_row
            filter_range = f"A1:{get_column_letter(max_col)}{max_row}"
            worksheet.auto_filter.ref = filter_range
        
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

def create_reward_summary_sheet(workbook, data_df):
    """Создание сводного листа для данных наград"""
    if 'DATA' not in workbook.sheetnames:
        return
    
    # Создаем лист REWARD_SUMMARY
    if 'REWARD_SUMMARY' in workbook.sheetnames:
        workbook.remove(workbook['REWARD_SUMMARY'])
    summary_sheet = workbook.create_sheet('REWARD_SUMMARY')
    
    # Сводная статистика по наградам
    summary_data = [
        ["Параметр", "Значение"],
        ["Общее количество профилей с наградами", len(data_df)],
        ["Количество уникальных кодов наград", data_df['rewardCode'].nunique() if 'rewardCode' in data_df.columns else 0],
        ["Количество уникальных сотрудников", data_df['employeeNumber'].nunique() if 'employeeNumber' in data_df.columns else 0],
        ["Количество уникальных подразделений", data_df['terDivisionName'].nunique() if 'terDivisionName' in data_df.columns else 0]
    ]
    
    # Статистика по типам наград
    if 'badgeType' in data_df.columns:
        badge_type_stats = data_df['badgeType'].value_counts()
        summary_data.append(["", ""])
        summary_data.append(["Статистика по типам наград", ""])
        for badge_type, count in badge_type_stats.items():
            summary_data.append([badge_type, count])
    
    # Статистика по категориям наград
    if 'badgeCategory' in data_df.columns:
        badge_category_stats = data_df['badgeCategory'].value_counts()
        summary_data.append(["", ""])
        summary_data.append(["Статистика по категориям наград", ""])
        for badge_category, count in badge_category_stats.items():
            summary_data.append([badge_category, count])
    
    # Статистика по структурам данных
    if 'structure' in data_df.columns:
        structure_stats = data_df['structure'].value_counts()
        summary_data.append(["", ""])
        summary_data.append(["Статистика по структурам данных", ""])
        for structure, count in structure_stats.items():
            summary_data.append([structure, count])
    
    # Записываем данные в лист
    for row_idx, row_data in enumerate(summary_data, 1):
        for col_idx, value in enumerate(row_data, 1):
            summary_sheet.cell(row=row_idx, column=col_idx, value=value)
    
    # Применяем стили
    header_fill = PatternFill(start_color=EXCEL_COLORS["subheader"], end_color=EXCEL_COLORS["subheader"], fill_type="solid")
    header_font = Font(bold=True)
    
    for cell in summary_sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    logger.info(LOG_MESSAGES['reward_summary_sheet_created'])

# =============================================================================
# ФУНКЦИИ ГЕНЕРАЦИИ СКРИПТОВ
# =============================================================================

def load_script_data(config_key, data_list=None):
    """
    Общая функция для загрузки данных для скриптов
    
    Args:
        config_key (str): Ключ конфигурации из FUNCTION_CONFIGS
        data_list (list, optional): Список данных для обработки
        
    Returns:
        tuple: (config, data_list, selected_variant, variant_config)
    """
    config = FUNCTION_CONFIGS[config_key]
    
    # Получение данных согласно конфигурации
    if data_list is None:
        if config["data_source"] == "file":
            # Загрузка данных из файла
            file_extension = FILE_EXTENSIONS.get(config["input_format"], ".txt")
            filename = f"{config_key}_data{file_extension}"
            config_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["CONFIG"])
            filepath = os.path.join(config_dir, filename)
            data_list = load_data_from_file(
                filepath, 
                config["input_format"],
                config["csv_delimiter"],
                config["csv_encoding"],
                config["csv_column"]
            )
        elif config["data_source"] == "external_file":
            # Загрузка данных из внешнего файла
            file_extension = FILE_EXTENSIONS.get(config["input_format"], ".csv")
            config_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["CONFIG"])
            filepath = os.path.join(config_dir, config["input_file"] + file_extension)
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
    
    # Получение варианта конфигурации
    selected_variant = config.get("selected_variant", "sigma")
    variant_config = config["variants"][selected_variant]
    
    # Логирование процесса генерации
    logger.debug(LOG_MESSAGES['script_generation'].format(script_name=f"{config['name']} ({selected_variant.upper()})"))
    logger.debug(LOG_MESSAGES['config_loaded'].format(script_name=f"{config['name']} ({selected_variant.upper()})"))
    logger.debug(LOG_MESSAGES['variant_selected'].format(variant=selected_variant.upper()))
    logger.debug(LOG_MESSAGES['data_source_selected'].format(
        source=config['data_source'], 
        format=config['input_format']
    ))
    
    return config, data_list, selected_variant, variant_config

def save_and_copy_script(script, config, config_key, data_list):
    """
    Общая функция для сохранения скрипта
    Args:
        script (str): Сгенерированный JavaScript скрипт
        config (dict): Конфигурация скрипта
        config_key (str): Ключ конфигурации
        data_list (list): Список данных
    """
    # Сохранение скрипта в файл
    saved_filepath = save_script_to_file(script, config['name'], config_key)
    logger.info(LOG_MESSAGES['script_generated'].format(script_name=config['name'], count=len(data_list)))

# =============================================================================
# ФУНКЦИИ ГЕНЕРАЦИИ JAVASCRIPT СКРИПТОВ (ЗАГЛУШКИ)
# =============================================================================

@measure_time
def generate_leaders_for_admin_script(data_list=None):
    """
    Генерация скрипта для получения информации по участникам турнира
    
    Args:
        data_list (list, optional): Список ID участников
        
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    logger.info(LOG_MESSAGES['script_generation_start'].format(script_name="LeadersForAdmin"))
    logger.debug(LOG_MESSAGES['function_start'].format(func="generate_leaders_for_admin_script", params=f"args=({data_list}), kwargs=[]"))
    
    # Загрузка данных и конфигурации
    logger.info(LOG_MESSAGES['data_loading'])
    config, data_list, selected_variant, variant_config = load_script_data("leaders_for_admin", data_list)
    
    logger.info(LOG_MESSAGES['config_loaded_count'].format(count=len(data_list)))
    logger.debug(LOG_MESSAGES['variant_selected'].format(variant=selected_variant))
    logger.debug(LOG_MESSAGES['domain_info'].format(domain=variant_config['domain']))
    logger.debug(LOG_MESSAGES['api_path_info'].format(api_path=variant_config['params']['api_path']))
    
    # Генерация JavaScript скрипта для LeadersForAdmin
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

  const ids = [{', '.join([f'"{item}"' for item in data_list])}];
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
    
    # Сохранение и копирование скрипта
    logger.info(LOG_MESSAGES['script_saving'])
    save_and_copy_script(script, config, "leaders_for_admin", data_list)
    
    logger.info(LOG_MESSAGES['script_generated_success'].format(script_name="LeadersForAdmin", count=len(data_list)))
    logger.debug(LOG_MESSAGES['function_completed'].format(func="generate_leaders_for_admin_script", params="args=(), kwargs=[]", time="0.0000"))
    return script

@measure_time
def generate_reward_script(data_list=None):
    """
    Генерация скрипта для выгрузки профилей участников по кодам наград с пагинацией
    Args:
        data_list (list, optional): Список кодов наград
    Returns:
        str: Сгенерированный JavaScript скрипт
    """
    logger.info(LOG_MESSAGES['script_generation_start'].format(script_name="Reward"))
    logger.debug(LOG_MESSAGES['function_start'].format(func="generate_reward_script", params=f"args=({data_list}), kwargs=[]"))
    
    import datetime
    import json
    
    logger.info(LOG_MESSAGES['data_loading'])
    config, data_list, selected_variant, variant_config = load_script_data("reward", data_list)
    
    logger.info(LOG_MESSAGES['config_loaded_count'].format(count=len(data_list)))
    logger.debug(LOG_MESSAGES['variant_selected'].format(variant=selected_variant))
    logger.debug(LOG_MESSAGES['domain_info'].format(domain=variant_config['domain']))
    logger.debug(LOG_MESSAGES['api_path_info'].format(api_path=variant_config['params']['api_path']))
    
    delay = variant_config.get('delay_between_requests', 5)
    max_retries = variant_config.get('retry_count', 3)
    timeout = variant_config.get('timeout', 30000)
    domain = variant_config['domain']
    api_path = variant_config['params']['api_path']
    service = variant_config['params']['service']
    base_url = f"{domain}{api_path}"
    
    logger.debug(LOG_MESSAGES['request_params'].format(delay=delay, max_retries=max_retries, timeout=timeout))
    logger.debug(LOG_MESSAGES['base_url_info'].format(base_url=base_url))
    
    ids_string = ', '.join([f'"{item}"' for item in data_list])
    logger.debug(LOG_MESSAGES['ids_generated'].format(count=len(data_list)))
    script = f'''// ==UserScript==
// Скрипт для DevTools. Выгрузка профилей участников по кодам наград с пагинацией
// Вариант: {selected_variant.upper()}
(async () => {{
  function removePhotoData(obj) {{
    if (Array.isArray(obj)) {{ obj.forEach(removePhotoData); }}
    else if (obj && typeof obj === 'object') {{
      Object.keys(obj).forEach(key => {{
        if (key === 'photoData') delete obj[key];
        else removePhotoData(obj[key]);
      }});
    }}
  }}

  function getTimestamp() {{
    const d = new Date();
    const pad = n => n.toString().padStart(2, '0');
    return d.getFullYear().toString() + pad(d.getMonth() + 1) + pad(d.getDate()) + '-' + pad(d.getHours()) + pad(d.getMinutes()) + pad(d.getSeconds());
  }}

  function extractProfiles(data) {{
    try {{
      if (data?.body?.badge?.profiles && Array.isArray(data.body.badge.profiles)) {{
        return {{ profiles: data.body.badge.profiles }};
      }} else if (data?.body?.profiles && Array.isArray(data.body.profiles)) {{
        return {{ profiles: data.body.profiles }};
      }} else if (Array.isArray(data?.body)) {{
        return {{ profiles: data.body }};
      }} else if (Array.isArray(data)) {{
        return {{ profiles: data }};
      }}
      return null;
    }} catch (e) {{
      console.error('Ошибка при извлечении профилей:', e);
      return null;
    }}
  }}

  function extractContestantsCount(text) {{
    const match = text?.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }}

  async function fetchWithRetry(url, options, maxRetries = {max_retries}, timeout = {timeout}) {{
    for (let attempt = 1; attempt <= maxRetries; attempt++) {{
      try {{
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        const response = await fetch(url, {{ ...options, signal: controller.signal }});
        clearTimeout(id);
        return response;
      }} catch (e) {{
        if (attempt === maxRetries) throw e;
        await new Promise(r => setTimeout(r, 1000 * attempt));
      }}
    }}
  }}

  const ids = [{ids_string}];
  const BASE_URL = '{base_url}';
  const results = {{}};
  let totalProfiles = 0;

  for (let i = 0; i < ids.length; i++) {{
    const code = ids[i];
    const baseUrl = `${{BASE_URL}}${{code}}/profiles`;
    console.log(`\\n🔍 [${{i + 1}}/${{ids.length}}] Код: ${{code}}`);
    try {{
      const firstResp = await fetchWithRetry(`${{baseUrl}}?pageNum=1&divisionLevel=BANK`, {{
        headers: {{ 'Accept': 'application/json', 'Cookie': document.cookie, 'User-Agent': navigator.userAgent }},
        credentials: 'include'
      }});
      const firstData = await firstResp.json();
      const count = extractContestantsCount(firstData?.body?.badge?.contestants);
      console.log(`👥 Участников: ${{count}}`);
      
      if (count === 0) {{
        console.log(`⏭️ Пропускаем ${{code}} - нет участников`);
        continue;
      }}
      
      const pages = Math.ceil(count / 100) || 1;
      console.log(`📄 Страниц: ${{pages}}`);
      let profiles = [];
      for (let page = 1; page <= pages; page++) {{
        const url = `${{baseUrl}}?pageNum=${{page}}&divisionLevel=BANK`;
        console.log(`📄 Страница ${{page}} из ${{pages}}`);
        const resp = await fetchWithRetry(url, {{
          headers: {{ 'Accept': 'application/json', 'Cookie': document.cookie, 'User-Agent': navigator.userAgent }},
          credentials: 'include'
        }});
        const data = await resp.json();
        const parsed = extractProfiles(data);
        if (parsed?.profiles?.length) profiles.push(...parsed.profiles);
        await new Promise(r => setTimeout(r, {delay}));
      }}
      results[code] = {{
        profilesCount: profiles.length,
        profiles,
        badgeInfo: firstData?.body?.badge || {{}},
        totalContestants: count,
        pages
      }};
      totalProfiles += profiles.length;
    }} catch (e) {{
      console.error(`❌ Ошибка при обработке ${{code}}:`, e);
    }}
  }}

  console.log('\\n📦 Удаляем photoData...');
  removePhotoData(results);
  const ts = getTimestamp();
  const blob = new Blob([JSON.stringify(results, null, 2)], {{ type: 'application/json' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `profiles_{selected_variant.upper()}_${{ts}}.json`;
  a.click();
  console.log(`\\n✅ Завершено. Всего профилей: ${{totalProfiles}}`);
}})();
'''
    logger.info(LOG_MESSAGES['script_saving'])
    save_script_to_file(script, config['name'], "reward")
    
    logger.info(LOG_MESSAGES['script_generated_success'].format(script_name="Reward", count=len(data_list)))
    logger.debug(LOG_MESSAGES['function_completed'].format(func="generate_reward_script", params="args=(), kwargs=[]", time="0.0000"))
    return script

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

def load_json_data(input_json_path):
    """
    Общая функция для загрузки JSON данных
    
    Args:
        input_json_path (str): Путь к входному JSON файлу
        
    Returns:
        dict: Загруженные JSON данные
    """
    try:
        logger.info(LOG_MESSAGES['json_data_loading'])
        with open(input_json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data
    except Exception as e:
        logger.error(LOG_MESSAGES['json_load_error'].format(file_path=input_json_path, error=e))
        return None

def save_excel_file(df, output_excel_path, config_key=None):
    """
    Общая функция для сохранения DataFrame в Excel с применением стилей
    
    Args:
        df (DataFrame): DataFrame для сохранения
        output_excel_path (str): Путь к выходному Excel файлу
        config_key (str, optional): Ключ конфигурации для получения настроек
        
    Returns:
        bool: True если сохранение успешно, False в противном случае
    """
    try:
        # Создание директории для выходного файла если не существует
        output_dir = os.path.dirname(output_excel_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(LOG_MESSAGES['json_directory_created'].format(directory=output_dir))
        
        # Создание Excel файла
        logger.info(LOG_MESSAGES['json_excel_creation'])
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='DATA', index=False)
            workbook = writer.book
            
            # Получаем настройки закрепления из конфигурации
            freeze_cell = "B2"  # По умолчанию закрепляем первую строку и первую колонку
            if config_key and config_key in FUNCTION_CONFIGS:
                freeze_cell = FUNCTION_CONFIGS[config_key].get('excel_freeze_cell', "B2")
            
            # Применяем стили с настройками закрепления
            apply_excel_styling(workbook, freeze_cell)
            
            # Создание дополнительных листов
            create_summary_sheet(workbook, df)
            create_statistics_sheet(workbook, df)
            
            # Создание специального листа для reward данных
            if config_key == "reward":
                create_reward_summary_sheet(workbook, df)
        
        logger.info(LOG_MESSAGES['json_excel_success'].format(file_path=output_excel_path))
        return True
        
    except Exception as e:
        logger.error(LOG_MESSAGES['excel_creation_error'].format(error=e))
        return False

@measure_time
def convert_leaders_json_to_excel(input_json_path, output_excel_path, config_key=None):
    """
    Конвертация JSON файла с данными лидеров в Excel
    
    Args:
        input_json_path (str): Путь к входному JSON файлу
        output_excel_path (str): Путь к выходному Excel файлу
        config_key (str, optional): Ключ конфигурации для получения настроек
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        logger.info(LOG_MESSAGES['json_conversion_start'].format(input=input_json_path, output=output_excel_path))
        
        # Проверка существования входного файла
        if not os.path.exists(input_json_path):
            logger.error(LOG_MESSAGES['json_file_not_found'].format(file_path=input_json_path))
            return False
        
        # Загрузка JSON данных
        json_data = load_json_data(input_json_path)
        if json_data is None:
            return False
        
        # Обработка данных
        logger.info(LOG_MESSAGES['json_data_processing'])
        all_leaders_data = []
        
        if isinstance(json_data, dict):
            # Обрабатываем все турниры в структуре LeadersForAdmin
            total_tournaments = 0
            total_leaders = 0
            
            for tournament_key, tournament_value in json_data.items():
                if isinstance(tournament_value, list) and len(tournament_value) > 0:
                    # Проверяем, содержит ли первый элемент данные о турнире
                    first_item = tournament_value[0]
                    if isinstance(first_item, dict) and 'body' in first_item:
                        body = first_item['body']
                        if 'tournament' in body:
                            tournament = body['tournament']
                            if 'leaders' in tournament:
                                tournament_leaders = tournament['leaders']
                                if tournament_leaders:
                                    # Добавляем информацию о турнире к каждому лидеру
                                    for leader in tournament_leaders:
                                        leader_with_tournament = leader.copy()
                                        leader_with_tournament['tournamentId'] = tournament.get('tournamentId', tournament_key)
                                        leader_with_tournament['tournamentIndicator'] = tournament.get('tournamentIndicator', '')
                                        leader_with_tournament['tournamentStatus'] = tournament.get('status', '')
                                        leader_with_tournament['contestants'] = tournament.get('contestants', '')
                                        all_leaders_data.append(leader_with_tournament)
                                    
                                    total_tournaments += 1
                                    total_leaders += len(tournament_leaders)
                                    logger.debug(LOG_MESSAGES['json_leaders_found'].format(key=tournament_key, count=len(tournament_leaders)))
            
            logger.info(LOG_MESSAGES['tournaments_processed'].format(tournaments=total_tournaments, leaders=total_leaders))
            leaders_data = all_leaders_data
            
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
            logger.warning(LOG_MESSAGES['no_data_warning'])
            return False
        
        logger.info(LOG_MESSAGES['json_records_processed'].format(count=len(df)))
        
        # Сохранение в Excel
        return save_excel_file(df, output_excel_path, config_key)
        
    except Exception as e:
        logger.error(LOG_MESSAGES['json_leaders_conversion_error'].format(error=e))
        return False

def extract_profiles_from_data(data, structure):
    """
    Извлечение профилей из данных API наград
    
    Args:
        data (dict): Данные ответа API
        structure (str): Тип структуры данных
        
    Returns:
        list: Список профилей или None
    """
    try:
        if structure == 'body.badge.profiles':
            # Структура 1: body.badge.profiles
            if data.get('body', {}).get('badge', {}).get('profiles'):
                return data['body']['badge']['profiles']
        elif structure == 'body.profiles':
            # Структура 2: body.profiles
            if data.get('body', {}).get('profiles'):
                return data['body']['profiles']
        elif structure == 'body.array':
            # Структура 3: прямой массив профилей в body
            if isinstance(data.get('body'), list):
                return data['body']
        elif structure == 'root.array':
            # Структура 4: прямой массив в корне
            if isinstance(data, list):
                return data
        
        # Попытка автоматического определения структуры
        if data.get('body', {}).get('badge', {}).get('profiles'):
            return data['body']['badge']['profiles']
        elif data.get('body', {}).get('profiles'):
            return data['body']['profiles']
        elif isinstance(data.get('body'), list):
            return data['body']
        elif isinstance(data, list):
            return data
        
        return None
    except Exception as e:
        logger.error(LOG_MESSAGES['profile_extraction_error'].format(error=e))
        return None

@measure_time
def convert_reward_json_to_excel(input_json_path, output_excel_path, config_key=None):
    """
    Конвертация JSON файла с данными наград в Excel
    
    Args:
        input_json_path (str): Путь к входному JSON файлу
        output_excel_path (str): Путь к выходному Excel файлу
        config_key (str, optional): Ключ конфигурации для получения настроек
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        logger.info(LOG_MESSAGES['json_conversion_start'].format(input=input_json_path, output=output_excel_path))
        
        # Проверка существования входного файла
        if not os.path.exists(input_json_path):
            logger.error(LOG_MESSAGES['json_file_not_found'].format(file_path=input_json_path))
            return False
        
        # Загрузка JSON данных
        json_data = load_json_data(input_json_path)
        if json_data is None:
            return False
        
        # Обработка данных
        logger.info(LOG_MESSAGES['json_data_processing'])
        all_profiles_data = []
        
        if isinstance(json_data, dict):
            # Обрабатываем все коды наград
            total_rewards = 0
            total_profiles = 0
            
            for reward_code, reward_value in json_data.items():
                # Новая структура данных (с информацией о структуре)
                if isinstance(reward_value, dict):
                    data = reward_value.get('data', {})
                    structure = reward_value.get('structure', 'unknown')
                    profiles_count = reward_value.get('profilesCount', 0)
                    badge_info = reward_value.get('badgeInfo', {})
                    
                    # Извлекаем профили из данных
                    profiles = extract_profiles_from_data(data, structure)
                    
                    if profiles:
                        # Добавляем информацию о коде награды и данных награды к каждому профилю
                        for profile in profiles:
                            if isinstance(profile, dict):
                                profile_with_reward = profile.copy()
                                profile_with_reward['rewardCode'] = reward_code
                                profile_with_reward['structure'] = structure
                                
                                # Добавляем информацию о награде
                                if badge_info:
                                    profile_with_reward['badgeName'] = badge_info.get('name', '')
                                    profile_with_reward['badgeDescription'] = badge_info.get('description', '')
                                    profile_with_reward['badgeType'] = badge_info.get('type', '')
                                    profile_with_reward['badgeCategory'] = badge_info.get('category', '')
                                
                                all_profiles_data.append(profile_with_reward)
                        
                        total_rewards += 1
                        total_profiles += len(profiles)
                        logger.debug(LOG_MESSAGES['json_reward_found'].format(key=reward_code, count=len(profiles)))
                        logger.info(LOG_MESSAGES['reward_profiles_found'].format(code=reward_code, count=len(profiles), structure=structure))
                
                # Старая структура данных (для обратной совместимости)
                elif isinstance(reward_value, list) and len(reward_value) > 0:
                    # Проверяем, содержит ли первый элемент данные о награде
                    first_item = reward_value[0]
                    if isinstance(first_item, dict) and 'body' in first_item:
                        body = first_item['body']
                        # Проверяем разные возможные структуры данных
                        profiles = None
                        badge_info = None
                        
                        # Структура 1: body.badge.profiles
                        if 'badge' in body and 'profiles' in body['badge']:
                            profiles = body['badge']['profiles']
                            badge_info = body['badge']
                        # Структура 2: body.profiles (прямые профили)
                        elif 'profiles' in body:
                            profiles = body['profiles']
                            badge_info = body
                        
                        if profiles and isinstance(profiles, list):
                            # Добавляем информацию о коде награды и данных награды к каждому профилю
                            for profile in profiles:
                                if isinstance(profile, dict):
                                    profile_with_reward = profile.copy()
                                    profile_with_reward['rewardCode'] = reward_code
                                    
                                    # Добавляем информацию о награде
                                    if badge_info:
                                        profile_with_reward['badgeName'] = badge_info.get('name', '')
                                        profile_with_reward['badgeDescription'] = badge_info.get('description', '')
                                        profile_with_reward['badgeType'] = badge_info.get('type', '')
                                        profile_with_reward['badgeCategory'] = badge_info.get('category', '')
                                    
                                    all_profiles_data.append(profile_with_reward)
                            
                            total_rewards += 1
                            total_profiles += len(profiles)
                            logger.debug(LOG_MESSAGES['json_reward_found'].format(key=reward_code, count=len(profiles)))
                            logger.info(LOG_MESSAGES['reward_profiles_found_old'].format(code=reward_code, count=len(profiles)))
            
            logger.info(LOG_MESSAGES['rewards_processed'].format(rewards=total_rewards, profiles=total_profiles))
            profiles_data = all_profiles_data
            
        elif isinstance(json_data, list):
            # Прямой список профилей
            profiles_data = json_data
            logger.info(LOG_MESSAGES['direct_profiles_list'].format(count=len(profiles_data)))
        else:
            logger.error(LOG_MESSAGES['json_invalid_format'])
            return False
        
        if not profiles_data:
            logger.error(LOG_MESSAGES['no_profiles_error'])
            return False
        
        # Преобразование данных в плоскую структуру
        flattened_data = []
        for profile in profiles_data:
            flattened_profile = flatten_reward_profile_data(profile)
            flattened_data.append(flattened_profile)
        
        # Создание DataFrame
        df = pd.DataFrame(flattened_data)
        
        if df.empty:
            logger.warning(LOG_MESSAGES['no_data_warning'])
            return False
        
        logger.info(LOG_MESSAGES['json_records_processed'].format(count=len(df)))
        
        # Сохранение в Excel
        return save_excel_file(df, output_excel_path, config_key)
        
    except Exception as e:
        logger.error(LOG_MESSAGES['json_reward_conversion_error'].format(error=e))
        return False

@measure_time
def convert_json_to_excel(input_json_path, output_excel_path, config_key=None):
    """
    Универсальная конвертация JSON файла в Excel (для обратной совместимости)
    
    Args:
        input_json_path (str): Путь к входному JSON файлу
        output_excel_path (str): Путь к выходному Excel файлу
        config_key (str, optional): Ключ конфигурации для получения настроек
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    # Определяем тип данных по config_key
    if config_key == "leaders_for_admin":
        return convert_leaders_json_to_excel(input_json_path, output_excel_path, config_key)
    elif config_key == "reward":
        return convert_reward_json_to_excel(input_json_path, output_excel_path, config_key)
    else:
        # По умолчанию используем обработку лидеров
        return convert_leaders_json_to_excel(input_json_path, output_excel_path, config_key)

@measure_time
def convert_specific_json_file(file_name_without_extension, config_key=None):
    """
    Конвертирует конкретный JSON файл в Excel
    
    Args:
        file_name_without_extension (str): Имя файла без расширения
        config_key (str, optional): Ключ конфигурации для получения настроек Excel
        
    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        # Формируем пути к файлам используя новую структуру
        json_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["JSON"])
        output_dir = os.path.join(BASE_DIR, SUBDIRECTORIES["OUTPUT"])
        input_json_path = os.path.join(json_dir, f"{file_name_without_extension}.json")
        
        # Генерируем уникальное имя Excel файла
        if config_key and config_key in FUNCTION_CONFIGS:
            config = FUNCTION_CONFIGS[config_key]
            excel_file_base = config.get("excel_file", file_name_without_extension)
            selected_variant = config.get("selected_variant", "sigma")
            
            # Создаем временную метку
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            
            # Формируем имя файла: имя_из_конфига_<SIGMA/ALPHA>_YYYY-MM-DD-HH-MM-SS.xlsx
            excel_filename = f"{excel_file_base}_{selected_variant.upper()}_{timestamp}{FILE_EXTENSIONS['EXCEL']}"
        else:
            # Fallback: используем имя JSON файла с временной меткой
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            excel_filename = f"{file_name_without_extension}_{timestamp}{FILE_EXTENSIONS['EXCEL']}"
        
        output_excel_path = os.path.join(output_dir, excel_filename)
        
        logger.info(LOG_MESSAGES['json_file_processing'].format(file_name=file_name_without_extension))
        logger.info(LOG_MESSAGES['excel_file_creation'].format(filename=excel_filename))
        
        # Конвертируем файл
        if convert_json_to_excel(input_json_path, output_excel_path, config_key):
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
    logger.info(LOG_MESSAGES['summary_output'].format(summary=summary_text))
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
    logger.info(LOG_MESSAGES['separator_line'])
    logger.info(LOG_MESSAGES['program_start'].format(time=start_time_str))
    logger.info(LOG_MESSAGES['processing_start_time'].format(time=start_time_str))
    logger.info(LOG_MESSAGES['logging_level'].format(level=LOG_LEVEL))
    logger.info(LOG_MESSAGES['separator_line'])
    
    try:
        # Выполнение операций для каждого активного скрипта
        if ACTIVE_SCRIPTS:
            logger.info(LOG_MESSAGES['active_scripts_info'].format(scripts=', '.join(ACTIVE_SCRIPTS)))
            
            # ПЕРВЫЙ ЭТАП: Генерация всех скриптов
            logger.info(LOG_MESSAGES['stage1_title'])
            for script_name in ACTIVE_SCRIPTS:
                if script_name in FUNCTION_CONFIGS:
                    config = FUNCTION_CONFIGS[script_name]
                    active_operations = config.get("active_operations", "scripts_only")
                    
                    logger.info(LOG_MESSAGES['script_processing'].format(script_name=script_name))
                    logger.info(LOG_MESSAGES['active_operations_info'].format(script_name=script_name, operations=active_operations))
                    
                    # Генерация скриптов
                    if active_operations in ["scripts_only", "both"]:
                        logger.info(LOG_MESSAGES['script_generation_info'].format(script_name=script_name))
                        if script_name == "leaders_for_admin":
                            generate_leaders_for_admin_script()
                        elif script_name == "reward":
                            generate_reward_script()
                        elif script_name == "profile":
                            generate_profile_script()
                        elif script_name == "news_details":
                            generate_news_details_script()
                        elif script_name == "address_book_tn":
                            generate_address_book_tn_script()
                        elif script_name == "address_book_dev":
                            generate_address_book_dev_script()
                        elif script_name == "orders":
                            generate_orders_script()
                        elif script_name == "news_list":
                            generate_news_list_script()
                        elif script_name == "rating_list":
                            generate_rating_list_script()
                        else:
                            generate_script_universal(script_name)
                    else:
                        logger.info(LOG_MESSAGES['script_generation_skipped'].format(script_name=script_name, operations=active_operations))
                else:
                    logger.error(LOG_MESSAGES['unknown_script_error'].format(script_name=script_name))
            
            # ВТОРОЙ ЭТАП: Обработка всех JSON файлов
            logger.info(LOG_MESSAGES['stage2_title'])
            for script_name in ACTIVE_SCRIPTS:
                if script_name in FUNCTION_CONFIGS:
                    config = FUNCTION_CONFIGS[script_name]
                    active_operations = config.get("active_operations", "scripts_only")
                    
                    # Обработка JSON файлов
                    if active_operations in ["json_only", "both"]:
                        if "json_file" in config:
                            json_file = config["json_file"]
                            logger.info(LOG_MESSAGES['json_file_processing_info'].format(json_file=json_file))
                            convert_specific_json_file(json_file, script_name)
                        else:
                            logger.warning(LOG_MESSAGES['no_json_file_warning'].format(script_name=script_name))
                    else:
                        logger.info(LOG_MESSAGES['json_processing_skipped'].format(script_name=script_name, operations=active_operations))
        else:
            logger.info(LOG_MESSAGES['no_active_scripts'])
            
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
        logger.info(LOG_MESSAGES['separator_line'])
        logger.info(LOG_MESSAGES['program_end'].format(time=end_time_str))
        logger.info(LOG_MESSAGES['total_execution_time'].format(time=total_time))
        logger.info(LOG_MESSAGES['separator_line'])

# Точка входа в программу
if __name__ == "__main__":
    main() 