import psycopg2

print("Conectando a la base de datos...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="POS",
        user="postgres",
        password="Tronquilo7*"
    )
    print("✓ Conexión exitosa")
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    exit(1)

cursor = conn.cursor()

# 1. Ver columnas actuales
print("\n1. Verificando columnas actuales en cash_register...")
try:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'cash_register'
        ORDER BY ordinal_position;
    """)
    columnas = cursor.fetchall()
    print(f"   Columnas encontradas: {len(columnas)}")
    for col in columnas:
        print(f"     - {col[0]}: {col[1]}")
except Exception as e:
    print(f"✗ Error: {e}")

# 2. Añadir columnas faltantes
print("\n2. Añadiendo columnas faltantes...")
try:
    cursor.execute("""
        ALTER TABLE cash_register 
        ADD COLUMN IF NOT EXISTS expected_cash NUMERIC(10, 2),
        ADD COLUMN IF NOT EXISTS difference NUMERIC(10, 2);
    """)
    conn.commit()
    print("✓ Columnas añadidas")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

# 3. Verificar columnas finales
print("\n3. Verificando columnas finales...")
try:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'cash_register'
        ORDER BY ordinal_position;
    """)
    columnas = cursor.fetchall()
    print(f"   Columnas finales: {len(columnas)}")
    for col in columnas:
        print(f"     - {col[0]}: {col[1]}")
except Exception as e:
    print(f"✗ Error: {e}")

cursor.close()
conn.close()

print("\n✅ Base de datos actualizada correctamente")
print("   Ahora reinicia el servidor: uvicorn main:app --reload")