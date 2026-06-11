"""Views do painel administrativo (SQLAdmin)."""

from sqladmin import ModelView

from app.accounts.models import User
from app.billing.models import BillingProfile
from app.catalog.models import (
    Author,
    Category,
    Product,
    ProductFile,
    ProductImage,
    Publisher,
    Series,
    Tag,
)
from app.coupons.models import Coupon
from app.delivery.models import DownloadGrant
from app.orders.models import Order
from app.payments.models import Payment
from app.refunds.models import Refund
from app.reviews.models import Review


class ProductAdmin(ModelView, model=Product):
    """Administração de e-books (produtos)."""

    name = "Produto"
    name_plural = "Produtos"
    column_list = [
        Product.id,
        Product.title,
        Product.slug,
        Product.author,
        Product.price,
        Product.status,
    ]
    column_searchable_list = [Product.title, Product.author, Product.slug]


class CategoryAdmin(ModelView, model=Category):
    """Administração de categorias."""

    name = "Categoria"
    name_plural = "Categorias"
    column_list = [Category.id, Category.name, Category.slug]


class ProductFileAdmin(ModelView, model=ProductFile):
    """Administração de arquivos de e-book (formatos/versões)."""

    name = "Arquivo"
    name_plural = "Arquivos"
    column_list = [
        ProductFile.id,
        ProductFile.product_id,
        ProductFile.file_format,
        ProductFile.version,
        ProductFile.is_primary,
        ProductFile.byte_size,
    ]


class ProductImageAdmin(ModelView, model=ProductImage):
    """Administração de imagens do produto (capa/galeria)."""

    name = "Imagem"
    name_plural = "Imagens"
    column_list = [
        ProductImage.id,
        ProductImage.product_id,
        ProductImage.url,
        ProductImage.is_cover,
        ProductImage.position,
    ]


class AuthorAdmin(ModelView, model=Author):
    """Administração de autores."""

    name = "Autor"
    name_plural = "Autores"
    column_list = [Author.id, Author.name, Author.slug]
    column_searchable_list = [Author.name]


class PublisherAdmin(ModelView, model=Publisher):
    """Administração de editoras."""

    name = "Editora"
    name_plural = "Editoras"
    column_list = [Publisher.id, Publisher.name, Publisher.slug]
    column_searchable_list = [Publisher.name]


class SeriesAdmin(ModelView, model=Series):
    """Administração de séries/coleções."""

    name = "Série"
    name_plural = "Séries"
    column_list = [Series.id, Series.name, Series.slug]
    column_searchable_list = [Series.name]


class TagAdmin(ModelView, model=Tag):
    """Administração de tags."""

    name = "Tag"
    name_plural = "Tags"
    column_list = [Tag.id, Tag.name, Tag.slug]
    column_searchable_list = [Tag.name]


class OrderAdmin(ModelView, model=Order):
    """Visualização de pedidos (somente leitura)."""

    name = "Pedido"
    name_plural = "Pedidos"
    column_list = [
        Order.id,
        Order.reference,
        Order.buyer_email,
        Order.status,
        Order.amount,
        Order.created_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class PaymentAdmin(ModelView, model=Payment):
    """Visualização de pagamentos (somente leitura)."""

    name = "Pagamento"
    name_plural = "Pagamentos"
    column_list = [
        Payment.id,
        Payment.provider_payment_id,
        Payment.status,
        Payment.processed_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class CouponAdmin(ModelView, model=Coupon):
    """Administração de cupons de desconto."""

    name = "Cupom"
    name_plural = "Cupons"
    column_list = [
        Coupon.id,
        Coupon.code,
        Coupon.discount_type,
        Coupon.value,
        Coupon.active,
        Coupon.redemptions_count,
        Coupon.valid_until,
    ]
    column_searchable_list = [Coupon.code]


class UserAdmin(ModelView, model=User):
    """Administração de usuários (sem expor o hash da senha)."""

    name = "Usuário"
    name_plural = "Usuários"
    column_list = [User.id, User.email, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email]


class ReviewAdmin(ModelView, model=Review):
    """Visualização de avaliações."""

    name = "Avaliação"
    name_plural = "Avaliações"
    column_list = [Review.id, Review.product_id, Review.user_id, Review.rating]
    can_create = False
    can_edit = False


class RefundAdmin(ModelView, model=Refund):
    """Visualização dos estornos (somente leitura)."""

    name = "Estorno"
    name_plural = "Estornos"
    column_list = [
        Refund.id,
        Refund.order_id,
        Refund.payment_id,
        Refund.amount,
        Refund.status,
        Refund.created_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class BillingProfileAdmin(ModelView, model=BillingProfile):
    """Visualização dos perfis fiscais (dados sensíveis — somente leitura)."""

    name = "Perfil Fiscal"
    name_plural = "Perfis Fiscais"
    column_list = [
        BillingProfile.id,
        BillingProfile.user_id,
        BillingProfile.person_type,
        BillingProfile.legal_name,
        BillingProfile.city,
        BillingProfile.state,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class DownloadGrantAdmin(ModelView, model=DownloadGrant):
    """Visualização das concessões de download (somente leitura)."""

    name = "Download"
    name_plural = "Downloads"
    column_list = [
        DownloadGrant.id,
        DownloadGrant.product_id,
        DownloadGrant.expires_at,
        DownloadGrant.download_count,
        DownloadGrant.max_downloads,
    ]
    can_create = False
    can_edit = False
    can_delete = False
