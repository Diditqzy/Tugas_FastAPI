import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base

# --- SETUP DATABASE TESTING ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# =================================================================
# 1. PENGUJIAN ALUR AUTENTIKASI (REGISTER/LOGIN)
# =================================================================

def test_register_user():
    response = client.post(
        "/register",
        json={"username": "didit_mahasiswa", "password": "password123", "role": "user"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "didit_mahasiswa"
    assert response.json()["role"] == "user"

def test_login_user():
    # Register dulu
    client.post("/register", json={"username": "didit_mahasiswa", "password": "password123", "role": "user"})
    
    # Coba Login (Form data pakai 'data', bukan 'json')
    response = client.post(
        "/login",
        data={"username": "didit_mahasiswa", "password": "password123"} 
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Helper function biar nggak capek login berulang kali di tes berikutnya
def get_token(username, role):
    client.post("/register", json={"username": username, "password": "password123", "role": role})
    response = client.post("/login", data={"username": username, "password": "password123"})
    return response.json()["access_token"]


# =================================================================
# 2. PENGUJIAN ENDPOINT CRUD OPERASIONAL
# =================================================================

def test_crud_create_read_update():
    # Ambil token JWT
    token = get_token("tester_crud", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # CREATE (POST) - Membutuhkan Login
    response_post = client.post(
        "/items/",
        json={"merk": "Yamaha", "tipe": "R15", "kapasitas_cc": 155, "siap_dijual": True},
        headers=headers
    )
    assert response_post.status_code == 200
    motor_id = response_post.json()["idmotor"]

    # READ (GET) - Bebas tanpa login
    response_get = client.get(f"/items/{motor_id}")
    assert response_get.status_code == 200
    assert response_get.json()["merk"] == "Yamaha"

    # UPDATE (PUT) - Membutuhkan Login
    response_put = client.put(
        f"/items/{motor_id}",
        json={"merk": "Yamaha", "tipe": "R15M", "kapasitas_cc": 155, "siap_dijual": False},
        headers=headers
    )
    assert response_put.status_code == 200
    assert response_put.json()["tipe"] == "R15M"
    assert response_put.json()["siap_dijual"] == False


# =================================================================
# 3. PENGUJIAN RBAC (ACCESS DENIED)
# =================================================================

def test_rbac_access_denied_untuk_user_biasa():
    # Setup: Buat data motor & token untuk User biasa
    token_user = get_token("user_biasa", "user")
    headers_user = {"Authorization": f"Bearer {token_user}"}
    
    post_response = client.post(
        "/items/",
        json={"merk": "Suzuki", "tipe": "GSX", "kapasitas_cc": 150, "siap_dijual": True},
        headers=headers_user
    )
    motor_id = post_response.json()["idmotor"]

    # EKSEKUSI RBAC: User biasa mencoba DELETE -> Harus Ditolak (403 Forbidden)
    response_delete = client.delete(f"/items/{motor_id}", headers=headers_user)
    assert response_delete.status_code == 403
    assert response_delete.json()["detail"] == "Access Denied! Fitur ini hanya untuk Admin."

def test_rbac_sukses_untuk_admin():
    # Setup: Buat token khusus Admin
    token_admin = get_token("super_admin", "admin")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Admin menambahkan data
    post_response = client.post(
        "/items/",
        json={"merk": "Kawasaki", "tipe": "Ninja", "kapasitas_cc": 250, "siap_dijual": True},
        headers=headers_admin
    )
    motor_id = post_response.json()["idmotor"]

    # EKSEKUSI RBAC: Admin mencoba DELETE -> Harus Berhasil (200 OK)
    response_delete = client.delete(f"/items/{motor_id}", headers=headers_admin)
    assert response_delete.status_code == 200
    assert response_delete.json()["message"] == "Motor berhasil dihapus"