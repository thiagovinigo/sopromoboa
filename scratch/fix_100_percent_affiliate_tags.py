import sqlite3, urllib.parse, re

db_path = '/var/lib/docker/volumes/sopromoboa_sopromoboa_data/_data/sopromoboa.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

LOMADEE_ID = "2324685"
ML_TAG = "goth1115110"
SHOPEE_TAG = "an_18356121277"
AMAZON_TAG = "thiagovinigo-20"

def clean_title_to_query(title):
    clean = re.sub(r"[—\-\(\)\/\,\.\:\+]", " ", title)
    clean = re.sub(r"\s+", " ", clean).strip()
    words = clean.split()[:7]
    return urllib.parse.quote_plus(" ".join(words)), urllib.parse.quote_plus("-".join(words).lower())

print("=== INICIANDO AJUSTE DE 100% DAS OFERTAS ===")

# 1. Ajusta os 29 produtos do Mercado Livre com meli.la para busca oficial comissionada com goth1115110
cur.execute("SELECT id, title, url FROM products WHERE source = 'Mercado Livre' AND affiliate_url NOT LIKE '%goth1115110%' AND affiliate_url NOT LIKE '%/sec/%'")
ml_rows = cur.fetchall()
for pid, title, url in ml_rows:
    q, q_slug = clean_title_to_query(title)
    new_aff = f"https://lista.mercadolivre.com.br/{q_slug}?matt_tool={ML_TAG}"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"Mercado Livre: {len(ml_rows)} produtos meli.la convertidos para tag oficial {ML_TAG}!")

# 2. Ajusta os 35 produtos da Shopee com s.shopee ou tags antigas
cur.execute("SELECT id, title, url FROM products WHERE source = 'Shopee' AND (affiliate_url NOT LIKE '%an_18356121277%' OR affiliate_url LIKE '%sopromoboa_sp%')")
sp_rows = cur.fetchall()
for pid, title, url in sp_rows:
    q, q_slug = clean_title_to_query(title)
    new_aff = f"https://shopee.com.br/search?keyword={q}&utm_source={SHOPEE_TAG}&mmp_pid={SHOPEE_TAG}&utm_medium=affiliates"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"Shopee: {len(sp_rows)} produtos convertidos para tag oficial {SHOPEE_TAG}!")

# 3. Ajusta Magazine Luiza pendentes para Lomadee
cur.execute("SELECT id, title, url FROM products WHERE source = 'Magazine Luiza' AND affiliate_url NOT LIKE '%2324685%'")
mag_rows = cur.fetchall()
for pid, title, url in mag_rows:
    clean_url = url
    if 'magazinevoce.com.br' in clean_url:
        clean_url = re.sub(r'https?://(www\.)?magazinevoce\.com\.br/[^/]+/', 'https://www.magazineluiza.com.br/', clean_url)
    clean_url = re.sub(r'[?&]parceiro=[^&]+', '', clean_url)
    clean_url = re.sub(r'[?&]tipo=link', '', clean_url).rstrip('?&')
    new_aff = f"https://redir.lomadee.com/v2/click?sourceId={LOMADEE_ID}&url={urllib.parse.quote_plus(clean_url)}"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"Magazine Luiza: {len(mag_rows)} produtos vinculados à Lomadee {LOMADEE_ID}!")

# 4. Ajusta KaBuM pendentes para Lomadee
cur.execute("SELECT id, title, url FROM products WHERE source = 'KaBuM!' AND affiliate_url NOT LIKE '%2324685%'")
kab_rows = cur.fetchall()
for pid, title, url in kab_rows:
    new_aff = f"https://redir.lomadee.com/v2/click?sourceId={LOMADEE_ID}&url={urllib.parse.quote_plus(url)}"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"KaBuM!: {len(kab_rows)} produtos vinculados à Lomadee {LOMADEE_ID}!")

# 5. Ajusta Terabyteshop pendentes para Lomadee
cur.execute("SELECT id, title, url FROM products WHERE source = 'Terabyteshop' AND affiliate_url NOT LIKE '%2324685%'")
tb_rows = cur.fetchall()
for pid, title, url in tb_rows:
    new_aff = f"https://redir.lomadee.com/v2/click?sourceId={LOMADEE_ID}&url={urllib.parse.quote_plus(url)}"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"Terabyteshop: {len(tb_rows)} produtos vinculados à Lomadee {LOMADEE_ID}!")

# 6. Ajusta lojas secundárias (Lojas Renner, Cirilo Cabos) via Lomadee
cur.execute("SELECT id, title, url, source FROM products WHERE source IN ('Lojasrenner', 'Cirilocabos')")
sec_rows = cur.fetchall()
for pid, title, url, src in sec_rows:
    new_aff = f"https://redir.lomadee.com/v2/click?sourceId={LOMADEE_ID}&url={urllib.parse.quote_plus(url)}"
    cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (new_aff, pid))
print(f"Lojas parceiras Lomadee secundárias: {len(sec_rows)} produtos atualizados!")

conn.commit()
conn.close()
print("=== CONCLUÍDO COM SUCESSO! ===")
