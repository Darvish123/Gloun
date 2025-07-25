
// guardian-stealth-ultimate.js
const fs = require('fs');
const { execSync } = require('child_process');

let existing = {};
const filePath = 'guardian-categorized.json';
if (fs.existsSync(filePath)) {
  try {
    const raw = fs.readFileSync(filePath);
    const json = JSON.parse(raw);
    for (const section of Object.keys(json)) {
      for (const article of json[section]) {
        existing[article.url] = true;
      }
    }
  } catch (e) {
    console.warn("⚠️ Failed to read existing JSON. Starting fresh.");
  }
}

const { chromium } = require('playwright');

const urls = [
  "https://www.theguardian.com/world",
  "https://www.theguardian.com/politics",
  "https://www.theguardian.com/environment",
  "https://www.theguardian.com/business",
  "https://www.theguardian.com/sport"
];

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    proxy: { server: 'socks5://127.0.0.1:9150' }
  });

  const context = await browser.newContext({
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    locale: 'en-US',
    viewport: { width: 1366, height: 768 },
    timezoneId: 'Europe/London',
    permissions: ['geolocation'],
  });

  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5]
    });
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false
    });
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      if (parameter === 37445) return 'Intel Inc.';
      if (parameter === 37446) return 'Intel Iris OpenGL Engine';
      return getParameter(parameter);
    };
  });

  const page = await context.newPage();
  const scraped = {};

  for (const baseUrl of urls) {
    console.log("🔍 Scanning:", baseUrl);
    try {
      await page.goto(baseUrl, { timeout: 60000, waitUntil: 'domcontentloaded' });
      await page.waitForSelector('a[data-link-name="article"]');

      const articleLinks = await page.$$eval('a[data-link-name="article"]', links =>
        Array.from(new Set(links.map(link => link.href).filter(h => h.includes('/202')))).slice(0, 10)
      );

      for (const link of articleLinks) {
        console.log("➡️ Visiting:", link);
        try {
          await page.goto(link, { timeout: 60000, waitUntil: 'domcontentloaded' });
          await sleep(800);

          const title = await page.$eval('h1', el => el.innerText).catch(() => '');
          const content = await page.$$eval('div.article-body-commercial-selector p', els =>
            els.map(e => e.innerText).join('\n')).catch(() => '');
          const author = await page.$eval('meta[name="author"]', el => el.content).catch(() => 'unknown');
          const category = await page.$eval('meta[property="article:section"]', el => el.content).catch(() => 'unknown');
          const tags = await page.$$eval('a[data-link-name="article keyword"]', els => els.map(e => e.innerText)).catch(() => []);

          if (!scraped[category]) scraped[category] = [];
          if (!existing[link]) {
            scraped[category].push({ title, url: link, author, tags, content });
            existing[link] = true;
          }

          console.log(`✅ Scraped: ${title}`);
          fs.writeFileSync('guardian-categorized.json', JSON.stringify(scraped, null, 2));
        } catch (err) {
          console.warn(`⚠️ Failed to scrape ${link}: ${err.message}`);
        }
      }
    } catch (err) {
      console.error("❌ Error visiting base URL:", err.message);
    }
  }

  await browser.close();
  console.log("✅ Done. Output saved to guardian-categorized.json");

  // 🔁 Auto Git Push
  try {
    if (fs.existsSync("guardian-categorized.json")) {
      execSync('git add guardian-categorized.json', { stdio: 'inherit' });
      execSync(`git commit -m "Auto-update: ${new Date().toISOString()}"`, { stdio: 'inherit' });
      execSync('git push origin main', { stdio: 'inherit' });
      console.log("🚀 Auto-push to GitHub completed.");
    } else {
      console.warn("⚠️ File guardian-categorized.json not found. Skipping Git step.");
    }
  } catch (e) {
    console.error("❌ Git push failed:", e.message);
  }

})();
