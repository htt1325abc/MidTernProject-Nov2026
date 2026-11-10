"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const rawDir = path.join(root, "artifacts", "demo_video_raw");
const iconPath = path.join(root, "web", "icons", "Icon-192.png");
const appUrl = "https://midtern-users-2026-htt1325.web.app/";
const demoEmail = "demo.video.2026@example.com";

fs.mkdirSync(rawDir, { recursive: true });

async function waitForFlutter(page, delay = 6500) {
  await page.waitForTimeout(delay);
  const enable = page.getByRole("button", { name: /Enable accessibility/i });
  if (await enable.count()) {
    await enable.first().evaluate((element) => element.click());
    await page.waitForTimeout(1000);
  }
}

async function titleCard(page, eyebrow, title, subtitle, duration = 2800) {
  await page.setContent(`<!doctype html>
    <html lang="vi"><head><meta charset="utf-8"><style>
      *{box-sizing:border-box} body{margin:0;background:linear-gradient(135deg,#071521,#0b2a38 55%,#123b3b);color:#f5fbfb;font-family:Arial,sans-serif;height:100vh;display:grid;place-items:center;overflow:hidden}
      .glow{position:fixed;width:520px;height:520px;border-radius:50%;background:#24b8a6;filter:blur(150px);opacity:.17;right:-130px;top:-170px}
      .card{width:min(980px,82vw);padding:64px 68px;border:1px solid rgba(106,234,215,.24);border-radius:34px;background:rgba(5,22,32,.72);box-shadow:0 30px 90px rgba(0,0,0,.32)}
      .brand{display:flex;align-items:center;gap:14px;margin-bottom:46px;color:#74e0d1;font-weight:800;letter-spacing:2px}.mark{font-size:34px}.eyebrow{color:#66d6c7;font-size:18px;font-weight:800;letter-spacing:3px;text-transform:uppercase;margin-bottom:18px}
      h1{font-size:54px;line-height:1.08;margin:0 0 24px;letter-spacing:-1.7px}p{font-size:23px;line-height:1.5;color:#b8cbd0;margin:0;max-width:820px}.line{height:5px;width:120px;background:#2ec6b2;border-radius:99px;margin-top:38px}
    </style></head><body><div class="glow"></div><main class="card"><div class="brand"><span class="mark">U/</span><span>USER REGISTRY</span></div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p>${subtitle}</p><div class="line"></div></main></body></html>`);
  await page.waitForTimeout(duration);
}

async function installOverlay(page) {
  await page.evaluate(() => {
    const style = document.createElement("style");
    style.textContent = `
      #demo-caption{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:2147483646;background:rgba(4,20,30,.92);color:#fff;border:1px solid rgba(77,221,200,.55);border-radius:16px;padding:13px 22px;font:700 18px/1.3 Arial,sans-serif;box-shadow:0 12px 34px rgba(0,0,0,.28);pointer-events:none;opacity:0;transition:opacity .25s;white-space:nowrap}
      #demo-cursor{position:fixed;left:0;top:0;width:25px;height:25px;border-radius:50%;background:rgba(33,194,171,.25);border:3px solid #10a991;z-index:2147483647;pointer-events:none;transform:translate(-50%,-50%);transition:left .45s ease,top .45s ease,transform .13s ease;box-shadow:0 0 0 5px rgba(255,255,255,.75)}
    `;
    document.head.appendChild(style);
    const caption = document.createElement("div");
    caption.id = "demo-caption";
    document.body.appendChild(caption);
    const cursor = document.createElement("div");
    cursor.id = "demo-cursor";
    cursor.style.left = "72px";
    cursor.style.top = "72px";
    document.body.appendChild(cursor);
  });
}

async function caption(page, text, hold = 900) {
  await page.evaluate((value) => {
    const element = document.getElementById("demo-caption");
    if (element) {
      element.textContent = value;
      element.style.opacity = "1";
    }
  }, text);
  await page.waitForTimeout(hold);
}

async function hideCaption(page) {
  await page.evaluate(() => {
    const element = document.getElementById("demo-caption");
    if (element) element.style.opacity = "0";
  });
}

async function point(page, x, y, click = false, pause = 450) {
  await page.evaluate(({ x, y }) => {
    const cursor = document.getElementById("demo-cursor");
    if (cursor) {
      cursor.style.left = `${x}px`;
      cursor.style.top = `${y}px`;
    }
  }, { x, y });
  await page.waitForTimeout(500);
  if (click) {
    await page.evaluate(() => {
      const cursor = document.getElementById("demo-cursor");
      if (cursor) cursor.style.transform = "translate(-50%,-50%) scale(.72)";
    });
    await page.mouse.click(x, y);
    await page.waitForTimeout(130);
    await page.evaluate(() => {
      const cursor = document.getElementById("demo-cursor");
      if (cursor) cursor.style.transform = "translate(-50%,-50%) scale(1)";
    });
  }
  await page.waitForTimeout(pause);
}

async function fillAt(page, x, y, value) {
  await point(page, x, y, true, 120);
  await page.keyboard.press("Control+A");
  await page.keyboard.type(value, { delay: 42 });
  await page.waitForTimeout(280);
}

