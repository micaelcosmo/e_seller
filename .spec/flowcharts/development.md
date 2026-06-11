# Fluxograma — Processo de Desenvolvimento (SDD + TDD)

> Trilha flowcharts · e_seller · 2026-06-07

```mermaid
flowchart TD
    A[Ideia / requisito] --> B[Escrever/atualizar SPEC em .spec/]
    B --> C{Spec revisada e aprovada?}
    C -- Nao --> B
    C -- Sim --> D[Escrever TESTE que falha - RED]
    D --> E[Implementar minimo - GREEN]
    E --> F[Refatorar mantendo verde]
    F --> G[Ruff + pytest local + pre-commit]
    G --> H{CI verde? cobertura >= 95%?}
    H -- Nao --> E
    H -- Sim --> I[Auto-reflexao - .spec/self_reflection]
    I --> J[Atualizar STATUS / CHANGELOG / UML / dashboard]
    J --> K[Merge na main]
    K --> L[Deploy - PC + Cloudflare Tunnel]
    L --> M[Verificar no ar]
```

> Regra de ouro: **nenhuma linha de código sem spec e sem teste que a justifique**
> (ver [`../standards/`](../standards/) e [`../planning/17-fluxo-sdd.md`](../planning/17-fluxo-sdd.md)).
