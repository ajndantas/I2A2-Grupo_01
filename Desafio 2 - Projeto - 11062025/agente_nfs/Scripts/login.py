import streamlit as st
from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import inspect, MetaData, Table, Column, String

def gestao_usuarios(engine, login, senha, nome = None, novo_usuario = False, esqueci_senha = False, autenticacao = False):
    
    """
        Função para gerenciar usuários.
        
        :param login: Login do usuário
        :param senha: Senha do usuário
        :param nome: Nome do usuário (opcional, usado para novo usuário)
        :param esqueci_senha: Flag para indicar se é uma solicitação de recuperação de senha
        :return: True se o procedimento ocorrer com sucesso, False caso contrário
    """
     # Objeto metadata para manter informações das tabelas
    metadata = MetaData()

    # Define a tabela com chave primária
    usuarios = Table(
            'usuarios', metadata,
            Column('login', String, primary_key=True),  # Chave primária
            Column('nome', String),
            Column('senha', String)
    )
        
    inspector = inspect(engine)  # INSPECTOR PARA LISTAR AS TABELAS DO BANCO DE DADOS
    
    if 'usuarios' not in inspector.get_table_names(): 
                        
        # Cria a tabela no banco
        metadata.create_all(engine)
               
    
    with engine.connect() as conn:
            
            if novo_usuario:
                hashed = hashpw(senha.encode('utf-8'), gensalt())
                conn.execute(usuarios.insert().values(login=login, senha=hashed.decode("utf-8"), nome=nome))
                conn.commit()
                return True
            
            elif esqueci_senha:
                hashed = hashpw(senha.encode('utf-8'), gensalt())
                
                result = conn.execute(usuarios.select().where(usuarios.c.login == login)).fetchone()
                
                if result is not None:
                    conn.execute(usuarios.update().where(usuarios.c.login == login).values(senha=hashed.decode("utf-8")))
                    return True
                else:
                    return False
                
            elif autenticacao:
                result = conn.execute(usuarios.select().where(usuarios.c.login == login)).fetchone()
                
                if result is not None:
                    senhabd = result[2]
                
                    if checkpw(senha.encode('utf-8'), senhabd.encode('utf-8')):
                        return True
                    else:
                        return False

# Função para calcular força da senha
def calcular_forca(senha):
    if not senha:
        return 0, "Digite uma senha"
    score = 0
    if len(senha) >= 8: score += 1
    if any(c.islower() for c in senha): score += 1
    if any(c.isupper() for c in senha): score += 1
    if any(c.isdigit() for c in senha): score += 1
    if any(not c.isalnum() for c in senha): score += 1
    niveis = ["Muito fraca", "Fraca", "Ok", "Boa", "Forte", "Excelente"]
    return score, niveis[score]


def login(engine):
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
            
        if st.button("Entrar"):
            if not login_user or not login_pass:
                st.warning("⚠️ Preencha login e senha.")
            elif st.session_state.login_fails >= 5:
                st.warning("⏳ Muitas tentativas falhas. Tente novamente mais tarde.")
                
            elif gestao_usuarios(engine=engine, login=login_user,senha=login_pass,autenticacao=True):
                st.session_state.login_fails = 0
                st.success("✅ Login realizado com sucesso.")
                st.session_state.pagina = "agente1"
                st.rerun()        
                
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
            elif len(su_pass) < 8:
                st.error("🔒 A senha deve ter pelo menos 8 caracteres.")
                
            elif gestao_usuarios(engine=engine, login=su_user,senha=su_pass,nome=su_name,novo_usuario=True):
                st.success("✅ Conta criada. Agora faça o login.")                
                

        with st.expander("Dicas para criar uma senha forte"):
            st.write(
                """
                - Use **frases** longas (≥ 8).
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
            elif len(rs_pass) < 8:
                st.error("🔒 A senha deve ter pelo menos 8 caracteres.")
            else:
                if gestao_usuarios(engine=engine, login=rs_user, senha=rs_pass, esqueci_senha=True):
                    st.success("✅ Senha redefinida. Faça o login.")
                    
                else:
                    st.error("❌ Login não encontrado.")