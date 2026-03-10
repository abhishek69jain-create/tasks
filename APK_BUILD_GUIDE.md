# QuickAssign - Download Code & Build APK Guide

## 🎯 Complete Step-by-Step Guide

---

## PART 1: Download Your Code from Emergent

### Option 1: Save to GitHub (Recommended)

1. **In Emergent Chat Interface:**
   - Click the **"Save to GitHub"** button
   - Select or create a repository
   - Click **"PUSH TO GITHUB"**
   - ✅ Your complete code is now on GitHub!

2. **Clone to Your Computer:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd YOUR-REPO
   ```

### Option 2: Manual Download
- Use the code editor view in Emergent
- Download files manually (tedious, not recommended)

---

## PART 2: Build Android APK

### Prerequisites Needed:

1. **Expo Account** (Free)
   - Go to https://expo.dev
   - Click "Sign Up" 
   - Create free account

2. **Node.js & npm** (Should already have)
   - Check: `node --version`
   - Check: `npm --version`

3. **Git** (Should already have)
   - Check: `git --version`

---

### Step-by-Step APK Build:

#### **1. Install EAS CLI**
```bash
npm install -g eas-cli
```

#### **2. Login to Expo**
```bash
eas login
```
(Enter your Expo account credentials)

#### **3. Navigate to Frontend Folder**
```bash
cd YOUR-REPO/frontend
```

#### **4. Configure EAS Build**
```bash
eas build:configure
```
- Press Enter to accept defaults
- Creates `eas.json` file

#### **5. Build the APK**
```bash
eas build -p android --profile preview
```

**What happens:**
- ✅ Uploads your code to Expo servers
- ✅ Builds APK in the cloud (10-20 minutes)
- ✅ Provides download link when done

**During build, you'll be asked:**
- "Generate a new Android Keystore?" → **Yes**
- "Build type?" → **APK** (not AAB)

#### **6. Download Your APK**
- Wait for build to complete
- You'll get a download link in terminal
- Or visit https://expo.dev → Your project → Builds
- Download the `.apk` file

**APK file will be named something like:**
`quickassign-1.0.0-preview.apk`

---

## PART 3: Distribute APK to Team

### Method 1: Share APK File Directly

**Upload to:**
- Google Drive
- Dropbox
- WeTransfer
- Company file server
- WhatsApp (if file size allows)

**Share link with team:** 
"Download and install this APK on your Android phone"

---

### Method 2: Use Expo Distribution Link

**After build completes:**
1. EAS gives you a public link like:
   `https://expo.dev/accounts/YOUR-NAME/projects/quickassign/builds/BUILD-ID`
2. Share this link with team
3. They can download APK directly from browser

---

### Method 3: Internal Distribution Page (Advanced)

Create a simple webpage:
```html
<!DOCTYPE html>
<html>
<head>
    <title>QuickAssign - Download</title>
</head>
<body>
    <h1>QuickAssign Task Manager</h1>
    <p>Download the latest version for Android:</p>
    <a href="YOUR-APK-LINK">Download APK</a>
    
    <h2>Installation Instructions:</h2>
    <ol>
        <li>Download the APK file</li>
        <li>Open Downloads folder</li>
        <li>Tap the APK file</li>
        <li>Allow "Install from Unknown Sources" if prompted</li>
        <li>Tap "Install"</li>
    </ol>
</body>
</html>
```

Host this page and share the URL with team.

---

## PART 4: Team Member Installation Instructions

**Send this to your team:**

---

### 📱 How to Install QuickAssign on Your Android Phone

**Step 1: Enable Unknown Sources**
1. Go to Settings → Security (or Apps & Security)
2. Enable "Install Unknown Apps" or "Unknown Sources"
3. Select your browser (Chrome/Firefox)
4. Toggle "Allow from this source"

**Step 2: Download APK**
1. Click the download link I shared
2. APK will download to your phone

**Step 3: Install**
1. Open your Downloads folder
2. Tap `quickassign-xxx.apk`
3. Tap "Install"
4. Wait for installation to complete
5. Tap "Open" or find "QuickAssign" in your app drawer

**Step 4: Login**
- Email: [I'll provide]
- Password: [I'll provide]

**Step 5: Start Using!**
- Create tasks
- Assign to team members
- Track progress

---

## PART 5: IMPORTANT - Keep Backend Running

### Current Setup:
✅ Your backend is running on Emergent: 
`https://quick-assign-1.preview.emergentagent.com`

✅ The APK will connect to this URL
✅ Keep your Emergent deployment active

### For Production (Later):
Deploy backend separately to:
- Railway.app (easiest)
- Render.com
- AWS/Google Cloud
- DigitalOcean

Then update `EXPO_PUBLIC_BACKEND_URL` in your app and rebuild APK.

---

## 📊 Build Options Explained

### APK vs AAB:
- **APK**: Direct install file (what you want)
- **AAB**: Google Play Store format (not needed for internal use)

### Build Profiles:
- **Preview**: For testing and internal distribution ✅
- **Production**: For app stores
- **Development**: For active development

For your use case: **Use `--profile preview`**

---

## 🔄 Updating the App

When you make changes:

1. **Update code on GitHub**
2. **Pull latest code locally**
   ```bash
   git pull origin main
   ```
3. **Rebuild APK**
   ```bash
   cd frontend
   eas build -p android --profile preview
   ```
4. **Distribute new APK to team**

Team members will need to:
- Uninstall old version (optional)
- Install new APK

---

## 💰 Cost Considerations

### Free Tier (Expo):
- **30 builds per month** (should be enough for updates)
- Unlimited projects
- Basic build features

### If You Need More:
- Expo Production Plan: ~$29/month
- More builds and priority queue

For most internal apps: **Free tier is sufficient**

---

## ❓ Common Issues & Solutions

### Issue: "App Not Installed"
**Solution:** Uninstall old version first, then reinstall

### Issue: "Can't install from unknown sources"
**Solution:** Enable in Settings → Security → Unknown Sources

### Issue: "APK parsing error"
**Solution:** Re-download APK, might be corrupted

### Issue: "Backend not connecting"
**Solution:** Check if Emergent deployment is running

### Issue: "Build failed"
**Solution:** Check `app.json` for errors, ensure all dependencies are installed

---

## ✅ Quick Command Reference

```bash
# Install EAS CLI
npm install -g eas-cli

# Login
eas login

# Configure (first time only)
cd frontend
eas build:configure

# Build APK
eas build -p android --profile preview

# Check build status
eas build:list

# View build details
eas build:view BUILD-ID
```

---

## 🎯 Summary Checklist

**Before Building:**
- [ ] Code saved to GitHub
- [ ] Expo account created
- [ ] EAS CLI installed
- [ ] Backend is accessible online

**Building:**
- [ ] Run `eas build -p android --profile preview`
- [ ] Wait for build to complete (10-20 min)
- [ ] Download APK file

**Distributing:**
- [ ] Upload APK to Google Drive/file server
- [ ] Share link with team
- [ ] Send installation instructions
- [ ] Create test accounts for team members

**Testing:**
- [ ] Install APK on your phone first
- [ ] Test all features
- [ ] Then distribute to team

---

## 📞 Next Steps

1. **Save code to GitHub** from Emergent
2. **Clone locally** to your computer
3. **Install EAS CLI** and login
4. **Run the build** command
5. **Download APK** when ready
6. **Share with team** via Drive/WhatsApp
7. **Your team starts using it!**

**Your internal app is ready for distribution! 🚀**
