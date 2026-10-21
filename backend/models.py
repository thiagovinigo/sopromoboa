import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from database import Base


class ProductModel(Base):
    """Modelo principal de produtos e ofertas agregadas."""
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    list_price = Column(Float, nullable=True) # Preço cheio ("de R$ ...")
    previous_price = Column(Float, nullable=True) # Preço antes da queda
    lowest_historic_price = Column(Float, nullable=True) # Menor valor registrado no histórico
    price_dropped = Column(Integer, default=0, index=True) # 1 = queda ativa na janela recente
    discount_percent = Column(Float, default=0.0, index=True)
    
    brand = Column(String, index=True, nullable=True)
    category = Column(String, index=True, default="geral")
    subcategory = Column(String, index=True, nullable=True)
    
    url = Column(Text, nullable=False) # Link original da loja
    affiliate_url = Column(Text, nullable=True) # Link comissionado
    source = Column(String, index=True, nullable=False) # Nome da loja (Amazon, Mercado Livre, etc.)
    image_url = Column(Text, nullable=True)
    
    is_available = Column(Integer, default=1, index=True) # 1 = disponível, 0 = esgotado
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    coupon_code = Column(String, nullable=True)
    free_shipping = Column(Integer, default=0) # 1 = frete grátis informado
    is_affiliate_deal = Column(Integer, default=0, index=True) # 1 = anúncio cadastrado no nosso painel de afiliados
    is_featured = Column(Integer, default=0, index=True) # 1 = destaque na vitrine
    clicks_count = Column(Integer, default=0) # total de cliques comissionados gerados
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    price_changed_at = Column(DateTime, nullable=True, index=True)


class PriceHistoryModel(Base):
    """Histórico de variações de preço para gráficos e auditoria de promoções reais."""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    seen_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class FavoriteModel(Base):
    """Produtos favoritados pelo usuário comum (identificado por token anônimo no navegador)."""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_token_hash = Column(String, index=True, nullable=False)
    product_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class StoreModel(Base):
    """Lojas monitoradas e suas configurações de afiliados."""
    __tablename__ = "stores"

    slug = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    logo_url = Column(Text, nullable=True)
    affiliate_network = Column(String, nullable=True) # Amazon, Magalu, Lomadee, Awin, etc.
    affiliate_tag = Column(String, nullable=True)
    redirect_template = Column(Text, nullable=True) # Ex: {url}&tag={tag}
    is_active = Column(Integer, default=1)
    total_deals = Column(Integer, default=0)


class AffiliateProgramModel(Base):
    """Gestão de programas e credenciais de afiliados da plataforma."""
    __tablename__ = "affiliate_programs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False) # Ex: Amazon Brasil, Parceiro Magalu, Lomadee
    network_slug = Column(String, unique=True, index=True, nullable=False) # amazon, magalu, mercadolivre
    tracking_id = Column(String, nullable=False) # Tag do afiliado / ID de comissão
    url_pattern = Column(Text, nullable=True) # Template para converter links
    commission_rate = Column(String, nullable=True) # Ex: "Até 12%"
    status = Column(String, default="active") # active, pending, paused
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class AlertModel(Base):
    """Alertas de preço criados por usuários (gerenciados via token do navegador)."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_token_hash = Column(String, index=True, nullable=False)
    search_term = Column(String, nullable=False)
    target_price = Column(Float, nullable=True)
    min_discount_percent = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_notified_at = Column(DateTime, nullable=True)
    matched_count = Column(Integer, default=0)


class ClickModel(Base):
    """Auditoria e métricas de cliques em links de afiliados."""
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    referrer = Column(String, nullable=True)
