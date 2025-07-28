
const fs = require('fs');

function generateTags(text) {
  const commonWords = ['the', 'and', 'of', 'to', 'a', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'as', 'is', 'an', 'that', 'this', 'it', 'be'];
  return text
    .toLowerCase()
    .split(/\W+/)
    .filter(word => word.length > 3 && !commonWords.includes(word))
    .slice(0, 5)
    .map(word => `#${word}`);
}

const categorized = JSON.parse(fs.readFileSync('guardian-categorized.json', 'utf8'));
const allArticles = [];

for (const category in categorized) {
  const entries = categorized[category];
  for (const article of Array.isArray(entries) ? entries : [entries]) {
    article.category = category;
    article.tags = generateTags(article.title + ' ' + article.content);
    allArticles.push(article);
  }
}

fs.writeFileSync('articles.json', JSON.stringify(allArticles, null, 2), 'utf8');
console.log('[✓] File "articles.json" created with tags.');
