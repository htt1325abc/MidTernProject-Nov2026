"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const out = path.join(root, "submission", "report_assets");
fs.mkdirSync(out, { recursive: true });

async function waitForFlutter(page) {
  await page.waitForTimeout(6500);
  const enable = page.getByRole("button", { name: /Enable accessibility/i });
  if (await enable.count()) {
    await enable.first().evaluate((element) => element.click());
    await page.waitForTimeout(1200);
  }
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.goto("https://midtern-users-2026-htt1325.web.app/", {
    waitUntil: "networkidle",
    timeout: 120000,
  });
  await waitForFlutter(page);
  await page.screenshot({ path: path.join(out, "01-dang-nhap.png") });

  await page.mouse.click(350, 518);
  await page.keyboard.type("admin@userhub.local");
  await page.mouse.click(350, 582);
  await page.keyboard.type("Admin@123");
  await page.mouse.click(390, 645);
  await page.waitForTimeout(6500);
  await page.screenshot({ path: path.join(out, "02-danh-sach.png") });

  await page.mouse.click(1320, 162);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(out, "03-them-nguoi-dung.png") });
  await page.mouse.click(1043, 75);
  await page.waitForTimeout(500);

  await page.mouse.click(1187, 300);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(out, "04-sua-nguoi-dung.png") });
  await page.mouse.click(1043, 75);
  await page.waitForTimeout(500);

  await page.mouse.click(1228, 300);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(out, "05-xac-nhan-xoa.png") });

  await page.mouse.click(840, 566);
  await page.waitForTimeout(500);
  await page.setViewportSize({ width: 412, height: 915 });
  await page.waitForTimeout(1200);
  await page.screenshot({
    path: path.join(out, "06-giao-dien-di-dong.png"),
    fullPage: true,
  });
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
