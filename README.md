# Mizoram VB-G RAM G Report Portal & Worker Passbook

A lightweight, automated web application and data aggregator for **Mizoram State (VB-G RAM G)**, designed to provide a fast, clean, and mobile-friendly community mirror.

---

## Target Villages (19 Panchayats)

The application and scraper are focused on the following 19 villages/Panchayats:
> **Buhban, Dilkhan, Keifang Leitan, Keifang Venghlun, Keifang Venglai, Khanpui, Lailak, Lenchim, Lungpher, Maite, Mualpheng, Ruallung, Rulchawm, Saitual 1 (Saitual I), Saitual 3 (Saitual III), Saitual Venglai, Sihfa, Tawizo, Tualbung.**

---

## Features

1. **Global Village Selector Bar (Controls All Tabs)**
   - Located at the top of the application.
   - Switch between **"All My 19 Villages (Combined)"** or any single village.
   - All tabs (Job Cards, Muster Rolls, Incomplete Works, Financials) dynamically filter and recalculate their KPIs and counters based on the selected village.

2. **Active Job Cards Register (5,151 Active Households)**
   - Automatically filters out all deleted job cards marked with an asterisk (`*`).
   - Fast client-side pagination (25, 50, 100, 250 per page) and instant search by Job Card No. or Household Head.
   - One-click access to official government dossiers and the embedded Worker Passbook.

3. **Integrated Worker Payment Passbook**
   - Click `[💳 View Passbook]` directly next to any active Job Card to launch the worker's payment history modal.
   - Tracks monthly wage disbursement status: 🟢 **Credited**, 🟡 **Pending**, or 🔴 **Rejected**.
   - Explicitly displays **`Paid in account of (in case of ABP)`** to confirm the Aadhaar-linked beneficiary receiving DBT funds.
   - Shows Bank Name, Branch, UTR Reference Number, Processed Date, and direct link to the official signed FTO.

4. **Muster Rolls (eMR)**
   - Searchable directory of official eMR slips with exact **Work Description**, **Work Code**, and **Labor Period** (`Date From` to `Date To` + `Month`).

5. **Incomplete Works Tracker**
   - Tracks works started vs. completed vs. incomplete across the 19 Panchayats with progress KPIs and official drill-down links.

6. **Financial Master Work Statements**
   - Overview of work sanction budgets, wage disbursements, and material expenditure with direct eMR references.

---

## 100% Free Hosting & Daily Automation

### Running Locally
To test the web app locally:
1. Open terminal in this folder (`mizoram-reports-app`).
2. Run the scraper:
   ```bash
   python scraper.py
   ```
3. Start a local server:
   ```bash
   python -m http.server 8000
   ```
4. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Deploying to GitHub Pages (Free Setup)

1. Create a new GitHub repository (e.g. `mizoram-vbgramg-portal`).
2. Push the files in this directory to your new repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Mizoram VB-G RAM G dashboard"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings > Pages**.
   - Under **Build and deployment > Source**, select **Deploy from a branch**.
   - Select branch **`main`** and folder **`/ (root)`**, then click **Save**.
4. That's it! 
   - Your web app is live at `https://<your-username>.github.io/<your-repo-name>/`.
   - The workflow in `.github/workflows/daily-sync.yml` will automatically run every morning at 6:30 AM IST (01:00 UTC) to fetch the newest data and commit updates.
