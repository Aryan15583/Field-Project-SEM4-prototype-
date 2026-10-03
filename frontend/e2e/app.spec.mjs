import { expect, test } from "@playwright/test";
import { signIn, uniqueEmail } from "./helpers.mjs";

test.describe("public pages", () => {
  test("landing page, privacy and terms", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("learn to code");
    await expect(page.getByText("Python", { exact: true })).toBeVisible();
    await page.getByRole("link", { name: "Privacy", exact: true }).last().click();
    await expect(page.getByRole("heading", { name: "Privacy Policy" })).toBeVisible();
    await page.getByRole("link", { name: "Terms", exact: true }).first().click();
    await expect(page.getByRole("heading", { name: "Terms of Service" })).toBeVisible();
  });

  test("unknown pages show the 404 page", async ({ page }) => {
    await page.goto("/definitely-not-a-page");
    await expect(page.getByText("404 - page not found")).toBeVisible();
  });

  test("signed-out visitors are sent to the landing page", async ({ page }) => {
    await page.goto("/learn");
    await page.waitForURL("/");
  });
});

test.describe("sign-up and 2-step verification", () => {
  test("a wrong code is refused, the right emailed code signs you in", async ({ page }) => {
    const email = uniqueEmail("signup");
    await page.goto("/");
    await page.getByPlaceholder("you@example.com").fill(email);
    await page.getByPlaceholder("Display name").fill("Sign Up");
    await page.getByRole("button", { name: "Dev sign in" }).click();
    await page.waitForURL(/2fa\/setup/);
    const box = page.getByLabel("6-digit verification code");
    await box.fill("000000");
    await page.getByRole("button", { name: "Verify" }).click();
    await expect(page.getByText(/didn't match|expired/i)).toBeVisible();
    await signInFromCodePage(page, email);
    await expect(page.getByText("Section 1")).toBeVisible();
  });

  test("sign out, then sign in again with a fresh code", async ({ page }) => {
    const email = uniqueEmail("again");
    await signIn(page, email, "Again");
    await page.goto("/profile");
    await page.getByRole("button", { name: "Log out", exact: true }).click();
    await page.waitForURL("/");
    await signIn(page, email, "Again");
    await expect(page).toHaveURL(/\/learn/);
  });
});

async function signInFromCodePage(page, email) {
  const { emailedCode } = await import("./helpers.mjs");
  const box = page.getByLabel("6-digit verification code");
  await box.fill(await emailedCode(email));
  await page.getByRole("button", { name: "Verify" }).click();
  await page.waitForURL(/\/learn/);
}

test.describe("learning", () => {
  test("every course loads and a lesson opens", async ({ page }) => {
    await signIn(page, uniqueEmail("learn"), "Learner");
    const tabs = page.getByRole("tab");
    await expect(tabs.first()).toBeVisible();
    expect(await tabs.count()).toBeGreaterThanOrEqual(10);
    await page.getByRole("button", { name: /unlocked/ }).first().click();
    await page.getByText(/Start \+/).click();
    await expect(page.getByText("Let's go")).toBeVisible();
    await page.getByText("Let's go").click();
    await expect(page.getByRole("button", { name: "Check" })).toBeVisible();
  });

  test("daily, practice, leagues, contests and progress pages open", async ({ page }) => {
    await signIn(page, uniqueEmail("pages"), "Pages");
    for (const [path, text] of [
      ["/daily", /Daily challenge|No challenge today/],
      ["/practice", "Practice"],
      ["/leaderboard", "Weekly League"],
      ["/contests", "Weekly contests"],
      ["/stats", "Your progress"],
    ]) {
      await page.goto(path);
      await expect(page.getByText(text).first()).toBeVisible();
    }
  });
});

test.describe("friends", () => {
  test("follow a friend with their invite link", async ({ browser }) => {
    const a = await (await browser.newContext()).newPage();
    const b = await (await browser.newContext()).newPage();
    await signIn(a, uniqueEmail("ann"), "Ann");
    await a.goto("/leaderboard");
    await a.getByRole("tab", { name: "Friends" }).click();
    const code = (await a.locator("p.font-mono").first().textContent()).replace("-", "").trim();
    expect(code).toHaveLength(8);

    await signIn(b, uniqueEmail("ben"), "Ben");
    await b.goto(`/leaderboard?add=${code}`);
    await expect(b.getByText("Ann invited you")).toBeVisible();
    await b.getByRole("button", { name: "Follow Ann" }).click();
    await expect(b.getByText("Following (1)")).toBeVisible();
  });
});

test.describe("contests", () => {
  test("enter a contest and see the timer", async ({ page }) => {
    await signIn(page, uniqueEmail("contest"), "Contestant");
    await page.goto("/contests");
    await page.getByRole("link", { name: /Python/ }).first().click();
    await page.getByRole("button", { name: "Enter contest" }).click();
    await page.getByRole("button", { name: "Start the clock" }).click();
    await expect(page.getByRole("timer")).toContainText(/\d+:\d\d/);
  });
});

test.describe("admin", () => {
  test("learners can't see the admin panel; the owner can promote someone", async ({ browser }) => {
    const learnerEmail = uniqueEmail("grace");
    const learner = await (await browser.newContext()).newPage();
    await signIn(learner, learnerEmail, "Grace");
    await expect(learner.getByRole("link", { name: "Admin" })).toHaveCount(0);
    await learner.goto("/admin");
    await expect(learner.getByText("404 - page not found")).toBeVisible();
    expect((await learner.request.get("/api/admin/users")).status()).toBe(404);

    const owner = await (await browser.newContext()).newPage();
    await signIn(owner, "owner@e2e.test", "Owner");
    await owner.goto("/admin");
    await owner.getByRole("tab", { name: "Users" }).click();
    await owner.getByLabel("Search users").fill(learnerEmail);
    await owner.getByRole("button", { name: "Search" }).click();
    const row = owner.getByRole("row", { name: new RegExp(learnerEmail) });
    await row.getByRole("button", { name: "Make admin" }).click();
    const { emailedCode } = await import("./helpers.mjs");
    await owner.getByLabel("Confirmation code").fill(await emailedCode("owner@e2e.test"));
    await owner.locator("form").getByRole("button", { name: "Make admin" }).click();
    await expect(row.getByText("admin", { exact: true })).toBeVisible();

    await learner.goto("/admin");
    await expect(learner.getByRole("heading", { name: "Admin" })).toBeVisible();
  });
});

test.describe("your data", () => {
  test("download my data, then delete the account", async ({ page }) => {
    const email = uniqueEmail("gone");
    await signIn(page, email, "Gone");
    await page.goto("/profile");
    const [download] = await Promise.all([page.waitForEvent("download"), page.getByRole("button", { name: "Download my data" }).click()]);
    expect(download.suggestedFilename()).toBe("codeingo-my-data.json");

    await page.getByRole("button", { name: "Delete my account" }).click();
    const { emailedCode } = await import("./helpers.mjs");
    await page.getByLabel("Confirmation code").fill(await emailedCode(email));
    await page.getByRole("button", { name: "Delete everything" }).click();
    await page.waitForURL("/");
    // the account is really gone: signing in again starts a brand-new sign-up
    await page.getByPlaceholder("you@example.com").fill(email);
    await page.getByPlaceholder("Display name").fill("Gone");
    await page.getByRole("button", { name: "Dev sign in" }).click();
    await page.waitForURL(/2fa\/setup/);
  });
});
