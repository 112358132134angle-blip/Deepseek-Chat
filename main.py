import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载 .env
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="DeepSeek Chat",
    page_icon="🧠",
    layout="wide"
)

# 初始化客户端
@st.cache_resource
def get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("❌ 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")
        st.stop()
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

client = get_client()

# 初始化消息历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏
with st.sidebar:
    st.title("⚙️ 设置")
    model = st.selectbox(
        "选择模型", 
        ["deepseek-v4-pro", "deepseek-v4-flash"], 
        index=0
    )
    temperature = st.slider("温度", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.slider("最大token", 512, 8192, 2048, 512)
    
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# 主界面
st.title("🧠 DeepSeek 智能聊天助手")
st.caption("实时流式对话 · 支持多轮对话")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入消息..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 构造消息
            messages = [{"role": "system", "content": "你是一个友好、专业、有帮助的AI助手，用中文回复。"}] + st.session_state.messages
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # 最终显示
            message_placeholder.markdown(full_response)
            
            # 保存到历史
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"❌ API调用出错: {str(e)}")
            st.info("💡 可能原因：API Key 无效、网络问题、或余额不足")

st.caption("Made with ❤️ by DeepSeek API + Streamlit")