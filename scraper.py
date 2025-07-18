
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import re
from urllib.parse import urljoin

DATA_FILE = 'data.json'

def generate_hashtags(text, count=5):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return ['#' + word[0] for word in sorted_words[:count]]

def scrape_cnbc():
    url = 'https://www.cnbc.com/economy/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    cards = soup.select('div.Card-standardBreakerCard')
    results = []

    for card in cards[:5]:
        a_tag = card.find('a', class_='Card-title')
        if not a_tag:
            continue

        title = a_tag.get_text(strip=True)
        link = a_tag['href']
        if not link.startswith('http'):
            link = urljoin('https://www.cnbc.com', link)

        try:
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.content, 'html.parser')
            paragraphs = article_soup.select('div.ArticleBody-articleBody p')
            body = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
            img_tag = article_soup.find('meta', property='og:image')
            image = img_tag['content'] if img_tag else ''
            hashtags = generate_hashtags(title + ' ' + body)
            results.append({
                'title': title,
                'link': link,
                'body': body,
                'image': image,
                'hashtags': hashtags,
                'tags': ['economy'],
                'source': 'CNBC',
                'date': datetime.now(timezone.utc).isoformat()
            })
        except:
            continue
    return results

def scrape_reuters():
    url = 'https://www.reuters.com/business/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    articles = soup.select('article.story')
    results = []

    for article in articles[:5]:
        a_tag = article.find('a')
        if not a_tag or not a_tag.get('href'):
            continue

        link = 'https://www.reuters.com' + a_tag['href']
        title = a_tag.get_text(strip=True)

        try:
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.content, 'html.parser')
            paragraphs = article_soup.select('div.article-body__content__17Yit p')
            body = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
            img_tag = article_soup.find('meta', property='og:image')
            image = img_tag['content'] if img_tag else ''
            hashtags = generate_hashtags(title + ' ' + body)
            results.append({
                'title': title,
                'link': link,
                'body': body,
                'image': image,
                'hashtags': hashtags,
                'tags': ['business'],
                'source': 'Reuters',
                'date': datetime.now(timezone.utc).isoformat()
            })
        except:
            continue
    return results

def scrape_marketwatch():
    url = 'https://www.marketwatch.com/economy-politics'
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    articles = soup.select('div.article__content')
    results = []

    for article in articles[:5]:
        a_tag = article.find('a')
        if not a_tag:
            continue

        link = a_tag['href']
        title = a_tag.get_text(strip=True)

        try:
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.content, 'html.parser')
            paragraphs = article_soup.select('div.article__body p')
            body = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
            img_tag = article_soup.find('meta', property='og:image')
            image = img_tag['content'] if img_tag else ''
            hashtags = generate_hashtags(title + ' ' + body)
            results.append({
                'title': title,
                'link': link,
                'body': body,
                'image': image,
                'hashtags': hashtags,
                'tags': ['politics', 'economy'],
                'source': 'MarketWatch',
                'date': datetime.now(timezone.utc).isoformat()
            })
        except:
            continue
    return results

def run_all():
    all_news = scrape_cnbc() + scrape_reuters() + scrape_marketwatch()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)
    print(f"✅ Done. {len(all_news)} news items saved to {DATA_FILE}")

if __name__ == '__main__':
    run_all()
