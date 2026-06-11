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
<title>Pedidos — e_seller Admin</title>
<style>
  body{{font-family:sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#1a1d2b}}
  h1{{margin-bottom:.5rem}}
  .filters{{display:flex;gap:10px;flex-wrap:wrap;margin:1rem 0;align-items:flex-end}}
  .filters label{{display:flex;flex-direction:column;gap:4px;font-size:.85rem;color:#6b7280}}
  .filters input,.filters select{{padding:8px 10px;border:1px solid #ddd;border-radius:8px;font:inherit}}
  .filters button{{padding:8px 16px;background:#6d5cff;color:#fff;border:0;border-radius:8px;cursor:pointer;font:inherit}}
  .filters button:hover{{filter:brightness(1.1)}}
  table{{width:100%;border-collapse:collapse;margin-top:.5rem}}
  th,td{{padding:.5rem .75rem;border:1px solid #e6e8f0;text-align:left;font-size:.9rem}}
  th{{background:#f6f7fb;font-weight:700}}
  tr:hover{{background:#fafbff}}
  .badge{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.78rem;font-weight:700}}
  .badge-paid{{background:#d4f1e4;color:#15a05a}}
  .badge-pending{{background:#fef3cd;color:#856404}}
  .badge-failed,.badge-cancelled{{background:#fde9ec;color:#d3455b}}
  .badge-refunded{{background:#e9ecef;color:#495057}}
  .mono{{font-family:monospace;font-size:.85rem;color:#6b7280}}
  #msg{{margin:.5rem 0;padding:.4rem .75rem;border-radius:6px;display:none;font-size:.85rem}}
  #msg.ok{{background:#d4f1e4;color:#15a05a}}
  #msg.err{{background:#fde9ec;color:#d3455b}}
  .empty{{text-align:center;padding:2rem;color:#6b7280}}
  a.link{{color:#6d5cff;text-decoration:none;font-size:.82rem}}
  a.link:hover{{text-decoration:underline}}
</style>
</head>
<body>
<h1>Pedidos</h1>
<p><a href="/admin">← Voltar ao painel</a></p>

<div class="filters">
  <label>Status
    <select id="f-status">{status_opts}</select>
  </label>
  <label>E-mail do comprador
    <input id="f-email" type="text" placeholder="parte do e-mail…" style="width:220px">
  </label>
  <label>Referência exata
    <input id="f-ref" type="text" placeholder="REF-abc123" style="width:160px">
  </label>
  <button onclick="loadOrders()">Filtrar</button>
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
    paid:"badge-paid",pending:"badge-pending",failed:"badge-failed",
    cancelled:"badge-cancelled",refunded:"badge-refunded"
  }};
  const cls = map[status] || "";
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
      <td>${{amount}}</td>
      <td>${{created}}</td>
      <td><a class="link" href="${{detailUrl}}" target="_blank">Ver JSON</a></td>
    </tr>`;
  }}
  tbody.innerHTML = rows;
}}

loadOrders();
</script>
</body></html>"""
    return HTMLResponse(html)
