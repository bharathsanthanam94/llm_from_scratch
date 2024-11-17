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


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal, Sequence, Annotated
from typing_extensions import TypedDict
import functools
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent

from langchain_community.tools.tavily_search import TavilySearchResults
# Define team members


from tool_cash_flow_statements import get_cash_flow_statements
from tool_balance_sheets import get_balance_sheets
from tool_stock_prices import get_stock_prices, get_current_stock_price
from tool_income_statement import get_income_statements 
from tool_options_chain import get_options_chain
from tool_insider_trades import get_insider_trades
from utils import *

# load API keys
load_dotenv()

rich = Console()

# News tool, use Tavily
get_news_tool = TavilySearchResults(max_results=5)


fundamental_tools = [get_income_statements, get_balance_sheets, get_cash_flow_statements]
# technical_tools = [get_stock_prices, get_current_stock_price]
technical_tools =[get_stock_prices, get_current_stock_price]
sentiment_tools = [get_options_chain, get_insider_trades, get_news_tool]


from langchain_core.messages import HumanMessage

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, name=name)]
    }


# Define team members
members = ["fundamental_analyst", "technical_analyst", "sentiment_analyst"]


# this is the supervisor prompt, routing the messages to the right analyst
system_prompt = (
    "You are a portfolio manager supervising a hedge fund team with the following analysts:"
    "{members}. Each analyst has specific expertise:"
    "\n- fundamental_analyst: Analyzes financial statements and company health"
    "\n- technical_analyst: Analyzes price patterns and market trends"
    "\n- sentiment_analyst: Analyzes insider trading activity, options flow, and the news"
    "\nGiven the user request, determine which analyst should act next."
    "Each analyst will analyze one ticker and provide their findings."
    "When all necessary analysis is compete, respond with FINISH." 
)

# summary prompt template

summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", 
         "You are a portfolio manager responsible for synthesizing analysis from your team of analysts. "
        "Review all the analysts' reports and provide a comprehensive summary including:\n"
            "1. Key financial metrics and their implications\n"
            "2. Technical analysis insights\n"
            "3. Market sentiment and news impact\n"
            "4. Overall investment recommendation\n"
            "Make sure to highlight any discrepancies or conflicting signals between different analyses."
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            "Based on all the analyst reports above, provide a comprehensive summary and investment recommendation."

        ),

    ]
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")

def supervisor_agent(state):
    message = HumanMessage(content="Proceed with the analysts.",name="supervisor")
    return {
        "messages": state["messages"] + [message]
    }

def final_summary_agent(state):
    summary_chain = summary_prompt | llm
    result= summary_chain.invoke(state)
    return {
        "messages": [HumanMessage(content=result.content, name="portfolio_manager")]

    }

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],operator.add]


#create the workflow
workflow= StateGraph(AgentState)

# create the analysts
fundamental_analyst = create_react_agent(llm,tools=fundamental_tools)
fundamental_analyst_node=functools.partial(agent_node, agent=fundamental_analyst, name="fundamental_analyst")

technical_analyst = create_react_agent(llm, tools=technical_tools)
technical_analyst_node=functools.partial(agent_node, agent=technical_analyst, name="technical_analyst")

sentiment_analyst = create_react_agent(llm, tools=sentiment_tools)
sentiment_analyst_node=functools.partial(agent_node, agent=sentiment_analyst, name="sentiment_analyst")

# add nodes
workflow.add_node("fundamental_analyst", fundamental_analyst_node)
workflow.add_node("technical_analyst", technical_analyst_node)
workflow.add_node("sentiment_analyst", sentiment_analyst_node)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("final_summary", final_summary_agent)

for member in members:
    workflow.add_edge("supervisor", member)

for member in members:
    workflow.add_edge(member, "final_summary")

workflow.add_edge(START, "supervisor")
workflow.add_edge("final_summary", END)

graph = workflow.compile()

input_data = {
    "messages": [HumanMessage(content="What is the latest news, stock price, and revenue for AAPL?")]
}
config = {"recursion_limit": 5}
stream_agent_execution(graph, input_data, config)