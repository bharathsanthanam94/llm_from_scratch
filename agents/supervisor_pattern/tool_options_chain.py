'''
Define the options chain(call/put) tool used by the supervisor

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


class GetOptionsChainInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock")
    limit : int = Field(default=5, description="Maximum number of options to return. Default is 5")
    strike_price : Optional[float] = Field(default=None, description="Optional filter for specific strike price")
    option_type: Optional[str] = Field(default=None, description="Optional filter for option type. Valid values are 'call' or 'put'.")
@tool("get_options_chain", args_schema=GetOptionsChainInput, return_direct=True)
def get_options_chain(
    ticker: str, 
    limit: int = 5,
    strike_price : Optional[float] = None,
    option_type: Optional[str] = None
)->Union[Dict,str]:
    '''
    Get options chain data for a given stock with optional filters for strike price and options
    '''
    
    # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    params = {
        'ticker': ticker,
        'limit': limit
    }

    if strike_price is not None:
        params['strike_price'] = strike_price
    if option_type is not None:
        params['option_type'] = option_type
    url='https://api.financialdatasets.ai/options/chain'
    
    try:
        response =requests.get(url, headers={"x-api-key": api_key}, params=params)
        return response.json()
    except Exception as e:
        return {"ticker": ticker, "options_chain":[], "error": str(e)}
    
if __name__ == "__main__":
    #pretty print the json
    import json
    print(json.dumps(get_options_chain("AAPL"), indent=2))

