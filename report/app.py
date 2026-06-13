"""Página de relatório do e_seller: backlog / em execução / concluído."""

from __future__ import annotations

import html as _html
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
    """Lê e organiza o backlog a partir do arquivo JSON."""

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
        "blocked": "🔴 Bloqueado",
        "done": "🟢 Concluído",
    }
    _STATE_ORDER = ["doing", "backlog", "blocked", "done"]
    _STATE_OPEN = {"doing"}

    def render(self, data: dict) -> str:
        """Monta o HTML completo do relatório."""
        tasks = data.get("tasks", [])
        groups = self._group_by_state(tasks)
        counters = self._counters(groups)
        total = len(tasks)
        done = counters.get("done", 0)
        pct = int((done / total) * 100) if total else 0
        server_time = self._brasilia_now()
        return self._page(data, groups, counters, total, pct, server_time)

    def _brasilia_now(self) -> str:
        """Retorna data/hora atual de Brasília (UTC-3) formatada."""
        now = datetime.now(timezone.utc) + timedelta(hours=-3)
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def _group_by_state(self, tasks: list) -> dict:
        """Agrupa tarefas por estado."""
        groups: dict[str, list] = {s: [] for s in self._STATE_ORDER}
        for task in tasks:
            state = task.get("state", "backlog")
            if state not in groups:
                groups[state] = []
            groups[state].append(task)
        return groups

    def _group_by_area(self, tasks: list) -> dict:
        """Agrupa tarefas por área, preservando ordem de inserção."""
        areas: dict[str, list] = {}
        for task in tasks:
            area = task.get("area", "Geral")
            if area not in areas:
                areas[area] = []
            areas[area].append(task)
        return areas

    def _counters(self, groups: dict) -> dict:
        """Conta tarefas por estado."""
        return {state: len(groups.get(state, [])) for state in self._STATE_ORDER}

    def _card(self, task: dict) -> str:
        """Renderiza cartão de uma tarefa (conteúdo escapado para evitar injeção HTML)."""
        state = task.get("state", "backlog")
        tid = _html.escape(str(task.get("id", "?")))
        title = _html.escape(str(task.get("title", "")))
        desc = _html.escape(str(task.get("desc", "")))
        note = _html.escape(str(task.get("note", "")))
        review = task.get("review")
        note_html = f'<p class="note">📝 {note}</p>' if note else ""
        review_html = ""
        if review:
            icon = "✅" if review.get("verdict") == "ok" else "🛠️"
            rev_note = _html.escape(str(review.get("note", "")))
            review_html = f'<p class="rev">{icon} {rev_note}</p>'
        return (
            f'<div class="card s-{state}">'
            f'<span class="cid">{tid}</span>'
            f'<strong>{title}</strong>'
            f'<p class="cdesc">{desc}</p>'
            f'{note_html}{review_html}'
            f'</div>'
        )

    def _area_block(self, area: str, tasks: list, open_by_default: bool) -> str:
        """Renderiza bloco colapsável de uma área dentro de uma seção."""
        cards = "".join(self._card(t) for t in tasks)
        open_attr = " open" if open_by_default else ""
        safe_area = _html.escape(area)
        return (
            f'<details class="area-group"{open_attr}>'
            f'<summary class="area-sum">'
            f'{safe_area} <span class="cnt">{len(tasks)}</span>'
            f'</summary>'
            f'<div class="cards">{cards}</div>'
            f'</details>'
        )

    def _state_section(self, state: str, tasks: list) -> str:
        """Renderiza seção colapsável por estado, agrupada por área."""
        if not tasks:
            return ""
        label = self._STATE_LABEL.get(state, state)
        open_attr = " open" if state in self._STATE_OPEN else ""
        areas = self._group_by_area(tasks)
        area_open = state in self._STATE_OPEN
        area_blocks = "".join(
            self._area_block(area, area_tasks, area_open)
            for area, area_tasks in areas.items()
        )
        return (
            f'<details class="state-section s-{state}"{open_attr}>'
            f'<summary class="sec-sum">'
            f'{label} <span class="cnt">{len(tasks)}</span>'
            f'</summary>'
            f'{area_blocks}'
            f'</details>'
        )

    def _header_links(self, data: dict) -> str:
        """Renderiza links do app e relatório no cabeçalho."""
        links = data.get("links", {})
        app_url = links.get("app", "")
        report_url = links.get("report", "")
        parts: list[str] = []
        if app_url:
            parts.append(f'<a href="{app_url}" target="_blank">🛒 Loja</a>')
        if report_url:
            parts.append(f'<a href="{report_url}" target="_blank">📊 Status</a>')
        if not parts:
            return ""
        joined = " &nbsp;·&nbsp; ".join(parts)
        return f'<div class="hlinks">{joined}</div>'

    def _review_panel(self, data: dict) -> str:
        """Renderiza painel colapsável de revisão cíclica."""
        rev = data.get("review_summary")
        if not rev:
            return ""
        verdict = _html.escape(str(rev.get("verdict", "—")))
        last = _html.escape(str(rev.get("last", "—")))
        note = _html.escape(str(rev.get("note", "")))
        repaired = int(rev.get("repaired", 0))
        added = int(rev.get("added", 0))
        return (
            f'<details class="rev-panel">'
            f'<summary>🧪 Revisão cíclica — <em>{verdict}</em></summary>'
            f'<dl>'
            f'<dt>Última</dt><dd>{last}</dd>'
            f'<dt>Auto-reparos</dt><dd>{repaired}</dd>'
            f'<dt>Itens adicionados</dt><dd>{added}</dd>'
            f'</dl>'
            f'<p class="rev-note">{note}</p>'
            f'</details>'
        )

    def _page(
        self,
        data: dict,
        groups: dict,
        counters: dict,
        total: int,
        pct: int,
        server_time: str,
    ) -> str:
        """Monta o documento HTML completo."""
        updated = data.get("updated", "?")
        goal = data.get("goal", "")
        done = counters.get("done", 0)
        doing = counters.get("doing", 0)
        backlog_n = counters.get("backlog", 0)
        blocked = counters.get("blocked", 0)
        links_html = self._header_links(data)
        review_html = self._review_panel(data)
        sections = "".join(
            self._state_section(s, groups.get(s, []))
            for s in self._STATE_ORDER
        )
        return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="20">
