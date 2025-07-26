#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    """Базовый класс для обработки JSON данных и сохранения в Excel"""
    
    def __init__(self, config_name, log_level="DEBUG"):
        self.config_name = config_name
        self.log_level = log_level
        self.logger = None
        self.processed_rows = 0
        self.start_time = None
        self.function_times = {}
        
        # Лог сообщения
        self.LOG_MESSAGES = {
            "start": "=== Старт обработки JSON для {script}: {time} ===",
            "reading_file": "Загрузка файла: {file_path}",
            "read_ok": "Файл успешно загружен: {file_path}, строк: {rows}",
            "read_fail": "Ошибка загрузки файла: {file_path}. {error}",
            "json_parse_start": "Начало парсинга JSON данных",
            "json_parse_ok": "JSON успешно распарсен: {rows} записей",
            "json_parse_fail": "Ошибка парсинга JSON: {error}",
            "excel_write_start": "Запись данных в Excel: {file_path}",
            "excel_write_ok": "Excel файл создан: {file_path} (строк: {rows}, колонок: {cols})",
            "excel_write_fail": "Ошибка записи Excel: {error}",
            "flatten_start": "Разворачивание вложенных объектов",
            "flatten_ok": "Разворачивание завершено: добавлено {cols} колонок",
            "field_filter": "Применение фильтров полей: включено {included}, исключено {excluded}",
            "finish": "=== Завершение обработки {script}. Строк: {rows}. Время: {time:.3f}s ===",
            "func_start": "[START] {func} {params}",
            "func_end": "[END] {func} (время: {time:.3f}s)",
            "func_error": "[ERROR] {func} — {error}"
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/LOGS"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        log_filename = f"json_parser_{self.config_name}_{self.log_level}_{timestamp}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        self.logger = logging.getLogger(f'JSONParser_{self.config_name}')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.log_level))
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def measure_time(self, func):
        """Декоратор для измерения времени выполнения"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            params_str = str(args[1:3]) if len(args) > 1 else ""
            self.logger.debug(self.LOG_MESSAGES['func_start'].format(func=func.__name__, params=params_str))
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                self.function_times[func.__name__] = execution_time
                self.logger.debug(self.LOG_MESSAGES['func_end'].format(func=func.__name__, time=execution_time))
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                self.function_times[func.__name__] = execution_time
                self.logger.error(self.LOG_MESSAGES['func_error'].format(func=func.__name__, error=str(e)))
                raise
        return wrapper
    
    def load_json_file(self, file_path):
        """Загрузка JSON файла"""
        self.logger.debug(self.LOG_MESSAGES['reading_file'].format(file_path=file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if isinstance(data, list):
                rows = len(data)
            elif isinstance(data, dict):
                rows = 1
                data = [data]
            else:
                rows = 0
                data = []
            
            self.logger.info(self.LOG_MESSAGES['read_ok'].format(file_path=file_path, rows=rows))
            return data
            
        except Exception as e:
            self.logger.error(self.LOG_MESSAGES['read_fail'].format(file_path=file_path, error=str(e)))
            return []
    
    def flatten_json(self, data, separator='_', prefix=''):
        """Разворачивание вложенных JSON объектов в плоскую структуру"""
        self.logger.debug(self.LOG_MESSAGES['flatten_start'])
        
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                        else:
                            items.append((f"{new_key}{sep}{i}", item))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if isinstance(data, list):
            flattened_data = [flatten_dict(item, prefix, separator) for item in data]
        else:
            flattened_data = [flatten_dict(data, prefix, separator)]
        
        if flattened_data:
            cols_count = len(flattened_data[0].keys())
            self.logger.debug(self.LOG_MESSAGES['flatten_ok'].format(cols=cols_count))
        
        return flattened_data
    
    def filter_fields(self, data, include_fields=None, exclude_fields=None):
        """Фильтрация полей по включению/исключению"""
        if not include_fields and not exclude_fields:
            return data
        
        included_count = len(include_fields) if include_fields else 0
        excluded_count = len(exclude_fields) if exclude_fields else 0
        
        self.logger.debug(self.LOG_MESSAGES['field_filter'].format(
            included=included_count, 
            excluded=excluded_count
        ))
        
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
                    filtered_row[key] = value
            
            filtered_data.append(filtered_row)
        
        return filtered_data
    
    def save_to_excel(self, data, output_path, sheet_name="Data"):
        """Сохранение данных в Excel"""
        self.logger.debug(self.LOG_MESSAGES['excel_write_start'].format(file_path=output_path))
        
        try:
            df = pd.DataFrame(data)
            
            # Создание директории если не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Сохранение в Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            rows, cols = df.shape
            self.processed_rows = rows
            
            self.logger.info(self.LOG_MESSAGES['excel_write_ok'].format(
                file_path=output_path, 
                rows=rows, 
                cols=cols
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(self.LOG_MESSAGES['excel_write_fail'].format(error=str(e)))
            return False
    
    def process(self, input_file, output_file, include_fields=None, exclude_fields=None, sheet_name="Data"):
        """Основная функция обработки"""
        self.start_time = time.time()
        start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        self.logger.info(self.LOG_MESSAGES['start'].format(script=self.config_name, time=start_time_str))
        
        try:
            # Загрузка JSON
            json_data = self.load_json_file(input_file)
            if not json_data:
                return False
            
            # Разворачивание структуры
            flattened_data = self.flatten_json(json_data)
            
            # Фильтрация полей
            filtered_data = self.filter_fields(flattened_data, include_fields, exclude_fields)
            
            # Сохранение в Excel
            success = self.save_to_excel(filtered_data, output_file, sheet_name)
            
            # Итоговое сообщение
            total_time = time.time() - self.start_time
            self.logger.info(self.LOG_MESSAGES['finish'].format(
                script=self.config_name, 
                rows=self.processed_rows, 
                time=total_time
            ))
            
            return success
            
        except Exception as e:
            self.logger.error(self.LOG_MESSAGES['func_error'].format(func="process", error=str(e)))
            return False

# =============================================================================
# УТИЛИТАРНЫЕ ФУНКЦИИ
# =============================================================================

def create_processor_config():
    """Создание конфигурации для различных типов данных"""
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