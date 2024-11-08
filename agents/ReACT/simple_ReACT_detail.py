''''
Let's build the graph of the ReACT agent manually in LangGraph.
Also track the tool calls and the agent's thought process!
'''

import os
from typing import TypedDict, Annotated
import operator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.messages import HumanMessage
from rich.console import Console
from PIL import Image as PILImage
import ipdb
# initialize dotenv to load environment variables
load_dotenv()

#Rich initialize
rich= Console()

tool = TavilySearchResults(max_results=2)
# print(type(tool))
# print(tool.name)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class Agent:

    def __init__(self, model, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if not t['name'] in self.tools:      # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("Back to the model!")
        return {"messages":results}


prompt= """
You are a smart research assistant. Use the search engine to look up information.
You are allowed to make multiple calls (either together or in sequence).
Only look up information when you are sure of what you want.
If you need to look up some information before asking a follow up question, you are allowed to do that!

"""

model = ChatOpenAI(model="gpt-4-turbo")
abot= Agent(model, [tool], system=prompt)
png_data = abot.graph.get_graph().draw_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
img = PILImage.open("graph.png")
img.show()
# Run the agent!

messages= [HumanMessage(content="Who won the 2024 T20 mens cricket world cup and what is the GDP of that country?")]

result= abot.graph.invoke({"messages":messages})
rich.print(result['messages'][-1].content)







