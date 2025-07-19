import json
import os
from datetime import datetime
import re

json_path = "economic_news_full.json"
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

with open(json_path, 'r', encoding='utf-8') as f:
    news_items = json.load(f)

def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

existing_titles = set()

for item in news_items:
    try:
        title = item['title'].strip()
        if title in existing_titles:
            continue
        existing_titles.add(title)

        dt = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
        date_str = dt.strftime('%Y-%m-%d')
        slug = slugify(title)[:50]
        filename = f"{date_str}-{slug}.md"
        filepath = os.path.join(posts_dir, filename)

        if os.path.exists(filepath):
            continue

        front_matter = f"""---
layout: post
title: "{title}"
date: {dt.isoformat()}
categories: [news]
tags: {item['tags'] + item['hashtags']}
image: {item['image']}
source: {item['source']}
---

{item['body']}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)

    except Exception as e:
        continue
