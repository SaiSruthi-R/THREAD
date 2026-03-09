# 🔑 How to Get AWS Credentials

## Step 1: Login to AWS Console

Go to: https://console.aws.amazon.com/

Login with your AWS account credentials.

---

## Step 2: Navigate to IAM

1. In the search bar at the top, type: **IAM**
2. Click on **IAM** (Identity and Access Management)

Or go directly to: https://console.aws.amazon.com/iam/

---

## Step 3: Create a New User

1. In the left sidebar, click **Users**
2. Click the **Add users** button (orange button)

---

## Step 4: Set User Details

1. **User name**: `memory-mapping-dev`
2. **Select AWS credential type**:
   - ✅ Check: **Access key - Programmatic access**
   - ❌ Uncheck: Console password (not needed)
3. Click **Next: Permissions**

---

## Step 5: Set Permissions

1. Click **Attach existing policies directly**
2. In the search box, type: **AdministratorAccess**
3. ✅ Check the box next to **AdministratorAccess**
4. Click **Next: Tags**

---

## Step 6: Add Tags (Optional)

1. You can skip this step
2. Click **Next: Review**

---

## Step 7: Review and Create

1. Review the details
2. Click **Create user**

---

## Step 8: SAVE YOUR CREDENTIALS! ⚠️

**IMPORTANT: This is the ONLY time you'll see these credentials!**

You'll see a screen with:
- **Access key ID**: Something like `AKIAIOSFODNN7EXAMPLE`
- **Secret access key**: Something like `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

**Do ONE of these:**
1. Click **Download .csv** button (saves to your computer)
2. Or copy both values to a text file

**Example:**
```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## Step 9: Close the Window

Click **Close** when done.

---

## ✅ You're Ready!

Now you have:
- ✅ Access Key ID
- ✅ Secret Access Key

**Next step:** Configure AWS CLI with these credentials!

---

## 🔒 Security Notes

- **Never share** these credentials
- **Never commit** them to Git
- **Rotate** them every 90 days
- If compromised, **delete** them immediately in IAM Console

---

## 📸 Visual Guide

If you need visual help, here's the flow:

```
AWS Console
    ↓
Search "IAM"
    ↓
Users → Add users
    ↓
Name: memory-mapping-dev
Select: Programmatic access
    ↓
Attach: AdministratorAccess
    ↓
Create user
    ↓
SAVE CREDENTIALS!
```

---

## ❓ Don't Have an AWS Account?

Create one at: https://aws.amazon.com/

**Free Tier includes:**
- 12 months of free services
- Always free services
- Perfect for this project!

**You'll need:**
- Email address
- Phone number
- Credit card (for verification, won't be charged for free tier usage)

---

**Once you have your credentials, come back and we'll configure AWS CLI!**
