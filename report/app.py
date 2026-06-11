"""Página de relatório do e_seller: backlog / em execução / concluído.

Lê o arquivo de backlog (JSON) a cada requisição e renderiza uma página HTML
descritiva, com data/hora de Brasília (GMT-3), parecer da skill validadora
(revisão cíclica) e auto-refresh. Serviço independente do app principal.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Healthcheck do serviço de relatório."""
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Renderiza a página de relatório a partir do backlog atual."""
    data = request.app.state.reader.load()
    return HTMLResponse(request.app.state.renderer.render(data))


class BacklogReader:
    """Lê e organiza o backlog a partir do arquivo JSON (caminho via config)."""

    def __init__(self, backlog_path: str) -> None:
        """Recebe o caminho do arquivo de backlog por configuração."""
        self.backlog_path = Path(backlog_path)

    def load(self) -> dict:
        """Carrega o backlog do disco; retorna estrutura vazia se ausente."""
        if not self.backlog_path.is_file():
            return {"project": "e_seller", "tasks": [], "updated": "?"}
        return json.loads(self.backlog_path.read_text(encoding="utf-8"))


class ReportRenderer:
    """Renderiza a página HTML do relatório a partir do backlog."""

    _STATE_LABEL = {
        "doing": "🟡 Em execução",
        "backlog": "⚪ A fazer",
        "done": "🟢 Concluído",
        "blocked": "🔴 Bloqueado",
    }
    _STATE_ORDER = ["doing", "backlog", "done", "blocked"]
    _BRASILIA_OFFSET_HOURS = -3

    def render(self, data: dict) -> str:
        """Monta o HTML completo do relatório."""
        tasks = data.get("tasks", [])
        groups = self._group_by_state(tasks)
        counters = self._counters(groups)
        sections_html = self._render_sections(groups)
        return self._page(data, counters, sections_html, len(tasks))

    def _brasilia_now(self) -> str:
        """Retorna a data/hora atual de Brasília (GMT-3) formatada (pt-BR)."""
        now = datetime.now(timezone.utc) + timedelta(hours=self._BRASILIA_OFFSET_HOURS)
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def _group_by_state(self, tasks: list) -> dict:
        """Agrupa as tarefas por estado (com laços explícitos)."""
        groups: dict[str, list] = {}
        for state in self._STATE_ORDER:
            groups[state] = []
        for task in tasks:
            state = task.get("state", "backlog")
            if state not in groups:
                groups[state] = []
            groups[state].append(task)
        return groups

    def _counters(self, groups: dict) -> dict:
        """Conta tarefas por estado."""
        counters: dict[str, int] = {}
        for state in self._STATE_ORDER:
            counters[state] = len(groups.get(state, []))
        return counters

    def _render_sections(self, groups: dict) -> str:
        """Renderiza uma seção por estado, com cartões descritivos."""
        parts: list[str] = []
        for state in self._STATE_ORDER:
            items = groups.get(state, [])
            if not items:
                continue
            cards: list[str] = []
            for task in items:
                cards.append(self._card(task))
            label = self._STATE_LABEL.get(state, state)
            joined = "".join(cards)
            parts.append(
                f'<section><h2>{label} <span class="count">{len(items)}</span></h2>'
                f'<div class="grid">{joined}</div></section>'
            )
        return "".join(parts)

    def _card(self, task: dict) -> str:
        """Renderiza o cartão de uma tarefa (id, área, título, descrição, parecer)."""
        state = task.get("state", "backlog")
        note = task.get("note", "")
        note_html = f'<p class="note">📝 {note}</p>' if note else ""
        review = task.get("review")
        review_html = ""
        if review:
            verdict = review.get("verdict", "ok")
            icon = "✅" if verdict == "ok" else "🛠️"
            review_html = f'<p class="review">{icon} {review.get("note", "")}</p>'
        return (
            f'<article class="card state-{state}">'
            f'<div class="tag">{task.get("area", "")}</div>'
            f'<div class="id">{task.get("id", "?")}</div>'
            f'<h3>{task.get("title", "")}</h3>'
            f'<p>{task.get("desc", "")}</p>{note_html}{review_html}</article>'
        )

    def _render_review_panel(self, data: dict) -> str:
        """Renderiza o parecer global da skill validadora (revisão cíclica)."""
        summary = data.get("review_summary")
        if not summary:
            return ""
        verdict = summary.get("verdict", "—")
        last = summary.get("last", "—")
        repaired = summary.get("repaired", 0)
        added = summary.get("added", 0)
        note = summary.get("note", "")
        return (
            '<div class="panel"><h2>🧪 Parecer da skill validadora (revisão cíclica)</h2>'
            f"<p><b>Veredito:</b> {verdict} &nbsp;·&nbsp; <b>Última revisão:</b> {last}</p>"
            f"<p><b>Auto-reparos:</b> {repaired} &nbsp;·&nbsp; <b>Itens incrementados:</b> {added}</p>"
            f"<p>{note}</p></div>"
        )

    def _render_links(self, data: dict) -> str:
        """Renderiza os links públicos (app e relatório), se presentes."""
        links = data.get("links")
        if not links:
            return ""
        app_url = links.get("app", "")
        report_url = links.get("report", "")
        return (
            f'<div class="links">🛒 <a href="{app_url}">App/Loja</a> &nbsp;·&nbsp; '
            f'📊 <a href="{report_url}">Relatório</a></div>'
        )

    def _page(self, data: dict, counters: dict, body: str, total: int) -> str:
        """Monta o documento HTML com estilo, relógio de Brasília e parecer."""
        updated = data.get("updated", "?")
        goal = data.get("goal", "")
        done = counters.get("done", 0)
        doing = counters.get("doing", 0)
        backlog = counters.get("backlog", 0)
        pct = int((done / total) * 100) if total else 0
        server_time = self._brasilia_now()
        panel = self._render_review_panel(data)
        links = self._render_links(data)
        return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="20">
<title>e_seller — Relatório</title>
<style>
:root {{ --bg:#0f1226; --card:#1a1f3a; --ink:#eef; --muted:#9aa;
        --doing:#f5b14c; --backlog:#5b6; --done:#5cd08a; --blocked:#e2607a; }}
*{{box-sizing:border-box}} body{{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;
  background:var(--bg);color:var(--ink)}}
header{{padding:18px 24px;background:#12152e;border-bottom:1px solid #2a2f55}}
h1{{margin:0;font-size:1.2rem}} main{{max-width:1100px;margin:0 auto;padding:24px}}
.clock{{font-size:1.05rem;color:#cdf;margin-top:6px}}
.links{{margin-top:6px}} .links a{{color:#7c5cff;font-weight:700}}
.bar{{height:14px;background:#2a2f55;border-radius:999px;overflow:hidden;margin:10px 0}}
.bar>div{{height:100%;background:linear-gradient(90deg,#5cd08a,#7c5cff)}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 18px}}
.kpi{{background:var(--card);border:1px solid #2a2f55;border-radius:12px;padding:10px 14px}}
.kpi b{{font-size:1.4rem}}
.panel{{background:#15193a;border:1px solid #3a3f7a;border-radius:12px;padding:14px 16px;margin:14px 0}}
.panel h2{{margin:0 0 8px;font-size:1rem;border:0}}
section{{margin:22px 0}} h2{{font-size:1rem;border-bottom:1px solid #2a2f55;padding-bottom:6px}}
.count{{background:#2a2f55;border-radius:999px;padding:1px 8px;font-size:.8rem;margin-left:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-top:12px}}
.card{{background:var(--card);border:1px solid #2a2f55;border-radius:12px;padding:12px;position:relative}}
.card.state-doing{{border-left:4px solid var(--doing)}}
.card.state-backlog{{border-left:4px solid var(--backlog)}}
.card.state-done{{border-left:4px solid var(--done);opacity:.8}}
.card.state-blocked{{border-left:4px solid var(--blocked)}}
.card h3{{margin:6px 0 4px;font-size:.98rem}} .card p{{margin:0;color:#cdd;font-size:.86rem}}
.tag{{display:inline-block;background:#2a2f55;color:#cdf;padding:1px 8px;border-radius:999px;font-size:.7rem}}
.id{{position:absolute;top:10px;right:10px;color:var(--muted);font-size:.72rem}}
.note{{color:#f5b14c !important;margin-top:6px !important;font-size:.8rem !important}}
.review{{color:#5cd08a !important;margin-top:6px !important;font-size:.8rem !important}}
.muted{{color:var(--muted)}}
</style></head><body>
<header><h1>📊 e_seller — Relatório de execução</h1>
<div class="muted">{goal}</div>
<div class="clock">🕒 Brasília: <span id="clock">{server_time}</span> (GMT-3)</div>
{links}
</header>
<main>
  <div class="bar"><div style="width:{pct}%"></div></div>
  <div class="kpis">
    <div class="kpi"><b>{total}</b><br><span class="muted">tarefas</span></div>
    <div class="kpi"><b>{done}</b><br><span class="muted">concluídas ({pct}%)</span></div>
    <div class="kpi"><b>{doing}</b><br><span class="muted">em execução</span></div>
    <div class="kpi"><b>{backlog}</b><br><span class="muted">a fazer</span></div>
    <div class="kpi"><b>{updated}</b><br><span class="muted">atualizado</span></div>
  </div>
  {panel}
  {body}
  <p class="muted" style="margin-top:24px">Atualiza sozinho a cada 20s · monitore só por aqui.</p>
</main>
<script>
function tick(){{
  var d = new Date();
  var utc = d.getTime() + d.getTimezoneOffset()*60000;
  var b = new Date(utc - 3*3600000);
  var el = document.getElementById('clock');
  if (el) el.textContent = b.toLocaleString('pt-BR');
}}
setInterval(tick, 1000); tick();
</script>
</body></html>"""


def create_report_app() -> FastAPI:
    """Cria o app FastAPI do relatório (caminho do backlog via env BACKLOG_PATH)."""
    backlog_path = os.environ.get("BACKLOG_PATH", "backlog.json")
    app = FastAPI(title="e_seller — Relatório", version="0.2.0")
    app.state.reader = BacklogReader(backlog_path)
    app.state.renderer = ReportRenderer()
    app.include_router(router)
    return app


app = create_report_app()
