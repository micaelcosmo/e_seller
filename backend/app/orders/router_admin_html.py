"""Painel administrativo de pedidos (HTML server-side, sem build)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/orders", tags=["admin-orders-panel"])

_require_staff = RequireRole("admin", "staff")

_STATUS_OPTIONS = ["", "pending", "paid", "failed", "cancelled", "refunded"]


@router.get("/panel", response_class=HTMLResponse)
async def orders_panel(
    request: Request,
    _staff: object = Depends(_require_staff),
) -> HTMLResponse:
    """Painel HTML de pedidos administrativo com filtros dinâmicos.

    Lista pedidos via GET /api/v1/orders; filtros por status, e-mail e referência.
    Sem reload de página — usa fetch para atualizar a tabela ao aplicar filtros.
    """
    status_opts = ""
    for s in _STATUS_OPTIONS:
        label = s.capitalize() if s else "Todos"
        status_opts += f'<option value="{s}">{label}</option>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos — e_seller Admin</title>
<link rel="stylesheet" href="/static/css/design-system.css">
<link rel="stylesheet" href="/static/css/components.css">
<style>
  .admin-wrap{{max-width:1100px;margin:var(--sp-8) auto;padding:0 var(--sp-4)}}
  .admin-header{{display:flex;align-items:center;gap:var(--sp-3);margin-bottom:var(--sp-6)}}
  .admin-filters{{display:flex;gap:var(--sp-3);flex-wrap:wrap;margin:var(--sp-4) 0;align-items:flex-end}}
  .admin-filters label{{display:flex;flex-direction:column;gap:var(--sp-1);font-size:var(--text-sm);color:var(--color-muted)}}
  table{{width:100%;border-collapse:collapse;margin-top:var(--sp-2)}}
  th,td{{padding:var(--sp-2) var(--sp-3);border:1px solid var(--color-border);text-align:left;font-size:var(--text-sm)}}
  th{{background:var(--color-surface);font-weight:var(--fw-bold)}}
  tr:hover td{{background:var(--color-surface)}}
  .mono{{font-family:monospace;font-size:var(--text-sm);color:var(--color-muted)}}
  #msg{{margin:var(--sp-2) 0;display:none}}
  .empty{{text-align:center;padding:var(--sp-8);color:var(--color-muted)}}
</style>
</head>
<body>
<div class="admin-wrap">
<div class="admin-header">
  <a href="/admin" class="btn btn-ghost btn-sm">← Painel</a>
  <h1 style="font-size:var(--text-xl);font-weight:var(--fw-bold)">Pedidos</h1>
  <span class="badge badge-muted" id="total-badge">–</span>
</div>

<div class="admin-filters">
  <label>Status
    <select id="f-status" class="input" style="width:140px">{status_opts}</select>
  </label>
  <label>E-mail do comprador
    <input id="f-email" class="input" type="text" placeholder="parte do e-mail…" style="width:220px">
  </label>
  <label>Referência exata
    <input id="f-ref" class="input" type="text" placeholder="REF-abc123" style="width:160px">
  </label>
  <button class="btn btn-primary" onclick="loadOrders()">Filtrar</button>
</div>

<div id="msg"></div>
<table id="tbl">
  <thead>
    <tr>
      <th>Referência</th><th>E-mail</th><th>Status</th>
      <th>Valor</th><th>Criado em</th><th>Ações</th>
    </tr>
  </thead>
  <tbody id="tbody"><tr><td colspan="6" class="empty">Carregando…</td></tr></tbody>
</table>

<script>
const token = () => localStorage.getItem("token") || "";

function badge(status) {{
  const map = {{
    paid:"badge-success",pending:"badge-warning",failed:"badge-danger",
    cancelled:"badge-danger",refunded:"badge-muted"
  }};
  const cls = map[status] || "badge-muted";
  return `<span class="badge ${{cls}}">${{status}}</span>`;
}}

async function loadOrders() {{
  const status = document.getElementById("f-status").value;
  const q = document.getElementById("f-email").value.trim();
  const ref = document.getElementById("f-ref").value.trim();
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (q) params.set("q", q);
  if (ref) params.set("ref", ref);
  params.set("page_size", "50");

  const resp = await fetch("/api/v1/orders?" + params.toString(), {{
    headers: {{"Authorization": "Bearer " + token()}}
  }});
  const msg = document.getElementById("msg");
  const tbody = document.getElementById("tbody");
  if (!resp.ok) {{
    const err = await resp.json().catch(() => ({{}}));
    msg.className = "err"; msg.style.display = "block";
    msg.textContent = "Erro " + resp.status + ": " + (err.detail || "desconhecido");
    return;
  }}
  msg.style.display = "none";
  const orders = await resp.json();
  if (!orders.length) {{
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Nenhum pedido encontrado.</td></tr>';
    return;
  }}
  document.getElementById("total-badge").textContent = orders.length + " pedidos";
  let rows = "";
  for (const o of orders) {{
    const created = o.created_at
      ? new Date(o.created_at).toLocaleString("pt-BR") : "—";
    const amount = "R$ " + Number(o.amount || 0).toFixed(2).replace(".",",");
    const detailUrl = "/api/v1/orders/admin/" + o.reference;
    rows += `<tr>
      <td class="mono">${{o.reference}}</td>
      <td>${{o.buyer_email || "—"}}</td>
      <td>${{badge(o.status)}}</td>
      <td style="font-weight:var(--fw-bold)">${{amount}}</td>
      <td style="color:var(--color-muted)">${{created}}</td>
      <td><a href="${{detailUrl}}" target="_blank" class="btn btn-ghost btn-sm">JSON</a></td>
    </tr>`;
  }}
  tbody.innerHTML = rows;
}}

loadOrders();
</script>
</div>
</body></html>"""
    return HTMLResponse(html)
