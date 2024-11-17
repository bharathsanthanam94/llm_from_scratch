'''
Define the cash flow statements used by the supervisor

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
from dotenv import load_dotenv


class GetCashFlowStatementsInput(BaseModel):
    ticker: str = Field(..., description="The ticker of the stock")
    period: str = Field(default="ttm", description="The period of the cash flow statements. Valid values are 'ttm' ,'quarterly' or 'annual'.")
    limit : int = Field(default=5, description="Maximum number of cash flow statements to return. Default is 5")

@tool("get_cash_flow_statements", args_schema=GetCashFlowStatementsInput, return_direct=True)
def get_cash_flow_statements(ticker: str, period: str ="ttm", limit: int=5) ->Union[Dict,str]:
    '''
    Get the cash flow statements of a stock
    '''
    
    # get the API key using load_dotenv
    load_dotenv()
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("FINANCIAL_DATASETS_API_KEY not found in environment variables")
    
    url=(
        f'https://api.financialdatasets.ai/financials/cash-flow-statements'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )
    
    try:
        response =requests.get(url, headers={"x-api-key": api_key})
        return response.json()
    except Exception as e:
        return {"ticker": ticker, "cash_flow_statements":[], "error": str(e)}
    
if __name__ == "__main__":

    #pretty print the json
    import json
    print(json.dumps(get_cash_flow_statements("AAPL"), indent=2))

  