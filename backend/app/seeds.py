"""Semeadura de dados de desenvolvimento (idempotente).

Os dados são lidos de arquivos JSON externos (`seeds/`) — sem hardcode no código.
"""

from __future__ import annotations

import json
import pathlib
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User, UserRole
from app.catalog.asset_service import ProductAssetService
from app.catalog.models import Product, ProductFileFormat, ProductStatus
from app.catalog.taxonomy_service import TaxonomyService
from app.coupons.models import Coupon, DiscountType
from app.security.passwords import PasswordHasher
from app.security.storage import ProtectedStorage

# Diretório padrão: <raiz do projeto>/seeds/ (um nível acima do pacote app/).
_DEFAULT_SEEDS_DIR = pathlib.Path(__file__).parent.parent / "seeds"


class DevSeeder:
    """Cria produtos de exemplo e seus arquivos no armazenamento protegido."""

    def __init__(
        self,
        session: AsyncSession,
        storage: ProtectedStorage,
        seeds_dir: pathlib.Path | None = None,
    ) -> None:
        """Recebe a sessão, o armazenamento e (opcionalmente) o diretório de seeds."""
        self.session = session
        self.storage = storage
        self.seeds_dir = seeds_dir or _DEFAULT_SEEDS_DIR

    async def ensure_admin(
        self, email: str, password: str, hasher: PasswordHasher
    ) -> None:
        """Cria o usuário admin (se não existir) a partir da config (sem hardcode)."""
        result = await self.session.scalars(select(User).where(User.email == email))
        if result.first() is not None:
            return
        admin = User(
            email=email,
            password_hash=hasher.hash(password),
            full_name="Administrador",
            role=UserRole.ADMIN,
        )
        self.session.add(admin)
        await self.session.commit()

    async def run(self) -> None:
        """Cria os dados de exemplo apenas se ainda não existirem (idempotente)."""
        result = await self.session.scalars(select(Product).limit(1))
        if result.first() is not None:
            return

        samples = self._load_json("dev_products.json")
        taxonomy = TaxonomyService(self.session)
        assets = ProductAssetService(self.session)
        for sample in samples:
            product = Product(
                title=sample["title"],
                slug=sample["slug"],
                author=sample["author"],
                description=sample["description"],
                price=Decimal(sample["price"]),
                file_name=sample["file_name"],
                status=ProductStatus(sample["status"]),
            )
            await taxonomy.apply_to_product(
                product,
                authors=sample.get("authors", []),
                publisher=sample.get("publisher"),
                series=sample.get("series"),
                tags=sample.get("tags", []),
            )
            self.session.add(product)
            await self.session.flush()
            content = self._sample_content(sample["title"])
            self.storage.write_bytes(sample["file_name"], content)
            await assets.add_file(
                product.id,
                file_format=ProductFileFormat.TXT,
                storage_key=sample["file_name"],
                byte_size=len(content),
                is_primary=True,
            )
        await self.session.commit()

    async def ensure_coupon(self) -> None:
        """Cria cupons de exemplo (idempotente) a partir de seeds/dev_coupons.json."""
        coupons = self._load_json("dev_coupons.json")
        for coupon_data in coupons:
            result = await self.session.scalars(
                select(Coupon).where(Coupon.code == coupon_data["code"])
            )
            if result.first() is not None:
                continue
            self.session.add(
                Coupon(
                    code=coupon_data["code"],
                    discount_type=DiscountType(coupon_data["discount_type"]),
                    value=Decimal(coupon_data["value"]),
                    active=bool(coupon_data.get("active", True)),
                )
            )
        await self.session.commit()

    def _load_json(self, filename: str) -> list[dict]:
        """Carrega e parseia um arquivo JSON do diretório de seeds."""
        path = self.seeds_dir / filename
        with open(path, encoding="utf-8") as file_handle:
            return json.load(file_handle)

    def _sample_content(self, title: str) -> bytes:
        """Gera o conteúdo (bytes) de um e-book de exemplo a partir do título."""
        header = "e_seller — e-book de demonstracao\n"
        body = "Este e um arquivo de exemplo entregue apos a compra simulada.\n"
        text = f"{header}Titulo: {title}\n\n{body}"
        return text.encode("utf-8")
