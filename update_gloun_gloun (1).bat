
@echo off
cd /d C:\Users\ModernSystem\Gloun\Gloun
echo [1] Running scraper...
node guardian-stealth-autopush.js

echo [2] Converting to articles.json...
node convert_to_articles.js

echo [3] Committing and pushing to GitHub...
git add articles.json
git commit -m "Auto update articles.json"
git push origin main

echo [✅] Done!
pause
