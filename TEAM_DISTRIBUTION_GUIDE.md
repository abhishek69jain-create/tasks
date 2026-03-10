# QuickAssign - Team Distribution Guide

## 🔒 Securing Your Internal Team App

Your QuickAssign app is configured for **team-only access**. Here are your options:

---

## ✅ Option 1: Admin Creates All Accounts (RECOMMENDED)

**Best for:** Small teams (5-20 people)

### How it works:
1. You (admin) create accounts for each team member
2. Share credentials securely
3. No public registration allowed

### Steps:

#### **Create Team Member Accounts:**

```bash
cd /app/backend
python3 create_user.py
```

The script will:
- Ask for name, email, password
- Let you choose role (Admin or Team Member)
- Create the account in the database
- Provide credentials to share with the team member

#### **Example:**
```
=== QuickAssign - Create Team Member Account ===

Enter full name: Rahul Kumar
Enter email: rahul@yourcompany.com
Enter password: SecurePass123
Select role:
1. Team Member (default)
2. Admin
Enter choice: 1

✅ Success! User created:
   Name: Rahul Kumar
   Email: rahul@yourcompany.com
   Role: team_member

📧 Share these credentials with the team member:
   Email: rahul@yourcompany.com
   Password: SecurePass123
```

#### **Share with Team:**
Send each member:
- App URL: https://quick-assign-1.preview.emergentagent.com
- Their email
- Their password
- Ask them to change password after first login

---

## ✅ Option 2: Invite Code System

**Best for:** Medium teams (want self-registration but controlled)

### Enable Invite Code:

1. **Add to backend/.env:**
```bash
INVITE_CODE=YOURTEAM2026
```

2. **Restart backend:**
```bash
sudo supervisorctl restart backend
```

3. **Share with team:**
   - App URL: https://quick-assign-1.preview.emergentagent.com
   - Invite Code: `YOURTEAM2026`
   - They can register themselves with the code

**Note:** Without the invite code, registration will be blocked after the first admin user is created.

---

## ✅ Option 3: Disable Registration Screen

**Best for:** Maximum security, fixed team size

### Implementation:
Remove the register screen link from the login page so users can only login with pre-created accounts.

**Edit:** `/app/frontend/app/auth/login.tsx`

Remove or comment out this section:
```typescript
<View style={styles.footer}>
  <Text style={styles.footerText}>Don't have an account? </Text>
  <TouchableOpacity onPress={() => router.push('/auth/register')}>
    <Text style={styles.link}>Sign Up</Text>
  </TouchableOpacity>
</View>
```

Then use Option 1 (Admin Creates All Accounts) to add team members.

---

## 📱 Distributing the App to Your Team

### **For Immediate Use (Current Setup):**

Your team can access the app **RIGHT NOW**:
- **Web App:** https://quick-assign-1.preview.emergentagent.com
- Works on any mobile browser
- No installation needed

### **For Native Mobile Apps:**

#### **Android Users (Easiest):**
1. Download code from Emergent (Save to GitHub)
2. Build APK using EAS:
   ```bash
   eas build --platform android --profile preview
   ```
3. Get download link from EAS
4. Share link with team
5. They install APK directly

#### **iOS Users:**
1. Build using EAS:
   ```bash
   eas build --platform ios --profile preview
   ```
2. Distribute via TestFlight
3. Team installs via TestFlight app

---

## 🎯 Recommended Workflow for Your Team

### **Current Setup (0 Setup Time):**
1. ✅ Already have 2 test accounts:
   - Admin: `admin@test.com` / `admin123`
   - Team: `team@test.com` / `team123`

2. ✅ App is live at: https://quick-assign-1.preview.emergentagent.com

3. ✅ Create accounts for your team:
   ```bash
   cd /app/backend
   python3 create_user.py
   ```

4. ✅ Share app URL and credentials with team via WhatsApp/Email

5. ✅ Your team can start using it TODAY!

### **For Production (After Testing):**
1. Save code to GitHub
2. Deploy backend to Railway/Render
3. Build native apps with EAS
4. Distribute APK/TestFlight links

---

## 🔐 Security Best Practices

1. **Change Default Passwords:**
   - Test accounts use simple passwords
   - Ask team members to change passwords after first login

2. **Use Strong Invite Codes:**
   - If using Option 2, use complex invite codes
   - Change periodically

3. **Regular Account Review:**
   - Review team members in the app
   - Remove accounts of ex-employees

4. **Backend Security:**
   - Keep `SECRET_KEY` in `.env` file secure
   - Don't share `.env` file publicly

---

## 📞 Support

For any issues:
- Check the admin panel for user management
- Use `python3 create_user.py` to add/list users
- Backend logs: `/var/log/supervisor/backend.err.log`

---

## ✨ Current Status

✅ App is fully functional
✅ Backend APIs tested and working
✅ Authentication secured
✅ Ready for team use
✅ Admin account: `admin@test.com` / `admin123`

**Your team can start using QuickAssign immediately!**
