# UML de Classe (DB) — viva

> Tipo: `db`/design · Área: `db` · 2026-06-10 · Status: **Vivo**
> Diagrama de **classes** dos models (SQLAlchemy). Atualizado a cada migração.

---

## ⚠️ Regra de manutenção (obrigatória)

**Atualizar este diagrama a CADA migração** (Alembic + SchemaSync). A migration e
a UML andam juntas: nenhuma mudança de schema é considerada pronta sem atualizar
este arquivo e o [`CHANGELOG`](../CHANGELOG.md) da pasta `unit/`.

---

## Diagrama (Mermaid `classDiagram`)

```mermaid
classDiagram
    class User {
        +int id
        +str email [unique, idx]
        +str password_hash
        +str full_name
        +UserRole role
        +bool is_active
        +datetime created_at
        +datetime? deleted_at  %% LGPD soft-delete
        +str? totp_secret_enc  %% AES-256-GCM encrypted
        +bool totp_enabled
    }

    class Product {
        +int id
        +str title
        +str slug [unique, idx]
        +str author
        +str description
        +Decimal price  %% CHECK >= 0
        +str? cover_url
        +str? file_name
        +ProductStatus status [idx]
        +int? category_id [FK, idx]
        +int? publisher_id [FK, idx]
        +int? series_id [FK, idx]
        +datetime created_at
    }

    class Category {
        +int id
        +str name
        +str slug [unique, idx]
    }

    class Author {
        +int id
        +str name
        +str slug [unique, idx]
    }

    class Publisher {
        +int id
        +str name
        +str slug [unique, idx]
    }

    class Series {
        +int id
        +str name
        +str slug [unique, idx]
    }

    class Tag {
        +int id
        +str name
        +str slug [unique, idx]
    }

    class ProductFile {
        +int id
        +int product_id [FK, idx]
        +ProductFileFormat file_format
        +str version
        +str storage_key
        +int byte_size
        +bool is_primary
        +datetime created_at
    }

    class ProductImage {
        +int id
        +int product_id [FK, idx]
        +str url
        +str alt_text
        +int position
        +bool is_cover
    }

    class Order {
        +int id
        +str reference [unique, idx]
        +str buyer_email [idx]
        +int? user_id [FK, idx]
        +int? billing_profile_id [FK, idx]
        +Decimal amount
        +OrderStatus status [idx]
        +datetime created_at
        +datetime? updated_at
    }

    class OrderItem {
        +int id
        +int order_id [FK, idx]
        +int product_id [FK, idx]
        +Decimal unit_price
        +int quantity  %% CHECK > 0
    }

    class Payment {
        +int id
        +int order_id [FK, idx]
        +str provider
        +str provider_payment_id [unique, idx]
        +str status [idx]
        +datetime? processed_at
        +datetime created_at
    }

    class DownloadGrant {
        +int id
        +int order_item_id [FK, idx]
        +int product_id [FK, idx]
        +str token [unique, idx]
        +datetime expires_at
        +int max_downloads
        +int download_count
        +datetime created_at
    }

    class DownloadLog {
        +int id
        +int download_grant_id [FK, idx]
        +str ip_hash
        +datetime downloaded_at
    }

    class Entitlement {
        +int id
        +int user_id [FK, idx]
        +int product_id [FK, idx]
        +int order_item_id [FK]
        +datetime created_at
        %% UNIQUE (user_id, product_id)
    }

    class Review {
        +int id
        +int product_id [FK, idx]
        +int user_id [FK, idx]
        +int rating  %% CHECK BETWEEN 1 AND 5
        +str comment
        +datetime created_at
        %% UNIQUE (user_id, product_id)
    }

    class BillingProfile {
        +int id
        +int user_id [FK, unique, idx]
        +PersonType person_type
        +str legal_name
        +str document [idx]
        +str address_line
        +str city
        +str state
        +str postal_code
        +str country
        +datetime created_at
        +datetime updated_at
    }

    class Refund {
        +int id
        +int payment_id [FK, idx]
        +int order_id [FK, idx]
        +Decimal amount
        +str reason
        +RefundStatus status
        +datetime created_at
    }

    class Cart {
        +int id
        +int user_id [FK, unique, idx]
    }

    class CartItem {
        +int id
        +int cart_id [FK, idx]
        +int product_id [FK, idx]
    }

    class Wishlist {
        +int id
        +int user_id [FK, unique, idx]
    }

    class WishlistItem {
        +int id
        +int wishlist_id [FK, idx]
        +int product_id [FK, idx]
    }

    class NewsletterSubscriber {
        +int id
        +str email [unique, idx]
        +bool is_active
        +datetime subscribed_at
    }

    class Coupon {
        +int id
        +str code [unique, idx]
        +str discount_type
        +Decimal discount_value
        +datetime? expires_at
        +int? max_uses
        +int uses
        +bool is_active
    }

    class RevokedToken {
        +int id
        +str jti [unique, idx]
        +datetime expires_at
        +datetime revoked_at
    }

    class UserActivityLog {
        +int id
        +int? user_id [FK, idx]
        +str event_type [idx]
        +dict? meta
        +datetime created_at [idx]
        %% COMPOUND IDX (user_id, created_at)
    }

    class ApiKey {
        +int id
        +int user_id [FK, idx]
        +str name
        +str key_hash [unique, idx]  %% SHA-256
        +str prefix  %% primeiros 8 chars
        +bool is_active
        +datetime? last_used_at
        +datetime? expires_at
        +datetime created_at
    }

    %% Associações M2M
    class product_author {
        +int product_id [PK, FK]
        +int author_id [PK, FK]
    }

    class product_tag {
        +int product_id [PK, FK]
        +int tag_id [PK, FK]
    }

    %% Relações
    User "1" --> "*" RevokedToken
    User "1" --> "*" UserActivityLog
    User "1" --> "*" ApiKey
    User "1" --> "0..1" BillingProfile
    User "1" --> "0..1" Cart
    User "1" --> "0..1" Wishlist
    User "1" --> "*" Order
    User "1" --> "*" Entitlement
    User "1" --> "*" Review

    Product "1" --> "*" ProductFile
    Product "1" --> "*" ProductImage
    Product "*" --> "0..1" Category
    Product "*" --> "0..1" Publisher
    Product "*" --> "0..1" Series
    Product "*" <-- "product_author" --> "*" Author
    Product "*" <-- "product_tag" --> "*" Tag
    Product "1" --> "*" Entitlement

    Order "1" --> "*" OrderItem
    Order "1" --> "*" Payment
    Order "1" --> "*" Refund
    OrderItem "1" --> "*" DownloadGrant
    OrderItem "1" --> "*" Entitlement
    DownloadGrant "1" --> "*" DownloadLog

    Cart "1" --> "*" CartItem
    Wishlist "1" --> "*" WishlistItem
    Payment "1" --> "*" Refund
```

---

## Histórico de atualizações

| Data       | Mudança |
|------------|---------|
| 2026-06-13 | Épico AAA: adicionados RevokedToken, UserActivityLog, ApiKey. User ganha totp_secret_enc e totp_enabled. Migration: d4e5f6g7h8i9. |
| 2026-06-10 | Adicionados: Author, Publisher, Series, Tag, product_author/tag M2M, ProductFile, ProductImage, BillingProfile, Refund, Cart, Wishlist, NewsletterSubscriber, Coupon. Corrigido Decimal nos campos monetários. Adicionados constraints CHECK (price≥0, rating 1-5, quantity>0), updated_at em Order, deleted_at em User (LGPD). Índices FK explícitos em todos os modelos. |
| 2026-06-07 | Versão inicial com User, Product, Category, Order, OrderItem, Payment, DownloadGrant, DownloadLog, Entitlement, Review. |
