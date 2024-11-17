'''
Define two tools
1. Get the stock prices for a given time range and interval
2. Get the latest stock price

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


class GetPricesInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock")
    start_date: str = Field(..., description="The start of the price time window. Either a data with the format YYYY-MM-DD or a millisecond timestamp ")
    end_date: str = Field(..., description="The end of rhe aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp ")
    interval: str= Field(default="day", description= "The time interval of the prices. Valid values are second, minute, day, week, month, quarter, year.")
    interval_multiplier: int = Field(default=1, description= "The multiplier for the interval. For example, if the interval is day and the interval_multiplier is 1, the prices will be daily. If the interval is minute and the interval_mulitplier is 5, then the prices will be every 5 minutes")
    limit :int = Field(default=5000, description="Maximum number of prices to return. Default is 5000 and the maximum is 50000")

@tool("get_stock_prices", args_schema=GetPricesInput, return_direct=True)
def get_stock_prices(ticker: str, start_date: str, end_date: str, interval: str, interval_multiplier: int=1, limit: int=5000) ->Union[Dict,str]:
    '''
    Get the stock prices for a given time range and interval
    '''
    
    # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    
    url=(
        f'https://api.financialdatasets.ai/prices'
        f'?ticker={ticker}'
        f'&start_date={start_date}'
        f'&end_date={end_date}'
        f'&interval={interval}'
        f'&interval_multiplier={interval_multiplier}'
        f'&limit={limit}'
    )
    
    try:
        response =requests.get(url, headers={"x-api-key": api_key})
        data= response.json()
        return data
    except Exception as e:
        return {"ticker": ticker, "prices":[], "error": str(e)}
    

class GetCurrentPriceInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock")

@tool("get_current_stock_price", args_schema=GetCurrentPriceInput, return_direct=True)
def get_current_stock_price(ticker: str) ->Union[Dict,str]:
    '''
    Get the latest stock price
    '''
     # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    
    url= f"https://api.financialdatasets.ai/prices/snapshot?ticker={ticker}"

    try:
        response =requests.get(url, headers={"x-api-key": api_key})
        return response.json()
    except Exception as e:
        return {"ticker": ticker, "price":None, "error": str(e)}

    
if __name__ == "__main__":
    #pretty print the json
    import json
    # print(json.dumps(get_current_stock_price("AAPL"), indent=2))
    print(json.dumps(get_stock_prices("AAPL", "2024-01-01", "2024-01-05", "day", 1, 10), indent=2))