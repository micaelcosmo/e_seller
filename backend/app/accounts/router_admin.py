"""Rotas administrativas de contas: auditoria de login e painel de usuários."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.accounts.services import CustomerAdminReader, LoginAuditReader
from app.core.db import get_session
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])

_require_admin = RequireRole("admin", "staff")


class LoginAttemptOut(BaseModel):
    """Dados de saída de uma tentativa de login."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    user_id: int | None
    success: bool
    ip_address: str
    attempted_at: datetime


class CustomerOut(BaseModel):
    """Dados de saída resumidos de um cliente (sem dados sensíveis)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


def get_customer_reader(
    session: AsyncSession = Depends(get_session),
) -> CustomerAdminReader:
    """Monta o leitor de clientes com a sessão injetada."""
    return CustomerAdminReader(session)


@router.get("/users", response_model=list[CustomerOut])
async def list_customers(
    q: str | None = Query(default=None, description="Filtro por e-mail ou nome"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _staff: object = Depends(_require_admin),
    reader: CustomerAdminReader = Depends(get_customer_reader),
) -> object:
    """Lista clientes (mais recentes primeiro) com busca parcial por e-mail/nome."""
    return await reader.search(q, page, page_size)


@router.patch("/users/{user_id}/toggle-active", response_model=CustomerOut)
async def toggle_user_active(
    user_id: int,
    _staff: object = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
) -> object:
    """Ativa ou desativa a conta de um usuário (toggle do campo is_active).

    Retorna 404 se o usuário não existir.
    """
    result = await session.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    user.is_active = not user.is_active
    await session.commit()
    return user


def get_audit_reader(
    session: AsyncSession = Depends(get_session),
) -> LoginAuditReader:
    """Monta o leitor de audit log com a sessão injetada."""
    return LoginAuditReader(session)


@router.get("/attempts", response_model=list[LoginAttemptOut])
async def list_login_attempts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    only_failures: bool = Query(default=False, description="Mostrar só falhas"),
    _staff: object = Depends(_require_admin),
    reader: LoginAuditReader = Depends(get_audit_reader),
) -> object:
    """Lista tentativas de login (mais recentes primeiro) para auditoria."""
    return await reader.list_attempts(page, page_size, only_failures)


@router.get("/users/panel", response_class=HTMLResponse)
async def users_panel(
    request: Request,
    _staff: object = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    """Painel HTML de usuários com busca por e-mail e toggle ativo/inativo.

    Lista usuários (não anonimizados), permite buscar por e-mail e
    ativar/desativar conta via PATCH /{id}/toggle-active sem recarregar.
    """
    result = await session.scalars(
        select(User)
        .where(User.deleted_at.is_(None))
        .order_by(User.id.desc())
        .limit(200)
    )
    users = list(result)
    rows = ""
    for u in users:
        active_badge = (
            '<span style="color:#15a05a;font-weight:700">● Ativo</span>'
            if u.is_active
            else '<span style="color:#888">○ Inativo</span>'
        )
        toggle_lbl = "Desativar" if u.is_active else "Ativar"
        toggle_btn = (
            f'<button onclick="toggleUser({u.id})">{toggle_lbl}</button>'
        )
        rows += (
            f"<tr>"
            f"<td>{u.id}</td>"
            f"<td>{u.email}</td>"
            f"<td>{u.role.value}</td>"
            f"<td>{active_badge}</td>"
            f"<td>{toggle_btn}</td>"
            f"</tr>"
        )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Usuários — e_seller Admin</title>
<style>
  body{{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
  .search{{display:flex;gap:8px;margin:1rem 0}}
  .search input{{flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:8px;font:inherit}}
  .search button{{padding:9px 16px;background:#6d5cff;color:#fff;border:0;border-radius:8px;cursor:pointer}}
  table{{width:100%;border-collapse:collapse}}
  th,td{{padding:.5rem .75rem;border:1px solid #e6e8f0;text-align:left;font-size:.9rem}}
  th{{background:#f6f7fb;font-weight:700}}
  tr:hover{{background:#fafbff}}
  button{{cursor:pointer;padding:.3rem .8rem;border:1px solid #999;border-radius:6px;font:inherit}}
  #msg{{margin:.5rem 0;padding:.4rem .75rem;border-radius:6px;display:none;font-size:.85rem}}
  #msg.ok{{background:#d4f1e4;color:#15a05a}}
  #msg.err{{background:#fde9ec;color:#d3455b}}
</style>
</head>
<body>
<h1>Usuários</h1>
<p><a href="/admin">← Voltar ao painel</a></p>
<div class="search">
  <input id="q" type="text" placeholder="Buscar por e-mail…" oninput="filterRows()">
</div>
<div id="msg"></div>
<table>
  <thead><tr><th>ID</th><th>E-mail</th><th>Papel</th><th>Status</th><th>Ação</th></tr></thead>
  <tbody id="tbody">{rows}</tbody>
</table>
<script>
const token = () => localStorage.getItem("token") || "";
const msg = document.getElementById("msg");

function filterRows() {{
  const q = document.getElementById("q").value.toLowerCase();
  const rows = document.querySelectorAll("#tbody tr");
  for (const row of rows) {{
    const email = row.cells[1] ? row.cells[1].textContent.toLowerCase() : "";
    row.style.display = email.includes(q) ? "" : "none";
  }}
}}

async function toggleUser(id) {{
  const resp = await fetch("/api/v1/admin/auth/users/" + id + "/toggle-active", {{
    method: "PATCH",
    headers: {{"Authorization": "Bearer " + token()}},
  }});
  if (resp.ok) {{
    msg.className = "ok"; msg.style.display = "block";
    msg.textContent = "Usuário " + id + " atualizado.";
    setTimeout(() => location.reload(), 700);
  }} else {{
    const d = await resp.json().catch(() => ({{}}));
    msg.className = "err"; msg.style.display = "block";
    msg.textContent = "Erro: " + (d.detail || resp.status);
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(html)
