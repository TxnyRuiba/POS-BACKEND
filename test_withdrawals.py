import requests

BASE_URL = "http://localhost:8000"

# 1. Login
print("1. Login...")
response = requests.post(f"{BASE_URL}/users/login", json={
    "Username": "testuser",
    "Password": "test1234"
})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Verificar límite
print("\n2. Verificando límite de efectivo...")
response = requests.get(f"{BASE_URL}/withdrawals/me/check-limit", headers=headers)
print(response.json())

# 3. Crear retiro
print("\n3. Creando retiro de $1000...")
response = requests.post(
    f"{BASE_URL}/withdrawals/",
    json={
        "Amount": 1000.00,
        "Reason": "security_limit",
        "Notes": "Retiro por exceso de efectivo"
    },
    headers=headers
)
if response.status_code == 201:
    retiro = response.json()
    print(f"✓ Retiro creado: ${retiro['amount']}")
    print(f"  Efectivo antes: ${retiro['cash_before']}")
    print(f"  Efectivo después: ${retiro['cash_after']}")
else:
    print(f"✗ Error: {response.json()}")

# 4. Ver mis retiros
print("\n4. Consultando mis retiros...")
response = requests.get(f"{BASE_URL}/withdrawals/me/current", headers=headers)
data = response.json()
print(f"✓ Total de retiros: {data['total_withdrawals']}")

print("\n✅ Prueba completada!")