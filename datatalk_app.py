from openai import OpenAI
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(page_title="DataSQLTalk - AI Data Analytics Assistant", layout="wide")
st.title("🧠 DataSQLTalk — AI Data Analytics Assistant")
st.write("Ask questions about your CSV data in natural language.")

# --- OpenAI API Key ---
api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("🔑 Enter your OpenAI API key:", type="password")
if not api_key:
    st.warning("Please provide your OpenAI API key to continue.")
    st.stop()

# Create OpenAI client
client = OpenAI(api_key=api_key)

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload a CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded successfully. {df.shape[0]} rows × {df.shape[1]} columns")
    st.dataframe(df.head())

    user_question = st.text_input("💬 Ask a question about your data:")
    if user_question:
        prompt = f"""
        You are a data analyst. The dataset has these columns: {list(df.columns)}.
        Write Python pandas code to answer this question:
        '{user_question}'
        Use df as the DataFrame variable.
        The code should:
        1. Perform the analysis.
        2. Print a textual answer (store it in a variable called result).
        3. Optionally create a matplotlib chart and save it as 'chart.png'.
        Do not include import statements.
        """

        with st.spinner("Analyzing your data..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": "You are DataTalk, an intelligent data analytics assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )

                code = response.choices[0].message.content
                st.code(code, language="python")

                local_vars = {"df": df, "plt": plt, "pd": pd}
                exec(code, {}, local_vars)

                if "result" in local_vars:
                    st.write("📊 **Answer:**", local_vars["result"])

                try:
                    st.image("chart.png")
                except FileNotFoundError:
                    pass

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
else:
    st.info("Please upload a CSV file to start.")
