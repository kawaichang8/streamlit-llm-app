import os
import traceback
import streamlit as st
from dotenv import load_dotenv

# ===== 早めにページメタと「起動済み」の目印を出す =====
st.set_page_config(page_title="LLMアプリ（専門家モード付き）", page_icon="🤖")
st.write("✅ アプリ起動: ここまで描画できていればレンダリングはOK")

# ===== 以降で例外が出たらUIに必ず表示する =====
def show_exception(e: Exception):
    st.error("エラーが発生しました。右の詳細を確認してください。")
    st.exception(e)
    st.code("".join(traceback.format_exception(type(e), e, e.__traceback__)))

try:
    load_dotenv()  # .env を読む
    api_key = os.getenv("OPENAI_API_KEY")

    # ---- 依存ライブラリ（LangChainのOpenAIクライアント）----
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    st.title("🤖 LLMアプリ（専門家モード付き）")
    st.write("入力した質問に対して、選んだ専門家の視点で回答します。")

    # APIキーチェック（無ければUIに警告）
    if not api_key:
        st.warning("OPENAI_API_KEY が読み込まれていません。.env か Streamlit の Secrets を確認してください。")

    # --- 専門家の種類 ---
    experts = {
        "心理学者": "あなたは心理学の専門家です。人間の感情や行動について深く理解し、優しく的確に助言を行ってください。",
        "経営コンサルタント": "あなたは経営コンサルタントです。ビジネス戦略や組織改善について論理的に回答してください。",
        "キャリアアドバイザー": "あなたはキャリアアドバイザーです。働き方やスキルアップについて前向きなアドバイスを行ってください。"
    }

    expert_choice = st.radio("どの専門家に相談しますか？", list(experts.keys()))
    user_input = st.text_area("質問を入力してください:", height=100, placeholder="例）在宅勤務で集中力を上げるコツは？")

    def get_llm_response(expert: str, query: str) -> str:
        # LangChainのOpenAIラッパ（分離版）
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=api_key)
        msgs = [SystemMessage(content=experts[expert]), HumanMessage(content=query)]
        resp = llm.invoke(msgs)  # ← .invoke を使う（新API）
        return resp.content

    if st.button("送信"):
        if not user_input.strip():
            st.warning("質問を入力してください。")
        else:
            with st.spinner("回答を生成中..."):
                try:
                    answer = get_llm_response(expert_choice, user_input)
                    st.subheader("💡 回答")
                    st.write(answer)
                except Exception as e:
                    show_exception(e)

except Exception as e:
    show_exception(e)