<title>e_seller — Relatório</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg:      #0d1117;
  --surface: #161b22;
  --border:  #30363d;
  --ink:     #c9d1d9;
  --muted:   #8b949e;
  --accent:  #58a6ff;
  --doing:   #d29922;
  --backlog: #388bfd;
  --done:    #3fb950;
  --blocked: #f85149;
}}
body {{
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.6 system-ui, "Segoe UI", sans-serif;
}}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* ── Header ── */
.hdr {{
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 12px 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}}
.hdr-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}}
.hdr h1 {{ font-size: .95rem; font-weight: 600; }}
.hlinks {{ display: flex; gap: 14px; font-size: .82rem; font-weight: 500; }}
.hlinks a {{ color: var(--accent); }}
.hdr-meta {{ margin-top: 4px; font-size: .75rem; color: var(--muted); }}
.hdr-meta span + span::before {{ content: " · "; }}

/* ── Main ── */
main {{ max-width: 1060px; margin: 0 auto; padding: 16px 20px 40px; }}

/* ── Progress ── */
.bar {{
  height: 5px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
  margin: 12px 0;
}}
.bar-fill {{ height: 100%; background: var(--done); border-radius: 999px; }}

/* ── KPIs ── */
.kpis {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}}
.kpi {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 14px;
  min-width: 80px;
  text-align: center;
}}
.kpi b {{ font-size: 1.25rem; display: block; color: var(--ink); }}
.kpi span {{ font-size: .7rem; color: var(--muted); }}
.updated {{
  font-size: .75rem;
  color: var(--muted);
  margin-bottom: 12px;
}}

/* ── Review panel ── */
.rev-panel {{
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-bottom: 12px;
  overflow: hidden;
}}
.rev-panel > summary {{
  cursor: pointer;
  padding: 8px 12px;
  background: var(--surface);
  font-size: .82rem;
  font-weight: 500;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
}}
.rev-panel > summary::-webkit-details-marker {{ display: none; }}
.rev-panel > summary::before {{ content: "▶"; font-size: .6rem; color: var(--muted); }}
details[open] > summary::before {{ content: "▼"; font-size: .6rem; }}
.rev-panel dl {{
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 4px 12px;
  padding: 10px 12px 4px;
  font-size: .78rem;
}}
.rev-panel dt {{ color: var(--muted); font-weight: 500; }}
.rev-panel dd {{ color: var(--ink); }}
.rev-note {{ font-size: .76rem; color: var(--muted); padding: 6px 12px 10px; }}

