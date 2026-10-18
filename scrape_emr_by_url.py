"""
Scrape authoritative Working Period ('Date From' and 'Date To') directly
from official Musternew.aspx sheets for all 1,586 UNIQUE Muster Roll URLs.
Crucial: MUST key by unique URL, NOT by muster_roll_no (which has 423 duplicate numbers across GPs!).
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_JSON = os.path.join(BASE_DIR, "data", "latest.json")
CACHE_FILE = os.path.join(BASE_DIR, "data", "emr_url_dates_cache.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def fetch_emr_working_dates(item):
    url = item.get('link', '')
    if not url:
        return url, "", ""
        
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=14) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                # Official exact Span IDs for Working Period
                s_from = soup.find('span', id='ContentPlaceHolder1_lbldatefrom')
                s_to = soup.find('span', id='ContentPlaceHolder1_lbldateto')
                
                d_from = s_from.get_text(strip=True) if s_from else ""
                d_to = s_to.get_text(strip=True) if s_to else ""
                
                # Fallback regex if span IDs differ
                if not d_from:
                    m = re.search(r'Date\s*From[^\d]*(\d{1,2}/\d{1,2}/\d{4})', html, re.I)
                    if m:
                        d_from = m.group(1)
                if not d_to:
                    m = re.search(r'Date\s*To[^\d]*(\d{1,2}/\d{1,2}/\d{4})', html, re.I)
                    if m:
                        d_to = m.group(1)
                        
                return url, d_from, d_to
        except Exception:
            if attempt < 3:
                time.sleep(1.0 + attempt * 0.5)
    return url, "", ""

def main():
    print("=" * 60)
    print("  SCRAPING AUTHORITATIVE eMR WORKING DATES BY UNIQUE URL")
    print("=" * 60)
    
    with open(LATEST_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    emrs = data.get('muster_rolls', [])
    print(f"Loaded {len(emrs)} muster rolls from latest.json.")
    
    cache = load_cache()
    print(f"Loaded {len(cache)} pre-cached URL entries.")
    
    to_fetch = [m for m in emrs if m.get('link') and (m['link'] not in cache or not cache[m['link']].get('date_from'))]
    print(f"Need to fetch dates for {len(to_fetch)} eMR URLs...")
    
    if to_fetch:
        start_time = time.time()
        completed = 0
        total = len(to_fetch)
        
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = {executor.submit(fetch_emr_working_dates, m): m for m in to_fetch}
            for fut in as_completed(futures):
                url, d_from, d_to = fut.result()
                if d_from:
                    cache[url] = {
                        "date_from": d_from,
                        "date_to": d_to
                    }
                completed += 1
                if completed % 50 == 0 or completed == total:
                    save_cache(cache)
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"  [{completed}/{total}] cached ({rate:.1f} req/s)...")
                    
        save_cache(cache)
        print(f"All {len(cache)} eMR URLs processed in {time.time() - start_time:.1f}s.")
        
    # Update latest.json
    month_counts = {}
    updated_count = 0
    
    for m in emrs:
        url = m.get('link', '')
        c_entry = cache.get(url)
        if c_entry and c_entry.get('date_from'):
            actual_from = c_entry['date_from']
            actual_to = c_entry['date_to']
            
            # Preserve original payment voucher date
            if 'payment_date' not in m or not m['payment_date']:
                m['payment_date'] = m.get('date_from', '')
                
            m['date_from'] = actual_from
            m['date_to'] = actual_to
            m['work_period'] = f"{actual_from} – {actual_to}" if actual_to else actual_from
            
            # Calculate Month strictly from actual physical work start date
            parts = actual_from.split('/')
            if len(parts) == 3:
                try:
                    dt = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                    mon = dt.strftime('%B %Y')
                except Exception:
                    mon = 'Other'
            else:
                mon = 'Other'
                
            m['work_month'] = mon
            month_counts[mon] = month_counts.get(mon, 0) + 1
            updated_count += 1
            
    # Also update master works emr_links in financial_statement
    for w in data.get('financial_statement', []):
        for l in w.get('emr_links', []):
            url = l.get('url', '')
            c_entry = cache.get(url)
            if c_entry and c_entry.get('date_from'):
                l['date_from'] = c_entry['date_from']
                l['date_to'] = c_entry['date_to']
                l['work_period'] = f"{c_entry['date_from']} – {c_entry['date_to']}"
                
    with open(LATEST_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        
    print("=" * 60)
    print(f" [SUCCESS] Updated {updated_count} eMRs in latest.json with URL-keyed working periods!")
    print(f" [TRUE MONTH DISTRIBUTION ACCORDING TO ACTUAL WORK DATES]:")
    for mon, count in sorted(month_counts.items(), key=lambda x: x[0]):
        print(f"    🗓️  {mon}: {count} eMRs")
    print("=" * 60)

if __name__ == '__main__':
    main()
