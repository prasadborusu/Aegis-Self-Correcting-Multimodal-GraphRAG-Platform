import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

(async () => {
  const videoDir = path.resolve('d:/rag/recordings');
  if (!fs.existsSync(videoDir)) {
    fs.mkdirSync(videoDir, { recursive: true });
  }

  console.log('[*] Launching Chromium browser with video recording enabled...');
  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1280, height: 720 },
    },
    viewport: { width: 1280, height: 720 },
  });

  const page = await context.newPage();

  // Test target URL (try port 5174 first, fallback to 5173)
  let appUrl = 'http://localhost:5174';
  try {
    const res = await page.goto(appUrl, { timeout: 3000 });
    if (!res || !res.ok()) throw new Error('Not ok');
  } catch {
    appUrl = 'http://localhost:5173';
    await page.goto(appUrl, { waitUntil: 'networkidle' });
  }

  console.log(`[*] Successfully loaded Aegis at ${appUrl}`);
  await delay(2000);

  // 1. SCENE: Dashboard Walkthrough
  console.log('[*] Scene 1: Dashboard Overview');
  // Click Dashboard tab if not already active
  const dashboardTab = await page.$('text=Dashboard');
  if (dashboardTab) await dashboardTab.click();
  await delay(2500);

  // Scroll down slightly to show metrics and scroll back up
  await page.mouse.wheel(0, 200);
  await delay(1500);
  await page.mouse.wheel(0, -200);
  await delay(1500);

  // 2. SCENE: Documents Management
  console.log('[*] Scene 2: Documents Tab');
  const docsTab = await page.$('text=Documents');
  if (docsTab) await docsTab.click();
  await delay(2500);

  // Scroll through uploaded documents
  await page.mouse.wheel(0, 300);
  await delay(2000);
  await page.mouse.wheel(0, -300);
  await delay(1500);

  // 3. SCENE: Ask Aegis & Interactive Factual Grounding
  console.log('[*] Scene 3: Ask Aegis Query Workspace');
  const askTab = await page.$('text=Ask Aegis');
  if (askTab) await askTab.click();
  await delay(2000);

  // Type a greeting: "hlo"
  console.log('[*] Testing colloquial greeting "hlo"...');
  const input = await page.$('input[placeholder*="Ask a question"]');
  if (input) {
    await input.fill('hlo');
    await delay(800);
    const askBtn = await page.$('button:has-text("Ask")');
    if (askBtn) await askBtn.click();
    await delay(3500);
  }

  // Click a suggested chip: "What is Aegis and how does it prevent hallucinations?"
  console.log('[*] Testing suggested chip query...');
  const chip = await page.$('button:has-text("What is Aegis and how does it prevent hallucinations?")');
  if (chip) {
    await chip.click();
    await delay(1000);
    const askBtn = await page.$('button:has-text("Ask")');
    if (askBtn) await askBtn.click();
    await delay(4000);
  }

  // Ask document-specific query: Technical skills
  console.log('[*] Testing document query: Technical Skills in resume...');
  if (input) {
    await input.fill('What technical skills are listed in Durga Prasad resume?');
    await delay(1000);
    const askBtn = await page.$('button:has-text("Ask")');
    if (askBtn) await askBtn.click();
    await delay(4500);
  }

  // Open "How Aegis reached this answer >" reasoning trace modal
  console.log('[*] Opening reasoning trace modal...');
  const traceLinks = await page.$$('text=How Aegis reached this answer');
  if (traceLinks.length > 0) {
    await traceLinks[traceLinks.length - 1].click();
    await delay(3000);
    // Close modal
    const closeBtn = await page.$('button:has(svg.lucide-x)');
    if (closeBtn) await closeBtn.click();
    await delay(1500);
  }

  // Open a citation context drawer
  console.log('[*] Inspecting evidence citation...');
  const citationButtons = await page.$$('button:has(svg.lucide-file-text)');
  if (citationButtons.length > 0) {
    await citationButtons[citationButtons.length - 1].click();
    await delay(3000);
    const closeBtn = await page.$('button:has(svg.lucide-x)');
    if (closeBtn) await closeBtn.click();
    await delay(1500);
  }

  // Final overview pause
  console.log('[*] Finalizing recording...');
  await delay(2000);

  // Close page and context to flush video to disk
  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();

  if (video) {
    const videoPath = await video.path();
    const finalPath = path.resolve('d:/rag/recordings/aegis_demo_walkthrough.webm');
    if (fs.existsSync(finalPath)) fs.unlinkSync(finalPath);
    fs.renameSync(videoPath, finalPath);
    console.log(`\n[SUCCESS] Video saved to: ${finalPath}`);
    const stats = fs.statSync(finalPath);
    console.log(`[INFO] Video file size: ${(stats.size / (1024 * 1024)).toFixed(2)} MB`);
  }
})();
