import Link from "next/link";
import { Logo } from "@/components/ui";

// Shown in the policies. Set NEXT_PUBLIC_SUPPORT_EMAIL (Vercel -> Settings -> Environment Variables) to your own address.
const CONTACT = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "";
const UPDATED = "3 October 2026";

function Page({ title, children }) {
  return (
    <div className="min-h-screen text-ink">
      <header className="mx-auto flex max-w-3xl items-center justify-between px-4 py-5">
        <Link href="/" aria-label="Codeingo home">
          <Logo />
        </Link>
        <nav className="flex gap-4 text-sm font-extrabold">
          <Link href="/privacy" className="btn-link">
            Privacy
          </Link>
          <Link href="/terms" className="btn-link">
            Terms
          </Link>
        </nav>
      </header>
      <main className="mx-auto max-w-3xl px-4 pb-16">
        <article className="card space-y-5 p-6 leading-relaxed sm:p-10 [&_h2]:mt-8 [&_h2]:text-xl [&_h2]:font-black [&_li]:ml-5 [&_li]:list-disc [&_p]:text-ink/90 [&_a]:font-bold [&_a]:text-primary">
          <h1 className="text-3xl font-black">{title}</h1>
          <p className="text-sm font-bold text-muted">Last updated {UPDATED}</p>
          {children}
        </article>
      </main>
    </div>
  );
}

const Contact = () =>
  CONTACT ? (
    <a href={`mailto:${CONTACT}`}>{CONTACT}</a>
  ) : (
    <span>the site owner (the contact address is shown on the site's hosting page)</span>
  );

export function Privacy() {
  return (
    <Page title="Privacy Policy">
      <p>
        Codeingo is a coding-practice website. This page explains what we collect, why, who sees it and how to remove it. We keep it short on
        purpose: we only collect what the app needs to work, and we don't sell your data or show ads.
      </p>

      <h2>What we collect</h2>
      <ul>
        <li>
          <strong>Account:</strong> the email address, name and profile picture from your Google account when you sign in with Google.
        </li>
        <li>
          <strong>Your learning:</strong> lessons and tests you complete, answers you miss (to build your practice list), XP, streaks, badges, certificates,
          contest scores, and the friends you follow.
        </li>
        <li>
          <strong>Security:</strong> your 2-step verification method. Emailed codes are stored only as a keyed hash and expire after 10 minutes;
          authenticator secrets are encrypted; passkeys store only a public key. We never see your biometrics or PIN.
        </li>
        <li>
          <strong>Technical logs:</strong> IP address and browser type for sign-in sessions and a security log (to spot abuse). We don't use advertising or
          tracking cookies.
        </li>
        <li>
          <strong>What you type:</strong> code you write runs in your own browser. It is sent to us only to be checked when you press Check (and, for Java,
          C and C++, to a sandbox if one is configured). Questions to the AI hint helper are sent to the AI provider the site owner configured.
        </li>
      </ul>

      <h2>How we use it</h2>
      <ul>
        <li>To sign you in and keep your account secure.</li>
        <li>To run the app: your progress, leagues, friends and contests.</li>
        <li>To email you sign-in codes and, if you leave it on, one streak reminder on evenings your streak is about to end. Every reminder has an unsubscribe link, and you can switch it off in your profile.</li>
      </ul>

      <h2>Who else handles it</h2>
      <p>
        Only the services needed to run the site: Google (sign-in), an email provider (sending codes), and the hosting and database providers. Other learners
        see only your display name, picture, friend code, streak and XP on leaderboards - never your email.
      </p>

      <h2>Cookies and storage</h2>
      <p>
        We use only essential cookies (your signed-in session and a security token) and your browser's local storage for preferences such as theme and sound.
        These are needed for the site to work, so there is no cookie banner.
      </p>

      <h2>Your rights</h2>
      <ul>
        <li>
          <strong>Download your data:</strong> Profile → Your data → Download. You get everything linked to your account as a JSON file.
        </li>
        <li>
          <strong>Delete your account:</strong> Profile → Your data → Delete. After you confirm with a 2-step code, your account and everything linked to it is
          removed immediately. A security-log entry that "an account was deleted" remains, without anything that identifies you.
        </li>
        <li>You can also ask us to correct or remove data by writing to <Contact />.</li>
      </ul>

      <h2>How long we keep it</h2>
      <p>For as long as your account exists. Sign-in sessions expire on their own. Deleting your account removes your data as described above.</p>

      <h2>Children</h2>
      <p>Codeingo is not directed at children under 13, and we don't knowingly collect their data. If a parent or guardian tells us a child has signed up, we will delete the account.</p>

      <h2>Changes and contact</h2>
      <p>
        If this policy changes we'll update the date above. Questions: <Contact />.
      </p>
    </Page>
  );
}

export function Terms() {
  return (
    <Page title="Terms of Service">
      <p>By creating an account or using Codeingo you agree to these terms. If you don't agree, please don't use the site.</p>

      <h2>Using Codeingo</h2>
      <ul>
        <li>You need a Google account and must be at least 13 years old (or have a parent or guardian's permission).</li>
        <li>You're responsible for your account and for keeping your 2-step verification, passkeys and recovery codes safe.</li>
        <li>Learn honestly: don't use bots or scripts to answer lessons, tests or contests, share contest answers while a contest is live, or try to read other people's answers.</li>
      </ul>

      <h2>What you must not do</h2>
      <ul>
        <li>Attack, overload or probe the service, or try to access other people's accounts or data.</li>
        <li>Use the code runners to harm anyone, mine cryptocurrency, or attack other systems. Code you run stays in your browser's sandbox.</li>
        <li>Upload unlawful, abusive or infringing content (for example in a display name).</li>
      </ul>
      <p>We may warn, limit or disable accounts that break these rules.</p>

      <h2>Content and certificates</h2>
      <p>
        Lessons, exercises and the Codeingo design are owned by the site owner or its licensors. You may use them for your own learning. A Codeingo
        certificate shows that you completed a course on Codeingo; it is not an accredited qualification.
      </p>

      <h2>No guarantees</h2>
      <p>
        Codeingo is provided "as is". We work hard to keep it accurate and available, but we can't promise it will be free of errors or always online, that
        every lesson is perfect, or that it will get you a particular job or grade. To the extent the law allows, we aren't liable for indirect or
        consequential losses arising from use of the site.
      </p>

      <h2>Ending your account</h2>
      <p>You can delete your account at any time in Profile → Your data. See the <Link href="/privacy">Privacy Policy</Link> for what happens to your data.</p>

      <h2>Changes and contact</h2>
      <p>
        We may update these terms; the date above shows the latest version, and continued use means you accept the changes. Questions: <Contact />.
      </p>
    </Page>
  );
}
