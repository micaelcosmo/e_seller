"""Models do catálogo: Category, Product e taxonomia (autor/editora/série/tag)."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Tabelas de associação muitos-para-muitos do catálogo. São metadados
# declarativos (ligam produto a autores e a tags), não funções soltas.
product_author = Table(
    "product_author",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True),
    Column("author_id", ForeignKey("author.id"), primary_key=True),
)

product_tag = Table(
    "product_tag",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)


class ProductStatus(enum.StrEnum):
    """Estado de publicação de um produto."""

    DRAFT = "draft"
    PUBLISHED = "published"


class ProductFileFormat(enum.StrEnum):
    """Formato do arquivo de e-book disponível."""

    PDF = "pdf"
    EPUB = "epub"
    TXT = "txt"


class Category(Base):
    """Categoria de produtos (classificação simples)."""

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)


class Author(Base):
    """Autor de e-books (um e-book pode ter vários autores)."""

    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)


class Publisher(Base):
    """Editora responsável por publicar o e-book."""

    __tablename__ = "publisher"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)


class Series(Base):
    """Coleção/série que agrupa vários e-books."""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)


class Tag(Base):
    """Marcação livre para facetas de busca."""

    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class Product(Base):
    """E-book à venda no catálogo."""

    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    author: Mapped[str] = mapped_column(String(160), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    # Numeric(10,2) → Decimal; evita erro de arredondamento em aritmética monetária.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus), default=ProductStatus.DRAFT, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.id"), nullable=True, index=True
    )
    publisher_id: Mapped[int | None] = mapped_column(
        ForeignKey("publisher.id"), nullable=True, index=True
    )
    series_id: Mapped[int | None] = mapped_column(
        ForeignKey("series.id"), nullable=True, index=True
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    featured: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relações de taxonomia (carregadas com selectin para uso em contexto async).
    publisher: Mapped[Publisher | None] = relationship(lazy="selectin")
    series: Mapped[Series | None] = relationship(lazy="selectin")
    authors: Mapped[list[Author]] = relationship(
        secondary=product_author, lazy="selectin"
    )
    tags: Mapped[list[Tag]] = relationship(secondary=product_tag, lazy="selectin")
    files: Mapped[list[ProductFile]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )
    images: Mapped[list[ProductImage]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )


class ProductFile(Base):
    """Arquivo de e-book de um produto (formato + versão; alvo de watermark)."""

    __tablename__ = "product_file"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    file_format: Mapped[ProductFileFormat] = mapped_column(Enum(ProductFileFormat))
    version: Mapped[str] = mapped_column(String(20), default="1")
    storage_key: Mapped[str] = mapped_column(String(500))
    byte_size: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ProductImage(Base):
    """Imagem de um produto (capa ou galeria), com ordem e texto alternativo."""

    __tablename__ = "product_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(200), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)
