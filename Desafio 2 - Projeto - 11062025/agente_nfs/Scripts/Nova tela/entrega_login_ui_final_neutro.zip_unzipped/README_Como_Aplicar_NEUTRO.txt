===== Entrega: Tela de Autenticação (UI) + Segurança – Design neutro =====

Conteúdo:
1) feat-login-ui-final-neutral.patch  -> patch único com a UI (login/cadastro/reset), redesign neutro e reforços de segurança
2) seguranca/gestao_usuario_secure.py -> exemplo opcional de backend seguro (mesma assinatura/retornos)

Como aplicar (na raiz do repositório):

git checkout -b feat/login-ui-final-neutral
git apply --index feat-login-ui-final-neutral.patch
git commit -m "Agente1: tela de autenticação (login/cadastro/reset) com segurança e design neutro"

Observações:
- A tela fica dentro de agente_nfs.py, em agente1(engine), com portão de autenticação no início.
- Chamadas e assinatura de gestao_usuario permanecem IGUAIS ao enunciado (retorno True/False).
  * Criar usuário:    gestao_usuario(login, senha, nome, novo_usuario=True)
  * Esqueci a senha:  gestao_usuario(login, senha, esqueci_senha=True)
  * Autenticação:     gestao_usuario(login, senha, autenticacao=True)
- Reforços na UI: senha >= 12, mensagens neutras, normalização do login (lowercase),
  indicador de força de senha, spinner e rate limit visual.
- Branding simples via env (opcional): APP_BRAND_NAME, APP_LOGO_URL
