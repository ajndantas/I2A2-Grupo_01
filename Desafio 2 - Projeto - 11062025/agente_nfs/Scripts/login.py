import streamlit as st

# Função para calcular força da senha
def calcular_forca(senha):
    if not senha:
        return 0, "Digite uma senha"
    score = 0
    if len(senha) >= 12: score += 1
    if any(c.islower() for c in senha): score += 1
    if any(c.isupper() for c in senha): score += 1
    if any(c.isdigit() for c in senha): score += 1
    if any(not c.isalnum() for c in senha): score += 1
    niveis = ["Muito fraca", "Fraca", "Ok", "Boa", "Forte", "Excelente"]
    return score, niveis[score]


# Configuração da página
st.set_page_config(page_title="Agente NFe", layout="centered")
st.title("🤖 Agente NFe")
st.write("Faça login ou crie sua conta para continuar.")

# Menu de abas
aba = st.tabs(["🔑 Realizar login", "🆕 Criar conta", "🧩 Esqueci minha senha"])

# Estado para tentativas de login
if "login_fails" not in st.session_state:
    st.session_state.login_fails = 0

# -------- LOGIN --------
with aba[0]:
    login_user = st.text_input("Login", key="login_user")
    login_pass = st.text_input("Senha", type="password", key="login_pass")
    if st.checkbox("Mostrar senha"):
        st.write(f"Senha: {login_pass}")
    if st.button("Entrar"):
        if not login_user or not login_pass:
            st.warning("⚠️ Preencha login e senha.")
        elif st.session_state.login_fails >= 5:
            st.warning("⏳ Muitas tentativas falhas. Tente novamente mais tarde.")
        elif len(login_pass) >= 12:
            st.session_state.login_fails = 0
            st.success("✅ Login realizado com sucesso.")
            
        else:
            st.session_state.login_fails += 1
            st.error("❌ Credenciais inválidas.")

# -------- SIGNUP --------
with aba[1]:
    su_user = st.text_input("Novo login", key="su_user")
    su_pass = st.text_input("Nova senha", type="password", key="su_pass")
    su_conf = st.text_input("Confirmar senha", type="password", key="su_conf")
    su_name = st.text_input("Nome completo", key="su_name")

    score, nivel = calcular_forca(su_pass)
    st.progress(score / 5)
    st.caption(f"Força da senha: {nivel}")

    if st.button("Criar conta"):
        if not su_user or not su_pass or not su_conf or not su_name:
            st.warning("⚠️ Preencha login, senha, confirmação e nome.")
        elif su_pass != su_conf:
            st.error("❌ As senhas não coincidem.")
        elif len(su_pass) < 12:
            st.error("🔒 A senha deve ter pelo menos 12 caracteres.")
        else:
            st.success("✅ Conta criada. Agora faça o login.")

    with st.expander("Dicas para criar uma senha forte"):
        st.write(
            """
            - Use **frases** longas (≥ 12).
            - Misture maiúsculas, minúsculas, números e símbolos.
            - Evite dados pessoais e senhas repetidas.
            """
        )

# -------- RESET --------
with aba[2]:
    rs_user = st.text_input("Login", key="rs_user")
    rs_pass = st.text_input("Nova senha", type="password", key="rs_pass")
    rs_conf = st.text_input("Confirmar nova senha", type="password", key="rs_conf")

    score_rs, nivel_rs = calcular_forca(rs_pass)
    st.progress(score_rs / 5)
    st.caption(f"Força da senha: {nivel_rs}")

    if st.button("Redefinir senha"):
        if not rs_user or not rs_pass or not rs_conf:
            st.warning("⚠️ Preencha login, nova senha e confirmação.")
        elif rs_pass != rs_conf:
            st.error("❌ As senhas não coincidem.")
        elif len(rs_pass) < 12:
            st.error("🔒 A senha deve ter pelo menos 12 caracteres.")
        else:
            st.success("✅ Senha redefinida. Faça o login.")