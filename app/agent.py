"""Agent configuration. External model requests require an API key."""
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class MissingAPIKeyError(RuntimeError):
    """Raised when the configured model provider credentials are unavailable."""


SYSTEM_PROMPT = """You are a Persian-speaking assistant for a fictional academy.
Use the available tools to answer every student-specific or financial question.
Do not invent student data, payments, balances, or enrollment status.
If the student ID is not provided, ask the user to supply it.
If a student cannot be found, explain that the ID is not present.
Explain monetary amounts in toman. Distinguish tuition due from extra credit.
Never suggest that an enrollment is confirmed merely because a payment exists.
Only answer questions about the fictional academy dataset.
"""


@lru_cache(maxsize=1)
def get_agent():
    if not os.getenv("OPENAI_API_KEY"):
        raise MissingAPIKeyError("OPENAI_API_KEY is missing. Set it in .env")

    # Lazy imports let deterministic unit and API tests run without LangChain.
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
    from app.tools import find_student, check_tuition_balance

    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
        max_retries=1,
        timeout=30,
    )
    return create_agent(
        model=model,
        tools=[find_student, check_tuition_balance],
        system_prompt=SYSTEM_PROMPT,
    )


def ask_agent(message: str) -> dict:
    agent = get_agent()
    from langchain_core.messages import AIMessage
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    messages = result["messages"]

    tools_used = [
        call["name"]
        for msg in messages
        if isinstance(msg, AIMessage)
        for call in msg.tool_calls
    ]

    answer_content = messages[-1].content
    if isinstance(answer_content, str):
        answer = answer_content
    else:
        answer = " ".join(
            block.get("text", "")
            for block in answer_content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    return {"answer": answer, "tools_used": tools_used}


if __name__ == "__main__":
    query = "شهریه و مانده حساب هنرجوی ST001 چقدر است؟"
    print(ask_agent(query))