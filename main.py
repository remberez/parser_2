import asyncio
import time
import json
from bs4 import BeautifulSoup
import aiohttp

NUMBER_PAGE = 38


async def get_requests(page, session):
    url = f'https://kupalniki-nsk.ru/catalog/zhenskie-kupalniki/page-{page}/'
    async with session.get(url) as r:
        start_request = time.time()
        data = await r.text()
        end_request = time.time()
        print(f'Время запросa: {end_request - start_request}')
        return data


async def main():
    tasks = []
    result = []
    async with aiohttp.ClientSession() as session:
        for page_number in range(1, NUMBER_PAGE + 1):
            task = asyncio.create_task(get_requests(page_number, session))
            tasks.append(task)
        for task in tasks:
            result.append(await task)
    return result


page_list = asyncio.run(main())
result = {}

for page in page_list:
    soup = BeautifulSoup(page, 'lxml')
    page_key = soup.title.text
    result[page_key] = []
    items_row = soup.find_all('div', {'data-entity': 'items-row', 'class': 'row'})

    for item in items_row:
        result[page_key].append({})
        title = item.find('a', class_='product-block__name padding-5-10 padding-5-10').text
        price = item.find('div', class_='product-block__price').text.replace('\xa0', '')
        img = item.find('img')
        link = item.find('a', class_='btn btn-purple btn-buy')
        result[page_key][-1][title.split()[-1]] = title
        result[page_key][-1]['Цена'] = price
        result[page_key][-1]['Фото'] = 'https://kupalniki-nsk.ru/' + img.get('src')
        result[page_key][-1]['Ссылка'] = 'https://kupalniki-nsk.ru/' + link.get('href')

with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(result, file, indent=3, ensure_ascii=False)
