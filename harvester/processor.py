import re
from datetime import datetime
from bs4 import BeautifulSoup


def clean_title(s):
    if not s or not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s[:500] if len(s) > 500 else s


def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Предполагаем формат вроде "2024-05-15" или "May 15, 2024"
        for fmt in ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
    except:
        pass
    return None


def extract_conference_data(html_content):
    if not html_content:
        return {}
    soup = BeautifulSoup(html_content, 'html.parser')
    
    data = {}
    
    # Title
    title_elem = soup.find('h1') or soup.find('title')
    if title_elem:
        data['title'] = clean_title(title_elem.get_text())
    
    # Event date
    event_date_elem = soup.find(text=re.compile(r'When:', re.I))
    if event_date_elem:
        parent = event_date_elem.parent
        date_text = parent.get_text().replace('When:', '').strip()
        data['event_date'] = parse_date(date_text)
    
    # Location
    location_elem = soup.find(text=re.compile(r'Where:', re.I))
    if location_elem:
        parent = location_elem.parent
        data['location'] = parent.get_text().replace('Where:', '').strip()
    
    # Deadline
    deadline_elem = soup.find(text=re.compile(r'Deadline:', re.I))
    if deadline_elem:
        parent = deadline_elem.parent
        deadline_text = parent.get_text().replace('Deadline:', '').strip()
        data['deadline'] = parse_date(deadline_text)
    
    # URL
    url_elem = soup.find('a', href=re.compile(r'http'))
    if url_elem:
        data['url'] = url_elem['href']
    
    return data


def extract_keywords_from_html(html_content, max_words=10):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    
    words = []
    
    # From title
    title = soup.find('h1') or soup.find('title')
    if title:
        t = clean_title(title.get_text())
        for w in t.split():
            w = re.sub(r"[^\w\-]", "", w)
            if len(w) > 2 and w.lower() not in ("the", "and", "for", "with", "from", "conference", "symposium"):
                words.append(w[:50])
                if len(words) >= max_words:
                    break
    
    # From description or abstract
    desc = soup.find('div', class_=re.compile(r'desc|abstract', re.I)) or soup.find('p')
    if desc:
        text = desc.get_text()
        for w in text.split():
            w = re.sub(r"[^\w\-]", "", w)
            if len(w) > 2 and w.lower() not in ("the", "and", "for", "with", "from"):
                words.append(w[:50])
                if len(words) >= max_words:
                    break
    
    return ", ".join(words[:max_words]) if words else None
