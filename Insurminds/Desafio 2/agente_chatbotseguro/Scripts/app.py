from time import sleep
import streamlit as st
import json
import html as html_lib
import re
from agente_chatbotseguro import AgenteChatbotSeguro
from random import randint
from datetime import datetime
from zoneinfo import ZoneInfo

#-------------------------------------------------------
# Para executar localmente, execute o seguinte comando:
# streamlit run app.py
#-------------------------------------------------------

# ──────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Chatbot Seguro · InsurMinds",
    page_icon="🛡️",
    layout="centered"
)

# ──────────────────────────────────────────────
# CSS para esconder o menu
# ──────────────────────────────────────────────
hide_menu_style = """
        <style>
            MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            /* Remove a barra preta do Streamlit Community Cloud (Stop / Deploy) */
            div[data-testid="stAppDeployDropdown"] {
                display: none !important;
            }
            /* Esconde completamente a barra de ferramentas superior (onde fica o Stop e os 3 pontos) */
            .stAppToolbar, [data-testid="stAppToolbar"] {
                display: none !important;
                background-color: transparent !important;
            }
            
            /* Remove qualquer elemento de status de carregamento decorativo do topo */
            [data-testid="stStatusWidget"] {
                display: none !important;
            }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CSS CUSTOMIZADO
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');

/* Fundo e tipografia global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f4f6fb;
}

/* Cabeçalho fixo */
.header {
    background: linear-gradient(135deg, #1a2e5a 0%, #2e4a8e 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 24px rgba(30,60,120,0.18);
}
.header-icon { font-size: 2.6rem; }
.header-title {
    font-family: 'DM Serif Display', serif;
    color: #ffffff;
    font-size: 1.7rem;
    margin: 0;
    line-height: 1.2;
}
.header-sub {
    color: #a8bde8;
    font-size: 0.85rem;
    margin-top: 4px;
}

/* Balões de chat */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 10px 0;
}
.msg-bot {
    display: flex;
    justify-content: flex-start;
    margin: 10px 0;
}
.bubble-user {
    background: #2e4a8e;
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    box-shadow: 0 2px 8px rgba(46,74,142,0.18);
}
.bubble-bot {
    background: #ffffff;
    color: #1a2e5a;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    max-width: 80%;
    font-size: 0.95rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-left: 4px solid #e8913a;
}
.bubble-bot .resposta { margin-bottom: 8px; }
.bubble-bot .fontes {
    font-size: 0.78rem;
    color: #7a8fb5;
    border-top: 1px solid #eef0f6;
    padding-top: 6px;
    margin-top: 8px;
}
.fontes strong { color: #e8913a; }

/* Avatar */
.avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.avatar-bot { background: #e8f0fe; margin-right: 8px; }
.avatar-user { background: #2e4a8e; margin-left: 8px; color: #fff; }

/* Chips de sugestão */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.chip {
    background: #ffffff;
    border: 1px solid #d0daf0;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #2e4a8e;
    cursor: pointer;
    transition: all 0.2s;
}
.chip:hover { background: #2e4a8e; color: #fff; }

/* Rodapé */
.footer {
    text-align: center;
    font-size: 0.75rem;
    color: #aab4cc;
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CABEÇALHO
# ──────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="header-icon">🛡️</div>
    <div>
        <p class="header-title">Assistente de Seguros</p>
        <p class="header-sub">Powered by IA</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 1 - INICIALIZAÇÃO DO AGENTE (cached)
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️ Carregando base de conhecimento…")
def carregar_agente():
    
    return AgenteChatbotSeguro() 


if "agente" not in st.session_state:
    print("Criando o agente pela primeira vez...")
    
    agente = carregar_agente()
    st.session_state.isprotocolo = False # Condição inicial para controle de geração do protocolo de atendimento.
    st.session_state.agente = agente

# ──────────────────────────────────────────────
# 2 - HISTÓRICO DE MENSAGENS
# ──────────────────────────────────────────────
if "historico" not in st.session_state: # INICIALIZA O HISTÓRICO DE MENSAGENS COMO UMA LISTA VAZIA SE AINDA NÃO EXISTIR
    st.session_state.historico = [] 

# ──────────────────────────────────────────────
# 3 - SUGESTÕES RÁPIDAS
# ──────────────────────────────────────────────
if not st.session_state.historico: # SE O HISTÓRICO ESTIVER VAZIO, MOSTRA AS SUGESTÕES

    st.markdown("**💡 Perguntas frequentes:**")
    st.markdown(" - O que é uma apólice de seguro ?")
    st.markdown(" - Qual é a cobertura do seguro ?")
    st.markdown(" - Como devo proceder caso tenha meu celular roubado ?")
    st.markdown(" - Quem descobriu o Brasil ?")
    
# ──────────────────────────────────────────────────────────────────────────────
# 6 - RENDERIZAR HISTÓRICO - 
# 
# TEM QUE VIR DEPOIS DO PROCESSAMENTO DA PERGUNTA PENDENTE, 
# PARA QUE O PROTOCOLO SEJA EXIBIDO NO HISTÓRICO ANTES DA RESPOSTA DO AGENTE.
# 
# Exibição das mensagens do histórico em formato de chat.
# ──────────────────────────────────────────────────────────────────────────────
chat_container = st.container() # Cria um container para o chat

with chat_container:

    for msg in st.session_state.historico:

        #print("Mensagem do histórico:", msg) # DEBUG: VERIFICA AS MENSAGENS QUE ESTÃO SENDO RENDERIZADAS DO HISTÓRICO

        if msg["role"] == "user":
            texto_usuario = html_lib.escape(msg["content"]) 
            st.markdown(f"""
            <div class="msg-user">
                <div class="bubble-user">{texto_usuario}</div>
                <div class="avatar avatar-user">👤</div>
            </div>""", unsafe_allow_html=True)
        
        if msg["role"] == "assistant":
                        
            content = msg["content"]
            # Tenta parsear JSON da resposta do agente
            try:
                    data = json.loads(content)
                    resposta = html_lib.escape(data.get("resposta", content))                
                    fontes = html_lib.escape(", ".join(data.get("fontes", [])) if isinstance(data.get("fontes", []), list) else data.get("fontes", ""))
                    
                    if isinstance(fontes, list):
                        fontes = ", ".join(fontes)

            except (json.JSONDecodeError, TypeError):
                resposta = html_lib.escape(content)
                fontes = ""           

            # VERIFICA SE O PROTOCOLO JÁ FOI GERADO (isprotocolo) PARA DECIDIR SE EXIBE AS FONTES OU NÃO.
            fontes_html = f'<div class="fontes"><strong>📄 Fontes:</strong> {fontes}</div>' if fontes else ""

            #print("Valor de isprotocolo:", st.session_state.isprotocolo) # DEBUG: VERIFICA O VALOR DE isprotocolo PARA ENTENDER POR QUE AS FONTES NÃO ESTÃO APARECENDO.

            if st.session_state.isprotocolo and msg != st.session_state.historico[0]: # EXIBE AS FONTES APENAS SE O PROTOCOLO JÁ FOI GERADO, PARA SIMULAR O FLUXO DE UM ATENDIMENTO REAL.
                st.markdown(f"""
                        <div class="msg-bot">
                            <div class="avatar avatar-bot">🛡️</div>
                            <div class="bubble-bot">
                                <div class="resposta">{resposta}</div>
                                {fontes_html}
                            </div>
                        </div>""", unsafe_allow_html=True)
                
            else: 
                st.markdown(f"""
                        <div class="msg-bot">
                            <div class="avatar avatar-bot">🛡️</div>
                            <div class="bubble-bot">
                                <div class="resposta">Protocolo de atendimento: {resposta}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)               


