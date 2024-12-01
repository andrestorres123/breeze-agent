"""Node for expanding topics with related subjects."""

from typing import Dict

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from react_agent.configuration import Configuration
from react_agent.state import State, RelatedTopics
from react_agent.utils import load_chat_model
from react_agent.prompts import RELATED_TOPICS_PROMPT


async def expand_topics(
    state: State, config: RunnableConfig
) -> Dict[str, RelatedTopics]:
    """Expand a topic with related subjects.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the related topics.
    """
    configuration = Configuration.from_runnable_config(config)

    # Initialize the fast LLM for topic expansion
    model = load_chat_model(configuration.fast_llm_model)

    # Get the topic from the last user message
    last_user_message = next(
        (msg for msg in reversed(state.messages) if msg.type == "human"),
        None,
    )
    if not last_user_message:
        raise ValueError("No user message found in state")

    # Create the chain for topic expansion with structured output
    chain = RELATED_TOPICS_PROMPT | model.with_structured_output(RelatedTopics)

    # Generate related topics
    related_topics = await chain.ainvoke({"topic": last_user_message.content}, config)

    return {
        "related_topics": related_topics,
    } 