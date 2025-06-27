#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import os
import logging


# In[4]:


# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("🌸 Starting AUM + ETH holdings scraper")


# In[5]:


# ------------------ File Path ------------------
csv_file_path = "eth_holdings_summary.csv"


# In[6]:


# ------------------ Selenium Setup ------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# In[7]:


# ------------------ Function: Scrape AUM from HKEX ------------------
def get_aum_and_time(sym):
    try:
        url = f"https://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sym={sym}&sc_lang=en"
        driver.get(url)
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        aum_element = soup.find('dt', {'class': 'ico_data col_aum'})
        aum_value = "N/A"
        if aum_element:
            aum_text = aum_element.text.strip().replace("US$", "").replace(",", "")
            if aum_text.endswith("M"):
                aum_value = float(aum_text[:-1]) * 1_000_000

        time_element = soup.find('dt', {'class': 'ico_data col_aum_date'})
        update_time = time_element.text.strip().replace("as at ", "").replace("(", "").replace(")", "") if time_element else "N/A"
        if update_time != "N/A":
            update_time = datetime.strptime(update_time, "%d %b %Y").strftime("%d-%m-%Y")

        return aum_value, update_time
    except Exception as e:
        logging.error(f"❌ Error scraping AUM for {sym}: {e}")
        return "N/A", "N/A"


# In[8]:


# ------------------ Function: Scrape ETHUSD_AP Price ------------------
def scrape_ethusd_ap_price():
    try:
        url = "https://www.cfbenchmarks.com/data/indices/ETHUSD_AP"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        price_span = soup.select_one('div.leading-6 span.text-sm.font-semibold.tabular-nums.md\\:text-2xl')
        if price_span:
            price_str = price_span.text.strip().replace('$', '').replace(',', '')
            return float(price_str)
    except Exception as e:
        logging.error(f"❌ Failed to scrape ETHUSD_AP: {e}")
    return None


# In[9]:


# ------------------ Function: Save ETH Holdings Summary ------------------
def save_eth_holdings_summary(date, price, aum_9009, aum_9046, aum_9179, file_path=csv_file_path):
    eth_9009 = aum_9009 / price if aum_9009 != "N/A" else None
    eth_9046 = aum_9046 / price if aum_9046 != "N/A" else None
    eth_9179 = aum_9179 / price if aum_9179 != "N/A" else None

    prev_9009 = prev_9046 = prev_9179 = None
    if os.path.exists(file_path):
        try:
            df_prev = pd.read_csv(file_path)
            if not df_prev.empty:
                last_row = df_prev.iloc[-1]
                prev_9009 = last_row["eth_holdings_9009"]
                prev_9046 = last_row["eth_holdings_9046"]
                prev_9179 = last_row["eth_holdings_9179"]
        except Exception as e:
            logging.warning(f"⚠️ Couldn't read previous holdings: {e}")

    flow_9009 = eth_9009 - prev_9009 if prev_9009 is not None else None
    flow_9046 = eth_9046 - prev_9046 if prev_9046 is not None else None
    flow_9179 = eth_9179 - prev_9179 if prev_9179 is not None else None

    row = {
        "date": date,
        "price": price,
        "eth_holdings_9009": eth_9009,
        "eth_holdings_9046": eth_9046,
        "eth_holdings_9179": eth_9179,
        "inflow_outflow_9009": flow_9009,
        "inflow_outflow_9046": flow_9046,
        "inflow_outflow_9179": flow_9179,
    }

    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame(columns=row.keys())

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(file_path, index=False)
        logging.info("✅ ETH holdings and inflows/outflows saved successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to save CSV: {e}")


# In[10]:


# ------------------ Main Scraping Logic ------------------
try:
    aum_9009, time_9009 = get_aum_and_time("9009")
    aum_9046, time_9046 = get_aum_and_time("9046")
    aum_9179, time_9179 = get_aum_and_time("9179")
finally:
    driver.quit()


# In[12]:


# Get the date from the scrape (fallback if N/A)
current_date = time_9009 if time_9009 != "N/A" else datetime.now().strftime("%d-%m-%Y")


# In[13]:


# Get ETH price from CF Benchmarks
eth_price = scrape_ethusd_ap_price()
if eth_price:
    save_eth_holdings_summary(
        date=current_date,
        price=eth_price,
        aum_9009=aum_9009,
        aum_9046=aum_9046,
        aum_9179=aum_9179
    )
else:
    logging.error("ETH price is missing — skipping save step.")

logging.info("🌼 Script completed successfully.")


# In[ ]:




