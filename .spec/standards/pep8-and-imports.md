# PEP 8 e Imports

> Padrão · e_seller · 2026-06-06

---

## 1. PEP 8 (essencial)

- Indentação de **4 espaços** (nunca tabs).
- `line-length = 88` (Ruff format cuida).
- 2 linhas em branco entre funções/classes de nível de módulo; 1 entre métodos.
- Espaço após vírgula; sem espaço sobrando dentro de parênteses.
- `snake_case` para funções/variáveis, `PascalCase` para classes, `UPPER_SNAKE` para constantes.

> A formatação automática (Ruff) resolve a maior parte. O foco humano é **clareza e estrutura**.

## 2. Hierarquia de imports (com linha em branco entre grupos)

Ordem em **três grupos**, separados por **uma linha em branco**:

1. Biblioteca padrão (stdlib)
2. Bibliotecas de terceiros
3. Locais (do próprio projeto)

### ✅ Certo
```python
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.payments.gateway_mercadopago import MercadoPagoGateway
```

### ❌ Errado
```python
from app.core.config import Settings
import secrets
from fastapi import APIRouter
from sqlalchemy.orm import Session
import datetime
```
(grupos misturados, sem separação, fora de ordem)

## 3. Regras de import

- **Imports absolutos** a partir de `app.` (evitar relativos longos).
- Sem `from module import *`.
- Dentro de cada grupo: ordem alfabética (Ruff `I` reordena).
- `import x` antes de `from x import y` quando no mesmo grupo (convenção do isort/Ruff).

## 4. Enforcement

- Grupos, ordem e separação são aplicados automaticamente pelo **Ruff** (regra `I`).
- Ver [`enforcement.md`](enforcement.md).
