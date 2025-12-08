import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("DIAGNÓSTICO COMPLETO DEL SISTEMA")
print("=" * 60)

# 1. Verificar que el servidor responde
print("\n1. Verificando servidor...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Servidor activo: {response.json()}")
except Exception as e:
    print(f"✗ Servidor no responde: {e}")
    exit(1)

# 2. Verificar endpoint de salud
print("\n2. Verificando salud del sistema...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.json()}")
except Exception as e:
    print(f"✗ Error en health: {e}")

# 3. Registrar usuario de prueba
print("\n3. Registrando usuario de prueba...")
try:
    response = requests.post(f"{BASE_URL}/users/register", json={
        "Username": "testuser",
        "Password": "test1234"
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Usuario registrado")
    elif response.status_code == 400:
        print(f"⚠ Usuario ya existe (OK)")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# 4. Login
print("\n4. Probando login...")
try:
    response = requests.post(f"{BASE_URL}/users/login", json={
        "Username": "testuser",
        "Password": "test1234"
    })
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"✓ Login exitoso")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"✗ Login falló")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 5. Verificar perfil
print("\n5. Verificando perfil de usuario...")
try:
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Perfil: {response.json()}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# 6. Verificar rol
print("\n6. Verificando rol de usuario...")
try:
    response = requests.get(f"{BASE_URL}/users/me/role", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Rol: {response.json()}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# 7. PROBLEMA: Abrir caja
print("\n7. Probando abrir caja registradora...")
print("   Enviando: {'InitialCash': 1000.00}")
try:
    response = requests.post(
        f"{BASE_URL}/cash-register/open",
        json={"InitialCash": 1000.00},
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    print(f"   Response Text: {response.text[:500]}")
    
    if response.status_code == 201:
        print(f"✓ Caja abierta: {response.json()}")
    else:
        print(f"✗ Error abriendo caja")
        if response.text:
            try:
                print(f"   JSON Error: {response.json()}")
            except:
                print(f"   Raw Text: {response.text}")
        
except Exception as e:
    print(f"✗ Exception: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)