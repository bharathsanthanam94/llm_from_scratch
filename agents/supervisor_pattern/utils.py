from typing import Dict, Any, List, Optional, Union
import json
import re
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

console = Console()

def format_bold_text(content: str) -> Text:
    """Convert **text** to rich Text with bold formatting."""
    text = Text()

    print(content)
    pattern = r'\*\*(.*?)\*\*'

    # Split the text by the bold markers
    parts = re.split(pattern, content)

    # Alternate between regular and bold text
    for i, part in enumerate(parts):
        if i % 2 == 0:
            text.append(part)
        else:
            text.append(part, style="bold")

    return text

def format_message_content(content: str) -> Union[str, Text]:
    """Format the message content, handling JSON and text with bold markers."""
    try:
        # Try to parse as JSON for prettier formatting
        data = json.loads(content)
        return json.dumps(data, indent=2)
    except:
        # If not JSON, check for bold markers
        if '**' in content:
            return format_bold_text(content)
        return content

def format_agent_message(message: HumanMessage) -> Union[str, Text]:
    """Format a single agent message."""
    return format_message_content(message.content)

def get_agent_title(agent: str, message: HumanMessage) -> str:
    """Get the title for the agent panel, with fallback handling."""
    base_title = agent.replace('_', ' ').title()

    if hasattr(message, 'name') and message.name is not None:
        try:
            return message.name.replace('_', ' ').title()
        except:
            return base_title
    return base_title

def print_step(step: Dict[str, Any]) -> None:
    """Pretty print a single step of the agent execution."""
    for agent, data in step.items():
        # Handle supervisor steps
        if 'next' in data:
            next_agent = data['next']
            text = Text()
            text.append("Portfolio Manager ", style="bold magenta")
            text.append("assigns next task to ", style="white")

            if next_agent == "final_summary":
                text.append("FINAL SUMMARY", style="bold yellow")
            elif next_agent == "END":
                text.append("END", style="bold red")
            else:
                text.append(f"{next_agent}", style="bold green")

            console.print(Panel(
                text,
                title="[bold blue]Supervision Step",
                border_style="blue"
            ))

        # Handle agent responses and final summary
        if 'messages' in data:
            message = data['messages'][0]
            formatted_content = format_agent_message(message)

            if agent == "final_summary":
                # Final summary formatting
                console.print(Rule(style="yellow", title="Portfolio Analysis"))
                console.print(Panel(
                    formatted_content,
                    title="[bold yellow]Investment Summary and Recommendation",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                console.print(Rule(style="yellow"))
            else:
                # Regular analyst reports
                title = get_agent_title(agent, message)
                console.print(Panel(
                    formatted_content,
                    title=f"[bold blue]{title} Report",
                    border_style="green"
                ))

def stream_agent_execution(graph, input_data: Dict, config: Dict) -> None:
    """Stream and pretty print the agent execution."""
    console.print("\n[bold blue]Starting Agent Execution...[/bold blue]\n")

    for step in graph.stream(input_data, config):
        if "__end__" not in step:
            print_step(step)
            console.print("\n")

    console.print("[bold blue]Analysis Complete[/bold blue]\n")