# ───────────────────────────────────────────────────
# 7 - PROCESSAR PERGUNTA PENDENTE (vinda dos chips)
# ───────────────────────────────────────────────────
ultima = st.session_state.historico[-1] if st.session_state.historico else None

if (ultima and ultima["role"] == "user"): # SE A ÚLTIMA MENSAGEM FOR DO USUÁRIO E O PROTOCOLO AINDA NÃO FOI GERADO, PROCESSA A PERGUNTA PENDENTE PARA GERAR O PROTOCOLO.
    
    with st.spinner("🔍 Consultando base de conhecimento…"):
            st.session_state.isprotocolo = True

            try:
                    agente = st.session_state.agente
                    resultado = agente.query(ultima["content"])           

                    try:
                        data = json.loads(resultado) # Tenta parsear a resposta como JSON para limpar as tags HTML dos campos "resposta" e "fontes", 
                                                    # sem afetar o restante da estrutura.

                        if "resposta" in data:
                                data["resposta"] = re.sub(r"<[^>]+>", "", data["resposta"]).strip()
                        if "fontes" in data:
                                data["fontes"] = re.sub(r"<[^>]+>", "", data["fontes"]).strip()

                        resultado = json.dumps(data, ensure_ascii=False)                        

                    except (json.JSONDecodeError, TypeError):
                        pass  # se não for JSON, html_lib.escape já trata na renderização


            except Exception as e:
                    resultado = json.dumps({
                        "resposta": f"Ocorreu um erro ao processar sua pergunta: {e}",
                        "fontes": ""
                    })
                
    st.session_state.historico.append({"role": "assistant", "content": resultado})
    st.rerun() # Recarrega o app para mostrar a resposta do agente.
    
