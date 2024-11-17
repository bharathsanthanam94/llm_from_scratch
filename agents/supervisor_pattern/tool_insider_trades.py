
'''
Define the insider transactions tool used by the supervisor

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



class GetInsiderTradesInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock.")
    limit: int = Field(default=10, description="The maximum number of insider transactions to return. Default is 10.")



@tool("get_insider_trades", args_schema=GetInsiderTradesInput, return_direct=True)
def get_insider_trades(ticker: str, limit: int = 10) -> Union[Dict, str]:
    """
    Get insider trading transactions for a ticker.
    """
    # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    

    url = (
        f'https://api.financialdatasets.ai/insider-transactions'
        f'?ticker={ticker}'
        f'&limit={limit}'
    )

    try:
        response = requests.get(url, headers={'X-API-Key': api_key})
        return response.json()
    except Exception as e:
        return {"ticker": ticker, "insider_transactions": [], "error": str(e)}
    
if __name__ == "__main__":
    #pretty print the json
    import json
    print(json.dumps(get_insider_trades("AAPL"), indent=2))

