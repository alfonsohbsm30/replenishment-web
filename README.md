# Inventory Management Dashboard

An interactive Streamlit dashboard showcasing inventory management across three different business models:

1. **Plant Nursery** - Manufacturing/growing inventory with plant-specific metrics
2. **Retail Storefront** - Traditional retail with SKUs, sizes, and seasonal tracking
3. **Service Business** - Equipment, chemicals, and supplies for a pressure washing business

## 🎯 Features

### Key Metrics Dashboard
- Total SKUs and inventory value
- Items needing reorder
- Critical stock alerts
- Real-time status monitoring

### Analytics & Insights
- **Stock Status Distribution** - Visual breakdown of inventory health
- **Category Analysis** - Value distribution across product categories
- **ABC Analysis** - Pareto principle applied to inventory (80/20 rule)
- **Turnover Rates** - Track how quickly inventory moves
- **Days of Inventory** - Forecast when items need restocking

### Interactive Features
- Switch between 3 different business models
- Search and filter inventory
- Sort by any column
- Download full reports as CSV
- Color-coded alerts (Critical = Red, Low = Yellow, Good = Green)

## 🚀 Quick Start

### Local Development

1. **Clone/Download** this repository

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the app:**
```bash
streamlit run app.py
```

4. **Open in browser:**
The app will automatically open at `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud (FREE)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial inventory dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/inventory-dashboard.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/inventory-dashboard`
5. Set main file path: `app.py`
6. Click "Deploy"
7. Your app will be live at: `https://YOUR_USERNAME-inventory-dashboard.streamlit.app`

### Step 3: Add to Your Portfolio

Once deployed, embed in your portfolio site:

```html
<iframe 
  src="https://YOUR_USERNAME-inventory-dashboard.streamlit.app/?embed=true" 
  width="100%" 
  height="800px" 
  frameborder="0"
></iframe>
```

Or simply link to it:
```markdown
[View Live Dashboard →](https://YOUR_USERNAME-inventory-dashboard.streamlit.app)
```

## 📊 Business Models Explained

### 1. Plant Nursery (Manufacturing)
**Scenario:** Growing and selling plants wholesale and retail

**Key Metrics:**
- Growth stages and pot sizes
- Supplier relationships
- Wholesale vs. retail pricing
- Plant-specific categories (tropicals, succulents, etc.)

**Use Case:** Shows understanding of manufacturing/production inventory where items are created over time.

### 2. Retail Storefront
**Scenario:** Boutique clothing store with multiple sizes and colors

**Key Metrics:**
- Size and color variants
- Seasonal inventory management
- Multi-attribute SKU tracking
- Traditional retail metrics

**Use Case:** Demonstrates classic retail inventory with variants and seasonal considerations.

### 3. Service Business
**Scenario:** Pressure washing/exterior cleaning company

**Key Metrics:**
- Consumables (chemicals, supplies)
- Equipment parts and maintenance
- Usage rates per job
- Safety equipment tracking
- Marketing materials

**Use Case:** Shows inventory for service-based businesses where supplies support operations rather than being sold directly.

## 🎨 Customization

### Change Colors
Edit the CSS in `app.py` (lines 17-35):
- Primary Navy: `#0A2540`
- Accent Coral: `#FF5757`
- Gold: `#F39C12`

### Add Your Own Data
Replace the CSV files in `/data/` with your own inventory data. Required columns:
- `sku` - Stock Keeping Unit
- `product_name` - Product name
- `quantity_on_hand` - Current stock level
- `reorder_point` - Minimum stock before reordering
- `cost_per_unit` - Cost per item

### Modify Metrics
Edit the calculation functions in `app.py`:
- `calculate_abc_analysis()` - ABC classification logic
- Stock status thresholds (currently 50% of reorder point = Critical)

## 📈 What This Dashboard Demonstrates

**For Data Analyst Roles:**
- Data visualization with Plotly
- KPI calculation and tracking
- Inventory turnover analysis
- ABC/Pareto analysis
- Business metrics knowledge

**For Business Operations:**
- Understanding of different business models
- Inventory management best practices
- Supply chain awareness
- Multi-attribute product tracking

**For Technical Skills:**
- Python (Pandas, Plotly)
- Streamlit framework
- Data manipulation and analysis
- Web app deployment

## 💡 Potential Enhancements

**Future Features to Add:**
- [ ] Time-series forecasting for reorder quantities
- [ ] Integration with Google Sheets for live data
- [ ] Email alerts for critical stock
- [ ] Supplier performance tracking
- [ ] Cost trend analysis over time
- [ ] Predictive analytics for seasonal demand
- [ ] Multi-location inventory tracking

## 📁 Project Structure

```
inventory-dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── data/
    ├── nursery_inventory.csv       # Plant nursery data
    ├── retail_inventory.csv        # Retail storefront data
    └── service_inventory.csv       # Service business data
```

## 🛠️ Tech Stack

- **Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly Express & Graph Objects
- **Deployment:** Streamlit Cloud (free hosting)

## 📝 License

Free to use for portfolio and learning purposes.

---

**Created by Andrew Felt**
[Portfolio](https://andrewfelt.com) | [GitHub](https://github.com/YOUR_USERNAME) | [LinkedIn](https://linkedin.com/in/YOUR_USERNAME)
