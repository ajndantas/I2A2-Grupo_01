# INSTALAÇÃO DA APLICAÇÃO
#
# REQUISITOS:
#   - A MÁQUINA DEVE TER O PYTHON 3.10 OU SUPERIOR JÁ INSTALADO
#
#   INSTRUÇÕES:
#   - DESCOMPACTAR O ARQUIVO ZIP agente_nfs.zip
#   - ACESSAR A PASTA Scripts, DENTRO DA PASTA agente_nfs
#   - EXECUTAR OS COMANDOS:
#       python -m pip install --upgrade pip
#       pip install -qqqr requirements.txt
#
#       EXECUÇÃO:
#           streamlit run frontend.py

import streamlit as st
import pandas as pd
import agente_nfs as agtnfs


st.set_page_config(page_title="Agente NFe", layout="centered")
st.title("🤖 Agente Inteligente para Notas Fiscais")

#api_key = st.sidebar.text_input("🔑 Google API Key", type="password")
zip_file = st.file_uploader("📎 Envie um arquivo ZIP com os CSVs da NFe", type="zip")
pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")


if st.button("🔍 Consultar"):
    if not zip_file:
        st.error("Você precisa fazer o upload de um arquivo ZIP.")
        
    elif not pergunta.strip():
        st.error("Digite uma pergunta válida.")
        
    else:
        with st.spinner("Analisando os dados com IA..."):
            try:
                resultado_df = agtnfs.agente3(pergunta, zip_file)

                if isinstance(resultado_df,str) and resultado_df == "SemArquivoCabecalho":
                    st.error("Erro: O arquivo ZIP não contém um CSV com cabeçalho válido.")
                
                elif isinstance(resultado_df,str) and resultado_df == "SemArquivoItens":
                    st.error("Erro: O arquivo ZIP não contém um CSV com itens válido.")
                
                elif (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (isinstance(resultado_df, pd.DataFrame) and resultado_df.empty):
                    st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                    
                elif isinstance(resultado_df, pd.DataFrame) and not resultado_df.empty:
                    st.success("✅ Resultado encontrado:")
                    st.dataframe(resultado_df)                                        
                    
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

