# Исправленная версия main.py с правильными f-строками
# Основная проблема была в том, что в f-строках Python нужно использовать двойные фигурные скобки для экранирования

# Конфигурация для тестирования
FUNCTION_CONFIGS = {
    "rating_list": {
        "business_blocks": [
            "KMKKSB",      # Клиентский менеджер крупнейшего, крупного и среднего бизнеса
            "MNS",         # Менеджер нефинансовых сервисов
            "SERVICEMEN",  # Сервис-менеджер
            "KMFACTORING", # Специалист СберФакторинга
            "KMSB1",       # Менеджер СберПервый
            "IMUB",        # Инвестиционный менеджер Управления Благосостояния
            "RNUB",        # Руководитель направления управления благосостояния
            "RSB1"         # Руководитель СберПервый
        ],
        "time_periods": [
            "ACTIVESEASON",  # Базовый параметр - активный сезон
            "SEASON_2025_1",  # Сезон 2025-1
            "SEASON_2024",  # Сезон 2024
            "ALLTHETIME"  # Все время
        ],
        "processing_options": {
            "max_participants_per_page": 100,
            "remove_photo_data": True,
            "skip_empty_pages": True
        },
        "delay_between_requests": 5,
        "retry_count": 3
    }
}

def generate_rating_list_script_fixed(data_list=None):
    """
    Генерирует JavaScript скрипт для выгрузки рейтинга участников по бизнес-блокам и периодам времени
    """
    # Получаем конфигурацию для rating_list
    config = FUNCTION_CONFIGS["rating_list"]
    
    # Получаем бизнес-блоки и периоды времени из конфигурации
    business_blocks = config.get('business_blocks', [])
    time_periods = config.get('time_periods', [])
    
    # Получаем параметры обработки
    max_participants_per_page = config.get('processing_options', {}).get('max_participants_per_page', 100)
    delay = config.get('delay_between_requests', 5)
    max_retries = config.get('retry_count', 3)
    remove_photo_data = config.get('processing_options', {}).get('remove_photo_data', True)
    skip_empty_pages = config.get('processing_options', {}).get('skip_empty_pages', True)
    
    # Создаем JavaScript код с правильными f-строками
    script = f'''
// ==UserScript==
// Скрипт для DevTools. Выгрузка рейтинга участников по бизнес-блокам и периодам времени с пагинацией
// Вариант: SIGMA
// API: https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/ratinglist
// Параметры: divisionLevel=BANK
// Бизнес-блоки: {", ".join(business_blocks)}
// Периоды времени: {", ".join(time_periods)}
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

  function extractParticipantsCount(data) {{
    try {{
      // Пытаемся извлечь количество участников из поля contestants (например: "1 557 участников по стране")
      if (data?.body?.rating?.contestants) {{
        const contestantsText = data.body.rating.contestants;
        const match = contestantsText.match(/(\\d+(?:\\s*\\d+)*)/);
        if (match) {{
          // Убираем пробелы и преобразуем в число
          const numberStr = match[1].replace(/\\s/g, '');
          const count = parseInt(numberStr, 10);
          if (!isNaN(count)) {{
            return count;
          }}
        }}
      }}
      
      // Пытаемся извлечь количество участников из различных возможных мест в ответе
      if (data?.body?.totalCount !== undefined) {{
        return data.body.totalCount;
      }} else if (data?.body?.participantsCount !== undefined) {{
        return data.body.participantsCount;
      }} else if (data?.body?.count !== undefined) {{
        return data.body.count;
      }} else if (data?.totalCount !== undefined) {{
        return data.totalCount;
      }} else if (data?.participantsCount !== undefined) {{
        return data.participantsCount;
      }} else if (data?.count !== undefined) {{
        return data.count;
      }}
      
      // Если не нашли явное количество, считаем по участникам на текущей странице
      const participants = data?.body?.participants || data?.body?.data || data?.participants || data?.data || [];
      return participants.length;
    }} catch (e) {{
      console.error('Ошибка при извлечении количества участников:', e);
      return 0;
    }}
  }}

  function extractParticipants(data) {{
    try {{
      // Пытаемся извлечь участников из поля leaders в структуре rating
      if (data?.body?.rating?.leaders && Array.isArray(data.body.rating.leaders)) {{
        return data.body.rating.leaders;
      }}
      
      // Пытаемся извлечь участников из различных возможных мест в ответе
      if (data?.body?.participants && Array.isArray(data.body.participants)) {{
        return data.body.participants;
      }} else if (data?.body?.data && Array.isArray(data.body.data)) {{
        return data.body.data;
      }} else if (data?.participants && Array.isArray(data.participants)) {{
        return data.participants;
      }} else if (data?.data && Array.isArray(data.data)) {{
        return data.data;
      }} else if (Array.isArray(data?.body)) {{
        return data.body;
      }} else if (Array.isArray(data)) {{
        return data;
      }}
      return [];
    }} catch (e) {{
      console.error('Ошибка при извлечении участников:', e);
      return [];
    }}
  }}

  async function fetchWithRetry(url, options, maxRetries = {max_retries}, timeout = 30000) {{
    for (let attempt = 1; attempt <= maxRetries; attempt++) {{
      try {{
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        const response = await fetch(url, {{ ...options, signal: controller.signal }});
        clearTimeout(id);
        return response;
      }} catch (e) {{
        if (attempt === maxRetries) throw e;
        console.log(`🔄 Попытка ${{attempt}}/${{maxRetries}} не удалась, повторяем через ${{attempt}} сек...`);
        await new Promise(r => setTimeout(r, 1000 * attempt));
      }}
    }}
  }}

  const businessBlocks = {business_blocks};
  const timePeriods = {time_periods};
  const BASE_URL = 'https://salesheroes.sberbank.ru/bo/rmkib.gamification/api/v1/ratinglist';
  const DIVISION_LEVEL = 'BANK';
  const results = {{}};
  let totalParticipants = 0;
  let processed = 0, skipped = 0, errors = 0;

  console.log(`🚀 Начинаем выгрузку рейтинга для ${{businessBlocks.length}} бизнес-блоков и ${{timePeriods.length}} периодов времени`);
  console.log(`📊 Максимум участников на страницу: {max_participants_per_page}`);
  console.log(`⏱️ Задержка между запросами: {delay} сек`);
  console.log(`🔄 Максимум попыток при ошибке: {max_retries}`);

  // Обрабатываем все комбинации бизнес-блоков и периодов времени
  let combinationIndex = 0;
  const totalCombinations = businessBlocks.length * timePeriods.length;

  for (let businessBlockIndex = 0; businessBlockIndex < businessBlocks.length; businessBlockIndex++) {{
    const businessBlock = businessBlocks[businessBlockIndex];
    
    for (let timePeriodIndex = 0; timePeriodIndex < timePeriods.length; timePeriodIndex++) {{
      const timePeriod = timePeriods[timePeriodIndex];
      combinationIndex++;
      
      console.log(`\\n🔍 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}}`);
      
      try {{
        // Первый запрос для получения информации о количестве участников
        console.log(`📄 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Запрос страницы 1`);
        const firstUrl = `${{BASE_URL}}?divisionLevel=${{DIVISION_LEVEL}}&timePeriod=${{timePeriod}}&pageNum=1&businessBlock=${{businessBlock}}`;
        console.log(`🔗 URL: ${{firstUrl}}`);
      
        const firstResp = await fetchWithRetry(firstUrl, {{
          headers: {{ 
            'Accept': '*/*',
            'Accept-Language': 'ru',
            'Cookie': document.cookie,
            'User-Agent': navigator.userAgent,
            'Referer': 'https://salesheroes.sberbank.ru/rating'
          }},
          credentials: 'include'
        }});
      
        if (!firstResp.ok) {{
          console.error(`❌ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - HTTP ошибка: ${{firstResp.status}}`);
          errors++;
          continue;
        }}
      
        const firstData = await firstResp.json();
        console.log(`📊 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Получен ответ, статус: ${{firstResp.status}}`);
      
        // Извлекаем количество участников
        const participantsCount = extractParticipantsCount(firstData);
        const contestantsText = firstData?.body?.rating?.contestants || 'не указано';
        console.log(`👥 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Участников: ${{participantsCount}} (из поля: "${{contestantsText}}")`);
      
        if (participantsCount === 0) {{
          console.log(`⏭️ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Пропускаем (нет участников или неверный формат данных)`);
          skipped++;
          continue;
        }}
      
        // Вычисляем количество страниц (делим на max_participants_per_page с округлением вверх)
        const maxParticipantsPerPage = {max_participants_per_page};
        const pagesCount = Math.ceil(participantsCount / maxParticipantsPerPage);
        console.log(`📊 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Страниц для запроса: ${{pagesCount}} (участников: ${{participantsCount}}, по ${{maxParticipantsPerPage}} на страницу)`);
      
        // Сохраняем первый запрос с ключом, включающим период времени
        const resultKey = `${{businessBlock}}_${{timePeriod}}`;
        results[resultKey] = [firstData];
        const firstParticipantsCount = extractParticipants(firstData).length;
        totalParticipants += firstParticipantsCount;
        console.log(`📊 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Участников на странице 1: ${{firstParticipantsCount}}`);
      
        // Отладочная информация о структуре данных
        if (firstParticipantsCount === 0 && participantsCount > 0) {{
          console.log(`🔍 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Отладка структуры данных:`);
          console.log(`  - body: ${{!!firstData?.body}}`);
          console.log(`  - rating: ${{!!firstData?.body?.rating}}`);
          console.log(`  - contestants: ${{firstData?.body?.rating?.contestants || 'undefined'}}`);
          console.log(`  - leaders: ${{!!firstData?.body?.rating?.leaders}}`);
          console.log(`  - leaders.length: ${{firstData?.body?.rating?.leaders?.length || 'undefined'}}`);
          console.log(`  - participants: ${{!!firstData?.body?.participants}}`);
          console.log(`  - data: ${{!!firstData?.body?.data}}`);
          console.log(`  - participants.length: ${{firstData?.body?.participants?.length || 'undefined'}}`);
          console.log(`  - data.length: ${{firstData?.body?.data?.length || 'undefined'}}`);
        }}
      
        // Запрашиваем дополнительные страницы, если нужно
        if (pagesCount > 1) {{
          for (let page = 2; page <= pagesCount; page++) {{
            try {{
              console.log(`📄 [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Запрос страницы ${{page}}/${{pagesCount}}`);
              const pageUrl = `${{BASE_URL}}?divisionLevel=${{DIVISION_LEVEL}}&timePeriod=${{timePeriod}}&pageNum=${{page}}&businessBlock=${{businessBlock}}`;
            
              const pageResp = await fetchWithRetry(pageUrl, {{
                headers: {{ 
                  'Accept': '*/*',
                  'Accept-Language': 'ru',
                  'Cookie': document.cookie,
                  'User-Agent': navigator.userAgent,
                  'Referer': 'https://salesheroes.sberbank.ru/rating'
                }},
                credentials: 'include'
              }});
            
              if (!pageResp.ok) {{
                console.error(`❌ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Страница ${{page}} - HTTP ошибка: ${{pageResp.status}}`);
                continue;
              }}
            
              const pageData = await pageResp.json();
              const pageParticipantsCount = extractParticipants(pageData).length;
            
              // Пропускаем пустые страницы если это включено в настройках
              if ({str(skip_empty_pages).lower()} && pageParticipantsCount === 0) {{
                console.log(`⏭️ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Страница ${{page}}/${{pagesCount}} - Пропускаем (пустая страница)`);
                continue;
              }}
            
              results[resultKey].push(pageData);
              totalParticipants += pageParticipantsCount;
              console.log(`✅ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Страница ${{page}}/${{pagesCount}} - Успешно, участников: ${{pageParticipantsCount}}`);
            
              // Задержка между ответом и следующим запросом страницы
              if (page < pagesCount) {{
                console.log(`⏱️ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Ожидание {delay} сек перед следующей страницей...`);
                await new Promise(resolve => setTimeout(resolve, {delay} * 1000));
              }}
            }} catch (pageError) {{
              console.error(`❌ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Страница ${{page}} - Ошибка:`, pageError);
            }}
          }}
        }}
      
        console.log(`✅ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Завершен, всего страниц: ${{results[resultKey].length}}`);
        processed++;
      
      }} catch (e) {{
        console.error(`❌ [${{combinationIndex}}/${{totalCombinations}}] Бизнес-блок: ${{businessBlock}}, Период: ${{timePeriod}} - Критическая ошибка:`, e);
        errors++;
      }}
    
      // Задержка между комбинациями
      if (combinationIndex < totalCombinations) {{
        console.log(`⏱️ [${{combinationIndex}}/${{totalCombinations}}] Ожидание {delay} сек перед следующей комбинацией...`);
        await new Promise(resolve => setTimeout(resolve, {delay} * 1000));
      }}
    }}
  }}

  // Удаляем photoData только если это включено в настройках
  if ({str(remove_photo_data).lower()}) {{
    console.log('\\n📦 Удаляем photoData...');
    removePhotoData(results);
  }} else {{
    console.log('\\n📦 Удаление photoData отключено в настройках');
  }}

  // Сохраняем результаты
  const ts = getTimestamp();
  const blob = new Blob([JSON.stringify(results, null, 2)], {{ type: 'application/json' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `rating_list_SIGMA_${{ts}}.json`;
  a.click();
  
  console.log(`\\n🏁 Обработка завершена!`);
  console.log(`📊 Итоговая статистика:`);
  console.log(`  - Бизнес-блоков обработано: ${{processed}}`);
  console.log(`  - Бизнес-блоков пропущено: ${{skipped}}`);
  console.log(`  - Ошибок: ${{errors}}`);
  console.log(`  - Всего участников: ${{totalParticipants}}`);
  console.log(`  - Файл скачан: rating_list_SIGMA_${{ts}}.json`);
  
  // Выводим детальную информацию по каждому бизнес-блоку
  console.log(`\\n📋 Детальная информация по бизнес-блокам:`);
  Object.keys(results).forEach((businessBlock, index) => {{
    const pagesCount = results[businessBlock].length;
    const totalBlockParticipants = results[businessBlock].reduce((sum, page) => {{
      return sum + extractParticipants(page).length;
    }}, 0);
    console.log(`  ${{index + 1}}. ${{businessBlock}}: ${{pagesCount}} страниц, ${{totalBlockParticipants}} участников`);
  }});
}})();
'''
    
    return script

# Тестируем исправленную функцию
if __name__ == "__main__":
    script = generate_rating_list_script_fixed()
    # Сохраняем только JavaScript код в файл
    with open('test_script.js', 'w', encoding='utf-8') as f:
        f.write(script)
    print("Исправленный скрипт сгенерирован успешно!")
    print("Длина скрипта:", len(script))
    print("Скрипт сохранен в test_script.js")
