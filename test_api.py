import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Login
print("1. Login...")
try:
    response = requests.post(f"{BASE_URL}/users/login", json={
        "Username": "Tronquilo",
        "Password": "Tronquilo7*"
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"✓ Token obtenido: {token[:20]}...")
    else:
        print(f"✗ Error en login:")
        print(f"   Status: {response.status_code}")
        try:
            print(f"   Detail: {response.json()}")
        except:
            print(f"   Text: {response.text}")
        exit(1)
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: No se puede conectar al servidor")
    print("   ¿Está corriendo 'uvicorn main:app --reload'?")
    exit(1)
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    exit(1)

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Abrir caja
print("\n2. Abriendo caja...")
try:
    response = requests.post(f"{BASE_URL}/cash-register/open", 
        json={"InitialCash": 1000.00},
        headers=headers
    )
    
    if response.status_code == 201:
        caja = response.json()
        print(f"✓ Caja abierta: ID {caja['id']}")
    else:
        print(f"✗ Error abriendo caja:")
        print(f"   Status: {response.status_code}")
        print(f"   Detail: {response.json()}")
        exit(1)
        
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    exit(1)

# 3. Ver caja actual
print("\n3. Consultando caja actual...")
response = requests.get(f"{BASE_URL}/cash-register/me/current", headers=headers)
print(f"✓ {response.json()}")

# 4. Crear carrito
print("\n4. Creando carrito...")
response = requests.post(f"{BASE_URL}/cart/", headers=headers)
if response.status_code != 201:
    print(f"✗ Error: {response.status_code} - {response.json()}")
    exit(1)
cart = response.json()
cart_id = cart["id"]
print(f"✓ Carrito creado: ID {cart_id}")

# 5. Agregar productos
print("\n5. Agregando productos...")
response = requests.post(f"{BASE_URL}/cart/{cart_id}/items",
    json={"product_id": 1, "quantity": 2},
    headers=headers
)
if response.status_code != 200:
    print(f"✗ Error: {response.status_code}")
    print(f"   Detail: {response.json()}")
    exit(1)
print(f"✓ Producto agregado")

# 6. Ver carrito
print("\n6. Consultando carrito...")
response = requests.get(f"{BASE_URL}/cart/{cart_id}", headers=headers)
cart_data = response.json()
print(f"✓ Total: ${cart_data['total']}")

# 7. Crear ticket
print("\n7. Creando ticket...")
response = requests.post(f"{BASE_URL}/tickets/",
    json={
        "CartId": cart_id,
        "PaymentMethod": "cash",
        "AmountPaid": 500.00
    },
    headers=headers
)
if response.status_code != 201:
    print(f"✗ Error: {response.status_code}")
    print(f"   Detail: {response.json()}")
    exit(1)
    
ticket = response.json()
print(f"✓ Ticket creado: {ticket['ticket_number']}")
print(f"  Total: ${ticket['total']}")
print(f"  Cambio: ${ticket['change_given']}")

# 8. Ver resumen de caja
print("\n8. Resumen de caja...")
response = requests.get(f"{BASE_URL}/cash-register/{caja['id']}/summary", 
    headers=headers
)
resumen = response.json()
print(f"✓ Ventas totales: ${resumen['resumen']['total_ventas']}")
print(f"  Transacciones: {resumen['resumen']['num_transacciones']}")

# 9. Cerrar caja
print("\n9. Cerrando caja...")
response = requests.post(f"{BASE_URL}/cash-register/{caja['id']}/close",
    json={"FinalCash": 1450.00},
    headers=headers
)
caja_cerrada = response.json()
print(f"✓ Caja cerrada")
print(f"  Diferencia: ${caja_cerrada['difference']}")

print("\n✅ Todas las pruebas completadas!")