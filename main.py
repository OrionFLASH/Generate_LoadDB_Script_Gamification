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
from functools import wraps

# Импорт библиотеки для работы с буфером обмена
import pyperclip

# =============================================================================
# КОНСТАНТЫ И НАСТРОЙКИ ПРОГРАММЫ
# =============================================================================

# Настройки логирования
LOG_LEVEL = "DEBUG"  # "INFO" или "DEBUG" - уровень детализации логов
LOG_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/LOGS"  # Директория для логов
LOG_FILENAME_BASE = "game_script_generator"  # Базовое имя файла лога

# Настройки входных и выходных данных
INPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"  # Директория входных файлов
OUTPUT_DIR = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"  # Директория выходных файлов

# Настройки обработки данных
DATA_SOURCE = "file"  # "file" - из файла, "variable" - из переменной
INPUT_FORMAT = "TXT"  # "TXT" - текстовый файл, "CSV" - CSV файл
INPUT_FILENAME = "input_data.txt"  # Имя входного файла
INPUT_FILE_EXTENSION = ".txt"  # Расширение входного файла

# Выбор активных скриптов для генерации
# Раскомментируйте нужные скрипты для генерации
ACTIVE_SCRIPTS = [
    # "leaders_for_admin",  # Информация по участникам турнира
    # "reward",             # Информация о наградах сотрудников
    # "profile",            # Профили сотрудников
    # "news_details",       # Детальная карточка новости
    # "address_book_tn",    # Карточка сотрудника по табельному номеру
    # "address_book_dev",   # Карточка подразделения
    # "orders",             # Список сотрудников с преференциями
    # "news_list",          # Список новостей
    # "rating_list"         # Рейтинг участников
]

# Настройки для TXT файлов
# Массив всех возможных разделителей для текстовых файлов
# Включает знаки препинания, пробелы, переносы строк и специальные символы
TXT_DELIMITERS = [",", ";", "\t", " ", "\n", "\r\n", "|", ":", ".", "!", "?", "@", "#", "$", "%", "^", "&", "*", "(", ")", "[", "]", "{", "}", "<", ">", "/", "\\", "=", "+", "~", "`", "'", '"']

# Настройки для CSV файлов
CSV_DELIMITER = ";"  # Разделитель колонок в CSV файлах
CSV_ENCODING = "utf-8"  # Кодировка CSV файлов
CSV_COLUMN_NAME = "data_column"  # Название столбца для извлечения данных

# Тестовые данные для работы без внешнего файла
# Используются когда DATA_SOURCE = "variable"
TEST_DATA_LIST = [
    "test_value_1",
    "test_value_2", 
    "test_value_3"
]

# =============================================================================
# ТЕКСТЫ ДЛЯ ЛОГИРОВАНИЯ
# =============================================================================

