"""Schemas (Pydantic) de entrada/saída do catálogo."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class ProductListItem(BaseModel):
    """Item de produto para listagem (não expõe o arquivo do e-book)."""

    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    author: str
    price: Decimal
    cover_url: str | None = None
    review_count: int = 0
    avg_rating: float = 0.0
    featured: bool = False
    created_at: datetime | None = None


class TaxonomyLabel(BaseModel):
    """Rótulo simples de taxonomia (nome + slug + total de produtos publicados)."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str
    count: int = 0


class ProductImageOut(BaseModel):
    """Imagem do produto para saída (capa ou galeria)."""

    model_config = ConfigDict(from_attributes=True)

    url: str
    alt_text: str
    is_cover: bool


class ProductFileOut(BaseModel):
    """Arquivo do produto para saída (formato e versão; sem expor a chave)."""

    model_config = ConfigDict(from_attributes=True)

    file_format: str
    version: str
    is_primary: bool


class ProductOut(ProductListItem):
    """Detalhe do produto (inclui descrição, taxonomia, imagens e formatos)."""

    description: str
    view_count: int = 0
    authors: list[TaxonomyLabel] = []
    tags: list[TaxonomyLabel] = []
    publisher: TaxonomyLabel | None = None
    series: TaxonomyLabel | None = None
    images: list[ProductImageOut] = []
    files: list[ProductFileOut] = []


class TopViewedProductOut(BaseModel):
    """Item de produto para relatório de mais visualizados (admin)."""

    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    view_count: int


class ProductCountOut(BaseModel):
    """Resposta do endpoint de contagem de produtos publicados."""

    total: int
    page: int
    page_size: int
    has_next: bool


class ImportIn(BaseModel):
    """Entrada do modo 'link': URL de um manifest JSON do e-book."""

    url: str


class ProductStatusIn(BaseModel):
    """Entrada para alterar o status de publicação de um produto."""

    status: str


class ProductUpdateIn(BaseModel):
    """Campos editáveis de um e-book (todos opcionais; envia só o que muda)."""

    title: str | None = None
    author: str | None = None
    description: str | None = None
    price: Decimal | None = None
    cover_url: str | None = None
    featured: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        """Garante que o título, se fornecido, não é vazio."""
        if value is not None:
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Título não pode ser vazio")
            return cleaned
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal | None) -> Decimal | None:
        """Garante preço não-negativo, se fornecido."""
        if value is not None and value < 0:
            raise ValueError("Preço não pode ser negativo")
        return value


class ProductDraftIn(BaseModel):
    """Schema canônico de um e-book a cadastrar (vale para os 3 modos)."""

    title: str
    author: str = ""
    description: str = ""
    price: Decimal
    category_slug: str | None = None
    cover_url: str | None = None
    authors: list[str] = []
    tags: list[str] = []
    publisher: str | None = None
    series: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Garante que o título não é vazio."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Título obrigatório")
        return cleaned

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        """Garante preço não-negativo."""
        if value < 0:
            raise ValueError("Preço não pode ser negativo")
        return value