# ──────────────────────────────────────────────
# 4 - INPUT DO USUÁRIO
# ──────────────────────────────────────────────
st.divider()

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        pergunta = st.text_input(
            label="Mensagem",
            placeholder="Digite sua dúvida sobre seguros…",
            label_visibility="collapsed",
        )
    with col2:
        enviar = st.form_submit_button("Enviar", use_container_width=True)

# 5 - QUANDO O USUÁRIO ENVIA A PERGUNTA, ELA É ADICIONADA AO HISTÓRICO E O APP É RECARREGADO
if enviar and pergunta.strip():
    if not st.session_state.isprotocolo: # GERA O PROTOCOLO APENAS NA PRIMEIRA PERGUNTA DA CONVERSA, PARA SIMULAR O INÍCIO DE UM ATENDIMENTO.
        protocolo = randint(1, 9999) # Gera um número de protocolo aleatório para a conversa.
        data = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d%m%y") # Obtém a data atual no formato dia, mês e ano (ex: 120624 para 12 de junho de 2024).
        protocolo = f"{protocolo:04d}{data}" # Formata o número do protocolo com zeros à esquerda e adiciona a data (ex: 0423120624). Sendo aqui 
                                             # a data do dia 12 de junho de 2024 e o número aleatório 423.    
        
        resultado = json.dumps({
                    "resposta": protocolo
                })
        st.session_state.historico.append({"role": "assistant", "content": resultado}) 

    st.session_state.historico.append({"role": "user", "content": pergunta.strip()}) # AQUI, CONTENT É A PERGUNTA DO USUÁRIO.
    st.rerun()

# Botão para limpar conversa
if st.session_state.historico:
    if st.button("🗑️ Nova conversa", type="secondary"):
        st.session_state.historico = []
        st.session_state.isprotocolo = False
        st.session_state.agente.reset_memory() # LIMPA A MEMÓRIA DO AGENTE PARA INICIAR UMA NOVA CONVERSA SEM HISTÓRICO.
        st.rerun()

# ──────────────────────────────────────────────
# RODAPÉ
# ──────────────────────────────────────────────
st.markdown("""
<div class="footer">
    As respostas são baseadas nos documentos da base de conhecimento. Consulte sempre um especialista.
</div>
""", unsafe_allow_html=True)