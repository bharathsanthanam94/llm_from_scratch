import requests
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
# add your API key to the headers
headers = {
    "X-API-KEY": api_key
}

# set your query params
ticker = 'NVDA'     # stock ticker
period = 'ttm'   # possible values are 'annual', 'quarterly', or 'ttm'
limit = 5         # number of statements to return

# create the URL
url = (
    f'https://api.financialdatasets.ai/financials/income-statements'
    f'?ticker={ticker}'
    f'&period={period}'
    f'&limit={limit}'
)

# make API request
response = requests.get(url, headers=headers)

# parse balance_sheets from the response
income_statements = response.json().get('income_statements')

#pretty print json
import json
print(json.dumps(income_statements, indent=2))

