# QuickAssign - Public Registration + Optional Invite Code

## ✅ Current Setup

Your app now supports **BOTH** registration modes:

1. **Public Registration (DEFAULT)** - Anyone can register
2. **Invite Code Protection (OPTIONAL)** - Require code to register

---

## 🔓 Mode 1: Public Registration (Current State)

**How it works:**
- Anyone can visit the app and create an account
- First user automatically becomes Admin
- All subsequent users are Team Members
- No invite code required

**Status:** ✅ **ACTIVE NOW** (default behavior)

---

## 🔐 Mode 2: Invite Code Protection

**Enable invite code protection anytime by:**

### **Step 1: Set Invite Code in Backend**

Add this line to `/app/backend/.env`:
```env
INVITE_CODE=YOURTEAM2026
```

(Change `YOURTEAM2026` to your preferred code)

### **Step 2: Restart Backend**
```bash
sudo supervisorctl restart backend
```

### **Step 3: Share the Code**
- Tell your team members the invite code
- They click "Have an invite code?" link on registration screen
- Enter the code and register

**Once enabled:**
- Public registration still works for the FIRST user (admin)
- All subsequent registrations require the invite code
- Wrong/missing code = registration blocked

---

## 🎯 How the UI Works

### **Registration Screen:**

**Without Invite Code Set (Default):**
```
[Name Field]
[Email Field]  
[Password Field]
[Confirm Password Field]
< Have an invite code? >  ← Optional link
[Sign Up Button]
```

**With Invite Code Set:**
- User tries to register without code → Gets error
- User clicks "Have an invite code?" →Invite code field appears
- User enters code and registers successfully

**Smart Behavior:**
- If registration fails due to missing invite code, the field automatically appears
- Users can show/hide the invite code field as needed

---

## 🔄 Switching Between Modes

### **Enable Invite Code Protection:**
```bash
# Edit /app/backend/.env
INVITE_CODE=YOURTEAM2026

# Restart
sudo supervisorctl restart backend
```

### **Disable Invite Code Protection:**
```bash
# Edit /app/backend/.env
# Remove or comment out the INVITE_CODE line:
# INVITE_CODE=YOURTEAM2026

# Restart
sudo supervisorctl restart backend
```

---

## 💡 Best Practices

### **When to Use Public Registration:**
- Testing the app
- Initial setup phase
- Want easy onboarding for team

### **When to Enable Invite Code:**
- After your admin account is created
- Want to control who can register
- Share the code only via private channels (WhatsApp, Email)

### **Invite Code Tips:**
✅ Use a memorable but unique code
✅ Change it periodically for security
✅ Share via secure channels only
✅ Make it 8-12 characters long

Examples:
- `ECOMMER2026`
- `KIDSFASH24`
- `TEAM-QUICK-ASSIGN`

---

## 📱 User Experience

### **Scenario 1: Public Registration (No Code Required)**
1. User opens app
2. Clicks "Sign Up"
3. Fills name, email, password
4. Clicks "Sign Up"
5. ✅ Account created!

### **Scenario 2: With Invite Code Protection**
1. User opens app
2. Clicks "Sign Up"
3. Fills name, email, password
4. Clicks "Sign Up"
5. ❌ Error: "Invalid or missing invite code"
6. Clicks "Have an invite code?"
7. Enters invite code
8. Clicks "Sign Up" again
9. ✅ Account created!

---

## 🔍 Technical Details

### **Backend Logic:**
```python
# In /app/backend/server.py

# INVITE_CODE from .env
INVITE_CODE = os.environ.get("INVITE_CODE", None)

# Registration endpoint checks:
if user_count > 0 and INVITE_CODE:
    # After first user, require code if INVITE_CODE is set
    if not user_data.invite_code or user_data.invite_code != INVITE_CODE:
        raise HTTPException(403, "Invalid or missing invite code")
```

### **Frontend UI:**
- `/app/frontend/app/auth/register.tsx`
- Invite code field is hiddenby default
- Shows automatically if needed
- "Have an invite code?" link toggles visibility

---

## ✅ Current Status

**Mode:** Public Registration ✅
**Invite Code:** Not Required ✅
**First User (Admin):** Already created ✅
**Team Registration:** Open ✅

**To Enable Invite Code Protection:**
Just add `INVITE_CODE=YOURCODE` to `/app/backend/.env` and restart!

---

## 📞 Quick Actions

### Enable Invite Code Now:
```bash
echo 'INVITE_CODE=YOURTEAM2026' >> /app/backend/.env
sudo supervisorctl restart backend
```

### Disable Invite Code:
```bash
# Remove the INVITE_CODE line from /app/backend/.env
sudo supervisorctl restart backend
```

---

**Your app is ready! Public registration is active by default, and you can enable invite code protection whenever you need it.**
