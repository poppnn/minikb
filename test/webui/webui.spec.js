// Tests du web UI avec l'API du firmware mockée : npx playwright test (dans test/webui)
const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

const HTML = fs.readFileSync(path.join(__dirname, "../../data/index.html"), "utf8");
const BASE = "http://minikb.test/";
const PINS = { allowed: [0, 1, 3, 4, 5, 6, 7, 10, 20, 21], wake: [0, 1, 3, 4, 5], max_keys: 10 };

function config(nKeys) {
  return {
    layout: "fr", ble_name: "MiniKB", ap_pass: "abcdefgh23", key_delay_ms: 8, debounce_ms: 30, sleep_min: 0,
    keys: PINS.allowed.slice(0, nKeys).map((pin, i) => ({ pin, label: `L${i + 1}`, send: `;k${i + 1}`, enter: false })),
  };
}

async function open(page, cfg = config(2)) {
  const posted = [];
  await page.route("**/*", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const json = (body, status = 200) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    if (url.pathname === "/") return route.fulfill({ contentType: "text/html", body: HTML });
    if (url.pathname === "/api/pins") return json(PINS);
    if (url.pathname === "/api/config" && req.method() === "GET") return json(cfg);
    if (url.pathname === "/api/config") { posted.push(req.postDataJSON()); return json({ ok: true }); }
    if (url.pathname === "/api/test") {
      const bad = [...req.postDataJSON().text].filter((c) => c === "😀");
      return json({ ok: !bad.length, ble: false, strokes: 3, unsupported: bad });
    }
    return route.fulfill({ status: 404, body: "" });
  });
  await page.goto(BASE);
  await expect(page.locator(".key")).toHaveCount(cfg.keys.length);
  return posted;
}

test("charge la config et affiche le compteur", async ({ page }) => {
  await open(page);
  await expect(page.locator("#counter")).toHaveText("2 touches / 10 max");
  await expect(page.locator("#ble_name")).toHaveValue("MiniKB");
  await expect(page.locator(".key").nth(1).locator("input").first()).toHaveValue("L2");
});

test("ajoute et supprime une touche", async ({ page }) => {
  await open(page);
  await page.click("#add");
  await expect(page.locator(".key")).toHaveCount(3);
  await expect(page.locator("#counter")).toHaveText("3 touches / 10 max");
  // la nouvelle touche prend le premier pin libre
  await expect(page.locator(".key").nth(2).locator("select")).toHaveValue("3");
  await page.getByRole("button", { name: "Supprimer la touche 1" }).click();
  await expect(page.locator(".key")).toHaveCount(2);
  await expect(page.locator(".key").first().locator("input").first()).toHaveValue("L2");
});

test("les listes de pins excluent les pins interdits et les doublons", async ({ page }) => {
  await open(page, config(3));
  const options = await page.locator(".key").nth(0).locator("select option").evaluateAll((os) => os.map((o) => Number(o.value)));
  expect(options).toContain(0);
  expect(options).not.toContain(1);  // pris par la touche 2
  for (const forbidden of [2, 8, 9, 18, 19]) expect(options).not.toContain(forbidden);
});

test("un pin interdit importé bloque l'enregistrement", async ({ page }) => {
  const cfg = config(1);
  cfg.keys[0].pin = 9;
  const posted = await open(page, cfg);
  await expect(page.locator(".key.invalid")).toHaveCount(1);
  await expect(page.locator("#errors")).toContainText("GPIO9 n'est pas autorisé");
  await page.click("#save");
  await expect(page.locator("#status")).toHaveText(/Corrigez/);
  expect(posted).toHaveLength(0);
});

test("limite de 10 touches", async ({ page }) => {
  await open(page, config(9));
  await page.click("#add");
  await expect(page.locator("#counter")).toHaveText("10 touches / 10 max");
  await expect(page.locator("#add")).toBeDisabled();
});

test("réordonne les touches", async ({ page }) => {
  await open(page);
  await page.locator(".key").nth(0).getByRole("button", { name: "Descendre" }).click();
  await expect(page.locator(".key").first().locator("input").first()).toHaveValue("L2");
});

test("enregistre une config valide", async ({ page }) => {
  const posted = await open(page);
  await page.locator(".key").nth(0).locator("input").nth(1).fill("été@mail.fr #1 €");
  await page.click("#save");
  await expect(page.locator("#status")).toHaveText(/Enregistré/);
  expect(posted[0].keys[0].send).toBe("été@mail.fr #1 €");
  expect(posted[0].keys).toHaveLength(2);
});

test("valide le mot de passe Wi-Fi", async ({ page }) => {
  const posted = await open(page);
  await page.fill("#ap_pass", "court");
  await page.click("#save");
  await expect(page.locator("#errors")).toContainText("Mot de passe Wi-Fi");
  expect(posted).toHaveLength(0);
});

test("mot de passe Wi-Fi vide = réseau ouvert accepté", async ({ page }) => {
  const posted = await open(page);
  await page.fill("#ap_pass", "");
  await page.click("#save");
  await expect(page.locator("#status")).toHaveText(/Enregistré/);
  expect(posted[0].ap_pass).toBe("");
});

test("tester une touche affiche les caractères non supportés", async ({ page }) => {
  await open(page);
  await page.locator(".key").nth(0).locator("input").nth(1).fill("ok 😀");
  await page.locator(".key").nth(0).getByRole("button", { name: "Tester" }).click();
  await expect(page.locator("#status")).toHaveText(/non supportés.*😀/);
});

test("exporte le YAML espanso", async ({ page }) => {
  await open(page);
  await page.locator(".key").nth(0).locator("input").nth(1).fill(';"mail');
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#export-espanso")]);
  expect(dl.suggestedFilename()).toBe("minikb.yml");
  const yaml = fs.readFileSync(await dl.path(), "utf8");
  expect(yaml).toContain("matches:");
  expect(yaml).toContain('  - trigger: ";\\"mail"\n    replace: "L1"');
  expect(yaml).toContain('  - trigger: ";k2"');
});
