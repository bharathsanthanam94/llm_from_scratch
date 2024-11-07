'''
Uses prebuilt langgraph ReACT agent to search the web using Tavily. 
This has a lot of abstractions and it not easy to interpret what 
the agent is doing.
'''
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from rich.console import Console

# initialize dotenv to load environment variables
load_dotenv()

#Rich initialize
rich= Console()

# initialize openAI LLM
llm= ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")

# initialize search tool
search= TavilySearchResults()

# create the agent
langgraph_agent= create_react_agent(model=llm, tools=[search])

def process_agent_outputs(chunk):
    if "agent" in chunk:
        for message in chunk["agent"]["messages"]:
            if "tool_calls" in message.additional_kwargs:
                tool_calls = message.additional_kwargs["tool_calls"]

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]

                    tool_arguments = eval(tool_call["function"]["arguments"])
                    tool_query = tool_arguments["query"]

                    rich.print(
                        f"\n The agent is calling the tool [on deep_sky_blue1]{tool_name}[/on deep_sky_blue1]", \
                        style="deep_sky_blue1",
                    )

            else:
                agent_message = message.content

                # display the agent answer
                rich.print(f"\nAgent:\n{agent_message}", style="black on white")

while True:
    user_input = input("\nEnter a query: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        rich.print("\n\nExiting the program...", style="bold red")
        break
    
    for chunk in langgraph_agent.stream({"messages": [HumanMessage(content=user_input)]}):
        process_agent_outputs(chunk)