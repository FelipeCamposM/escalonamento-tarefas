import { chromium } from "playwright-core";
import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const baseUrl = "http://127.0.0.1:5173";
const output = resolve("prints");
const executablePath = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath, headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.screenshot({ path: resolve(output, "01-visao-geral.png") });

  await page.locator("#laboratorio").screenshot({ path: resolve(output, "02-laboratorio.png") });

  await page.locator("#instance-select").selectOption("inviavel");
  await page.locator("#algorithm-select").selectOption("dp");
  await page.locator("#run-button").click();
  await page.waitForTimeout(600);
  await page.locator("#laboratorio").scrollIntoViewIfNeeded();
  await page.screenshot({ path: resolve(output, "03-prazo-inviavel.png") });

  await page.addStyleTag({ content: ".topbar{position:absolute!important}" });
  await page.locator("#experimentos").screenshot({ path: resolve(output, "04-experimentos.png") });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.screenshot({ path: resolve(output, "05-mobile.png") });
  console.log(`Capturas gravadas em ${output}`);
} finally {
  await browser.close();
}
