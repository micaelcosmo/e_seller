"""Instala e confere o harness agnóstico da skill /qa num projeto.

A fonte canônica é `~/.claude/skills/qa/`. Num projeto ficam duas cópias, nunca
editadas à mão:
  - `qa-harness/motor/`     o motor que roda (`python qa-harness/executar.py ...`)
  - `.claude/skills/qa/`    espelho da skill (SKILL.md, metodologia, modelos,
                            este script) — versionado com o projeto, para quem
                            clona sem ter a skill global

Uso:
  python ~/.claude/skills/qa/sincronizar.py <projeto>              global → projeto
  python ~/.claude/skills/qa/sincronizar.py <projeto> --conferir   só compara (0 igual · 2 diverge)
  python <projeto>/.claude/skills/qa/sincronizar.py <projeto> --instalar-global
                                                                   projeto → global (máquina nova)
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

GLOBAL = Path.home() / ".claude" / "skills" / "qa"
ARQUIVOS_DA_SKILL = ["SKILL.md", "metodologia.md", "adotar.md", "sincronizar.py"]
PASTAS_DA_SKILL = ["modelos"]
IGNORAR = {"__pycache__", ".pytest_cache"}


def versao(pasta_do_motor: Path) -> tuple:
    caminho = pasta_do_motor / "VERSAO"
    if not caminho.exists():
        return (0,)
    partes = []
    for pedaco in caminho.read_text(encoding="utf-8").strip().split("."):
        if pedaco.isdigit():
            partes.append(int(pedaco))
    return tuple(partes)


def texto_da_versao(numeros: tuple) -> str:
    convertidos = []
    for numero in numeros:
        convertidos.append(str(numero))
    return ".".join(convertidos)


def arquivos(pasta: Path) -> dict:
    """{caminho relativo: sha256} de uma pasta, ignorando cache."""
    encontrados: dict = {}
    if not pasta.exists():
        return encontrados
    for caminho in sorted(pasta.rglob("*")):
        if not caminho.is_file():
            continue
        relativas = caminho.relative_to(pasta).parts
        ignorado = False
        for parte in relativas:
            if parte in IGNORAR:
                ignorado = True
        if ignorado:
            continue
        encontrados[caminho.relative_to(pasta).as_posix()] = hashlib.sha256(caminho.read_bytes()).hexdigest()
    return encontrados


def arquivos_da_skill(pasta: Path) -> dict:
    """Só o que pertence ao espelho da skill (sem o motor)."""
    encontrados: dict = {}
    for nome in ARQUIVOS_DA_SKILL:
        caminho = pasta / nome
        if caminho.is_file():
            encontrados[nome] = hashlib.sha256(caminho.read_bytes()).hexdigest()
    for nome in PASTAS_DA_SKILL:
        for relativo, hash_ in arquivos(pasta / nome).items():
            encontrados[nome + "/" + relativo] = hash_
    return encontrados


def diferencas(origem: dict, destino: dict) -> list:
    linhas = []
    for relativo in sorted(set(origem) | set(destino)):
        if relativo not in destino:
            linhas.append("+ " + relativo)
        elif relativo not in origem:
            linhas.append("- " + relativo)
        elif origem[relativo] != destino[relativo]:
            linhas.append("~ " + relativo)
    return linhas


def listar(origem: Path, projeto: Path) -> dict:
    return {
        "motor": diferencas(arquivos(origem / "motor"), arquivos(projeto / "qa-harness" / "motor")),
        "skill": diferencas(arquivos_da_skill(origem), arquivos_da_skill(projeto / ".claude" / "skills" / "qa")),
    }


def copiar_motor(origem: Path, destino: Path) -> None:
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origem, destino, ignore=shutil.ignore_patterns(*IGNORAR))


def copiar_skill(origem: Path, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    for nome in ARQUIVOS_DA_SKILL:
        if (origem / nome).is_file():
            shutil.copy2(origem / nome, destino / nome)
    for nome in PASTAS_DA_SKILL:
        if (destino / nome).exists():
            shutil.rmtree(destino / nome)
        if (origem / nome).exists():
            shutil.copytree(origem / nome, destino / nome, ignore=shutil.ignore_patterns(*IGNORAR))


def conferir(origem: Path, projeto: Path) -> int:
    v_global = versao(origem / "motor")
    v_projeto = versao(projeto / "qa-harness" / "motor")
    print("motor global " + texto_da_versao(v_global) + " · motor do projeto " + texto_da_versao(v_projeto))
    divergencias = listar(origem, projeto)
    total = len(divergencias["motor"]) + len(divergencias["skill"])
    if total == 0:
        print("sincronizado: motor e espelho da skill idênticos à fonte global")
        return 0
    for rotulo in ("motor", "skill"):
        for linha in divergencias[rotulo]:
            print("  " + rotulo + ": " + linha)
    if v_projeto > v_global:
        print("o projeto tem motor MAIS NOVO que o global — confirme com o usuário e rode --instalar-global")
    else:
        print("desatualizado: rode  python ~/.claude/skills/qa/sincronizar.py " + str(projeto))
    return 2


def instalar_no_projeto(origem: Path, projeto: Path) -> int:
    if not (projeto / "qa-harness").exists():
        print(str(projeto) + " não tem qa-harness/ — veja adotar.md antes de sincronizar")
        return 1
    v_global = versao(origem / "motor")
    v_projeto = versao(projeto / "qa-harness" / "motor")
    if v_projeto > v_global:
        print("recusado: o motor do projeto (" + texto_da_versao(v_projeto) + ") é mais novo que o global ("
              + texto_da_versao(v_global) + ")")
        return 1
    divergencias = listar(origem, projeto)
    copiar_motor(origem / "motor", projeto / "qa-harness" / "motor")
    copiar_skill(origem, projeto / ".claude" / "skills" / "qa")
    total = 0
    for rotulo in ("motor", "skill"):
        for linha in divergencias[rotulo]:
            print("  " + rotulo + ": " + linha)
            total = total + 1
    print(str(total) + " arquivo(s) atualizados — motor " + texto_da_versao(v_global) + " instalado em " + str(projeto))
    return 0


def instalar_global(projeto: Path) -> int:
    espelho = projeto / ".claude" / "skills" / "qa"
    motor = projeto / "qa-harness" / "motor"
    if not espelho.exists() or not motor.exists():
        print("o projeto não tem .claude/skills/qa/ e qa-harness/motor/ para instalar")
        return 1
    if versao(GLOBAL / "motor") > versao(motor):
        print("recusado: o motor global é mais novo que o do projeto")
        return 1
    copiar_skill(espelho, GLOBAL)
    copiar_motor(motor, GLOBAL / "motor")
    print("skill /qa instalada em " + str(GLOBAL) + " (motor " + texto_da_versao(versao(motor)) + ")")
    return 0


def principal() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("projeto", help="raiz do projeto (a que tem qa-harness/)")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--conferir", action="store_true")
    grupo.add_argument("--instalar-global", action="store_true", dest="instalar_global")
    argumentos = parser.parse_args()
    projeto = Path(argumentos.projeto).resolve()
    if argumentos.instalar_global:
        return instalar_global(projeto)
    if argumentos.conferir:
        return conferir(GLOBAL, projeto)
    return instalar_no_projeto(GLOBAL, projeto)


if __name__ == "__main__":
    sys.exit(principal())
