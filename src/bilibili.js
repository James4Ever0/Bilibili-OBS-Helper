const { chromium } = require('playwright');
const fs = require("fs")
const path = require("path")

const cookieFilePath = path.join(__dirname, "../cookie.txt");

function parseCookieString(cookieString) {
  const arr = cookieString.split("; ").filter(_ => _);
  return arr.map(s => {
    const [name, value] = s.split("=");
    return {
      name,
      value,
      path: "/",
      domain: ".bilibili.com",
    }
  })
}

function readCookieFile() {
  const cookieString = fs.readFileSync(cookieFilePath, "utf8");
  if (!cookieString) {
    throw new Error("Cookie file empty.")
  }
  return cookieString;
}

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, Math.ceil(time)));
}

async function fetchLiveKey() {
  const browser = await chromium.launch({
    headless: true,
  });
  const context = await browser.newContext();
  context.addCookies(parseCookieString(readCookieFile()));

  const page = await context.newPage();
  await page.goto('https://link.bilibili.com/p/center/index#/my-room/start-live');

  let keyPromiseResoveFn;
  const liveKeyPromise = new Promise((resolve, reject) => {
    keyPromiseResoveFn = resolve;
  });

  let first = true;
  let firstPromiseResolve;
  let firstPromise = new Promise((resolve, reject) => {
    firstPromiseResolve = resolve;
  });

  const doneCb = async () => {
    if (first === true) {
      first = false;
      // click refresh button in case input value is not set yet
      await page.locator('div.refresh img').click();
      await sleep(200);
      liveKey = await page.inputValue("div.live-code input");
      keyPromiseResoveFn(liveKey);
      firstPromiseResolve();
    } else {
      await firstPromise;
    }
  }

  async function liveIsOn() {
    await page.locator(`button:has-text("关闭直播")`).waitFor();
    await doneCb();
  }
  async function liveIsOff() {
    const categoryLocator = page.locator(`a:has-text("选择分类")`);
    await categoryLocator.waitFor();
    await categoryLocator.click();
    await page.locator('div.live-category  a:has-text("陪伴学习")').click();
    await page.locator('button:has-text("开始直播")').click();
    await doneCb();
  }

  try {
    await Promise.any([
      liveIsOn(),
      liveIsOff(),
    ])
  } catch (err) {
    console.log(err)
  }
  await context.close();
  await browser.close();
  return liveKeyPromise;
}

module.exports = {
  fetchLiveKey,
}
