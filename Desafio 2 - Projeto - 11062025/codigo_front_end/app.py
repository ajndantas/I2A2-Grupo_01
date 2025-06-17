import streamlit as st
import pandas as pd
from agente_nfs_core import responder_pergunta

st.set_page_config(page_title="Agente NFe", layout="centered")
st.title("🤖 Agente Inteligente para Notas Fiscais")

api_key = st.sidebar.text_input("🔑 Google API Key", type="password")
zip_file = st.file_uploader("📎 Envie um arquivo ZIP com os CSVs da NFe", type="zip")
pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")

if st.button("🔍 Consultar"):
    if not api_key:
        st.error("Você precisa fornecer sua Google API Key.")
    elif not zip_file:
        st.error("Você precisa fazer o upload de um arquivo ZIP.")
    elif not pergunta.strip():
        st.error("Digite uma pergunta válida.")
    else:
        with st.spinner("Analisando os dados com IA..."):
            try:
                resultado_df = responder_pergunta(pergunta, zip_file.read(), api_key)

                if resultado_df.empty:
                    st.warning("Consulta realizada, mas nenhum dado foi encontrado.")
                else:
                    st.success("✅ Resultado encontrado:")
                    st.dataframe(resultado_df)
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
