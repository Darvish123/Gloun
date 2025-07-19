import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
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
        link = urljoin(url, a_tag['href'])
        
        # ورود به لینک خبر
        article_res = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(article_res.content, 'html.parser')
        
        # متن خبر
        content_div = article_soup.select_one('div.ArticleBody-articleBody')
        body_text = content_div.get_text(strip=True) if content_div else ''
        
        # عکس خبر
        img_tag = article_soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else ''
        
        # دسته‌بندی خبر
        category_tag = article_soup.find('meta', property='article:section')
        category = category_tag['content'] if category_tag else 'Uncategorized'

        results.append({
            'title': title,
            'link': link,
            'body': body_text,
            'image': image_url,
            'category': category,
            'hashtags': generate_hashtags(title + ' ' + body_text)
        })

    return results

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    news = scrape_cnbc()
    save_data(news)
    print(f"{len(news)} خبر ذخیره شد.")

