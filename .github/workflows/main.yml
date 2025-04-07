name: Update ETH Holdings Daily 

on:
  schedule:
    - cron: '0 0 * * *' # UTC midnight
  workflow_dispatch: # optional: allows manual trigger from GitHub UI

jobs:
  run-script:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Chrome & ChromeDriver
      run: |
        sudo apt update
        sudo apt install -y wget unzip xvfb
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo apt install -y ./google-chrome-stable_current_amd64.deb
        CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3)
        wget -N https://chromedriver.storage.googleapis.com/$(echo $CHROME_VERSION | cut -d '.' -f 1-3)/chromedriver_linux64.zip || \
        wget -N https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
        unzip chromedriver_linux64.zip
        sudo mv -f chromedriver /usr/local/bin/chromedriver
        sudo chmod +x /usr/local/bin/chromedriver

    - name: Run script
      run: |
        xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' python eth_holdings.py

    - name: Commit changes
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add eth_holdings_data.csv
        git commit -m "Daily update: $(date -u '+%Y-%m-%d %H:%M:%S') UTC" || echo "No changes to commit"
        git push