async function login(page) {
  await caption(page, "Đăng nhập bằng tài khoản quản trị Firebase", 700);
  await fillAt(page, 350, 518, "admin@userhub.local");
  await fillAt(page, 350, 582, "Admin@123");
  await point(page, 390, 645, true, 500);
  await waitForFlutter(page, 6200);
  await installOverlay(page);
}

async function recordDesktop(browser) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    recordVideo: { dir: rawDir, size: { width: 1152, height: 720 } },
  });
  const page = await context.newPage();
  const video = page.video();

  await titleCard(page, "Video demo", "Ứng dụng CRUD quản lý người dùng", "Flutter Web • Firebase Authentication • Realtime Database");
  await page.goto(appUrl, { waitUntil: "networkidle", timeout: 120000 });
  await waitForFlutter(page);
  await installOverlay(page);
  await login(page);

  await caption(page, "Dashboard hiển thị dữ liệu theo thời gian thực", 1600);
  await hideCaption(page);
  await page.waitForTimeout(500);

  await caption(page, "Tìm kiếm hồ sơ theo họ tên hoặc email", 650);
  await fillAt(page, 700, 162, "Lan");
  await page.waitForTimeout(1100);
  await fillAt(page, 700, 162, "");

  await caption(page, "Sắp xếp danh sách và ẩn/hiện mật khẩu", 650);
  await point(page, 1165, 162, true, 700);
  await point(page, 1205, 162, true, 900);
  await point(page, 1205, 162, true, 450);

  await caption(page, "Thêm hồ sơ mới — đủ đúng 4 trường dữ liệu", 700);
  await point(page, 1320, 162, true, 500);
  const fileChooserPromise = page.waitForEvent("filechooser");
  await point(page, 557, 220, true, 100);
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles(iconPath);
  await page.waitForTimeout(700);
  await fillAt(page, 720, 285, "Demo Video");
  await fillAt(page, 720, 349, demoEmail);
  await fillAt(page, 720, 413, "Demo@123");
  await point(page, 968, 478, true, 3300);

  await caption(page, "Hồ sơ vừa tạo đã đồng bộ lên Firebase", 650);
  await fillAt(page, 700, 162, "demo.video");
  await page.waitForTimeout(900);

  await caption(page, "Chỉnh sửa thông tin người dùng", 650);
  await point(page, 1187, 300, true, 500);
  await fillAt(page, 720, 285, "Demo Video Đã Sửa");
  await point(page, 968, 478, true, 2700);

  await caption(page, "Xóa hồ sơ và xác nhận thao tác", 650);
  await point(page, 1228, 300, true, 500);
  await point(page, 932, 496, true, 2800);

  await fillAt(page, 700, 162, "");
  await caption(page, "Dữ liệu trở lại 4 hồ sơ ban đầu", 1800);
  await hideCaption(page);
  await page.waitForTimeout(400);

  const storageState = await context.storageState({ indexedDB: true });
  await context.close();
  const videoPath = await video.path();
  const target = path.join(rawDir, "desktop.webm");
  fs.copyFileSync(videoPath, target);
  return { storageState, target };
}

async function recordMobile(browser, storageState) {
  const context = await browser.newContext({
    viewport: { width: 412, height: 915 },
    deviceScaleFactor: 1,
    storageState,
    recordVideo: { dir: rawDir, size: { width: 324, height: 720 } },
  });
  const page = await context.newPage();
  const video = page.video();

  await titleCard(page, "Responsive", "Giao diện trên thiết bị di động", "Danh sách tự chuyển thành các thẻ hồ sơ dễ thao tác.", 2200);
  await page.goto(appUrl, { waitUntil: "networkidle", timeout: 120000 });
  await waitForFlutter(page);
  await installOverlay(page);

  // Nếu phiên Firebase chưa được trình duyệt khôi phục, đăng nhập lại bằng tọa độ
  // tương ứng với màn hình di động.
  const loginButton = page.getByText("Đăng nhập", { exact: true });
  if (await loginButton.count()) {
    await fillAt(page, 206, 535, "admin@userhub.local");
    await fillAt(page, 206, 599, "Admin@123");
    await point(page, 206, 662, true, 500);
    await waitForFlutter(page, 6200);
    await installOverlay(page);
  }

  await caption(page, "Responsive: hồ sơ hiển thị dạng thẻ", 1800);
  await hideCaption(page);
  await page.waitForTimeout(500);
  await page.mouse.wheel(0, 500);
  await page.waitForTimeout(1800);
  await page.mouse.wheel(0, -500);
  await page.waitForTimeout(800);

  await context.close();
  const videoPath = await video.path();
  const target = path.join(rawDir, "mobile.webm");
  fs.copyFileSync(videoPath, target);
  return target;
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--autoplay-policy=no-user-gesture-required"],
  });
  try {
    const desktop = await recordDesktop(browser);
    const mobile = await recordMobile(browser, desktop.storageState);
    console.log(JSON.stringify({ desktop: desktop.target, mobile }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
