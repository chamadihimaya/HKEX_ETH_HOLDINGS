#!/usr/bin/env python
# coding: utf-8

# In[21]:


import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import numpy as np
from datetime import datetime
import os


# In[22]:


def fetch_and_store_9009():

    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the URL
    url_9009 = 'https://www.bosera.com.hk/en-US/products/fund/detail/ETHL'
    driver.get(url_9009)
    time.sleep(5)

    # Get page source after JavaScript has executed
    html = driver.page_source
    soup_9009 = BeautifulSoup(html, 'lxml')

    # Close the Selenium driver
    driver.quit()

    # Extract ETH Holdings
    all_tds_9009 = soup_9009.find_all('td', {'class': 'ant-table-cell'})
    eth_holdings_9009 = all_tds_9009[169].get_text(strip=True)
    eth_holdings_9009 = float(eth_holdings_9009.replace(',', ''))

    # Extract the date
    date_9009 = all_tds_9009[1].get_text(strip=True)
    date_9009 = datetime.strptime(date_9009, '%d/%m/%Y')
    date_9009 = date_9009.strftime('%Y-%m-%d')

    print(date_9009)
    print(eth_holdings_9009)
    print('9009')

    # Return data
    return(date_9009, eth_holdings_9009)


# In[23]:


def fetch_and_store_9046():

    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the URL
    url_9046 = 'https://www.chinaamc.com.hk/product/chinaamc-ether-etf/#Holdings'
    driver.get(url_9046)
    time.sleep(5)

    # Get page source after JavaScript has executed
    html = driver.page_source
    soup_9046 = BeautifulSoup(html, 'lxml')

    # Close the Selenium driver
    driver.quit()

    # Net Asset Value (mil)
    table_nav = soup_9046.find('table', {'class': 'amc-table fund-overview'})
    rows_nav = table_nav.find_all('tr')
    nav = None
    for row in rows_nav:
        cells = row.find_all('td')
        if 'Net Asset Value (mil)' in cells[0].get_text(strip=True):
            nav = cells[1].get_text(strip=True)
            break
    nav = float(nav.replace(',', '')) * 1000000

    # Closing Level
    table_cl = soup_9046.find('table', {'class': 'amc-table index-information'})
    rows_cl = table_cl.find_all('tr')
    closing_level = None
    for row in rows_cl:
        cells = row.find_all('td')
        if 'Closing Level' in cells[0].get_text(strip=True):
            closing_level = cells[1].get_text(strip=True)
            break
    closing_level = float(closing_level.replace(',', ''))

    # Weighting %
    tables = soup_9046.find_all('table', {'class': 'amc-table'})
    table_w = tables[7]
    rows_w = table_w.find_all('tr')
    weighting = None
    for row_w in rows_w:
        cells_w = row_w.find_all('td')
        if cells_w and 'VA ETHEREUM CURRENCY' in cells_w[0].get_text(strip=True):
            weighting = cells_w[1].get_text(strip=True)
            break
    weighting = float(weighting)

    # Calculate ETH Holdings
    eth_holdings_9046 = (nav * weighting / 100) / closing_level

    # Extract the date
    all_ps_9046 = soup_9046.find_all('p', {'class': 'as-of-date'})
    date_9046 = all_ps_9046[1].get_text(strip=True).replace('As of ', '')
    date_9046 = datetime.strptime(date_9046, '%d-%m-%Y').strftime('%Y-%m-%d')

    print(date_9046)
    print(eth_holdings_9046)
    print('9046')

    return(date_9046, eth_holdings_9046)


# In[24]:


def fetch_and_store_9179():

    # Step 1: Fetch the ETH price from BOS bitcoin
    url_9009 = 'https://www.bosera.com.hk/en-US/products/fund/detail/ETHL'
    response_9009 = requests.get(url_9009)
    soup_9009 = BeautifulSoup(response_9009.content, 'lxml')

    # Locate the price
    all_tds_9009 = soup_9009.find_all('td', {'class': 'ant-table-cell'})
    price = all_tds_9009[3].get_text(strip=True)
    print(price)
    price = float(price.replace(',', ''))

    # Step 2: Use Selenium to fetch AUM data from HKEX
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    url_9179 = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sym=9179&sc_lang=en"
    driver.get(url_9179)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the AUM element
    aum_element_9179 = soup.find('dt', {'class': 'ico_data col_aum'})
    aum_9179 = aum_element_9179.text.strip() if aum_element_9179 else "N/A"

    # Extract and convert AUM to float
    if aum_9179 != "N/A":
        aum_9179 = aum_9179[3:]  # Remove "US$"
        aum_9179 = float(aum_9179[:-1].replace(',', '')) * 1000000

    driver.quit()

    # Calculate ETH Holdings
    eth_holdings_9179 = aum_9179 / price if price != 0 else 0

    # Step 3: Scrape and format the date
    date_9179_element = soup.find('dt', {'class': 'ico_data col_aum_date'})
    date_9179 = date_9179_element.text.strip() if date_9179_element else "N/A"

    if date_9179 != "N/A":
        date_9179 = date_9179.replace('as at ', '').replace('(', '').replace(')', '').strip()
        date_9179 = datetime.strptime(date_9179, '%d %b %Y').strftime('%Y-%m-%d')

    print(date_9179)
    print(eth_holdings_9179)
    print('9179')

    return(date_9179, eth_holdings_9179)


# In[25]:


def fetch_price():
    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the URL
    url_9009 = 'https://www.bosera.com.hk/en-US/products/fund/detail/ETHL'
    driver.get(url_9009)
    time.sleep(5)

    # Get page source after JavaScript has executed
    html = driver.page_source
    soup_9009 = BeautifulSoup(html, 'lxml')

    # Close the Selenium driver
    driver.quit()

    # Extract the price
    all_tds_9009 = soup_9009.find_all('td', {'class': 'ant-table-cell'})
    price = all_tds_9009[3].get_text(strip=True)
    price = float(price.replace(',', ''))

    # Extract the date
    price_date = all_tds_9009[1].get_text(strip=True)
    price_date = datetime.strptime(price_date, '%d/%m/%Y').strftime('%Y-%m-%d')

    return price_date, price


# In[26]:


def store_data_in_csv(Data):

    # Path to the CSV file
    csv_file_path = "eth_holdings_data.csv"

    # Load existing data if the CSV exists
    if os.path.exists(csv_file_path):
        df_existing = pd.read_csv(csv_file_path)
    else:
        df_existing = pd.DataFrame(columns=["DATE", "ETH_HOLDINGS_9009", "ETH_HOLDINGS_9046", "ETH_HOLDINGS_9179", "INFLOW_OUTFLOW_9009","INFLOW_OUTFLOW_9046", "INFLOW_OUTFLOW_9179", "PRICE", "VALUE_9009", "VALUE_9046", "VALUE_9179"])

   # Convert new data to a DataFrame
    df_new = pd.DataFrame([Data])


    df_combined = pd.concat([df_existing, df_new])

    # sort by index
    df_combined = df_combined.sort_values(by="DATE").reset_index(drop=True)

    # Calculate inflow/outflow for each type of bitcoin holding
    for holding in ["9009", "9046", "9179"]:
        holding_col = f"ETH_HOLDINGS_{holding}"
        inflow_outflow_col = f"INFLOW_OUTFLOW_{holding}"

        # Ensure numeric values for calculation
        df_combined[holding_col] = pd.to_numeric(df_combined[holding_col], errors="coerce")

        # Calculate the inflow/outflow
        df_combined[inflow_outflow_col] = df_combined[holding_col].diff()

    # Calculate the value for each holding
    for holding in ["9009", "9046", "9179"]:
        holding_col = f"ETH_HOLDINGS_{holding}"
        value_col = f"VALUE_{holding}"

        # Calculate the value (price * holdings)
        df_combined[value_col] = df_combined[holding_col] * df_combined["PRICE"]

    df_combined = df_combined.drop_duplicates(subset=["DATE"], keep="last")
    print(df_combined)

    df_combined.replace("-", np.nan, inplace=True)
    df_combined.fillna(method='ffill', inplace=True)


    # Save the updated DataFrame back to the CSV file
    df_combined.to_csv(csv_file_path, index=False)


# In[27]:


def update_price_in_csv(price, price_date):

    csv_file_path="eth_holdings_data.csv"

    """
    Updates the price in the 'PRICE' column where the date matches the given price_date.

    Parameters:
    - price (float): The new price to update.
    - price_date (str): The date (in 'YYYY-MM-DD' format) to match and update the price.
    - csv_file_path (str): Path to the CSV file (default is 'eth_holdings_data.csv').
    """
    # Check if the file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"The file '{csv_file_path}' does not exist.")

    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Ensure the DATE column exists
    if "DATE" not in df.columns:
        raise KeyError("'DATE' column is missing in the CSV file.")

    # Update the price where the DATE matches the price_date
    df.loc[df["DATE"] == price_date, "PRICE"] = price

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, index=False)

    print(f"Price updated to {price} for date {price_date} in '{csv_file_path}'.")


# In[28]:


def update_dollar_values(price_date):

  csv_file_path="eth_holdings_data.csv"

  # Check if the file exists
  if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"The file '{csv_file_path}' does not exist.")

  # Load the CSV into a DataFrame
  df = pd.read_csv(csv_file_path)

  # Ensure the DATE column exists
  if "DATE" not in df.columns:
      raise KeyError("'DATE' column is missing in the CSV file.")


  # Calculate the value for each holding
  df.loc[df["DATE"] == price_date]
  for holding in ["9009", "9046", "9179"]:
      inflow_outflow_col = f"INFLOW_OUTFLOW_{holding}"
      value_col = f"VALUE_{holding}"

      # Calculate the value (inflow_outflow * holdings) for the matching price_date
      df.loc[df["DATE"] == price_date, value_col] = df.loc[df["DATE"] == price_date, inflow_outflow_col] * df["PRICE"]


  # Save the updated DataFrame back to the CSV file
  df.to_csv(csv_file_path, index=False)

  print(f"Dollar values updated to {price} for date {price_date} in '{csv_file_path}'.")


# In[29]:


date_9009, eth_holdings_9009 = fetch_and_store_9009()


# In[30]:


date_9046, eth_holdings_9046 = fetch_and_store_9046()


# In[31]:


date_9179, eth_holdings_9179 = fetch_and_store_9179()


# In[32]:


price_date, price = fetch_price()


# In[33]:


print(date_9009, eth_holdings_9009)


# In[34]:


print(date_9046, eth_holdings_9046)


# In[35]:


print(date_9179, eth_holdings_9179)


# In[36]:


Data = {
        "DATE": date_9009,
        "ETH_HOLDINGS_9009": eth_holdings_9009,
        "ETH_HOLDINGS_9046": eth_holdings_9046,
        "ETH_HOLDINGS_9179": eth_holdings_9179,
        "INFLOW_OUTFLOW_9009": "",
        "INFLOW_OUTFLOW_9046": "",
        "INFLOW_OUTFLOW_9179": "",
        "PRICE": price,
        "VALUE_9009": "",
        "VALUE_9046": "",
        "VALUE_9179": "",
        }


# In[37]:


store_data_in_csv(Data)


# In[38]:


update_price_in_csv(price, price_date)


# In[39]:


# Call this function at the end
update_dollar_values(price_date)


# In[ ]:




