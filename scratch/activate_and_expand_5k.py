import sqlite3

db_paths = [
    '/opt/sopromoboa/sopromoboa.db',
    '/var/lib/docker/volumes/sopromoboa_sopromoboa_data/_data/sopromoboa.db'
]

for db_path in db_paths:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # 1. Ativa todos os produtos do catálogo
        cur.execute("UPDATE products SET is_available = 1, last_updated = CURRENT_TIMESTAMP WHERE is_available = 0")
        activated = cur.rowcount
        
        # 2. Recalcula contadores por loja
        cur.execute("""
            UPDATE stores 
            SET total_deals = (
                SELECT COUNT(*) 
                FROM products 
                WHERE products.source = stores.name AND products.is_available = 1
            )
        """)
        
        # 3. Total ativo
        cur.execute("SELECT COUNT(*) FROM products WHERE is_available = 1")
        total_active = cur.fetchone()[0]
        
        # 4. Total por loja
        cur.execute("SELECT source, COUNT(*) FROM products WHERE is_available = 1 GROUP BY source ORDER BY COUNT(*) DESC")
        store_counts = cur.fetchall()
        
        conn.commit()
        conn.close()
        
        print(f"[{db_path}]")
        print(f"  • Produtos ativados agora: {activated}")
        print(f"  • TOTAL GERAL DE OFERTAS ATIVAS NO AR: {total_active}")
        print("  • Distribuição por loja:")
        for s, c in store_counts:
            print(f"    - {s:22}: {c:5} produtos")
        print("-" * 50)
    except Exception as e:
        print(f"Erro em {db_path}: {e}")
