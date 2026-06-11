# 15 — CI/CD

> Documento de planning · e_seller · 2026-06-06
> Integração e entrega contínuas, com custo zero.

---

## 1. Objetivo

Garantir que **nada quebrado** entre na branch principal: a cada push/PR, rodar
lint, testes e checagens, automaticamente.

## 2. Plataforma

- **GitHub Actions** (gratuito para repositórios, dentro das cotas) — assumido por padrão.
  - Se o repositório não for GitHub, alternativa: GitLab CI (também gratuito).
- Toda a pipeline roda em **containers**, espelhando o ambiente Docker local.

## 3. Pipeline de CI (em cada PR / push)

```
1. checkout
2. setup Python 3.14.x  (ou usar imagem Docker do projeto)
3. instalar dependências (cacheadas)
4. ruff check  +  ruff format --check     # PEP 8 (RNF-30)
5. subir Postgres de serviço (efêmero)
6. pytest + cobertura                      # TDD (RNF-31)
7. falhar se cobertura < limite acordado
```

> 💡 *Por que Postgres "de serviço"?* O GitHub Actions sobe um container Postgres
> só para o job de teste, idêntico ao de produção — testes realistas, descartável.

## 4. Gates (o que bloqueia o merge)

- ❌ Ruff com erros.
- ❌ Qualquer teste falhando.
- ❌ Cobertura abaixo do limite (sugestão inicial: 85% nos módulos de domínio).
- ✅ (Opcional) revisão aprovada por outra pessoa.

## 5. CD (entrega)

Para o MVP, **CD é manual/simples** (custo zero):
- Build da imagem Docker de produção.
- Deploy manual no destino escolhido (a definir — manter custo baixo).

Evolução futura (fora do MVP):
- Tag/release → build automático da imagem → deploy automatizado.
- Migrations (Alembic) aplicadas no deploy via `entrypoint.sh` (`alembic upgrade head`).

## 6. Branching

- `main`: sempre verde e implantável.
- Trabalho em branches `feat/...`, `fix/...` → PR → CI → merge.
- Specs acompanham o código no mesmo PR (SDD).

## 7. Artefatos

- Relatório de cobertura como artefato do job.
- Imagem Docker versionada (por commit/tag) quando o CD for ativado.

## 8. Pendências

- [ ] Confirmar plataforma (GitHub Actions vs outra).
- [ ] Destino de deploy de produção mantendo custo baixo.
- [ ] Limite de cobertura definitivo.
