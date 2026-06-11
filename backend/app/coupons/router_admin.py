"""Rotas administrativas de cupons: listagem, criação e painel HTML."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.admin.audit import AdminAuditService
from app.core.db import get_session
from app.coupons.models import Coupon, CouponRedemption
from app.coupons.services import CouponAdminService, CouponCodeAlreadyExists
from app.orders.models import Order
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/coupons", tags=["admin-coupons"])

_require_staff = RequireRole("admin", "staff")


class CouponAdminOut(BaseModel):
    """Dados de saída de um cupom para o painel administrativo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    discount_type: str
    value: float
    active: bool
    valid_until: datetime | None
    max_redemptions: int | None
    redemptions_count: int
    created_at: datetime


class CouponAdminReader:
    """Lista e pesquisa cupons para o painel administrativo."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def list_coupons(
        self,
        page: int,
        page_size: int,
        only_active: bool,
    ) -> list[Coupon]:
        """Retorna página de cupons (mais recentes primeiro).

        Filtro only_active=True retorna apenas cupons com active=True.
        """
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = select(Coupon)
        if only_active:
            stmt = stmt.where(Coupon.active.is_(True))
        stmt = stmt.order_by(Coupon.id.desc())
        stmt = stmt.offset((page - 1) * effective_size).limit(effective_size)
        result = await self.session.scalars(stmt)
        return list(result.all())


class CouponCreateIn(BaseModel):
    """Entrada para criar um novo cupom."""

    code: str
    discount_type: str
    value: Decimal
    max_redemptions: int | None = None
    valid_until: datetime | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        """Normaliza o código para maiúsculas e valida comprimento."""
        cleaned = value.strip().upper()
        if not cleaned or len(cleaned) > 40:
            raise ValueError("Código inválido (máx 40 chars)")
        return cleaned

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: Decimal) -> Decimal:
        """Garante valor positivo."""
        if value <= 0:
            raise ValueError("Valor do desconto deve ser positivo")
        return value


def get_coupon_admin_service(
    session: AsyncSession = Depends(get_session),
) -> CouponAdminService:
    """Monta o serviço admin de cupons com a sessão injetada."""
    return CouponAdminService(session)


def get_coupon_reader(
    session: AsyncSession = Depends(get_session),
) -> CouponAdminReader:
    """Monta o leitor de cupons com a sessão injetada."""
    return CouponAdminReader(session)


@router.post("", response_model=CouponAdminOut, status_code=201)
async def create_coupon(
    data: CouponCreateIn,
    actor: User = Depends(_require_staff),
    service: CouponAdminService = Depends(get_coupon_admin_service),
    session: AsyncSession = Depends(get_session),
) -> object:
    """Cria um novo cupom de desconto.

    Levanta 409 se o código já estiver em uso, 422 se os dados forem inválidos.
    Registra a criação no audit log.
    """
    try:
        coupon = await service.create(
            code=data.code,
            discount_type=data.discount_type,
            value=data.value,
            max_redemptions=data.max_redemptions,
            valid_until=data.valid_until,
        )
        await AdminAuditService(session).log(
            actor_email=actor.email,
            action="create",
            resource_type="coupon",
            resource_id=coupon.code,
        )
        await session.commit()
        return coupon
    except CouponCodeAlreadyExists as exc:
        raise HTTPException(
            status_code=409, detail="Código de cupom já existe"
        ) from exc
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


class CouponUpdateIn(BaseModel):
    """Campos editáveis de um cupom existente (todos opcionais)."""

    value: Decimal | None = None
    valid_until: datetime | None = None
    max_redemptions: int | None = None

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: Decimal | None) -> Decimal | None:
        """Garante valor positivo quando informado."""
        if value is not None and value <= 0:
            raise ValueError("Valor do desconto deve ser positivo")
        return value


@router.patch("/{code}", response_model=CouponAdminOut)
async def update_coupon(
    code: str,
    data: CouponUpdateIn,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
) -> object:
    """Edita value, valid_until e max_redemptions de um cupom existente.

    O código do cupom não pode ser alterado. Levanta 404 se não existir.
    """
    result = await session.scalars(
        select(Coupon).where(Coupon.code == code.upper())
    )
    coupon = result.first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    if data.value is not None:
        coupon.value = float(data.value)
    if data.valid_until is not None:
        coupon.valid_until = data.valid_until
    if data.max_redemptions is not None:
        coupon.max_redemptions = data.max_redemptions
    await session.commit()
    return coupon


@router.patch("/{code}/toggle", response_model=CouponAdminOut)
async def toggle_coupon(
    code: str,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
) -> object:
    """Ativa ou desativa um cupom (toggle do campo active).

    Retorna 404 se o código não existir.
    """
    result = await session.scalars(
        select(Coupon).where(Coupon.code == code.upper())
    )
    coupon = result.first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    coupon.active = not coupon.active
    await session.commit()
    return coupon


@router.get("/panel", response_class=HTMLResponse)
async def coupons_panel(
    request: Request,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    """Painel HTML de gestão de cupons.

    Lista cupons, permite criar novo (modal) e ativar/desativar via toggle.
    Sem reload de página — usa fetch para todas as operações.
    """
    result = await session.scalars(
        select(Coupon).order_by(Coupon.id.desc()).limit(200)
    )
    coupons = list(result)
    rows = ""
    for c in coupons:
        active_badge = (
            '<span style="color:#15a05a;font-weight:700">● Ativo</span>'
            if c.active
            else '<span style="color:#888">○ Inativo</span>'
        )
        val_label = (
            f"{float(c.value):.0f}%" if c.discount_type == "percent"
            else f"R$ {float(c.value):.2f}"
        )
        valid = (
            c.valid_until.strftime("%d/%m/%Y") if c.valid_until else "—"
        )
        max_r = str(c.max_redemptions) if c.max_redemptions is not None else "∞"
        toggle_lbl = "Desativar" if c.active else "Ativar"
        toggle_btn = (
            f'<button onclick="toggleCoupon(\'{c.code}\')">{toggle_lbl}</button>'
        )
        rows += (
            f"<tr>"
            f"<td><code>{c.code}</code></td>"
            f"<td>{c.discount_type}</td>"
            f"<td>{val_label}</td>"
            f"<td>{active_badge}</td>"
            f"<td>{c.redemptions_count}/{max_r}</td>"
            f"<td>{valid}</td>"
            f"<td>{toggle_btn}</td>"
            f"</tr>"
        )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Cupons — e_seller Admin</title>
<style>
  body{{font-family:sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#1a1d2b}}
  h1{{margin-bottom:.5rem}}
  .toolbar{{display:flex;gap:10px;margin:1rem 0;align-items:center}}
  table{{width:100%;border-collapse:collapse;margin-top:.5rem}}
  th,td{{padding:.5rem .75rem;border:1px solid #e6e8f0;text-align:left;font-size:.9rem}}
  th{{background:#f6f7fb;font-weight:700}}
  tr:hover{{background:#fafbff}}
  code{{font-size:.85rem;background:#f1f2f8;padding:2px 6px;border-radius:4px}}
  button{{cursor:pointer;padding:.3rem .8rem;border:1px solid #999;border-radius:6px;font:inherit}}
  .btn-primary{{background:#6d5cff;color:#fff;border-color:#6d5cff;padding:.5rem 1.1rem}}
  .btn-primary:hover{{filter:brightness(1.1)}}
  #msg{{margin:.5rem 0;padding:.4rem .75rem;border-radius:6px;display:none;font-size:.85rem}}
  #msg.ok{{background:#d4f1e4;color:#15a05a}}
  #msg.err{{background:#fde9ec;color:#d3455b}}
  /* Modal */
  #overlay{{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:10}}
  #overlay.show{{display:flex}}
  #modal{{background:#fff;border-radius:12px;padding:24px;max-width:400px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,.15)}}
  #modal h3{{margin:0 0 14px}}
  .field{{display:flex;flex-direction:column;gap:4px;margin-bottom:12px;font-size:.85rem;color:#555}}
  .field input,.field select{{padding:9px 10px;border:1px solid #ddd;border-radius:8px;font:inherit}}
  .modal-btns{{display:flex;gap:8px;justify-content:flex-end;margin-top:4px}}
</style>
</head>
<body>
<h1>Cupons</h1>
<p><a href="/admin">← Voltar ao painel</a></p>

<div class="toolbar">
  <button class="btn-primary" onclick="openModal()">+ Novo cupom</button>
</div>
<div id="msg"></div>
<table>
  <thead>
    <tr><th>Código</th><th>Tipo</th><th>Valor</th><th>Status</th>
    <th>Resgates</th><th>Válido até</th><th>Ação</th></tr>
  </thead>
  <tbody id="tbody">{rows}</tbody>
</table>

<!-- Modal criar cupom -->
<div id="overlay">
  <div id="modal">
    <h3>Criar cupom</h3>
    <div class="field"><label>Código<input id="m-code" type="text" placeholder="PROMO10"></label></div>
    <div class="field">
      <label>Tipo de desconto
        <select id="m-type">
          <option value="percent">Percentual (%)</option>
          <option value="fixed">Fixo (R$)</option>
        </select>
      </label>
    </div>
    <div class="field"><label>Valor<input id="m-value" type="number" min="0.01" step="0.01" placeholder="10"></label></div>
    <div class="field"><label>Máx. resgates (vazio=ilimitado)<input id="m-max" type="number" min="1" placeholder=""></label></div>
    <div class="field"><label>Válido até (vazio=sem limite)<input id="m-until" type="date"></label></div>
    <div class="modal-btns">
      <button onclick="closeModal()">Cancelar</button>
      <button class="btn-primary" onclick="createCoupon()">Criar</button>
    </div>
  </div>
</div>

<script>
const token = () => localStorage.getItem("token") || "";
const msg = document.getElementById("msg");

function showMsg(text, type) {{
  msg.className = type; msg.style.display = "block";
  msg.textContent = text;
}}

function openModal() {{
  document.getElementById("overlay").classList.add("show");
}}

function closeModal() {{
  document.getElementById("overlay").classList.remove("show");
}}

async function toggleCoupon(code) {{
  const resp = await fetch("/api/v1/admin/coupons/" + code + "/toggle", {{
    method: "PATCH",
    headers: {{"Authorization": "Bearer " + token()}},
  }});
  if (resp.ok) {{
    showMsg("Cupom " + code + " atualizado.", "ok");
    setTimeout(() => location.reload(), 700);
  }} else {{
    const d = await resp.json().catch(() => ({{}}));
    showMsg("Erro: " + (d.detail || resp.status), "err");
  }}
}}

async function createCoupon() {{
  const code = document.getElementById("m-code").value.trim().toUpperCase();
  const discount_type = document.getElementById("m-type").value;
  const value = parseFloat(document.getElementById("m-value").value);
  const maxRaw = document.getElementById("m-max").value.trim();
  const untilRaw = document.getElementById("m-until").value;
  if (!code || isNaN(value) || value <= 0) {{
    showMsg("Preencha código e valor corretamente.", "err");
    return;
  }}
  const body = {{code, discount_type, value}};
  if (maxRaw) body.max_redemptions = parseInt(maxRaw, 10);
  if (untilRaw) body.valid_until = untilRaw + "T23:59:59";
  const resp = await fetch("/api/v1/admin/coupons", {{
    method: "POST",
    headers: {{"Content-Type":"application/json","Authorization":"Bearer "+token()}},
    body: JSON.stringify(body),
  }});
  closeModal();
  if (resp.ok || resp.status === 201) {{
    showMsg("Cupom " + code + " criado!", "ok");
    setTimeout(() => location.reload(), 700);
  }} else {{
    const d = await resp.json().catch(() => ({{}}));
    const detail = d.detail || resp.status;
    showMsg("Erro " + resp.status + ": " + (typeof detail === "string" ? detail : JSON.stringify(detail)), "err");
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(html)


@router.get("/{code}/stats")
async def coupon_stats(
    code: str,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Retorna estatísticas de uso de um cupom.

    Campos: total_uses, last_used_at (ISO 8601 ou null se nunca usado).
    Levanta 404 se o código não existir.
    """
    from sqlalchemy import func as sa_func

    result = await session.scalars(select(Coupon).where(Coupon.code == code.upper()))
    coupon = result.first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    row = await session.execute(
        select(
            sa_func.count(CouponRedemption.id).label("total"),
            sa_func.max(CouponRedemption.created_at).label("last_at"),
        ).where(CouponRedemption.coupon_id == coupon.id)
    )
    data = row.one()
    last_at = data.last_at.isoformat() if data.last_at else None
    return {"total_uses": int(data.total or 0), "last_used_at": last_at}


