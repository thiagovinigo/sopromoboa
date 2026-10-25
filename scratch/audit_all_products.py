import sqlite3

db_path = '/var/lib/docker/volumes/sopromoboa_sopromoboa_data/_data/sopromoboa.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Checa produtos sem source (loja)
cur.execute("SELECT id, title FROM products WHERE source IS NULL OR trim(source) = ''")
no_source = cur.fetchall()
print(f"1. Produtos SEM LOJA (source vazio): {len(no_source)}")

# 2. Checa produtos sem affiliate_url (vazio ou nulo)
cur.execute("SELECT id, title, source FROM products WHERE affiliate_url IS NULL OR trim(affiliate_url) = ''")
no_aff = cur.fetchall()
print(f"2. Produtos SEM affiliate_url: {len(no_aff)}")
if no_aff:
    for r in no_aff[:5]:
        print("   Exemplo:", r)

# 3. Auditoria rigorosa por loja e tag do usuário:
user_tags = {
    "Amazon": ("thiagovinigo-20", ["%thiagovinigo-20%"]),
    "Mercado Livre": ("goth1115110", ["%goth1115110%", "%mercadolivre.com/sec/%", "%mercadolivre.com.br/sec/%"]),
    "Shopee": ("an_18356121277", ["%an_18356121277%"]),
    "Magazine Luiza": ("2324685", ["%2324685%"]),
    "KaBuM!": ("2324685", ["%2324685%"]),
    "Casas Bahia": ("2324685", ["%2324685%"]),
    "Terabyteshop": ("2324685", ["%2324685%"]),
}

print("\n3. Auditoria loja por loja contra suas tags oficiais:")
total_com_tag = 0
total_sem_tag = 0
sem_tag_exemplos = []

for store, (tag, patterns) in user_tags.items():
    # Total de produtos da loja
    cur.execute("SELECT count(*) FROM products WHERE source = ?", (store,))
    total_store = cur.fetchone()[0]
    
    # Produtos com a tag
    where_clauses = " OR ".join(["affiliate_url LIKE ?" for _ in patterns])
    cur.execute(f"SELECT count(*) FROM products WHERE source = ? AND ({where_clauses})", (store, *patterns))
    ok_count = cur.fetchone()[0]
    
    missing_count = total_store - ok_count
    total_com_tag += ok_count
    total_sem_tag += missing_count
    
    print(f"   - {store:18} | Total: {total_store:5} | COM sua tag: {ok_count:5} | SEM sua tag: {missing_count:3}")
    
    if missing_count > 0:
        cur.execute(f"SELECT id, title, source, url, affiliate_url FROM products WHERE source = ? AND NOT ({where_clauses}) LIMIT 5", (store, *patterns))
        sem_tag_exemplos.extend(cur.fetchall())

# 4. Outras lojas fora das 7 principais
cur.execute("""
    SELECT source, count(*) 
    FROM products 
    WHERE source NOT IN ('Amazon', 'Mercado Livre', 'Shopee', 'Magazine Luiza', 'KaBuM!', 'Casas Bahia', 'Terabyteshop')
    GROUP BY source
""")
other_stores = cur.fetchall()
print(f"\n4. Lojas secundárias no banco fora das 7 principais:")
for s, c in other_stores:
    print(f"   - {s}: {c} produtos")

if sem_tag_exemplos:
    print(f"\n5. Detalhes das ofertas que ainda não tinham a tag no banco ({len(sem_tag_exemplos)} amostras):")
    for r in sem_tag_exemplos:
        print(f"   ID: {r[0]} | Loja: {r[2]} | Titulo: {r[1][:40]}")
        print(f"     URL original: {r[3][:70]}")
        print(f"     URL afiliado atual: {str(r[4])[:70]}")

conn.close()
