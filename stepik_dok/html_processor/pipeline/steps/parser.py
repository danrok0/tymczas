from bs4 import BeautifulSoup
import os

def parse_html_files(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Get the title
    title = soup.find('title')
    title_text = title.text.strip() if title else ""

    # Parse all top-level elements in <body>
    body = soup.find('body')
    content = []
    if body:
        for elem in body.children:
            if getattr(elem, 'name', None) is None:
                continue
            if elem.name == 'h1':
                content.append({'type': 'heading', 'text': elem.text.strip()})
            elif elem.name == 'table':
                headers = [th.text.strip() for th in elem.find_all('th')]
                rows = []
                for tr in elem.find_all('tr')[1:]:
                    cells = [td.text.strip() for td in tr.find_all('td')]
                    if cells:
                        row = dict(zip(headers, cells))
                        rows.append(row)
                content.append({'type': 'table', 'headers': headers, 'rows': rows})
            elif elem.name == 'p':
                content.append({'type': 'paragraph', 'text': elem.text.strip()})
            elif elem.name == 'footer':
                content.append({'type': 'footer', 'text': elem.text.strip()})

    return {
        'title': title_text,
        'content': content
    }