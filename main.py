import random
import string
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import URL

from typing import Optional

# Crée les tables en DB si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

# Schéma Pydantic
class URLRequest(BaseModel):
    url: HttpUrl
    expiration_days: Optional[int] = None

# Gestion propre des sessions DB (ouvre et ferme automatiquement)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.post("/shorten", status_code=201)
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    target_url = str(request.url)
    
    # 1. Vérifier l'unicité du code généré
    code = generate_code()
    while db.query(URL).filter(URL.short_code == code).first():
        code = generate_code()


    expires_at = None
    if request.expiration_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expiration_days)

    # 2. Sauvegarder en DB avec SQLAlchemy
    db_url = URL(original_url=target_url, short_code=code, expires_at=expires_at)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # 3. Retourner la réponse
    return {
        "short_code": code,
        "short_url": f"http://localhost:8000/{code}",
        "expires_at": db_url.expires_at
    }


@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    # 1. Chercher l'URL en DB
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    
    # Si le code n'existe pas -> Erreur 404
    if not db_url:
        raise HTTPException(status_code=404, detail="Code court introuvable")

    # Vérification de l'expiration
    if db_url.expires_at and db_url.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Ce lien a expiré")
    
    # 2. Incrémenter le compteur de clics
    db_url.clicks += 1
    db.commit()

    # 3. Rediriger vers l'URL d'origine
    return RedirectResponse(url=db_url.original_url)


@app.get("/stats/{short_code}")
def get_stats(short_code: str, db: Session = Depends(get_db)):
    # 1. Chercher l'URL en DB
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Code court introuvable")

    # 2. Retourner les informations et le compteur de clics
    return {
        "original_url": db_url.original_url,
        "short_code": db_url.short_code,
        "clicks": db_url.clicks,
        "created_at": db_url.created_at
    }