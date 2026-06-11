"""Rotas administrativas de catálogo: cadastro dinâmico de e-book (3 modos)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.asset_service import ProductAssetService
from app.catalog.models import Product, ProductFileFormat, ProductStatus
from app.catalog.schemas import (
    ImportIn,
    ProductDraftIn,
    ProductOut,
    ProductStatusIn,
    ProductUpdateIn,
    TopViewedProductOut,
)
from app.catalog.services import (
    HttpManifestImporter,
    ProductDeleter,
    ProductDeletionNotAllowed,
    ProductEditor,
    ProductPublisher,
    ProductRegistrar,
    ProductViewReporter,
)
from app.core.db import get_session
from app.security.deps import RequireRole
from app.security.storage import ProtectedStorage

_templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

router = APIRouter(prefix="/api/v1/admin/products", tags=["admin-products"])

# Dependency de autorização: apenas staff/admin cadastram e-books.
require_staff = RequireRole("admin", "staff")


def get_registrar(
    session: AsyncSession = Depends(get_session),
) -> ProductRegistrar:
    """Monta o cadastrador de e-books com o importador HTTP."""
    return ProductRegistrar(session, HttpManifestImporter())


def get_publisher(
    session: AsyncSession = Depends(get_session),
) -> ProductPublisher:
    """Monta o serviço de publicação com a sessão injetada."""
    return ProductPublisher(session)


def get_editor(
    session: AsyncSession = Depends(get_session),
) -> ProductEditor:
    """Monta o editor de e-books com a sessão injetada."""
    return ProductEditor(session)


def get_deleter(
    session: AsyncSession = Depends(get_session),
) -> ProductDeleter:
    """Monta o deletador de e-books com a sessão injetada."""
    return ProductDeleter(session)


@router.get("", response_model=list[ProductOut])
async def list_all_products(
    status: str | None = Query(default=None, description="Filtro: published | draft"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _staff: object = Depends(require_staff),
    session: AsyncSession = Depends(get_session),
) -> list:
    """Lista todos os e-books (draft e published) para gestão administrativa.

    Filtro opcional por status; paginação via page/page_size.
    """
    from app.catalog.models import ProductStatus

    stmt = select(Product)
    if status is not None:
        try:
            status_enum = ProductStatus(status)
            stmt = stmt.where(Product.status == status_enum)
        except ValueError:
            return []
    stmt = stmt.order_by(Product.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await session.scalars(stmt)
    return list(result.all())


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    data: ProductDraftIn,
    _staff: object = Depends(require_staff),
    registrar: ProductRegistrar = Depends(get_registrar),
) -> object:
    """Cadastra um e-book (modos manual e JSON colado usam este endpoint)."""
    return await registrar.from_fields(data)


@router.post("/import", response_model=ProductOut, status_code=201)
async def import_product(
    data: ImportIn,
    _staff: object = Depends(require_staff),
    registrar: ProductRegistrar = Depends(get_registrar),
) -> object:
    """Cadastra um e-book importando um manifest de uma URL (modo link).

    Levanta InvalidManifestUrl (422) ou ManifestError (422) via handler global.
    """
    return await registrar.from_link(data.url)


@router.delete("/{slug}", status_code=204, response_class=Response)
async def delete_product(
    slug: str,
    _staff: object = Depends(require_staff),
    deleter: ProductDeleter = Depends(get_deleter),
) -> None:
    """Remove permanentemente um e-book do catálogo.

    Levanta 404 se o slug não existir.
    Levanta 409 se houver pedido pago vinculado ao produto.
    """
    try:
        await deleter.delete(slug)
    except ProductDeletionNotAllowed as exc:
        raise HTTPException(
            status_code=409,
            detail="Produto possui pedidos pagos e não pode ser excluído.",
        ) from exc


@router.patch("/{slug}", response_model=ProductOut)
async def update_product(
    slug: str,
    data: ProductUpdateIn,
    _staff: object = Depends(require_staff),
    editor: ProductEditor = Depends(get_editor),
) -> object:
    """Edita campos básicos de um e-book (título, preço, descrição, autor, capa).

    Envia apenas os campos que deseja alterar; os demais são preservados.
    Levanta ProductNotFound (404) via handler global.
    """
    return await editor.update(slug, data)


@router.patch("/{slug}/status", response_model=ProductOut)
async def set_product_status(
    slug: str,
    data: ProductStatusIn,
    _staff: object = Depends(require_staff),
    publisher: ProductPublisher = Depends(get_publisher),
) -> object:
    """Altera o status de publicação de um e-book (published/draft).

    Levanta ProductNotFound (404) ou InvalidStatus (422) via handler global.
    """
    return await publisher.set_status(slug, data.status)


@router.get("/new", response_class=HTMLResponse)
async def product_new_panel(
    request: Request,
    _staff: object = Depends(require_staff),
) -> HTMLResponse:
    """Painel de cadastro dinâmico de e-book com 3 modos (manual/JSON/link).

    Renderiza template com formulário que chama POST /admin/products ou /import.
    """
    return _templates.TemplateResponse(
        "admin_product_new.html", {"request": request}
    )


@router.get("/status-panel", response_class=HTMLResponse)
async def product_status_panel(
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> HTMLResponse:
    """Painel simples de publicação/despublicação de e-books (HTML).

    Lista todos os produtos com status atual e botão de ação rápida.
    Chama PATCH /{slug}/status via fetch ao clicar no botão.
    """
    result = await session.scalars(select(Product).order_by(Product.title))
    products = list(result)
    rows = ""
    for p in products:
        is_published = p.status == ProductStatus.PUBLISHED
        action = "draft" if is_published else "published"
        label = "Despublicar" if is_published else "Publicar"
        badge = (
            '<span style="color:#1a7a1a">● Publicado</span>'
            if is_published
            else '<span style="color:#888">○ Rascunho</span>'
        )
        del_btn = f'<button class="btn-del" onclick="confirmDelete(\'{p.slug}\')">Excluir</button>'
        toggle_btn = f'<button onclick="toggle(\'{p.slug}\',\'{action}\')">{label}</button>'
        rows += (
            f'<tr><td>{p.id}</td><td>{p.title}</td>'
            f'<td>{badge}</td>'
            f'<td>{toggle_btn} {del_btn}</td></tr>'
        )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Publicação — e_seller Admin</title>
<style>
  body{{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
  table{{width:100%;border-collapse:collapse}}
  th,td{{padding:.5rem .75rem;border:1px solid #ddd;text-align:left}}
  th{{background:#f5f5f5}}
  button{{cursor:pointer;padding:.3rem .8rem;border:1px solid #999;border-radius:4px}}
  .btn-del{{border-color:#d3455b;color:#d3455b;margin-left:6px}}
  .btn-del:hover{{background:#fde9ec}}
  #msg{{margin:1rem 0;padding:.5rem;border-radius:4px;display:none}}
  /* Modal de confirmação de exclusão */
  #confirm-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:10}}
  #confirm-overlay.show{{display:flex}}
  #confirm-box{{background:#fff;border-radius:12px;padding:24px;max-width:380px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,.15)}}
  #confirm-box h3{{margin:0 0 8px}}
  #confirm-box p{{color:#555;margin:0 0 16px}}
  .conf-btns{{display:flex;gap:10px;justify-content:flex-end}}
  .conf-btns button{{padding:.4rem 1.1rem;border-radius:6px;border:1px solid #ccc;cursor:pointer}}
  .conf-btns .danger{{background:#d3455b;color:#fff;border-color:#d3455b}}
  .conf-btns .danger:hover{{filter:brightness(1.1)}}
</style>
</head>
<body>
<h1>Publicação de e-books</h1>
<p><a href="/admin">← Voltar ao painel</a></p>
<div id="msg"></div>
<table>
  <thead><tr><th>ID</th><th>Título</th><th>Status</th><th>Ações</th></tr></thead>
  <tbody id="tbody">{rows}</tbody>
</table>

<!-- Modal de confirmação de exclusão -->
<div id="confirm-overlay">
  <div id="confirm-box">
    <h3>Excluir produto?</h3>
    <p id="confirm-text">Esta ação é permanente e não pode ser desfeita.</p>
    <div class="conf-btns">
      <button onclick="closeConfirm()">Cancelar</button>
      <button class="danger" id="confirm-ok">Excluir</button>
    </div>
  </div>
</div>

<script>
const token = () => localStorage.getItem("token") || "";
const msg = document.getElementById("msg");
let _pendingSlug = null;

async function toggle(slug, newStatus) {{
  const resp = await fetch("/api/v1/admin/products/" + slug + "/status", {{
    method: "PATCH",
    headers: {{"Content-Type":"application/json","Authorization":"Bearer "+token()}},
    body: JSON.stringify({{status: newStatus}}),
  }});
  if (resp.ok) {{
    msg.style.background="#d4edda"; msg.style.display="block";
    msg.textContent = slug + " → " + newStatus;
    setTimeout(() => location.reload(), 800);
  }} else {{
    const data = await resp.json().catch(() => ({{}}));
    msg.style.background="#f8d7da"; msg.style.display="block";
    msg.textContent = "Erro: " + (data.detail || resp.status);
  }}
}}

function confirmDelete(slug) {{
  _pendingSlug = slug;
  document.getElementById("confirm-text").textContent =
    "Deseja excluir permanentemente o produto "" + slug + ""?";
  document.getElementById("confirm-overlay").classList.add("show");
}}

function closeConfirm() {{
  _pendingSlug = null;
  document.getElementById("confirm-overlay").classList.remove("show");
}}

document.getElementById("confirm-ok").onclick = async function() {{
  if (!_pendingSlug) return;
  const slug = _pendingSlug;
  closeConfirm();
  const resp = await fetch("/api/v1/admin/products/" + slug, {{
    method: "DELETE",
    headers: {{"Authorization":"Bearer "+token()}},
  }});
  if (resp.status === 204) {{
    msg.style.background="#d4edda"; msg.style.display="block";
    msg.textContent = slug + " excluído com sucesso.";
    setTimeout(() => location.reload(), 800);
  }} else if (resp.status === 409) {{
    msg.style.background="#fff3cd"; msg.style.display="block";
    msg.textContent = "Não é possível excluir: produto possui pedidos pagos vinculados.";
  }} else {{
    const data = await resp.json().catch(() => ({{}}));
    msg.style.background="#f8d7da"; msg.style.display="block";
    msg.textContent = "Erro " + resp.status + ": " + (data.detail || "desconhecido");
  }}
}};
</script>
</body></html>"""
    return HTMLResponse(html)


