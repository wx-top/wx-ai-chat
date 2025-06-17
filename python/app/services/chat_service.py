from langchain.chat_models import init_chat_model
import os
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.schema import SystemMessage
from typing import List
import uuid
from flask import current_app


embeddings = OllamaEmbeddings(model="bge-m3")
PERSIST_DIRECTORY = "chroma_db"
memory = MemorySaver()


class ChatService:
    def __init__(self, model_name: str = None, repository_id: int = None):
        # 从Flask配置获取API密钥
        os.environ["OPENAI_API_KEY"] = current_app.config['OPENAI_API_KEY']
        os.environ["LANGSMITH_TRACING"] = current_app.config['LANGSMITH_TRACING']
        os.environ["LANGSMITH_API_KEY"] = current_app.config['LANGSMITH_API_KEY']
        
        # 初始化模型
        self.model = init_chat_model(base_url=current_app.config['OPENAI_API_URL'],
                                      model=model_name,
                                      model_provider=current_app.config['MODEL_PROVIDER'])

        
        self.repository_id = repository_id
        
        # 只有在有 repository_id 时才初始化向量数据库
        if repository_id is not None:
            print('加载向量数据库...')
            self.vector_store = Chroma(
                collection_name=f"user_{repository_id}_benefits",
                embedding_function=embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
            print(self.list_documents())
            # 创建工具
            self.retrieve_tool = self._create_retrieve_tool()
            self.tools = ToolNode([self.retrieve_tool])

            # 创建带检索功能的图
            self.graph_builder = StateGraph(MessagesState)
            self.graph_builder.add_node(self._query_or_respond)
            self.graph_builder.add_node(self.tools)
            self.graph_builder.add_node(self._generate)
            
            self.graph_builder.set_entry_point("_query_or_respond")
            self.graph_builder.add_conditional_edges(
                "_query_or_respond",
                tools_condition,
                {END: END, "tools": "tools"},
            )
            self.graph_builder.add_edge("tools", "_generate")
            self.graph_builder.add_edge("_generate", END)
        else:
            # 创建不带检索功能的简单图
            print('不加载向量数据库...')
            self.graph_builder = StateGraph(MessagesState)
            self.graph_builder.add_node(self._simple_generate)
            self.graph_builder.set_entry_point("_simple_generate")
            self.graph_builder.add_edge("_simple_generate", END)
        # 添加聊天记录
        # self.graph = self.graph_builder.compile(checkpointer=memory)
        self.graph = self.graph_builder.compile()

    def _create_retrieve_tool(self):
        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query."""
            # 检查向量数据库中的文档数量
            result = self.vector_store.get()
            print(f"向量数据库中的文档数量: {len(result['ids'])}")
            
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            print(f"检索到的文档数量: {len(retrieved_docs)}")
            
            # 打印检索到的文档内容
            for i, doc in enumerate(retrieved_docs):
                print(f"\n检索到的文档 {i+1}:")
                print(f"元数据: {doc.metadata}")
                print(f"内容: {doc.page_content}")
            
            serialized = "\n\n".join(
                f"Source: {doc.metadata}\n" f"Content: {doc.page_content}"
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        return retrieve

    def _query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.model.bind_tools([self.retrieve_tool])
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def _generate(self, state: MessagesState):
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
        print("\n提供给模型的上下文信息:")
        print(docs_content)
        
        system_message_content = (
            "你是一个专注用中文交流的政务助手，请遵守以下规则：1. 无论用户输入何种语言，始终使用简体中文回应。2. 不使用任何英文词汇，代码注释、网页链接例外。"
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
        response = self.model.invoke(prompt)
        return {"messages": [response]}

    def _simple_generate(self, state: MessagesState):
        """直接生成回答，不使用检索"""
        system_message_content = (
            "你是一个专注用中文交流的政务助手，请遵守以下规则：1. 无论用户输入何种语言，始终使用简体中文回应。2. 不使用任何英文词汇，代码注释、网页链接例外。"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
               or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages
        response = self.model.invoke(prompt)
        return {"messages": [response]}

    def load_documents(self, file_path: str, file_type: int):
        """加载用户文档到向量数据库"""
        try:
            # 验证文件路径安全性
            if not os.path.exists(file_path):
                raise FileNotFoundError("文件不存在")
                
            # 验证文件权限
            if not os.access(file_path, os.R_OK):
                raise PermissionError("没有文件读取权限")
            loader = None
            if file_type == 1:
                loader = TextLoader(file_path, encoding="utf-8")
            elif file_type == 2:
                loader = PyPDFLoader(file_path)

            docs = loader.load()
            print(f"成功加载文档，共 {len(docs)} 个文档")
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            all_splits = text_splitter.split_documents(docs)
            print(f"文档分块后，共 {len(all_splits)} 个块")
            
            # 生成文件ID
            file_id = str(uuid.uuid4())
            
            # 添加文件信息到元数据
            for doc in all_splits:
                doc.metadata["file_id"] = file_id
                doc.metadata["file_path"] = file_path
                doc.metadata["file_name"] = os.path.basename(file_path)
            
            # 添加文档到用户专属的向量数据库
            ids = self.vector_store.add_documents(documents=all_splits)
            print(f"成功添加文档到向量存储，共 {len(ids)} 个文档")
            
            # 验证文档是否成功添加
            result = self.vector_store.get()
            print(f"当前向量存储中的文档数量: {len(result['ids'])}")
            
            return file_id
        except Exception as e:
            print(f"加载文档时出错: {str(e)}")
            return None

    def delete_documents(self, file_id: str = None):
        """删除向量数据库中的文档
        
        Args:
            file_id: 要删除的文件ID。如果为 None，则删除所有文档。
        """
        try:
            if file_id:
                # 删除指定文件ID的文档
                self.vector_store.delete(
                    where={"file_id": {"$eq": file_id}}
                )
            else:
                # 删除所有文档
                self.vector_store.delete(
                    where={"file_id": {"$ne": ""}}
                )
            return True
        except Exception as e:
            print(f"删除文档时出错: {str(e)}")
            return False

    def list_documents(self):
        """列出已加载的所有文件信息"""
        try:
            # 获取所有文档的元数据
            results = self.vector_store.get(
                where={"file_id": {"$ne": ""}},
                include=["metadatas"]
            )
            
            # 提取唯一的文件信息
            unique_files = {}
            for metadata in results["metadatas"]:
                if "file_id" in metadata and "file_path" in metadata:
                    file_id = metadata["file_id"]
                    if file_id not in unique_files:
                        unique_files[file_id] = {
                            "file_id": file_id,
                            "file_path": metadata["file_path"],
                            "file_name": metadata.get("file_name", "")
                        }
            
            return list(unique_files.values())
        except Exception as e:
            print(f"列出文档时出错: {str(e)}")
            return []

    def get_chat_history(self, chat_id: str = None) -> List[dict]:
        """获取对话历史记录
        
        Args:
            chat_id: 对话ID。如果为None，则获取当前对话的历史记录。
            
        Returns:
            List[dict]: 历史记录列表，每条记录包含：
                - role: 角色（user/assistant）
                - content: 消息内容
                - timestamp: 时间戳
        """
        try:
            # 构造 RunnableConfig
            config = {
                "configurable": {
                    "thread_id": str(chat_id)
                }
            }
            
            # 从 memory 中获取历史记录
            checkpoint = memory.get(config)
            if not checkpoint:
                return []
                
            # 从 checkpoint 中获取消息
            messages = []
            if "messages" in checkpoint.get("channel_values", {}):
                for msg in checkpoint["channel_values"]["messages"]:
                    if isinstance(msg, dict):
                        messages.append({
                            "role": msg.get("role", "unknown"),
                            "content": msg.get("content", ""),
                            "timestamp": msg.get("timestamp", "")
                        })
                    elif hasattr(msg, "type"):
                        messages.append({
                            "role": "assistant" if msg.type == "ai" else "user",
                            "content": msg.content if hasattr(msg, "content") else str(msg),
                            "timestamp": ""  # 如果消息对象没有时间戳，则留空
                        })
                    
            return messages
        except Exception as e:
            print(f"获取历史记录时出错: {str(e)}")
            return []

    def chat(self, chat_id: int, message: str) -> str:
        try:
            # 使用相同的thread_id来保持对话历史
            config = {"configurable": {"thread_id": chat_id}}
            
            print("\n用户问题:", message)
            r = self.graph.invoke(
                    {"messages": [{"role": "user", "content": message}]},
                    config=config
            )
            content = r["messages"][-1].content
            print(f"AI回答：{content}")
            return content
        except Exception as e:
            print(f"聊天处理错误: {str(e)}")
            raise


# if __name__ == '__main__':
    # 初始化环境变量    # os.environ["OPENAI_API_KEY"] = "sk-f0d69c29581c40c8a38d0e9a726be2f8"
    # os.environ["LANGSMITH_TRACING"] = "true"
    # os.environ["LANGSMITH_API_KEY"] = "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"
    # # 创建用户专属的聊天服务实例
    # cs = ChatService(1, "deepseek-chat", repository_id=1)
    # print(cs.get_chat_history())
    # # 加载用户文档
    # print(cs.list_documents())
    # # cs.load_documents(r"C:\Users\wenxin\Desktop\公司福利.txt")
    # # cs.delete_documents("15897ff1-a73f-4b16-8613-f4a7e9eab411")
    # print(cs.list_documents())
    # cs.chat("公司有餐补吗？")
    # cs.chat("我刚刚问的什么？")
    # print(cs.get_chat_history())




