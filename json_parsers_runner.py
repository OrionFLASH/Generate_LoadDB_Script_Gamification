#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный запускающий скрипт для всех JSON парсеров
Автор: OrionFLASH
Описание: Предоставляет функции для запуска отдельных JSON парсеров или всех сразу.
         Поддерживает как динамический импорт модулей, так и универсальный режим
         через базовый класс JSONToExcelProcessor.
"""

import os
import sys
import importlib.util
from json_to_excel_base import JSONToExcelProcessor, create_processor_config

# =============================================================================
# КОНФИГУРАЦИЯ ПАРСЕРОВ
# =============================================================================

# Словарь с конфигурацией для каждого парсера
# Содержит информацию о модуле, входном и выходном файлах
PARSER_CONFIGS = {
    "leaders_for_admin": {
        "module": "json_parser_leaders_for_admin",  # Имя модуля для динамического импорта
        "input_file": "leaders_for_admin_response.json",  # Имя входного JSON файла
        "output_file": "leaders_for_admin_data.xlsx"  # Имя выходного Excel файла
    },
    "reward": {
        "module": "json_parser_reward", 
        "input_file": "reward_response.json",
        "output_file": "reward_data.xlsx"
    },
    "profile": {
        "module": "json_parser_profile",
        "input_file": "profile_response.json", 
        "output_file": "profile_data.xlsx"
    },
    "news_details": {
        "module": "json_parser_news_details",
        "input_file": "news_details_response.json",
        "output_file": "news_details_data.xlsx"
    },
    "address_book_tn": {
        "module": "json_parser_address_book_tn",
        "input_file": "address_book_tn_response.json",
        "output_file": "address_book_tn_data.xlsx"
    },
    "address_book_dev": {
        "module": "json_parser_address_book_dev",
        "input_file": "address_book_dev_response.json",
        "output_file": "address_book_dev_data.xlsx"
    },
    "orders": {
        "module": "json_parser_orders",
        "input_file": "orders_response.json",
        "output_file": "orders_data.xlsx"
    },
    "news_list": {
        "module": "json_parser_news_list",
        "input_file": "news_list_response.json",
        "output_file": "news_list_data.xlsx"
    },
    "rating_list": {
        "module": "json_parser_rating_list",
        "input_file": "rating_list_response.json",
        "output_file": "rating_list_data.xlsx"
    }
}

# =============================================================================
# ФУНКЦИИ ЗАПУСКА ПАРСЕРОВ
# =============================================================================

def run_single_parser(parser_name):
    """
    Запуск одного парсера через динамический импорт модуля
    
    Импортирует соответствующий модуль и вызывает его основную функцию.
    Используется когда нужно запустить конкретный парсер с его специфической логикой.
    
    Args:
        parser_name (str): Имя парсера из PARSER_CONFIGS
        
    Returns:
        bool: True если парсер выполнен успешно, False в случае ошибки
    """
    # Проверка существования парсера в конфигурации
    if parser_name not in PARSER_CONFIGS:
        print(f"❌ Неизвестный парсер: {parser_name}")
        return False
    
    # Получение конфигурации парсера
    config = PARSER_CONFIGS[parser_name]
    module_name = config["module"]
    
    try:
        # Проверка существования файла модуля
        if os.path.exists(f"{module_name}.py"):
            # Динамический импорт модуля
            spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Запуск основной функции модуля
            result = module.main()
            return result
        else:
            print(f"❌ Файл {module_name}.py не найден")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске {parser_name}: {str(e)}")
        return False

def run_universal_parser(parser_name):
    """
    Универсальный запуск парсера через базовый класс
    
    Использует JSONToExcelProcessor для обработки JSON данных.
    Более надежный способ, так как не зависит от существования отдельных модулей.
    
    Args:
        parser_name (str): Имя парсера из PARSER_CONFIGS
        
    Returns:
        bool: True если парсер выполнен успешно, False в случае ошибки
    """
    # Проверка существования парсера в конфигурации
    if parser_name not in PARSER_CONFIGS:
        print(f"❌ Неизвестный парсер: {parser_name}")
        return False
    
    # Настройка путей к директориям
    # Жестко заданные пути для INPUT и OUTPUT директорий
    input_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"
    output_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"
    
    # Получение конфигурации парсера
    parser_config = PARSER_CONFIGS[parser_name]
    
    # Формирование полных путей к файлам
    input_file = os.path.join(input_dir, parser_config["input_file"])
    output_file = os.path.join(output_dir, parser_config["output_file"])
    
    # Создание процессора с именем парсера и уровнем логирования DEBUG
    processor = JSONToExcelProcessor(parser_name, "DEBUG")
    
    # Получение конфигурации полей для фильтрации
    field_configs = create_processor_config()
    if parser_name in field_configs:
        # Если есть специфическая конфигурация для данного парсера
        config = field_configs[parser_name]
    else:
        # Конфигурация по умолчанию
        config = {"sheet_name": "Data", "include_fields": None, "exclude_fields": None}
    
    # Обработка файла через базовый класс
    success = processor.process(
        input_file=input_file,
        output_file=output_file,
        include_fields=config.get("include_fields"),
        exclude_fields=config.get("exclude_fields"),
        sheet_name=config.get("sheet_name", "Data")
    )
    
    # Вывод результата обработки
    if success:
        print(f"✅ {parser_name}: Обработка завершена успешно")
    else:
        print(f"❌ {parser_name}: Ошибка при обработке")
    
    return success

def run_all_parsers():
    """
    Запуск всех парсеров последовательно
    
    Обрабатывает все парсеры из PARSER_CONFIGS и выводит итоговую статистику.
    Использует универсальный режим для надежности.
    
    Returns:
        dict: Словарь с результатами выполнения каждого парсера
    """
    print("🚀 Запуск всех JSON парсеров...")
    results = {}
    
    # Последовательный запуск всех парсеров
    for parser_name in PARSER_CONFIGS.keys():
        print(f"\n--- Обработка {parser_name} ---")
        results[parser_name] = run_universal_parser(parser_name)
    
    # Формирование и вывод итоговой статистики
    print("\n" + "="*50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*50)
    
    # Подсчет успешных и неуспешных парсеров
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    # Вывод статуса каждого парсера
    for parser_name, success in results.items():
        status = "✅ Успешно" if success else "❌ Ошибка"
        print(f"{parser_name}: {status}")
    
    # Вывод общего результата
    print(f"\nОбщий результат: {success_count}/{total_count} парсеров выполнено успешно")
    
    return results

# =============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# =============================================================================

def main():
    """
    Основная функция для обработки аргументов командной строки
    
    Поддерживает два режима работы:
    - Запуск одного парсера: python script.py <parser_name>
    - Запуск всех парсеров: python script.py all
    
    Выходные коды:
    - 0: успешное выполнение
    - 1: ошибка выполнения
    """
    # Проверка количества аргументов командной строки
    if len(sys.argv) < 2:
        # Вывод справки по использованию
        print("Использование:")
        print(f"  python {sys.argv[0]} <parser_name>  - запуск одного парсера")
        print(f"  python {sys.argv[0]} all            - запуск всех парсеров")
        print("\nДоступные парсеры:")
        
        # Вывод списка доступных парсеров
        for name in PARSER_CONFIGS.keys():
            print(f"  - {name}")
        return
    
    # Получение команды из аргументов командной строки
    command = sys.argv[1].lower()
    
    # Обработка команды
    if command == "all":
        # Запуск всех парсеров
        run_all_parsers()
    elif command in PARSER_CONFIGS:
        # Запуск конкретного парсера
        success = run_universal_parser(command)
        if not success:
            # Выход с кодом ошибки при неудачном выполнении
            sys.exit(1)
    else:
        # Неизвестная команда
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)

# Точка входа в программу
if __name__ == "__main__":
    main() 