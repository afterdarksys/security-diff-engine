# llmsecurity.dev Deployment Guide

## Quick Deploy Options

### Option 1: Vercel (Recommended - Free & Fast)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd llmsecurity-website
   vercel
   ```

3. **Follow prompts:**
   - Set up and deploy? **Yes**
   - Which scope? **Your account**
   - Link to existing project? **No**
   - Project name? **llmsecurity**
   - Directory? **./ (current)**

4. **Add custom domain:**
   - Go to Vercel Dashboard → Settings → Domains
   - Add: **llmsecurity.dev**
   - Follow DNS instructions

**Deployment Time:** ~2 minutes
**Cost:** Free

---

### Option 2: Netlify (Free & Easy)

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy:**
   ```bash
   cd llmsecurity-website
   netlify deploy --prod
   ```

3. **Add custom domain:**
   - Netlify Dashboard → Domain settings
   - Add: **llmsecurity.dev**

**Deployment Time:** ~2 minutes
**Cost:** Free

---

### Option 3: GitHub Pages (Free, Manual Setup)

1. **Create repository:**
   ```bash
   cd llmsecurity-website
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/llmsecurity.dev.git
   git push -u origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: **main branch**
   - Custom domain: **llmsecurity.dev**

3. **Add CNAME file:**
   ```bash
   echo "llmsecurity.dev" > CNAME
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

**Deployment Time:** ~5 minutes
**Cost:** Free

---

### Option 4: Simple HTTP Server (Local Testing)

```bash
cd llmsecurity-website
python3 -m http.server 8000
# Open: http://localhost:8000
```

---

## DNS Configuration

Once deployed, configure DNS for **llmsecurity.dev**:

### For Vercel:
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com

Type: A
Name: @
Value: 76.76.21.21
```

### For Netlify:
```
Type: CNAME
Name: www
Value: your-site.netlify.app

Type: A
Name: @
Value: 75.2.60.5
```

---

## SSL/HTTPS

All platforms automatically provide free SSL certificates via Let's Encrypt:
- ✅ Vercel: Auto-configured
- ✅ Netlify: Auto-configured
- ✅ GitHub Pages: Auto-configured

---

## Post-Deployment Checklist

- [ ] Test all navigation links
- [ ] Verify mobile responsiveness
- [ ] Check all CTAs ("Get Started", "GitHub", etc.)
- [ ] Test form submissions (if added)
- [ ] Verify analytics tracking
- [ ] Submit to search engines
- [ ] Share on social media

---

## Quick Deploy Command (Vercel)

```bash
# One command deployment
cd /Users/ryan/development/afterdark-enhancements/llmsecurity-website && vercel --prod
```

---

## Analytics Setup (Optional)

### Plausible (Privacy-Friendly)
```html
<script defer data-domain="llmsecurity.dev" src="https://plausible.io/js/script.js"></script>
```

### Google Analytics
```html
<!-- Add before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
```

---

## Monitoring

- **Uptime**: uptime robot.com (free)
- **Performance**: PageSpeed Insights
- **Analytics**: Plausible/Fathom

---

**Recommended:** Use Vercel for fastest deployment with automatic HTTPS and global CDN.
