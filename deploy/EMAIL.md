# Setting up email (sign-in codes)

Codeingo emails a 6-digit code to the user's own address at every 2-step verification. It needs one
sender account. Without these settings the code is only printed in the API terminal (development),
and the production server refuses to start.

## Gmail (fine for a small site)

1. On the Google account that will send the mail: Security -> turn on **2-Step Verification**.
2. Security -> **App passwords** -> create one named "Codeingo" -> copy the 16 characters.
3. Put these in `backend/.env` (local) or in the Render service's environment variables (live):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USERNAME=your.sender@gmail.com
SMTP_PASSWORD=the16characterapppassword
SMTP_FROM=Codeingo <your.sender@gmail.com>
```

4. Test it (from the `backend` folder, virtual environment active):

```
python scripts/send_test_email.py your.own@gmail.com
```

5. Restart the API. Signing in now emails the code. Check spam the first time.

Gmail allows a few hundred messages a day. For more users use Brevo, Resend, Postmark, Mailgun or
Amazon SES with the same six settings (their dashboards show the host, port and credentials), and set
up SPF/DKIM for your own domain so the codes do not land in spam.
