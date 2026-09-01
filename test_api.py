import pytest
import requests

# URL de base de notre API locale
BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
def short_code():
    """
    Fixture Pytest : Crée automatiquement une nouvelle URL courte 
    avant chaque test qui en a besoin et retourne son code.
    """
    payload = {"url": "https://www.example.com/test-pytest"}
    response = requests.post(f"{BASE_URL}/shorten", json=payload)
    assert response.status_code == 201, f"Erreur lors de la création : {response.text}"
    return response.json()["short_code"]


def test_shorten_url():
    """1. Teste la création d'une URL courte (POST /shorten)"""
    payload = {"url": "https://www.example.com/une-tres-longue-url-a-raccourcir"}
    response = requests.post(f"{BASE_URL}/shorten", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["short_url"].startswith("http://localhost:8000/")


def test_redirect_and_clicks_increment(short_code):
    """2. Teste la redirection ET l'incrémentation du compteur de clics (3 clics)"""
    # Étape A : Vérifier que les clics sont à 0 au départ
    stats_before = requests.get(f"{BASE_URL}/stats/{short_code}").json()
    assert stats_before["clicks"] == 0

    # Étape B : Simuler 3 clics (Redirections)
    for _ in range(3):
        redirect_res = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        assert redirect_res.status_code in (307, 302)
        assert redirect_res.headers["location"] == "https://www.example.com/test-pytest"

    # Étape C : Vérifier que le compteur est bien passé à 3
    stats_after = requests.get(f"{BASE_URL}/stats/{short_code}").json()
    assert stats_after["clicks"] == 3


def test_code_inexistant():
    """3. Teste qu'un code inexistant renvoie une erreur 404 (GET /{code})"""
    response = requests.get(f"{BASE_URL}/codeInexistant123", allow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "Code court introuvable"


def test_url_invalide():
    """4. Teste la validation Pydantic sur une URL mal formée (POST /shorten -> 422)"""
    response = requests.post(f"{BASE_URL}/shorten", json={"url": "pas-une-url-valide"})
    assert response.status_code == 422

def test_url_avec_expiration_courte():
    """Crée une URL qui expire immédiatement (0 jour = déjà expirée après création)"""
    response = requests.post(
        f"{BASE_URL}/shorten",
        json={"url": "https://example.com", "expiration_days": -1}  # date dans le passé
    )
    code = response.json()["short_code"]

    redirect_response = requests.get(f"{BASE_URL}/{code}", allow_redirects=False)
    assert redirect_response.status_code == 410
    print("✅ Lien expiré correctement bloqué (410)")


def test_url_sans_expiration():
    """Vérifie qu'une URL sans expiration_days fonctionne toujours normalement"""
    response = requests.post(f"{BASE_URL}/shorten", json={"url": "https://example.com"})
    code = response.json()["short_code"]

    redirect_response = requests.get(f"{BASE_URL}/{code}", allow_redirects=False)
    assert redirect_response.status_code == 307
    print("✅ URL sans expiration toujours fonctionnelle")