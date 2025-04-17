import json
import os
import sys

def generate_agent_code(config, base_path="generated"):
    # Generate orchestrator.py
    orchestrator_content = f"""
# filepath: /Users/ujjwal/Documents/starkhack/trade-agent/examples/orchestrator.py
\"\"\"
This demonstrates creating multiple agents and an orchestrator to coordinate them.
\"\"\"

import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("Orchestrator-Workers")

# Define worker agents
"""
    for agent in config["agents"]:
        orchestrator_content += f"""
@fast.agent(
    name="{agent['agent']}",
    instruction=\"\"\"{agent['agent_instruction']}\"\"\",
    servers={[mcp['mcp_name'] for mcp in agent['mcps']]}
)
"""
    orchestrator_content += f"""
# Define the orchestrator to coordinate the other agents
@fast.orchestrator(
    name="orchestrate",
    instruction="Have minumum number of steps to accomplish the task while deciding the plan as speed is crucial, avoid unnecessary steps",
    agents={[agent['agent'] for agent in config["agents"]]},
    plan_type="full",
    max_iterations=1,
)
async def main() -> None:
    async with fast.run() as agent:
        # The orchestrator can be used just like any other agent
        task = \"\"\"{config["orchestrator"]["task"]}\"\"\"

        await agent.orchestrate(task)
        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
"""

    # Write orchestrator.py
    os.makedirs(base_path, exist_ok=True)
    with open(f"{base_path}/orchestrator.py", "w") as orchestrator_file:
        orchestrator_file.write(orchestrator_content)

    # Generate fastagent.secrets.yaml
    secrets_content = f"""
# filepath: /Users/ujjwal/Documents/starkhack/trade-agent/fastagent.secrets.yaml
# FastAgent Secrets Configuration
# WARNING: Keep this file secure and never commit to version control

openai:
    api_key: <your-api-key-here>
anthropic:
    api_key: {os.getenv("ANTHROPIC_API_KEY")}

mcp:
    servers:
"""
    for agent in config["agents"]:
        for mcp in agent["mcps"]:
            if not 'mcp_env' in mcp:
                continue
            secrets_content += f"""
        {mcp['mcp_name']}:
            env:"""
            for key, value in mcp['mcp_env'].items():
                secrets_content += f"""
                {key}: \"{value}\"
"""

    # Write fastagent.secrets.yaml
    with open(f"{base_path}/fastagent.secrets.yaml", "w") as secrets_file:
        secrets_file.write(secrets_content)

    # Generate fastagent.config.yaml
    config_content = f"""
# filepath: /Users/ujjwal/Documents/starkhack/trade-agent/fastagent.config.yaml
# FastAgent Configuration File

default_model: "claude-3-7-sonnet-latest"

logger:
    progress_display: false
    show_chat: true
    show_tools: false
    truncate_tools: true

mcp:
    servers:
"""
    for agent in config["agents"]:
        for mcp in agent["mcps"]:
            config_content += f"""
        {mcp['mcp_name']}:
            command: "{mcp['mcp_command']}"
            args: {mcp['mcp_args']}
"""

    # Write fastagent.config.yaml
    with open(f"{base_path}/fastagent.config.yaml", "w") as config_file:
        config_file.write(config_content)

    print("Files generated successfully!")

if __name__ == "__main__":
    # Load the config.json file
    if len(sys.argv) < 2:
        print("Usage: python generator.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    generate_agent_code(config)