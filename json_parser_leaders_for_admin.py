#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Индивидуальный парсер для обработки JSON данных LeadersForAdmin
Автор: OrionFLASH
Описание: Специализированный скрипт для обработки данных об участниках турнира.
         Использует базовый класс JSONToExcelProcessor для разворачивания JSON
         и сохранения в Excel с настройками для данного типа данных.
"""

from json_to_excel_base import JSONToExcelProcessor, create_processor_config
import os

def main():
    """
    Основная функция для обработки данных LeadersForAdmin
    
    Загружает JSON файл с данными об участниках турнира, разворачивает
    вложенные структуры и сохраняет в Excel с применением специфических
    фильтров полей.
    
    Returns:
        bool: True если обработка успешна, False в случае ошибки
    """
    # Настройка путей к директориям
    # Жестко заданные пути для INPUT и OUTPUT директорий
    input_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/INPUT"
    output_dir = r"/Users/orionflash/Desktop/MyProject/Gen_Load_Game_Script/OUTPUT"
    
    # Формирование имен файлов
    input_file = os.path.join(input_dir, "leaders_for_admin_response.json")  # Входной JSON файл
    output_file = os.path.join(output_dir, "leaders_for_admin_data.xlsx")    # Выходной Excel файл
    
    # Создание процессора с именем "leaders_for_admin" и уровнем логирования DEBUG
    processor = JSONToExcelProcessor("leaders_for_admin", "DEBUG")
    
    # Получение конфигурации для данного типа данных
    # Включает настройки листа, включаемые и исключаемые поля
    config = create_processor_config()["leaders_for_admin"]
    
    # Обработка файла с применением конфигурации
    success = processor.process(
        input_file=input_file,                    # Путь к входному JSON файлу
        output_file=output_file,                  # Путь к выходному Excel файлу
        include_fields=config["include_fields"],  # Список полей для включения
        exclude_fields=config["exclude_fields"],  # Список полей для исключения
        sheet_name=config["sheet_name"]           # Имя листа в Excel
    )
    
    # Вывод результата обработки
    if success:
        print(f"✅ Обработка завершена успешно: {output_file}")
    else:
        print("❌ Ошибка при обработке файла")
    
    return success

# Точка входа в программу
if __name__ == "__main__":
    main() 