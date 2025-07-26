#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Универсальный запускающий скрипт для всех JSON парсеров
"""

import os
import sys
import importlib.util
from json_to_excel_base import JSONToExcelProcessor, create_processor_config

# Настройки
PARSER_CONFIGS = {
    "leaders_for_admin": {
        "module": "json_parser_leaders_for_admin",
        "input_file": "leaders_for_admin_response.json",
        "output_file": "leaders_for_admin_data.xlsx"
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

def run_single_parser(parser_name):
    """Запуск одного парсера"""
    if parser_name not in PARSER_CONFIGS:
        print(f"❌ Неизвестный парсер: {parser_name}")
        return False
    
    config = PARSER_CONFIGS[parser_name]
    module_name = config["module"]
    
    try:
        # Динамический импорт модуля
        if os.path.exists(f"{module_name}.py"):
            spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Запуск основной функции
            result = module.main()
            return result
        else:
            print(f"❌ Файл {module_name}.py не найден")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске {parser_name}: {str(e)}")
        return False

def run_universal_parser(parser_name):
    """Универсальный запуск парсера через базовый класс"""
    if parser_name not in PARSER_CONFIGS:
        print(f"❌ Неизвестный парсер: {parser_name}")
        return False
    
    # Настройка путей
    input_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"
    output_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"
    
    parser_config = PARSER_CONFIGS[parser_name]
    input_file = os.path.join(input_dir, parser_config["input_file"])
    output_file = os.path.join(output_dir, parser_config["output_file"])
    
    # Создание процессора
    processor = JSONToExcelProcessor(parser_name, "DEBUG")
    
    # Получение конфигурации полей
    field_configs = create_processor_config()
    if parser_name in field_configs:
        config = field_configs[parser_name]
    else:
        config = {"sheet_name": "Data", "include_fields": None, "exclude_fields": None}
    
    # Обработка файла
    success = processor.process(
        input_file=input_file,
        output_file=output_file,
        include_fields=config.get("include_fields"),
        exclude_fields=config.get("exclude_fields"),
        sheet_name=config.get("sheet_name", "Data")
    )
    
    if success:
        print(f"✅ {parser_name}: Обработка завершена успешно")
    else:
        print(f"❌ {parser_name}: Ошибка при обработке")
    
    return success

def run_all_parsers():
    """Запуск всех парсеров"""
    print("🚀 Запуск всех JSON парсеров...")
    results = {}
    
    for parser_name in PARSER_CONFIGS.keys():
        print(f"\n--- Обработка {parser_name} ---")
        results[parser_name] = run_universal_parser(parser_name)
    
    # Итоговая статистика
    print("\n" + "="*50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*50)
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for parser_name, success in results.items():
        status = "✅ Успешно" if success else "❌ Ошибка"
        print(f"{parser_name}: {status}")
    
    print(f"\nОбщий результат: {success_count}/{total_count} парсеров выполнено успешно")
    
    return results

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  python {sys.argv[0]} <parser_name>  - запуск одного парсера")
        print(f"  python {sys.argv[0]} all            - запуск всех парсеров")
        print("\nДоступные парсеры:")
        for name in PARSER_CONFIGS.keys():
            print(f"  - {name}")
        return
    
    command = sys.argv[1].lower()
    
    if command == "all":
        run_all_parsers()
    elif command in PARSER_CONFIGS:
        success = run_universal_parser(command)
        if not success:
            sys.exit(1)
    else:
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 