@router.get("/{code}/usage")
async def coupon_usage(
    code: str,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
) -> list:
    """Retorna até 50 resgates recentes de um cupom com referência e e-mail do comprador.

    Levanta 404 se o código não existir.
    """
    result = await session.scalars(select(Coupon).where(Coupon.code == code.upper()))
    coupon = result.first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    rows = await session.execute(
        select(CouponRedemption, Order)
        .join(Order, CouponRedemption.order_id == Order.id)
        .where(CouponRedemption.coupon_id == coupon.id)
        .order_by(CouponRedemption.id.desc())
        .limit(50)
    )
    usage = []
    for redemption, order in rows.all():
        usage.append(
            {
                "order_reference": order.reference,
                "buyer_email": order.buyer_email,
                "redeemed_at": redemption.created_at.isoformat()
                if redemption.created_at
                else None,
            }
        )
    return usage


@router.get("", response_model=list[CouponAdminOut])
async def list_admin_coupons(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    only_active: bool = Query(default=False, description="Mostrar apenas ativos"),
    _staff: object = Depends(_require_staff),
    reader: CouponAdminReader = Depends(get_coupon_reader),
) -> object:
    """Lista todos os cupons para o painel administrativo (mais recentes primeiro)."""
    return await reader.list_coupons(page, page_size, only_active)
