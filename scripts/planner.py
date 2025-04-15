
# filepath: /Users/ujjwal/Documents/starkhack/trade-agent/examples/orchestrator.py
"""
This demonstrates creating multiple agents and an orchestrator to coordinate them.
"""

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("Orchestrator-Workers")

# Define worker agents

@fast.agent(
    name="jsonvalidator",
    instruction="""You are developer agent that can validate JSON files. Your task is to check the JSON file for syntax errors and return a boolean indicating whether the JSON is valid or not. You can use the test.json as reference.""",
    servers=['filesystem']
)

@fast.agent(
    name="router",
    instruction="""""",
    servers=['fetch', 'filesystem', 'google', 'twitter']
)

@fast.agent(
    name="writer",
    instruction="""You are an agent that can write to the filesystem. You are tasked with taking the user's input, addressing it, and writing the result to disk in the appropriate location.""",
    servers=['filesystem']
)

@fast.agent(
    name="proofreader",
    instruction="""Review the short story for grammar, spelling, and punctuation errors.Identify any awkward phrasing or structural issues that could improve clarity. Provide detailed feedback on corrections.""",
    servers=['fetch']
)

# Define the orchestrator to coordinate the other agents
@fast.orchestrator(
    name="orchestrate",
    agents=['author', 'finder', 'writer', 'proofreader'],
    plan_type="full",
)
async def main() -> None:
    async with fast.run() as agent:
        # The orchestrator can be used just like any other agent
        task = """Load the student's short story from short_story.md, and generate a report with feedback across proofreading, factuality/logical consistency and style adherence. Use the style rules from https://apastyle.apa.org/learn/quick-guide-on-formatting and https://apastyle.apa.org/learn/quick-guide-on-references. Write the graded report to graded_report.md in the same directory as short_story.md"""

        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
