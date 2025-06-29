import streamlit as st
import pandas as pd
import agente_nfs as agtnfs


st.set_page_config(page_title="Agente NFe", layout="centered")
st.title("🤖 Agente Inteligente para Notas Fiscais")

uploaded_file = st.file_uploader("📂 Envie um arquivo CSV, PDF ou PNG da NFe", type=["csv","pdf","png"])

pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")


if st.button("🔍 Consultar"):
    if not uploaded_file:
        st.error("Você precisa fazer o upload de um arquivo CSV, PDF ou de uma imagem PNG.")
        
    elif not pergunta.strip():
        st.error("Digite uma pergunta válida.")
        
    else:
        with st.spinner("Analisando os dados com IA..."):
            try:
                resultado_df = agtnfs.agente3(pergunta, uploaded_file)

                if (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (isinstance(resultado_df, pd.DataFrame) and resultado_df.empty):
                    st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                    
                elif isinstance(resultado_df, pd.DataFrame) and not resultado_df.empty:
                    st.success("✅ Resultado encontrado:")
                    st.dataframe(resultado_df)                                        
                    
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