# Словарь с сообщениями для логирования
# Поддерживает форматирование с переменными в фигурных скобках
LOG_MESSAGES = {
    # Сообщения о начале и конце программы
    "program_start": "=== СТАРТ ПРОГРАММЫ - Генератор JavaScript скриптов: {time} ===",
    "program_end": "=== ФИНАЛ ПРОГРАММЫ - {time} ===",
    "processing_start_time": "Время начала обработки: {time}",
    "logging_level": "Уровень логирования: {level}",
    "total_execution_time": "Итоговое время работы: {time:.4f} секунд",
    
    # Сообщения о выполнении функций
    "function_start": "[START] {func} {params}",
    "function_completed": "[END] {func} {params} (время: {time:.4f}s)",
    "function_error": "[ERROR] {func} {params} — {error}",
    
    # Сообщения о данных
    "data_received": "Получено данных для обработки: {count}",
    "program_success": "Программа выполнена успешно",
    "critical_error": "Критическая ошибка в программе: {error}",
    
    # Сообщения для итоговой статистики
    "summary_title": "SUMMARY - Итоговая статистика",
    "total_time": "Общее время: {time:.4f} сек",
    "actions_processed": "Действий: {count}",
    "functions_executed": "Функций: {count}",
    "function_time": "Функция {func}: {time:.4f} сек",
    "program_completed": "Программа завершена: {time}",
    
    # Сообщения о работе с файлами
    "file_loading": "Загрузка данных из файла: {file_path}, формат: {format}",
    "file_not_found": "Файл не найден: {file_path}",
    "file_loaded": "Файл успешно загружен: {file_path}, элементов: {count}",
    "file_load_error": "Ошибка загрузки файла: {file_path}. {error}",
    "using_test_data": "Использование тестовых данных: {count} элементов",
    
    # Сообщения о буфере обмена
    "clipboard_copied": "Текст скопирован в буфер обмена",
    "clipboard_error": "Ошибка при копировании в буфер: {error}",
    
    # Сообщения о генерации скриптов
    "script_generation": "Генерация скрипта: {script_name}",
    "script_generated": "Скрипт {script_name} сгенерирован успешно (данных: {count})",
    
    # Сообщения для итоговой статистики
    "summary_stats": "ИТОГОВАЯ СТАТИСТИКА РАБОТЫ ПРОГРАММЫ",
    "total_execution": "Общее время выполнения: {time:.4f} секунд",
    "processed_actions": "Обработано действий: {count}",
    "executed_functions": "Выполнено функций: {count}",
    "execution_times": "Время выполнения функций:",
    "selected_script": "Выбранный скрипт для генерации: {script_name}",
    "config_loaded": "Конфигурация загружена для: {script_name}",
    
    # Сообщения о обработке файлов
    "csv_processing": "Обработка CSV: разделитель '{delimiter}', кодировка '{encoding}', столбец '{column}'",
    "txt_processing": "Обработка TXT: найдено разделителей {delimiters_count}",
    "data_source_selected": "Источник данных: {source} ({format})"
}

# =============================================================================
# КОНФИГУРАЦИЯ ФУНКЦИЙ
# =============================================================================

