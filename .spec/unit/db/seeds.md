# Unit: seeds (`fixture`/dados)

> Tipo: `seed`/dados · Área: `db`
> Deriva de: [`planning/10`](../../planning/10-modelo-de-dados.md) §4 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Popular dados de exemplo para **dev** (e base de cenários de teste): produtos,
pedidos em vários estados, um admin.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/db/seeds.py::seed_dev_data` |
| Teste | `backend/tests/db/test_seeds.py` |

## 3. Contrato

```python
class DevSeeder:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self) -> None:
        ...  # idempotente: não duplica se já existir
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `session` | inserir |
| models do Tier 🟢 | dados |
| `security/password_hashing` | senha do admin de dev |

## 5. Comportamento / regras

- Cria: 1 admin (`is_staff`), 3 produtos publicados + 1 rascunho, pedidos `pending`/`paid`/`failed`.
- **Idempotente**: rodar duas vezes não duplica (checar antes de inserir — laço explícito).
- Apenas em ambiente **dev** (nunca em prod).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Seed em DB vazio | cria os registros esperados |
| T2 | Seed repetido | não duplica (idempotente) |
| T3 | Ambiente prod | recusa rodar |

## 7. Rastreabilidade

- Planning [`10`](../../planning/10-modelo-de-dados.md) · Units: `tests/factories` (testes usam factories, não o seed de dev)

## 8. Pendências

- [ ] Senha do admin de dev via env (não fixa no código).
