# Email Setup Guide for Feedback Form

The Feedback & Support page can automatically send emails to daniellevitt32@gmail.com when users submit feedback. To enable this feature, you need to configure email credentials.

## Setup Instructions

### Option 1: Gmail (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account settings
   - Enable 2-Step Verification

2. **Generate an App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Portland Thorns App" as the name
   - Copy the generated 16-character password

3. **Configure Streamlit Secrets**
   - Create or edit `.streamlit/secrets.toml` in your project root
   - Add the following:
   ```toml
   [email]
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   sender_email = "your-email@gmail.com"
   sender_password = "your-16-character-app-password"
   ```

### Option 2: Other Email Providers

For other email providers, update the SMTP settings:

**Outlook/Hotmail:**
```toml
[email]
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587
sender_email = "your-email@outlook.com"
sender_password = "your-password"
```

**Yahoo:**
```toml
[email]
smtp_server = "smtp.mail.yahoo.com"
smtp_port = 587
sender_email = "your-email@yahoo.com"
sender_password = "your-app-password"
```

## Streamlit Cloud Setup

If deploying to Streamlit Cloud:

1. Go to your app settings
2. Click "Secrets"
3. Add the email configuration as shown above
4. Save and redeploy

## Testing

After configuration:
1. Go to "Feedback & Support" page in the app
2. Fill out the form
3. Submit - you should receive an email at daniellevitt32@gmail.com

## Security Notes

- Never commit `.streamlit/secrets.toml` to version control
- Use App Passwords, not your main account password
- The `.gitignore` should already exclude secrets files

## Fallback

If email is not configured, users will see instructions and can still contact you directly at daniellevitt32@gmail.com.




