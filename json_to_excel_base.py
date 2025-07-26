#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый модуль для обработки JSON данных и сохранения в Excel
Автор: OrionFLASH
Описание: Предоставляет базовый класс JSONToExcelProcessor для парсинга JSON файлов,
         разворачивания вложенных структур, фильтрации полей и сохранения в Excel
"""

import json
import pandas as pd
import logging
import os
import time
import datetime
from functools import wraps

# =============================================================================
# БАЗОВЫЙ КЛАСС ДЛЯ ПАРСИНГА JSON В EXCEL
# =============================================================================

class JSONToExcelProcessor:
    """
    Базовый класс для обработки JSON данных и сохранения в Excel
    
    Предоставляет функциональность для:
    - Загрузки JSON файлов
    - Разворачивания вложенных структур в плоскую таблицу
    - Фильтрации полей по включению/исключению
    - Сохранения данных в Excel файлы
    - Логирования всех операций
    - Измерения времени выполнения
    """
    
    def __init__(self, config_name, log_level="DEBUG"):
        """
        Инициализация процессора JSON данных
        
        Args:
            config_name (str): Имя конфигурации для логирования и идентификации
            log_level (str): Уровень логирования ("DEBUG", "INFO", "WARNING", "ERROR")
        """
        self.config_name = config_name
        self.log_level = log_level
        self.logger = None
        self.processed_rows = 0  # Количество обработанных строк
        self.start_time = None   # Время начала обработки
        self.function_times = {} # Словарь для хранения времени выполнения функций
        
        # Словарь с сообщениями для логирования
        # Поддерживает форматирование с переменными в фигурных скобках
        self.LOG_MESSAGES = {
            # Сообщения о начале и завершении обработки
            "start": "=== Старт обработки JSON для {script}: {time} ===",
            "finish": "=== Завершение обработки {script}. Строк: {rows}. Время: {time:.3f}s ===",
            
            # Сообщения о работе с файлами
            "reading_file": "Загрузка файла: {file_path}",
            "read_ok": "Файл успешно загружен: {file_path}, строк: {rows}",
            "read_fail": "Ошибка загрузки файла: {file_path}. {error}",
            
            # Сообщения о парсинге JSON
            "json_parse_start": "Начало парсинга JSON данных",
            "json_parse_ok": "JSON успешно распарсен: {rows} записей",
            "json_parse_fail": "Ошибка парсинга JSON: {error}",
            
            # Сообщения о работе с Excel
            "excel_write_start": "Запись данных в Excel: {file_path}",
            "excel_write_ok": "Excel файл создан: {file_path} (строк: {rows}, колонок: {cols})",
            "excel_write_fail": "Ошибка записи Excel: {error}",
            
            # Сообщения о разворачивании структуры
            "flatten_start": "Разворачивание вложенных объектов",
            "flatten_ok": "Разворачивание завершено: добавлено {cols} колонок",
            
            # Сообщения о фильтрации полей
            "field_filter": "Применение фильтров полей: включено {included}, исключено {excluded}",
            
            # Сообщения о выполнении функций
            "func_start": "[START] {func} {params}",
            "func_end": "[END] {func} (время: {time:.3f}s)",
            "func_error": "[ERROR] {func} — {error}"
        }
        
        # Настройка логирования
        self.setup_logging()
    
    def setup_logging(self):
        """
        Настройка системы логирования
        
        Создает логгер с уникальным именем для каждого процессора.
        Настраивает запись в файл и вывод в консоль.
        """
        # Директория для логов (жестко заданный путь)
        log_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/LOGS"
        os.makedirs(log_dir, exist_ok=True)
        
        # Формирование имени файла лога с временной меткой
        # Формат: json_parser_leaders_for_admin_DEBUG_2024-01-15.log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        log_filename = f"json_parser_{self.config_name}_{self.log_level}_{timestamp}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        # Создание логгера с уникальным именем
        self.logger = logging.getLogger(f'JSONParser_{self.config_name}')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Удаление существующих handlers для избежания дублирования
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Создание file handler для записи в файл
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.log_level))
        
        # Создание console handler для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        
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
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def measure_time(self, func):
        """
        Декоратор для измерения времени выполнения методов
        
        Логирует начало и конец выполнения метода, а также время выполнения.
        Сохраняет время выполнения в словарь function_times.
        
        Args:
            func: Метод для декорирования
            
        Returns:
            wrapper: Обернутый метод с измерением времени
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Формирование строки параметров для логирования
            # Пропускаем self (первый аргумент) и берем следующие 2 аргумента
            params_str = str(args[1:3]) if len(args) > 1 else ""
            self.logger.debug(self.LOG_MESSAGES['func_start'].format(func=func.__name__, params=params_str))
            
            try:
                # Выполнение метода
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Сохранение времени выполнения
                self.function_times[func.__name__] = execution_time
                
                # Логирование успешного завершения
                self.logger.debug(self.LOG_MESSAGES['func_end'].format(func=func.__name__, time=execution_time))
                return result
                
            except Exception as e:
                # Обработка ошибок
                execution_time = time.time() - start_time
                self.function_times[func.__name__] = execution_time
                self.logger.error(self.LOG_MESSAGES['func_error'].format(func=func.__name__, error=str(e)))
                raise
                
        return wrapper
    
    def load_json_file(self, file_path):
        """
        Загрузка JSON файла
        
        Поддерживает загрузку как списков объектов, так и отдельных объектов.
        Автоматически преобразует одиночный объект в список для единообразной обработки.
        
        Args:
            file_path (str): Путь к JSON файлу
            
        Returns:
            list: Список объектов из JSON файла (даже если был один объект)
        """
        self.logger.debug(self.LOG_MESSAGES['reading_file'].format(file_path=file_path))
        
        try:
            # Чтение JSON файла
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Определение типа данных и преобразование в список
            if isinstance(data, list):
                # Если это список объектов
                rows = len(data)
            elif isinstance(data, dict):
                # Если это одиночный объект, оборачиваем в список
                rows = 1
                data = [data]
            else:
                # Неожиданный тип данных
                rows = 0
                data = []
            
            self.logger.info(self.LOG_MESSAGES['read_ok'].format(file_path=file_path, rows=rows))
            return data
            
        except Exception as e:
            # Обработка ошибок чтения файла
            self.logger.error(self.LOG_MESSAGES['read_fail'].format(file_path=file_path, error=str(e)))
            return []
    
    def flatten_json(self, data, separator='_', prefix=''):
        """
        Разворачивание вложенных JSON объектов в плоскую структуру
        
        Рекурсивно проходит по всем вложенным объектам и массивам,
        создавая плоскую структуру с составными ключами.
        
        Args:
            data (list or dict): Данные для разворачивания
            separator (str): Разделитель для составных ключей (по умолчанию '_')
            prefix (str): Префикс для ключей (используется в рекурсии)
            
        Returns:
            list: Список развернутых объектов
        """
        self.logger.debug(self.LOG_MESSAGES['flatten_start'])
        
        def flatten_dict(d, parent_key='', sep='_'):
            """
            Внутренняя функция для рекурсивного разворачивания словаря
            
            Args:
                d (dict): Словарь для разворачивания
                parent_key (str): Ключ родительского элемента
                sep (str): Разделитель для составных ключей
                
            Returns:
                dict: Развернутый словарь
            """
            items = []
            for k, v in d.items():
                # Формирование нового ключа
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                
                if isinstance(v, dict):
                    # Если значение - словарь, рекурсивно разворачиваем его
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    # Если значение - список, обрабатываем каждый элемент
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            # Если элемент списка - словарь, разворачиваем его
                            items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                        else:
                            # Если элемент списка - простое значение
                            items.append((f"{new_key}{sep}{i}", item))
                else:
                    # Если значение - простое (строка, число, булево)
                    items.append((new_key, v))
            return dict(items)
        
        # Обработка входных данных
        if isinstance(data, list):
            # Если это список объектов, разворачиваем каждый
            flattened_data = [flatten_dict(item, prefix, separator) for item in data]
        else:
            # Если это одиночный объект, разворачиваем его
            flattened_data = [flatten_dict(data, prefix, separator)]
        
        # Логирование результата разворачивания
        if flattened_data:
            cols_count = len(flattened_data[0].keys())
            self.logger.debug(self.LOG_MESSAGES['flatten_ok'].format(cols=cols_count))
        
        return flattened_data
    
    def filter_fields(self, data, include_fields=None, exclude_fields=None):
        """
        Фильтрация полей по включению/исключению
        
        Позволяет включить только указанные поля или исключить указанные поля.
        Приоритет отдается списку включения (если он задан).
        
        Args:
            data (list): Список объектов для фильтрации
            include_fields (list, optional): Список полей для включения
            exclude_fields (list, optional): Список полей для исключения
            
        Returns:
            list: Список объектов с отфильтрованными полями
        """
        # Если фильтры не заданы, возвращаем исходные данные
        if not include_fields and not exclude_fields:
            return data
        
        # Подсчет количества полей в фильтрах для логирования
        included_count = len(include_fields) if include_fields else 0
        excluded_count = len(exclude_fields) if exclude_fields else 0
        
        self.logger.debug(self.LOG_MESSAGES['field_filter'].format(
            included=included_count, 
            excluded=excluded_count
        ))
        
        # Фильтрация данных
        filtered_data = []
        for row in data:
            filtered_row = {}
            for key, value in row.items():
                # Если есть список включения - берем только из него
                if include_fields:
                    if key in include_fields:
                        filtered_row[key] = value
                # Если есть список исключения - берем все кроме него
                elif exclude_fields:
                    if key not in exclude_fields:
                        filtered_row[key] = value
                else:
                    # Если фильтры не заданы, берем все поля
                    filtered_row[key] = value
            
            filtered_data.append(filtered_row)
        
        return filtered_data
    
    def save_to_excel(self, data, output_path, sheet_name="Data"):
        """
        Сохранение данных в Excel файл
        
        Использует pandas для создания Excel файла с указанным именем листа.
        Автоматически создает директории если они не существуют.
        
        Args:
            data (list): Список словарей для сохранения
            output_path (str): Путь к выходному Excel файлу
            sheet_name (str): Имя листа в Excel файле
            
        Returns:
            bool: True если сохранение успешно, False в случае ошибки
        """
        self.logger.debug(self.LOG_MESSAGES['excel_write_start'].format(file_path=output_path))
        
        try:
            # Создание DataFrame из списка словарей
            df = pd.DataFrame(data)
            
            # Создание директории если не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Сохранение в Excel с использованием openpyxl
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Получение размеров данных
            rows, cols = df.shape
            self.processed_rows = rows
            
            # Логирование успешного сохранения
            self.logger.info(self.LOG_MESSAGES['excel_write_ok'].format(
                file_path=output_path, 
                rows=rows, 
                cols=cols
            ))
            
            return True
            
        except Exception as e:
            # Обработка ошибок сохранения
            self.logger.error(self.LOG_MESSAGES['excel_write_fail'].format(error=str(e)))
            return False
    
    def process(self, input_file, output_file, include_fields=None, exclude_fields=None, sheet_name="Data"):
        """
        Основная функция обработки JSON данных
        
        Координирует весь процесс обработки:
        1. Загрузка JSON файла
        2. Разворачивание вложенных структур
        3. Фильтрация полей
        4. Сохранение в Excel
        
        Args:
            input_file (str): Путь к входному JSON файлу
            output_file (str): Путь к выходному Excel файлу
            include_fields (list, optional): Список полей для включения
            exclude_fields (list, optional): Список полей для исключения
            sheet_name (str): Имя листа в Excel файле
            
        Returns:
            bool: True если обработка успешна, False в случае ошибки
        """
        # Инициализация времени начала обработки
        self.start_time = time.time()
        start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Логирование начала обработки
        self.logger.info(self.LOG_MESSAGES['start'].format(script=self.config_name, time=start_time_str))
        
        try:
            # 1. Загрузка JSON данных
            json_data = self.load_json_file(input_file)
            if not json_data:
                return False
            
            # 2. Разворачивание структуры в плоскую таблицу
            flattened_data = self.flatten_json(json_data)
            
            # 3. Фильтрация полей (если заданы фильтры)
            filtered_data = self.filter_fields(flattened_data, include_fields, exclude_fields)
            
            # 4. Сохранение в Excel
            success = self.save_to_excel(filtered_data, output_file, sheet_name)
            
            # Итоговое сообщение с статистикой
            total_time = time.time() - self.start_time
            self.logger.info(self.LOG_MESSAGES['finish'].format(
                script=self.config_name, 
                rows=self.processed_rows, 
                time=total_time
            ))
            
            return success
            
        except Exception as e:
            # Обработка критических ошибок
            self.logger.error(self.LOG_MESSAGES['func_error'].format(func="process", error=str(e)))
            return False

