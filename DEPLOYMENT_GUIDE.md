# 🚀 Deployment Guide - Get Your Dashboard Live in 10 Minutes

## Prerequisites
- GitHub account
- Streamlit Cloud account (free - sign up with GitHub)

## Step-by-Step Deployment

### 1️⃣ Create GitHub Repository (3 minutes)

**Option A: Using GitHub Web Interface**
1. Go to [github.com](https://github.com) and log in
2. Click the "+" icon (top right) → "New repository"
3. Repository name: `inventory-dashboard`
4. Description: "Interactive inventory management dashboard with 3 business examples"
5. Make it **Public** (required for free Streamlit hosting)
6. **DON'T** initialize with README (we have one)
7. Click "Create repository"

**Option B: Using Command Line**
```bash
# Navigate to the inventory-dashboard folder
cd inventory-dashboard

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Inventory management dashboard"

# Add your GitHub repo as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/inventory-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy to Streamlit Cloud (5 minutes)

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "Sign in" and use your GitHub account

2. **Create New App**
   - Click "New app" button
   - Repository: Select `YOUR_USERNAME/inventory-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Wait for Deployment**
   - Takes 2-3 minutes
   - You'll see logs as it installs dependencies
   - When done, your app is live!

4. **Get Your URL**
   - Your app will be at: `https://YOUR_USERNAME-inventory-dashboard.streamlit.app`
   - You can customize this URL in settings

### 3️⃣ Add to Your Portfolio (2 minutes)

**Option 1: Direct Link**

In your portfolio's Projects section:
```astro
{
  title: "Inventory Management Dashboard",
  description: "Interactive Streamlit dashboard analyzing inventory across 3 business models: plant nursery, retail store, and service business. Features ABC analysis, reorder alerts, and real-time metrics.",
  tags: ["Python", "Streamlit", "Pandas", "Plotly"],
  link: "https://YOUR_USERNAME-inventory-dashboard.streamlit.app",
  github: "https://github.com/YOUR_USERNAME/inventory-dashboard",
}
```

**Option 2: Embedded Dashboard**

Create a new page in your portfolio to showcase the live dashboard:

```astro
---
// src/pages/dashboards/inventory.astro
import Layout from '../../layouts/Layout.astro';
import Header from '../../components/Header.astro';
import Footer from '../../components/Footer.astro';
---

<Layout title="Inventory Dashboard - Andrew Felt">
  <Header />
  <main>
    <section class="dashboard-section">
      <div class="container">
        <h1>Inventory Management Dashboard</h1>
        <p>Interactive analysis of inventory across three business models</p>
        
        <div class="dashboard-embed">
          <iframe 
            src="https://YOUR_USERNAME-inventory-dashboard.streamlit.app?embed=true" 
            width="100%" 
            height="900px"
            frameborder="0"
            style="border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);"
          ></iframe>
        </div>
        
        <div class="dashboard-info">
          <h2>About This Dashboard</h2>
          <p>Built with Python, Streamlit, and Plotly to demonstrate inventory management across different business types...</p>
          <a href="https://github.com/YOUR_USERNAME/inventory-dashboard" target="_blank">View Code on GitHub →</a>
        </div>
      </div>
    </section>
  </main>
  <Footer />
</Layout>

<style>
  .dashboard-section {
    padding: 4rem 0;
  }
  
  .dashboard-embed {
    margin: 2rem 0;
    background: white;
    padding: 1rem;
    border-radius: 8px;
  }
  
  .dashboard-info {
    margin-top: 3rem;
    padding: 2rem;
    background: var(--neutral-light);
    border-radius: 8px;
  }
</style>
```

## 🎯 Customization After Deployment

### Update Your Info
1. Edit `app.py` line 45-46:
   ```python
   st.markdown("**Created by Andrew Felt**")
   st.markdown("[Portfolio](https://andrewfelt.com) | [GitHub](https://github.com/YOUR_USERNAME)")
   ```

2. Push changes:
   ```bash
   git add app.py
   git commit -m "Update contact info"
   git push
   ```

3. Streamlit Cloud auto-deploys in ~30 seconds!

### Add Your Own Data
1. Replace CSV files in `/data/` folder
2. Keep the same column structure
3. Push to GitHub
4. Auto-deploys!

## 🐛 Troubleshooting

**App won't deploy:**
- Check `requirements.txt` has all dependencies
- Make sure `app.py` is in the root directory
- Verify CSV files are in `/data/` folder

**App is slow:**
- Add `@st.cache_data` decorators (already included)
- Check data file sizes (keep under 50MB)

**Can't access the URL:**
- Make sure repository is **public**
- Check Streamlit Cloud logs for errors
- Wait 2-3 minutes for initial deployment

## 📊 Share Your Dashboard

Once live, share it:
- Add to LinkedIn projects section
- Include in job applications
- Share on Twitter/social media
- Add to your portfolio site

**Example LinkedIn Post:**
```
🚀 Just deployed a new data analytics project!

Built an interactive Inventory Management Dashboard using Python, Streamlit, and Plotly. 

Features:
✅ Real-time inventory tracking
✅ ABC analysis (Pareto principle)
✅ Automated reorder alerts
✅ 3 business model examples

Check it out: [YOUR_URL]
Code: [YOUR_GITHUB_URL]

#DataAnalytics #Python #Streamlit #BusinessIntelligence
```

## 🎉 You're Done!

Your dashboard is now live and you can:
- ✅ Share the link with potential employers
- ✅ Embed it in your portfolio
- ✅ Update it anytime by pushing to GitHub
- ✅ Show real-time analytics capabilities

**Next Steps:**
1. Test all three business types
2. Try the search and filter features
3. Download a sample CSV report
4. Add the link to your resume/LinkedIn
5. Consider adding more features (see README for ideas)

---

Need help? Check the [Streamlit documentation](https://docs.streamlit.io) or feel free to reach out!
