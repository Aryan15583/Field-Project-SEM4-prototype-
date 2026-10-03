import fs from "node:fs";
import { OUTBOX } from "../playwright.config.mjs";

let n = 0;
export const uniqueEmail = (name) => `${name}${Date.now()}${++n}@e2e.test`;

/** The newest 6-digit code the API "emailed" to this address. */
export async function emailedCode(email) {
  for (let i = 0; i < 40; i++) {
    if (fs.existsSync(OUTBOX)) {
      const rows = fs.readFileSync(OUTBOX, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
      const hit = rows.reverse().find((r) => r.to === email && /^\d{6} is your/.test(r.subject));
      if (hit) return hit.subject.slice(0, 6);
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`no code was emailed to ${email}`);
}

/** Sign up (first time) or sign in (returning) through the real UI, including the emailed 2-step code. */
export async function signIn(page, email, name = "Tester") {
  await page.goto("/");
  await page.getByPlaceholder("you@example.com").fill(email);
  await page.getByPlaceholder("Display name").fill(name);
  await page.getByRole("button", { name: "Dev sign in" }).click();
  await page.waitForURL(/2fa\/(setup|verify)/);
  const box = page.getByLabel("6-digit verification code");
  await box.waitFor();
  const code = await emailedCode(email);
  await box.fill(code);
  await page.getByRole("button", { name: "Verify" }).click();
  await page.waitForURL(/\/learn/);
}
