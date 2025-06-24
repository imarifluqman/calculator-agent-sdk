from agents import Agent,AsyncOpenAI, OpenAIChatCompletionsModel,Runner,function_tool
from agents.run import RunConfig
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import chainlit as cl
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise Exception("GEMINI_API_KEY is not set")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model=OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client=external_client
)
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
@function_tool
def add(*args):
    print("add called")
    return sum(args)


@function_tool
def subtract(*args):
    print("subtract called")
    num = args[0]
    for i, arg in enumerate(args[1:]):
        print("arg",arg)
        num = num - arg
    return num


@function_tool
def multiply(*args):
    print("multiply called")
    num = args[0]
    for i, arg in enumerate(args[1:]):
        num = num * arg
    return num

@function_tool
def divide(*args):
    print("divide called")
    num = args[0]
    for i, arg in enumerate(args[1:]):
        num = num / arg
    return num


@function_tool
def age_calculator(dob):
    print("age_calculator called" , dob)
    today = datetime.now()
    return today.year - dob


age_calculator_agent = Agent(
    name="Age Calculator Agent",
    instructions="""
    when users ask about age, extract the year from input and pass as argument in parameter of age-calculator tool
    """,
    handoff_description=" your are a specialist agent of age calculator",
    model=model,
    tools=[age_calculator]
)

async def main():
    print("Hello from calculator-agent!")
    agent = Agent(
        name="Assistant Agent",
        instructions="""
        you are a helpful assistant
        1-when usres ask about addition you must call the add tool function.
        2-when usres ask about subtraction you must call the subtract tool function.
        3-when usres ask about multiplication you must call the multiply tool function.
        4-when usres ask about division you must call the divide tool function.
        5-when usres ask about age you must handoff the age-calculator-agent.
        """,
        model=model,
        tools=[add,subtract,multiply,divide],
        handoffs=[age_calculator_agent]
    )
    
    result = await Runner.run(
        agent,input=input("Enter your prompt: "),run_config=config
    )
    
    print(result.final_output)
    


if __name__ == "__main__":
    asyncio.run(main())
