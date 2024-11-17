# Multi-Agent Stock Analysis System

## Overview

This project implements a multi-agent system for comprehensive financial investment analysis using LangChain and LangGraph. The system mimics a hedge fund's analytical structure, employing multiple specialized agents that work together to provide detailed stock analysis and investment recommendations.

## Architecture

### Agent Structure

The system uses a supervisor pattern with three specialized analysts:

1. **Fundamental Analyst**

   - Analyzes company financial health
   - Reviews income statements, balance sheets, and cash flow statements
   - Evaluates company's financial metrics and performance
2. **Technical Analyst**

   - Focuses on price patterns and market trends
   - Analyzes historical and current stock prices
   - Identifies technical indicators and patterns
3. **Sentiment Analyst**

   - Monitors market sentiment and news
   - Tracks insider trading activity
   - Analyzes options chain data
   - Reviews latest news and market sentiment
4. **Portfolio Manager (Supervisor)**

   - Coordinates analysis between different analysts
   - Ensures comprehensive coverage of analysis
   - Synthesizes findings into final recommendations

### Control Flow

1. User query is received
2. Supervisor routes the query to appropriate analysts
3. Analysts perform their specialized analysis using their tools
4. Results are collected and synthesized into a final summary
5. Comprehensive investment recommendation is generated

## Tools and APIs

### Fundamental Analysis Tools

- `get_income_statements`: Retrieves company income statements
- `get_balance_sheets`: Fetches balance sheet data
- `get_cash_flow_statements`: Obtains cash flow statement information

### Technical Analysis Tools

- `get_stock_prices`: Historical price data with customizable intervals
- `get_current_stock_price`: Real-time stock price information

### Sentiment Analysis Tools

- `get_options_chain`: Options market data
- `get_insider_trades`: Insider trading activity
- `get_news_tool`: News aggregation via Tavily

## Setup and Configuration

### Prerequisites

- Python 3.10.12
- OpenAI API key
- Financial Datasets API key ([link](https://www.financialdatasets.ai/))
- Tavily API key ([link](https://tavily.com/))
- Dependencies are managed with Poetry
  - Once the repo is cloned,  do `poetry install` to install dependencies and poetry installs all dependencies in a virtual environment. do `poetry shell` to activate the virtual environment

### Environment Variables

Create a `.env` file with the API keys

### Acknowledgements

The entire project idea is from Virat ([link](https://x.com/virattt))
