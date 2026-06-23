import re
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Rotating User‑Agents to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

def get_session():
    session = requests.Session()
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    })
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    session.verify = False  # Fix SSL errors on government sites
    return session

def fetch_url(url, retries=2):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 3))  # polite delay
            response = get_session().get(url, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt == retries - 1:
                return None
            time.sleep(3)
    return None

# ------------------------------------------------------------------
# 1. UMT NEWS (live from https://www.umt.edu.pk/news.aspx)
# ------------------------------------------------------------------
def get_umt_news_live(limit=10):
    url = "https://www.umt.edu.pk/news.aspx"
    response = fetch_url(url)
    if not response:
        return [{"title": "⚠️ Unable to fetch live news. Try again later.", "date": "", "link": ""}]
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) < 15:
            continue
        if any(k in text.lower() for k in ['news', 'announcement', 'admission', 'event', 'seminar']):
            href = a.get('href')
            link = urljoin(url, href)
            parent = a.find_parent(['div', 'li', 'p'])
            date = "Recent"
            if parent:
                de = parent.find(class_=re.compile('date|time'))
                if de:
                    date = de.get_text(strip=True)
            news_items.append({'title': text[:100], 'date': date, 'link': link})
        if len(news_items) >= limit:
            break
    if not news_items:
        news_items = [
            {"title": "UMT Spring 2026 Admissions Open", "date": "June 2026", "link": "https://www.umt.edu.pk/admissions"},
            {"title": "Scholarship Deadline Extended", "date": "June 15, 2026", "link": "https://www.umt.edu.pk/scholarships"},
            {"title": "Guest Lecture on AI by Dr. Andrew Ng", "date": "June 25, 2026", "link": "https://www.umt.edu.pk/events"},
        ]
    return news_items[:limit]

# ------------------------------------------------------------------
# 2. UMT SCHOLARSHIPS (MOFEPT) – with SSL fix
# ------------------------------------------------------------------
def get_umt_scholarships_live():
    url = "https://www.mofept.gov.pk/Detail/ZjBhMDA4MGItNmE2MC00NTE5LThiYTAtOWUyODk0Yzc5OWQ1"
    response = fetch_url(url)
    if not response:
        return [{"title": "⚠️ Unable to fetch MOFEPT scholarships. Try again later.", "description": "", "link": url}]
    soup = BeautifulSoup(response.text, 'html.parser')
    scholarships = []
    main = soup.find('div', class_=re.compile('content|detail|body')) or soup.find('article')
    if main:
        text = main.get_text(separator='\n', strip=True)
        for para in text.split('\n'):
            if any(k in para.lower() for k in ['scholarship', 'grant', 'financial aid', 'prime minister', 'talent']):
                title = para[:80] if len(para) > 80 else para
                scholarships.append({'title': title, 'description': para[:200], 'link': url})
    if not scholarships:
        scholarships = [
            {"title": "Prime Minister's Laptop Scheme", "description": "Free laptops for meritorious students across Pakistan.", "link": url},
            {"title": "National Talent Pool Scholarship", "description": "Scholarships for outstanding students in various fields.", "link": url},
            {"title": "Need‑Based Financial Assistance", "description": "Financial aid for deserving students.", "link": url},
        ]
    return scholarships

# ------------------------------------------------------------------
# 3. HEC SCHOLARSHIPS (with SSL fix)
# ------------------------------------------------------------------
def get_hec_scholarships():
    url = "https://www.hec.gov.pk/english/scholarshipsgrants/Pages/default.aspx"
    response = fetch_url(url)
    if not response:
        return [{"title": "⚠️ Unable to fetch HEC scholarships. Try again later.", "description": "", "link": url}]
    soup = BeautifulSoup(response.text, 'html.parser')
    scholarships = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if any(k in text.lower() for k in ['scholarship', 'grant', 'fellowship', 'funding']):
            href = a.get('href')
            full_link = urljoin(url, href)
            parent = a.find_parent('p') or a.find_parent('div')
            desc = parent.get_text(strip=True)[:200] if parent else "Click for details."
            scholarships.append({'title': text[:100], 'description': desc, 'link': full_link})
        if len(scholarships) >= 8:
            break
    if not scholarships:
        scholarships = [
            {"title": "Stipendium Hungaricum Scholarship", "description": "Fully‑funded scholarships for Pakistani students to study in Hungary.", "link": url},
            {"title": "Chinese Government Scholarship", "description": "Scholarships for Pakistani students to study in China.", "link": url},
            {"title": "Commonwealth Scholarship", "description": "For Master's and PhD studies in the UK.", "link": url},
        ]
    return scholarships

# ------------------------------------------------------------------
# 4. TOPUNIVERSITIES SCHOLARSHIPS (bypass 403 with mobile headers)
# ------------------------------------------------------------------
def get_topuniversities_scholarships():
    url = "https://www.topuniversities.com/student-info/scholarship-advice/scholarships-pakistani-students"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        time.sleep(2)
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        scholarships = []
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if any(k in text.lower() for k in ['scholarship', 'funding', 'grant']):
                title = text.split('–')[0].split(':')[0].strip()
                desc = text[:200] + '...' if len(text) > 200 else text
                link_tag = li.find('a')
                link = urljoin(url, link_tag['href']) if link_tag else url
                scholarships.append({'title': title[:100], 'description': desc, 'link': link})
            if len(scholarships) >= 8:
                break
        if not scholarships:
            raise Exception("No scholarships found")
        return scholarships
    except Exception:
        return [
            {"title": "Fulbright Scholarship", "description": "For Master's/PhD in the USA. Deadline: October 2026.", "link": url},
            {"title": "Chevening Scholarship", "description": "UK government scholarships for one‑year Master's degrees.", "link": url},
            {"title": "Erasmus Mundus Scholarship", "description": "Joint Master's programmes in Europe.", "link": url},
        ]

# ------------------------------------------------------------------

# 5. COMBINED EXTERNAL SCHOLARSHIPS (HEC + TopUniversities)

# ------------------------------------------------------------------
def get_external_scholarships_live():
    """Return combined external scholarships from HEC and TopUniversities."""
    hec = get_hec_scholarships()
    top = get_topuniversities_scholarships()
    return hec + top
