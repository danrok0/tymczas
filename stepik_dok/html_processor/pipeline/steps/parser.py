from bs4 import BeautifulSoup
import os

def parse_html_files(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table')
    if not table:
        raise ValueError("No table found in HTML")

    headers = [th.text.strip() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = [td.text.strip() for td in tr.find_all('td')]
        if cells:
            row = dict(zip(headers, cells))
            rows.append(row)
    return rows