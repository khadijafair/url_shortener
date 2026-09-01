# 🔗 URL Shortener API

Une API REST simple qui raccourcit des URLs longues, redirige vers l'URL d'origine, et garde un compteur de clics. Les liens peuvent aussi avoir une date d'expiration optionnelle.

> Projet réalisé dans le cadre d'un défi personnel "1 jour = 1 mini-projet" — Jour 1, thème Développement.

---

## 🎯 Fonctionnalités

- Raccourcir une URL longue en un code court unique (6 caractères)
- Rediriger automatiquement vers l'URL d'origine
- Compter le nombre de clics par lien
- Consulter les statistiques d'un lien (URL d'origine, clics, date de création)
- Définir une expiration optionnelle pour un lien (en jours)
- Documentation interactive auto-générée (Swagger)

---

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.10+ |
| Framework API | FastAPI |
| Base de données | SQLite + SQLAlchemy (ORM) |
| Serveur | Uvicorn |
| Validation | Pydantic |

---

## 📦 Installation

```bash
# Cloner le repo
git clone https://github.com/<ton-username>/url-shortener.git
cd url-shortener

# Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate   # sous Windows : venv\Scripts\activate

# Installer les dépendances
pip install fastapi uvicorn sqlalchemy pydantic
```

---

## 🚀 Lancer le projet

```bash
uvicorn main:app --reload
```

L'API est alors accessible sur `http://localhost:8000`.

La documentation interactive (Swagger) est disponible sur :
👉 `http://localhost:8000/docs`

---

## 📡 Endpoints

### `POST /shorten`
Crée une URL raccourcie.

**Body :**
```json
{
  "url": "https://www.example.com/une-tres-longue-url",
  "expiration_days": 7
}
```
> `expiration_days` est optionnel — si omis, le lien n'expire jamais.

**Réponse (201) :**
```json
{
  "short_code": "aZ3xK9",
  "short_url": "http://localhost:8000/aZ3xK9",
  "expires_at": "2026-09-08T12:00:00"
}
```

---

### `GET /{short_code}`
Redirige vers l'URL d'origine et incrémente le compteur de clics.

- **307** → redirection réussie
- **404** → code inexistant
- **410** → lien expiré

---

### `GET /stats/{short_code}`
Renvoie les statistiques d'un lien.

**Réponse (200) :**
```json
{
  "original_url": "https://www.example.com/...",
  "short_code": "aZ3xK9",
  "clicks": 12,
  "created_at": "2026-09-01T10:00:00"
}
```

---

## 🧪 Lancer les tests

```bash
# Terminal 1 : lancer le serveur
uvicorn main:app --reload

# Terminal 2 : lancer les tests
python test_api.py
```

---

## 📁 Structure du projet
url-shortener/
├── main.py # Routes et logique API
├── models.py # Modèle SQLAlchemy (table URL)
├── database.py # Configuration de la connexion DB
├── test_api.py # Tests manuels de l'API
└── shortener.db # Base SQLite (générée automatiquement)


---

## 💡 Pistes d'amélioration futures

- [ ] Ajouter une page HTML simple pour créer des liens sans passer par `/docs`
- [ ] Limiter le nombre de requêtes par IP (rate limiting)
- [ ] Permettre un code personnalisé (au lieu d'un code aléatoire)
- [ ] Migrer vers PostgreSQL pour un usage en production
- [ ] Ajouter Alembic pour gérer les migrations de schéma

---

## 📄 Licence

Projet personnel à but pédagogique — libre d'utilisation.