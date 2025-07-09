from langchain.chat_models import init_chat_model
import os
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

if not os.environ.get("OPENAI_API_KEY"):
    print("OpenAI API key not set")
    os.environ["OPENAI_API_KEY"] = "sk-f0d69c29581c40c8a38d0e9a726be2f8"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = "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"

model = init_chat_model(base_url="https://api.deepseek.com", model="deepseek-chat", model_provider="openai")

# 准备嵌入模型
embeddings = OllamaEmbeddings(model="bge-m3")

# 使用Chroma作为持久化向量存储
PERSIST_DIRECTORY = "chroma_db"
vector_store = Chroma(
    collection_name="company_benefits",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

# 检查是否需要加载文档
result = vector_store.get()
if not result["ids"]:  # 如果集合为空
    print("正在加载文档...")
    try:
        loader = TextLoader(r"C:\Users\wenxin\Desktop\公司福利.txt", encoding="utf-8")
        docs = loader.load()
        print(f"成功加载文档，共 {len(docs)} 个文档")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        print(f"文档分块后，共 {len(all_splits)} 个块")

        # 添加文档到向量存储
        ids = vector_store.add_documents(documents=all_splits)
        print(f"成功添加文档到向量存储，共 {len(ids)} 个文档")

        # 验证文档是否成功添加
        result = vector_store.get()
        print(f"当前向量存储中的文档数量: {len(result['ids'])}")
    except Exception as e:
        print(f"加载文档时出错: {str(e)}")
else:
    print(f"向量存储中已有 {len(result['ids'])} 个文档")

# prompt = hub.pull("rlm/rag-prompt")

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\n" f"Content: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = model.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tools = ToolNode([retrieve])

def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "你是一个用于问答任务的助手。"
        "请使用下面提供的上下文信息来回答问题。"
        "如果你不知道答案，请直接说明你不知道。"
        "答案最多使用三句话，并保持简洁。"
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = model.invoke(prompt)
    return {"messages": [response]}

graph_builder = StateGraph(MessagesState)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# 使用相同的thread_id来保持对话历史
config = {"configurable": {"thread_id": "abc123"}}
# 测试对话
input_message = "公司有餐补吗？"
print("\n用户问题:", input_message)
for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
    config=config
):
    step["messages"][-1].pretty_print()


input_message = "我刚刚问什么了？"
print("\n用户问题:", input_message)
for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
    config=config
):
    step["messages"][-1].pretty_print()