# Extensões suportadas para envio de arquivo de e-book.
_FILE_EXTENSIONS: dict[str, ProductFileFormat] = {
    "pdf": ProductFileFormat.PDF,
    "epub": ProductFileFormat.EPUB,
    "txt": ProductFileFormat.TXT,
}

# Tamanho máximo de upload: 50 MB.
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@router.post("/{slug}/upload-file", status_code=201)
async def upload_product_file(
    slug: str,
    request: Request,
    file: UploadFile,
    _staff: object = Depends(require_staff),
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    """Recebe o arquivo do e-book (PDF/EPUB/TXT) e o grava no armazenamento protegido.

    Associa o arquivo ao produto via ProductAssetService.
    Levanta 404 se o produto não existir, 422 se o formato não for suportado.
    """
    result = await session.scalars(select(Product).where(Product.slug == slug))
    product = result.first()
    if product is None:
        return JSONResponse({"detail": "Produto não encontrado."}, status_code=404)

    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    file_format = _FILE_EXTENSIONS.get(ext)
    if file_format is None:
        return JSONResponse(
            {"detail": f"Formato não suportado: .{ext}. Use pdf, epub ou txt."},
            status_code=422,
        )

    data = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(data) > _MAX_UPLOAD_BYTES:
        return JSONResponse(
            {"detail": "Arquivo excede o limite de 50 MB."}, status_code=413
        )

    storage_dir = getattr(request.app.state.settings, "storage_dir", "storage/ebooks")
    storage = ProtectedStorage(storage_dir)
    storage_key = f"{slug}/{uuid.uuid4().hex}.{ext}"
    storage.write_bytes(storage_key, data)

    asset_service = ProductAssetService(session)
    product_file = await asset_service.add_file(
        product_id=product.id,
        file_format=file_format,
        storage_key=storage_key,
        byte_size=len(data),
        is_primary=True,
    )
    await session.commit()
    return JSONResponse(
        {
            "id": product_file.id,
            "product_id": product.id,
            "file_format": product_file.file_format,
            "storage_key": product_file.storage_key,
            "byte_size": product_file.byte_size,
            "is_primary": product_file.is_primary,
        },
        status_code=201,
    )


@router.get("/top-viewed", response_model=list[TopViewedProductOut])
async def top_viewed_products(
    limit: int = Query(default=10, ge=1, le=50),
    _staff: object = Depends(require_staff),
    session: AsyncSession = Depends(get_session),
) -> list:
    """Retorna os produtos com mais visualizações (view_count), em ordem decrescente.

    Máximo 50 itens. Requer staff/admin.
    """
    reporter = ProductViewReporter(session)
    return await reporter.top_viewed(limit)
