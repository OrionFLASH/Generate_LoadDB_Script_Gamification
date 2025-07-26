#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json_to_excel_base import JSONToExcelProcessor, create_processor_config
import os

def main():
    """Основная функция для обработки JSON данных Profile"""
    
    # Настройка путей
    input_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"
    output_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"
    
    input_file = os.path.join(input_dir, "profile_response.json")
    output_file = os.path.join(output_dir, "profile_data.xlsx")
    
    # Создание процессора
    processor = JSONToExcelProcessor("profile", "DEBUG")
    
    # Получение конфигурации
    config = create_processor_config()["profile"]
    
    # Обработка файла
    success = processor.process(
        input_file=input_file,
        output_file=output_file,
        include_fields=config["include_fields"],
        exclude_fields=config["exclude_fields"],
        sheet_name=config["sheet_name"]
    )
    
    if success:
        print(f"✅ Обработка завершена успешно: {output_file}")
    else:
        print("❌ Ошибка при обработке файла")
    
    return success

if __name__ == "__main__":
    main() 