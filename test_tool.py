"""
Simple test script for verifying the tool implementations work correctly.
"""

import asyncio
import logging
from tools import topic_tool, get_topic_impl, GetTopicParams
from agents import Runner, Agent
from messages import UserMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_topic_tool():
    """Test the topic tool implementation directly."""
    logging.info("Testing topic tool implementation...")
    
    # Create a simple context object (this might need adjustment based on actual SDK requirements)
    context = {}
    params = {"unique_seed": "test-seed-123"}
    
    try:
        # Call the tool implementation directly
        result = await get_topic_impl(context, params)
        logging.info(f"Tool returned topic: {result.topic}")
        logging.info(f"Reasoning: {result.reasoning}")
        logging.info(f"Category: {result.category}/{result.sub_category}")
        return True
    except Exception as e:
        logging.error(f"Error testing tool: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_with_tool():
    """Test creating an agent with the topic tool."""
    logging.info("Testing agent with topic tool...")
    
    try:
        # Create a simple agent with our tool
        agent = Agent(
            name="Test Agent",
            instructions="You are a test agent for the 20 questions game.",
            tools=[topic_tool]
        )
        
        # Add a message to the agent
        agent.add_message(UserMessage(content="Generate a topic for 20 questions."))
        
        logging.info("Agent created successfully with the tool.")
        return True
    except Exception as e:
        logging.error(f"Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    tool_test = await test_topic_tool()
    agent_test = await test_agent_with_tool()
    
    if tool_test and agent_test:
        logging.info("All tests passed!")
        return 0
    else:
        logging.error("Some tests failed!")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(result) 