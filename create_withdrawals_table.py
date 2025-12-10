import psycopg2

print("Conectando a la base de datos...")
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="POS",
    user="postgres",
    password="Tronquilo7*"
)

cursor = conn.cursor()

print("\n1. Añadiendo columnas nuevas a cash_register...")
try:
    cursor.execute("""
        ALTER TABLE cash_register 
        ADD COLUMN IF NOT EXISTS total_withdrawals NUMERIC(10, 2) DEFAULT 0.00,
        ADD COLUMN IF NOT EXISTS current_cash NUMERIC(10, 2) DEFAULT 0.00,
        ADD COLUMN IF NOT EXISTS cash_limit NUMERIC(10, 2) DEFAULT 5000.00;
    """)
    conn.commit()
    print("✓ Columnas añadidas a cash_register")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

print("\n2. Creando tabla cash_withdrawals...")
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_withdrawals (
            id BIGSERIAL PRIMARY KEY,
            cash_register_id BIGINT REFERENCES cash_register(id) NOT NULL,
            user_id INTEGER REFERENCES "Users"("ID") NOT NULL,
            
            amount NUMERIC(10, 2) NOT NULL,
            reason VARCHAR NOT NULL,
            notes TEXT,
            
            cash_before NUMERIC(10, 2) NOT NULL,
            cash_after NUMERIC(10, 2) NOT NULL,
            
            status VARCHAR DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            approved_by INTEGER REFERENCES "Users"("ID"),
            approved_at TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_withdrawal_date ON cash_withdrawals(created_at);
        CREATE INDEX IF NOT EXISTS idx_withdrawal_register ON cash_withdrawals(cash_register_id);
        CREATE INDEX IF NOT EXISTS idx_withdrawal_user ON cash_withdrawals(user_id);
    """)
    conn.commit()
    print("✓ Tabla cash_withdrawals creada")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

print("\n3. Verificando tablas...")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('cash_register', 'cash_withdrawals')
    ORDER BY table_name;
""")
tablas = cursor.fetchall()
print(f"Tablas encontradas: {[t[0] for t in tablas]}")

cursor.close()
conn.close()

print("\n✅ Base de datos actualizada correctamente")