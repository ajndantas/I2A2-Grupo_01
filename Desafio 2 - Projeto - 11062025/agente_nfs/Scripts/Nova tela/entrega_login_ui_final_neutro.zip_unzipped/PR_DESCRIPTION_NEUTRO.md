# feat(agente1): Tela de autenticação segura + redesign neutro

## Resumo
Implementa a tela de **Login / Criar conta / Esqueci minha senha** no `agente1(engine)` conforme solicitado, mantendo as **chamadas e retornos (True/False)** de `gestao_usuario(...)`. Redesign **neutro** (sem capa), melhorias de **UX** e reforços de **cibersegurança**.

## O que foi feito
- Abas: **🔑 Login**, **🆕 Criar conta**, **🧩 Esqueci minha senha**.
- **Placeholders**, **mostrar/ocultar senha**, **spinner** em operações.
- **Validações**: senha **≥ 12**, confirmação (criar/reset) + força da senha.
- **Mensagens neutras** e **rate limit visual** (5 falhas/ sessão).
- Branding opcional: `APP_BRAND_NAME`, `APP_LOGO_URL`.

## Contrato preservado
```python
# retorna True/False
gestao_usuario(login, senha, nome, novo_usuario=True)
gestao_usuario(login, senha, esqueci_senha=True)
gestao_usuario(login, senha, autenticacao=True)
```

## Como testar
1) Criar conta com senha ≥ 12 → sucesso; < 12 → bloqueado.  
2) Login 5x errado → bloqueio visual; correto → sucesso.  
3) Reset: confirma senha + política ≥ 12; mensagens neutras.  

## Segurança (UI)
- Login normalizado (**lowercase**).
- Feedback neutro; exceções não aparecem na UI.
- Política de senha + indicador de força antes do backend.

## Backend (opcional)
- `seguranca/gestao_usuario_secure.py` com **Argon2id + pepper (APP_PEPPER)**, lockout e jitter.  
  Mesma assinatura e retornos. Recomenda-se DB/Redis, reset por token e HTTPS.