/* ── State sections ── */
.state-section {{
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-bottom: 8px;
  overflow: hidden;
}}
.sec-sum {{
  cursor: pointer;
  padding: 9px 12px;
  background: var(--surface);
  font-size: .85rem;
  font-weight: 600;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
  user-select: none;
}}
.sec-sum::-webkit-details-marker {{ display: none; }}
.sec-sum::before {{ content: "▶"; font-size: .6rem; color: var(--muted); }}
details[open] > .sec-sum::before {{ content: "▼"; }}

/* ── Area groups ── */
.area-group {{ border-top: 1px solid var(--border); }}
.area-sum {{
  cursor: pointer;
  padding: 6px 12px 6px 24px;
  font-size: .75rem;
  color: var(--muted);
  font-weight: 500;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  user-select: none;
}}
.area-sum::-webkit-details-marker {{ display: none; }}
.area-sum::before {{ content: "▶"; font-size: .55rem; }}
details[open] > .area-sum::before {{ content: "▼"; }}

/* ── Cards ── */
.cards {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 7px;
  padding: 8px 12px 12px 24px;
}}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 9px 11px;
  position: relative;
  font-size: .78rem;
}}
.card.s-doing   {{ border-left: 3px solid var(--doing); }}
.card.s-backlog {{ border-left: 3px solid var(--backlog); opacity: .9; }}
.card.s-done    {{ border-left: 3px solid var(--done); opacity: .65; }}
.card.s-blocked {{ border-left: 3px solid var(--blocked); }}
.cid {{
  position: absolute;
  top: 7px;
  right: 9px;
  font-size: .68rem;
  color: var(--muted);
  font-family: monospace;
}}
.card strong {{
  display: block;
  margin-bottom: 3px;
  padding-right: 52px;
  line-height: 1.4;
  color: var(--ink);
  font-size: .8rem;
}}
.cdesc {{ color: var(--muted); font-size: .74rem; line-height: 1.5; }}
.note {{ color: var(--doing) !important; margin-top: 5px; font-size: .72rem; }}
.rev  {{ color: var(--done)  !important; margin-top: 4px; font-size: .72rem; }}

/* ── Counter badge ── */
.cnt {{
  background: var(--border);
  border-radius: 999px;
  padding: 1px 7px;
  font-size: .68rem;
  font-weight: 400;
  color: var(--muted);
}}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-row">
    <h1>📊 e_seller — Relatório</h1>
    {links_html}
  </div>
  <div class="hdr-meta">
    <span>🕒 Brasília: <span id="clk">{server_time}</span></span>
    <span>Atualiza a cada 20s</span>
  </div>
</header>

<main>
  <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>

  <div class="kpis">
    <div class="kpi"><b>{total}</b><span>tarefas</span></div>
    <div class="kpi"><b style="color:var(--done)">{done}</b><span>concluídas ({pct}%)</span></div>
    <div class="kpi"><b style="color:var(--doing)">{doing}</b><span>em execução</span></div>
    <div class="kpi"><b style="color:var(--backlog)">{backlog_n}</b><span>a fazer</span></div>
    <div class="kpi"><b style="color:var(--blocked)">{blocked}</b><span>bloqueadas</span></div>
  </div>

  <p class="updated">Backlog atualizado: {updated}</p>
  <p class="updated" style="margin-bottom:12px;font-size:.72rem;color:#555">{goal}</p>

  {review_html}
  {sections}
</main>

<script>
(function () {{
  function tick() {{
    var el = document.getElementById('clk');
    if (el) {{
      el.textContent = new Date().toLocaleString('pt-BR', {{
        timeZone: 'America/Sao_Paulo'
      }});
    }}
  }}
  setInterval(tick, 1000);
  tick();
}})();
</script>
</body>
</html>"""


def create_report_app() -> FastAPI:
    """Cria o app FastAPI do relatório (caminho do backlog via env BACKLOG_PATH)."""
    backlog_path = os.environ.get("BACKLOG_PATH", "backlog.json")
    app = FastAPI(title="e_seller — Relatório", version="0.3.0")
    app.state.reader = BacklogReader(backlog_path)
    app.state.renderer = ReportRenderer()
    app.include_router(router)
    return app


app = create_report_app()
