'''
Define the balance sheet tool used by the supervisor

'''

from pydantic import BaseModel
from langchain_core.tools import tool
from typing import List, Dict, Optional

from typing import List, Dict, Optional, Union
import requests
import os
from typing import Dict, Union
from pydantic import BaseModel, Field
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import json

class GetBalanceSheetsInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock")
    period: str = Field(default="ttm", description="The period of the balance sheets. Valid values are 'ttm' ,'quarterly' or 'annual'.")
    limit : int = Field(default=5, description="Maximum number of balance sheets to return. Default is 5")

@tool("get_balance_sheets", args_schema=GetBalanceSheetsInput, return_direct=True)
def get_balance_sheets(ticker: str, period: str ="ttm", limit: int=5) ->Union[Dict,str]:
    '''
    Get the balance sheet of a stock
    '''
    
    # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    
    url=(
        f'https://api.financialdatasets.ai/financials/balance-sheets'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )
    
    try:
        response =requests.get(url, headers={"x-api-key": api_key})
        return response.json()
    except Exception as e:
        return {"ticker": ticker, "balance_sheets":[], "error": str(e)}
    
if __name__ == "__main__":
    #pretty print the json
    print(json.dumps(get_balance_sheets("AAPL"), indent=2))