# =============================================================================
# УТИЛИТАРНЫЕ ФУНКЦИИ
# =============================================================================

def create_processor_config():
    """
    Создание конфигурации для различных типов данных
    
    Возвращает словарь с настройками для каждого типа JSON данных:
    - sheet_name: имя листа в Excel
    - include_fields: список полей для включения
    - exclude_fields: список полей для исключения
    
    Returns:
        dict: Словарь конфигураций для всех типов данных
    """
    return {
        "leaders_for_admin": {
            "sheet_name": "Leaders",
            "include_fields": ["id", "name", "score", "level", "rank", "achievements"],
            "exclude_fields": ["internal_data", "debug_info"]
        },
        "reward": {
            "sheet_name": "Rewards", 
            "include_fields": ["employee_id", "reward_type", "amount", "date", "status"],
            "exclude_fields": ["approval_chain", "internal_notes"]
        },
        "profile": {
            "sheet_name": "Profiles",
            "include_fields": ["profile_id", "name", "department", "position", "stats"],
            "exclude_fields": ["password_hash", "session_data"]
        },
        "news_details": {
            "sheet_name": "NewsDetails",
            "include_fields": ["news_id", "title", "content", "author", "date", "category"],
            "exclude_fields": ["edit_history", "metadata"]
        },
        "address_book_tn": {
            "sheet_name": "EmployeesbyTN", 
            "include_fields": ["employee_number", "name", "department", "position", "contacts"],
            "exclude_fields": ["salary", "internal_id"]
        },
        "address_book_dev": {
            "sheet_name": "Departments",
            "include_fields": ["department_id", "name", "manager", "employees", "location"],
            "exclude_fields": ["budget", "internal_codes"]
        },
        "orders": {
            "sheet_name": "Orders",
            "include_fields": ["employee_id", "preference_type", "selected_option", "date"],
            "exclude_fields": ["processing_notes", "system_data"]
        },
        "news_list": {
            "sheet_name": "NewsList",
            "include_fields": ["news_id", "title", "preview", "author", "date", "category"],
            "exclude_fields": ["full_content", "metadata"]
        },
        "rating_list": {
            "sheet_name": "Ratings",
            "include_fields": ["participant_id", "name", "total_points", "rank", "rewards", "crystals"],
            "exclude_fields": ["calculation_details", "system_data"]
        }
    } 