# Словарь с конфигурацией для каждого типа скрипта
# Содержит параметры для генерации JavaScript и обработки данных
FUNCTION_CONFIGS = {
    "leaders_for_admin": {
        "name": "LeadersForAdmin",
        "description": "Информация по загруженным в турнир данным об участниках",
        "domain": "tournament.example.com",
        "params": {
            "api_endpoint": "/api/tournament/leaders",
            "include_stats": True,
            "format": "json",
            "limit": 1000
        },
        "data_source": "file",  # Источник данных: "file" или "variable"
        "input_format": "CSV",  # Формат входных данных: "CSV" или "TXT"
        "csv_column": "participant_id",  # Название столбца в CSV
        "csv_delimiter": ";",  # Разделитель в CSV
        "csv_encoding": "utf-8"  # Кодировка CSV
    },
    "reward": {
        "name": "REWARD",
        "description": "Информация о сотрудниках которые уже получили награды",
        "domain": "rewards.example.com",
        "params": {
            "api_endpoint": "/api/rewards/list",
            "include_details": True,
            "status": "received",
            "date_from": "2024-01-01"
        },
        "data_source": "file",
        "input_format": "CSV",
        "csv_column": "employee_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "profile": {
        "name": "PROFILE",
        "description": "Профили сотрудников в героях продаж",
        "domain": "profiles.example.com",
        "params": {
            "api_endpoint": "/api/profiles/employee",
            "include_stats": True,
            "include_achievements": True,
            "format": "detailed"
        },
        "data_source": "file",
        "input_format": "TXT",
        "csv_column": "profile_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "news_details": {
        "name": "NewsDetails",
        "description": "Детальная карточка новости",
        "domain": "news.example.com",
        "params": {
            "api_endpoint": "/api/news/details",
            "include_content": True,
            "include_attachments": True,
            "format": "full"
        },
        "data_source": "file",
        "input_format": "TXT",
        "csv_column": "news_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "address_book_tn": {
        "name": "AdressBookTN",
        "description": "Карточка сотрудника из адресной книги по табельным номерам",
        "domain": "directory.example.com",
        "params": {
            "api_endpoint": "/api/directory/employee",
            "search_by": "employee_number",
            "include_contacts": True,
            "include_department": True
        },
        "data_source": "file",
        "input_format": "CSV",
        "csv_column": "employee_number",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "address_book_dev": {
        "name": "AdressBookDev",
        "description": "Карточка подразделения из адресной книги со списком сотрудников",
        "domain": "directory.example.com",
        "params": {
            "api_endpoint": "/api/directory/department",
            "include_employees": True,
            "include_hierarchy": True,
            "format": "detailed"
        },
        "data_source": "file",
        "input_format": "CSV",
        "csv_column": "department_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "orders": {
        "name": "Orders",
        "description": "Список сотрудников выбравших преференции",
        "domain": "orders.example.com",
        "params": {
            "api_endpoint": "/api/orders/preferences",
            "status": "selected",
            "include_details": True,
            "date_from": "2024-01-01"
        },
        "data_source": "file",
        "input_format": "CSV",
        "csv_column": "employee_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "news_list": {
        "name": "NewsList",
        "description": "Список новостей",
        "domain": "news.example.com",
        "params": {
            "api_endpoint": "/api/news/list",
            "status": "published",
            "include_preview": True,
            "limit": 100
        },
        "data_source": "variable",  # Использует тестовые данные
        "input_format": "TXT",
        "csv_column": "news_category",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    },
    "rating_list": {
        "name": "RaitingList",
        "description": "Рейтинг участников по полученным наградам и кристаллам",
        "domain": "rating.example.com",
        "params": {
            "api_endpoint": "/api/rating/participants",
            "sort_by": "total_points",
            "include_rewards": True,
            "include_crystals": True,
            "limit": 500
        },
        "data_source": "file",
        "input_format": "CSV",
        "csv_column": "participant_id",
        "csv_delimiter": ";",
        "csv_encoding": "utf-8"
    }
}

# Настройки для генерации JavaScript скриптов (глобальные по умолчанию)
BASE_DOMAIN = "example.com"  # Базовый домен для API запросов
REQUEST_PARAMETERS = {  # Дополнительные параметры запросов
    "param1": "value1",
    "param2": "value2"
}

# =============================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# =============================================================================

logger = None  # Глобальный объект логгера
program_start_time = None  # Время начала выполнения программы
function_execution_times = {}  # Словарь для хранения времени выполнения функций
processed_actions_count = 0  # Счетчик обработанных действий

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
        filepath = os.path.join(INPUT_DIR, INPUT_FILENAME)
        return load_data_from_file(filepath, INPUT_FORMAT)
    else:
        # Использование тестовых данных
        logger.info(LOG_MESSAGES['using_test_data'].format(count=len(TEST_DATA_LIST)))
        return TEST_DATA_LIST.copy()

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
            filename = f"{config_key}_data.{config['input_format'].lower()}"
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
    logger.debug(LOG_MESSAGES['script_generation'].format(script_name=config['name']))
    logger.debug(LOG_MESSAGES['config_loaded'].format(script_name=config['name']))
    logger.debug(LOG_MESSAGES['data_source_selected'].format(
        source=config['data_source'], 
        format=config['input_format']
    ))
    
    # Генерация JavaScript скрипта (заглушка)
    # TODO: Реализовать реальную логику генерации скриптов
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
        # Получение данных (для общего использования)
        data_list = get_data()
        logger.info(LOG_MESSAGES['data_received'].format(count=len(data_list)))
        
        # Генерация скриптов согласно настройкам ACTIVE_SCRIPTS
        if ACTIVE_SCRIPTS:
            logger.info(f"Активные скрипты для генерации: {', '.join(ACTIVE_SCRIPTS)}")
            for script_name in ACTIVE_SCRIPTS:
                if script_name in FUNCTION_CONFIGS:
                    logger.info(LOG_MESSAGES['selected_script'].format(script_name=script_name))
                    generate_script_universal(script_name)
                else:
                    logger.error(f"Неизвестный скрипт: {script_name}")
        else:
            logger.info("Нет активных скриптов для генерации. Настройте ACTIVE_SCRIPTS.")
            
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