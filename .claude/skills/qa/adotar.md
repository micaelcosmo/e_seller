# Como levar o harness de QA a um projeto — e a uma máquina nova

A skill `/qa` é uma só, agnóstica, instalada em `~/.claude/skills/qa/`. Cada
projeto contribui apenas com configuração, adaptador e especificação.

## A. Projeto novo (ainda sem `qa-harness/`)

Só com pedido explícito do usuário. Na raiz do projeto:

1. **Estrutura e motor.**
   ```bash
   mkdir -p qa-harness/testes/api qa-harness/evidencias spec/qa spec/test/historias spec/test/planos spec/test/jornadas spec/code
   cp ~/.claude/skills/qa/modelos/qa-harness/{executar.py,requirements.txt,config.yaml,adaptador.py} qa-harness/
   cp ~/.claude/skills/qa/modelos/qa-harness/testes/_contrato.yaml qa-harness/testes/
   cp ~/.claude/skills/qa/modelos/qa-harness/evidencias/_contrato.yaml qa-harness/evidencias/
   python ~/.claude/skills/qa/sincronizar.py .      # instala qa-harness/motor/ e .claude/skills/qa/
   ```
2. **Especificação.** Copie os modelos de `~/.claude/skills/qa/modelos/spec/` para
   `spec/` e preencha os trechos marcados `PREENCHER` (fontes de verdade, papéis,
   destinos da convenção de comentários). Escreva `spec/qa/05-harness-metodologia.md`
   com o que é específico do projeto.
3. **`qa-harness/config.yaml`.** Nome, assinatura da aplicação na home, pastas do
   produto (somente leitura), URLs, perfis com a conta de cada um, alvos do coletor
   de comentários.
4. **`qa-harness/adaptador.py`.** `autenticar(perfil)` (obrigatório se há perfil com
   conta), `verificar_ambiente()`, `preparar_massa()`, `suites_de_integracao()` e,
   se o login não é por cookie, `entrar_no_navegador()`.
5. **`.gitignore`.** Acrescente o conteúdo de `modelos/gitignore.txt`.
6. **Dependências.** `pip install -r qa-harness/requirements.txt` (mais as do adaptador,
   declaradas em `dependencias_extras` do config).
7. **Primeira cadeia.** Derive as histórias pela `_instrucao.md`, escreva os planos,
   as suítes de API, as jornadas (uma por história de frontend) e o catálogo da
   base visual. `python qa-harness/executar.py lint` até zerar as lacunas.
8. `/qa completo`.

## B. Projeto com harness anterior ao motor (modo legado)

A skill funciona nele seguindo o `spec/qa/05-harness-metodologia.md` do projeto.
Para migrar: faça o passo A.1 sem sobrescrever o que existe, mova para o
`adaptador.py` o que era específico (autenticação, massa, verificações, suítes),
troque os percursos/fluxos visuais escritos em código por jornadas YAML com passos
de conferência, e o catálogo de telas por `_base-visual.yaml`. Evidências antigas
(um `.json` por print) são substituídas na primeira execução.

## C. Máquina nova (o projeto já tem o harness)

O espelho da skill vem versionado com o projeto:

```bash
pip install -r qa-harness/requirements.txt
python .claude/skills/qa/sincronizar.py . --instalar-global   # copia para ~/.claude/skills/qa/
python qa-harness/executar.py bootstrap                        # baixa o Chromium sozinho
```

Verifique: numa sessão do Claude Code, `/qa` aparece como skill. Teste com
`/qa relatorios` — inofensivo: sem manifesto, ele só avisa que é preciso executar
uma suíte antes.

## Regra de manutenção

Toda mudança no harness começa em `~/.claude/skills/qa/` (SKILL.md, metodologia,
motor, modelos). Suba `motor/VERSAO` quando o motor mudar de comportamento. Depois,
em cada projeto: `python ~/.claude/skills/qa/sincronizar.py .` e proposta de commit.
`qa-harness/motor/` e `.claude/skills/qa/` dos projetos nunca se editam à mão.
