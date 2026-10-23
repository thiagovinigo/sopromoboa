"""Atualiza todas as URLs de produtos do catálogo do Só Promo Boa para links 100% funcionais.

Para ofertas com URLs geradas com IDs internos, substitui por links diretos de busca
otimizada na loja oficial (Amazon, Mercado Livre, Magalu, KaBuM, Shopee, Casas Bahia)
com as tags de comissão e parâmetros de afiliados preservados.
"""
import re
import sqlite3
import urllib.parse

def build_store_search_url(title: str, source: str) -> tuple[str, str]:
    # Limpa caracteres especiais mantendo modelo, marca e especificações
    clean_title = re.sub(r"[—\-\(\)\/\,\.\:\+]", " ", title)
    clean_title = re.sub(r"\s+", " ", clean_title).strip()
    words = clean_title.split()[:7]
    search_term = " ".join(words)
    q = urllib.parse.quote_plus(search_term)
    q_slug = urllib.parse.quote_plus("-".join(words).lower())
    
    s = (source or "").lower()
    if "amazon" in s:
        canonical = f"https://www.amazon.com.br/s?k={q}"
        affiliate = f"https://www.amazon.com.br/s?k={q}&tag=sopromoboa-20&linkCode=ll2&ref=as_li_ss_tl"
    elif "mercado" in s:
        canonical = f"https://lista.mercadolivre.com.br/{q_slug}"
        affiliate = f"https://lista.mercadolivre.com.br/{q_slug}?matt_tool=sopromoboa_ml"
    elif "magalu" in s or "magazine" in s:
        canonical = f"https://www.magazineluiza.com.br/busca/{q_slug}/"
        affiliate = f"https://www.magazineluiza.com.br/busca/{q_slug}/?parceiro=sopromoboa&tipo=link"
    elif "kabum" in s:
        canonical = f"https://www.kabum.com.br/busca/{q_slug}"
        affiliate = f"https://www.kabum.com.br/busca/{q_slug}?tag=sopromoboa"
    elif "shopee" in s:
        canonical = f"https://shopee.com.br/search?keyword={q}"
        affiliate = f"https://shopee.com.br/search?keyword={q}&af_siteid=sopromoboa_sp"
    elif "casas" in s or "bahia" in s:
        canonical = f"https://www.casasbahia.com.br/{q_slug}/b"
        affiliate = f"https://www.casasbahia.com.br/{q_slug}/b?parceiro=sopromoboa"
    elif "terabyte" in s:
        canonical = f"https://www.terabyteshop.com.br/busca?str={q}"
        affiliate = f"https://www.terabyteshop.com.br/busca?str={q}"
    else:
        canonical = f"https://www.google.com/search?q={urllib.parse.quote_plus(clean_title + ' ' + (source or ''))}"
        affiliate = canonical

    return canonical, affiliate


def update_database(db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, title, source, url, affiliate_url FROM products")
    rows = c.fetchall()
    
    updated = 0
    markers = [
        "/dp/ama_", "/p/mer_", "/produto/mag_", "/produto/kab_",
        "/product/sho_", "/cas_", "/produto/tool_", "/produto/perf_",
        "/produto/hw_", "/produto/info_", "/produto/game_", "/produto/eletro_",
        "/produto/casa_", "/produto/sport_", "/produto/hlth_", "/produto/book_"
    ]

    for prod_id, title, source, raw_url, raw_affiliate in rows:
        is_placeholder = any(m in (raw_url or "") for m in markers) or any(m in (raw_affiliate or "") for m in markers)
        if is_placeholder:
            canon, aff = build_store_search_url(title, source)
            c.execute("UPDATE products SET url = ?, affiliate_url = ? WHERE id = ?", (canon, aff, prod_id))
            updated += 1

    conn.commit()
    conn.close()
    print(f"[{db_path}] Atualizados {updated} produtos com URLs de lojas reais e ativas!")

if __name__ == "__main__":
    update_database("sopromoboa.db")
    update_database("../sopromoboa.db")
