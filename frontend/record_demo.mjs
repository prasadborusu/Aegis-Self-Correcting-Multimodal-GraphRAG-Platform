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

  // Clear prior saved conversations for a clean, pristine demonstration
  const convStorage = path.resolve('d:/rag/.storage/conversations/default.json');
  if (fs.existsSync(convStorage)) {
    try {
      fs.writeFileSync(convStorage, JSON.stringify([], null, 2), 'utf-8');
      console.log('[*] Reset conversation history for clean demo recording.');
    } catch (e) {
      console.warn('[!] Note on storage clear:', e.message);
    }
  }

  console.log('[*] Launching Chromium browser (1280x720) with video recording...');
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

  // Connect to the frontend server
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

  // ==========================================
  // SCENE 1: Ask Aegis & Interactive Chat Answers
  // ==========================================
  console.log('[*] Navigating to Ask Aegis...');
  const askTab = await page.$('text=Ask Aegis');
  if (askTab) await askTab.click();
  await delay(2000);

  const inputSelector = 'input[placeholder*="Ask a question"]';
  const askBtnSelector = 'button:has-text("Ask")';

  // Helper function to ask a query, wait for the response, and linger so answers are fully readable
  async function askAndShowAnswer(queryText, waitSeconds = 6, typeSpeed = 25) {
    console.log(`\n[QUERY] Typing: "${queryText}"`);
    const input = await page.$(inputSelector);
    if (!input) return;

    await input.click();
    await input.fill(queryText);
    await delay(800);

    const askBtn = await page.$(askBtnSelector);
    if (askBtn) await askBtn.click();

    // Wait for query processing to begin
    await delay(1200);

    // Wait until loading spinner finishes
    try {
      await page.waitForSelector('text=Retrieving evidence', { state: 'detached', timeout: 35000 });
    } catch {
      console.log('[!] Loading wait timed out, proceeding...');
    }

    // Additional buffer for complete DOM rendering and smooth auto-scroll
    await delay(1500);

    // Linger so viewers can comfortably read the entire chat answer, coverage badge, and citations
    console.log(`[*] Displaying chat answer for ${waitSeconds} seconds for viewer reading...`);
    await delay(waitSeconds * 1000);
  }

  // Question 1: Natural Conversation & Capability Overview
  await askAndShowAnswer('Hello Aegis, who are you and what can you do?', 6);

  // Question 2: Factual Document Extraction (Academics & CGPA)
  await askAndShowAnswer("What is Durga Prasad's educational qualification, college name, and GPA?", 7);

  // Question 3: Deep Technical Skills & Languages from Resume
  await askAndShowAnswer('What technical skills and programming languages are listed in his resume?', 7);

  // Question 4: Self-Correction & Hallucination Prevention Architecture
  await askAndShowAnswer('How does Aegis self-correct and prevent hallucinations?', 7);

  // ==========================================
  // SCENE 2: Inspect Supporting Evidence Citation
  // ==========================================
  console.log('\n[*] Inspecting Supporting Evidence Citation Modal...');
  const citationButtons = await page.$$('button:has(svg.lucide-file-text)');
  if (citationButtons.length > 0) {
    await citationButtons[citationButtons.length - 1].click();
    console.log('[*] Opened Citation Context Modal: displaying excerpt, relevance, chunk ID.');
    await delay(4500); // Linger so viewer can read the cited document text

    // Close citation modal
    const closeBtn = await page.$('button:has(svg.lucide-x)');
    if (closeBtn) await closeBtn.click();
    await delay(1200);
  }

  // ==========================================
  // SCENE 3: Inspect Retrieval & Reasoning Trace Modal
  // ==========================================
  console.log('\n[*] Inspecting "How Aegis reached this answer" Trace Modal...');
  const traceLinks = await page.$$('text=How Aegis reached this answer');
  if (traceLinks.length > 0) {
    await traceLinks[traceLinks.length - 1].click();
    console.log('[*] Opened Reasoning Trace Modal: candidate chunks, evidence count, coverage 100%.');
    await delay(5000); // Linger so viewer can read trace details

    // Close trace modal
    const closeBtn = await page.$('button:has(svg.lucide-x)');
    if (closeBtn) await closeBtn.click();
    await delay(1200);
  }

  // ==========================================
  // SCENE 4: Full Chat Review (Smooth Scroll-Through)
  // ==========================================
  console.log('\n[*] Smoothly reviewing entire chat conversation thread...');
  const chatBox = await page.$('.overflow-y-auto');
  if (chatBox) {
    // Scroll up to review earlier answers
    await chatBox.evaluate((el) => el.scrollTo({ top: 0, behavior: 'smooth' }));
    await delay(3500);
    // Scroll halfway
    await chatBox.evaluate((el) => el.scrollTo({ top: el.scrollHeight / 2, behavior: 'smooth' }));
    await delay(2500);
    // Scroll back to bottom
    await chatBox.evaluate((el) => el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' }));
    await delay(2500);
  }

  // ==========================================
  // SCENE 5: Ingested Documents Management
  // ==========================================
  console.log('\n[*] Navigating to Documents Tab...');
  const docsTab = await page.$('text=Documents');
  if (docsTab) await docsTab.click();
  await delay(2000);

  // Scroll through documents
  await page.mouse.wheel(0, 250);
  await delay(2500);
  await page.mouse.wheel(0, -250);
  await delay(2000);

  // ==========================================
  // SCENE 6: Dashboard Telemetry & System Health
  // ==========================================
  console.log('\n[*] Navigating to Dashboard Tab...');
  const dashboardTab = await page.$('text=Dashboard');
  if (dashboardTab) await dashboardTab.click();
  await delay(2000);

  // Scroll through telemetry metrics
  await page.mouse.wheel(0, 200);
  await delay(2500);
  await page.mouse.wheel(0, -200);
  await delay(2500);

  // Final concluding pause
  console.log('[*] Finalizing and encoding video recording...');
  await delay(2000);

  // Close page and context to flush video to disk
  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();

  if (video) {
    const videoPath = await video.path();
    const finalWebm = path.resolve('d:/rag/recordings/aegis_demo_walkthrough.webm');
    if (fs.existsSync(finalWebm)) fs.unlinkSync(finalWebm);
    fs.renameSync(videoPath, finalWebm);
    console.log(`\n[SUCCESS] WebM Video saved to: ${finalWebm}`);
    const stats = fs.statSync(finalWebm);
    console.log(`[INFO] WebM File size: ${(stats.size / (1024 * 1024)).toFixed(2)} MB`);
  }
})();
