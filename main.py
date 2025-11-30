from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import json
import base64
import hmac
import hashlib
import os

from database import db
from models import UserRegister, UserLogin, RequestSubmit
from auth import hash_password, verify_password


# --------------------------------------------------------
# Lifespan : init DB au démarrage Render - CORRIGÉ
# --------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage - initialisation de la base de données
    print("🔄 Démarrage de l'application...")
    try:
        await db.init_db()
        print("✅ Base de données initialisée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base: {e}")
        raise
    
    yield
    
    # Arrêt - fermeture propre des connexions
    print("🔄 Arrêt de l'application...")
    try:
        await db.close()
        print("✅ Connexions fermées avec succès")
    except Exception as e:
        print(f"⚠️ Erreur lors de la fermeture: {e}")


app = FastAPI(
    title="Gestion des Requêtes Universitaires",
    lifespan=lifespan
)


# --------------------------------------------------------
# Config templates + static
# --------------------------------------------------------
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --------------------------------------------------------
# Cookies sécurisés
# --------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")


def sign_data(data: str) -> str:
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()


def create_user_cookie(user_data: dict) -> str:
    data_json = json.dumps(user_data)
    data_b64 = base64.b64encode(data_json.encode()).decode()
    signature = sign_data(data_b64)
    return f"{data_b64}.{signature}"


def verify_user_cookie(cookie_data: str) -> dict | None:
    try:
        if not cookie_data:
            return None

        data_b64, signature = cookie_data.split(".")
        if sign_data(data_b64) != signature:
            return None

        data_json = base64.b64decode(data_b64).decode()
        return json.loads(data_json)

    except Exception:
        return None


def get_current_user(user_data: str = Cookie(None, alias="user_data")):
    if not user_data:
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    user = verify_user_cookie(user_data)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    return user


# --------------------------------------------------------
# ROUTES HTML
# --------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(request: Request):
    form = await request.form()

    try:
        user_data = UserRegister(
            matricule=form.get("matricule"),
            name=form.get("name"),
            last_name=form.get("last_name"),
            email=form.get("email"),
            phone=form.get("phone"),
            password=form.get("password")
        )

        # Vérifier email / matricule
        user_exists = await db.fetch_one(
            "SELECT user_id FROM users WHERE email = %s OR matricule = %s",
            (user_data.email, user_data.matricule)
        )

        if user_exists:
            raise HTTPException(status_code=400, detail="Email ou matricule déjà utilisé")

        # Insert MySQL
        await db.execute_query(
            """INSERT INTO users (matricule, name, last_name, email, phone, password)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                user_data.matricule,
                user_data.name,
                user_data.last_name,
                user_data.email,
                user_data.phone,
                hash_password(user_data.password)
            )
        )

        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        })


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_user(request: Request):
    form = await request.form()

    try:
        login_data = UserLogin(
            login=form.get("login"),
            password=form.get("password")
        )

        user = await db.fetch_one(
            """SELECT user_id, matricule, name, last_name, email, password 
               FROM users WHERE email = %s OR matricule = %s""",
            (login_data.login, login_data.login)
        )

        if not user or not verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=400, detail="Identifiants incorrects")

        user_session = {
            "user_id": user["user_id"],
            "matricule": user["matricule"],
            "name": user["name"],
            "last_name": user["last_name"],
            "email": user["email"]
        }

        cookie = create_user_cookie(user_session)

        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(
            key="user_data",
            value=cookie,
            httponly=True,
            max_age=86400,
            samesite="lax"
        )
        return response

    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": str(e)
        })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })


@app.get("/submit-request", response_class=HTMLResponse)
async def submit_request_form(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("submit_request.html", {
        "request": request,
        "user": current_user
    })


@app.post("/submit-request")
async def submit_request(request: Request, current_user=Depends(get_current_user)):
    form = await request.form()

    try:
        note_exam = form.get("note_exam") == "on"
        note_cc = form.get("note_cc") == "on"
        note_tp = form.get("note_tp") == "on"
        note_tpe = form.get("note_tpe") == "on"
        autre = form.get("autre") == "on"
        just_p = form.get("just_p") == "on"

        req_data = RequestSubmit(
            all_name=f"{current_user['name']} {current_user['last_name']}",
            matricule=current_user["matricule"],
            cycle=form.get("cycle"),
            level=int(form.get("level")),
            nom_code_ue=form.get("nom_code_ue"),
            note_exam=note_exam,
            note_cc=note_cc,
            note_tp=note_tp,
            note_tpe=note_tpe,
            autre=autre,
            comment=form.get("comment"),
            just_p=just_p
        )

        await db.execute_query(
            """INSERT INTO requests (user_id, all_name, matricule, cycle, level,
                                     nom_code_ue, note_exam, note_cc, note_tp, note_tpe,
                                     autre, comment, just_p)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                current_user["user_id"],
                req_data.all_name,
                req_data.matricule,
                req_data.cycle,
                req_data.level,
                req_data.nom_code_ue,
                note_exam, note_cc, note_tp, note_tpe,
                autre, req_data.comment, just_p
            )
        )

        return RedirectResponse(url="/my-requests", status_code=303)

    except Exception as e:
        return templates.TemplateResponse("submit_request.html", {
            "request": request,
            "user": current_user,
            "error": str(e)
        })






@app.get("/my-requests", response_class=HTMLResponse)
async def my_requests(request: Request, current_user=Depends(get_current_user)):
    try:
        print(f"🔍 DEBUG - User connecté: {current_user}")
        
        # Vérifiez aussi toutes les requêtes dans la base
        all_requests = await db.fetch_all("SELECT user_id, request_id FROM requests")
        print(f"🔍 DEBUG - Toutes les requêtes dans la DB: {all_requests}")
        
        rows = await db.fetch_all(
            """SELECT request_id, all_name, state, matricule, cycle, level, nom_code_ue,
                      note_exam, note_cc, note_tp, note_tpe, autre, comment,
                      just_p, created_at
               FROM requests
               WHERE user_id = %s
               ORDER BY created_at DESC""",
            (current_user["user_id"],)
        )
        
        print(f"🔍 DEBUG - Requêtes trouvées pour user_id {current_user['user_id']}: {len(rows)}")
        
        return templates.TemplateResponse("my-requests.html", {
            "request": request,
            "user": current_user,
            "requests": rows
        })

    except Exception as e:
        print(f"❌ Erreur dans my_requests: {e}")
        return templates.TemplateResponse("my-requests.html", {
            "request": request,
            "user": current_user,
            "error": str(e),
            "requests": []
        })



"""
@app.get("/my-requests", response_class=HTMLResponse)
async def my_requests(request: Request, current_user=Depends(get_current_user)):
    try:
        rows = await db.fetch_all(
            """"""SELECT request_id, all_name, matricule, cycle, level, nom_code_ue,
                      note_exam, note_cc, note_tp, note_tpe, autre, comment,
                      just_p, created_at
               FROM requests
               WHERE user_id = %s
               ORDER BY created_at DESC"""""",
            (current_user["user_id"],)
        )

        return templates.TemplateResponse("my-requests.html", {
            "request": request,
            "user": current_user,
            "requests": rows
        })

    except Exception as e:
        return templates.TemplateResponse("my-requests.html", {
            "request": request,
            "user": current_user,
            "error": str(e),
            "requests": []
        })

"""
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_data")
    return response


# --------------------------------------------------------
# Debug - AMÉLIORÉ
# --------------------------------------------------------
@app.get("/test-db")
async def test_db():
    """Test complet de la connexion et des opérations de base"""
    try:
        # Test de connexion
        connection_test = await db.test_connection()
        
        # Test des tables
        users_count = await db.fetch_one("SELECT COUNT(*) AS count FROM users")
        requests_count = await db.fetch_one("SELECT COUNT(*) AS count FROM requests")
        
        # Test d'écriture
        test_insert = await db.execute_query("SELECT 1 as test")
        
        return {
            "status": "success",
            "connection": connection_test,
            "tables": {
                "users": users_count["count"],
                "requests": requests_count["count"]
            },
            "write_test": "ok" if test_insert is not None else "failed"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
















@app.get("/debug-requests")
async def debug_requests():
    """Route temporaire pour debug"""
    try:
        all_requests = await db.fetch_all("""
            SELECT r.request_id, r.user_id, r.all_name, u.name, u.last_name 
            FROM requests r 
            LEFT JOIN users u ON r.user_id = u.user_id
        """)
        return {"status": "success", "all_requests": all_requests}
    except Exception as e:
        return {"status": "error", "message": str(e)}




@app.get("/db-status")
async def db_status():
    """Statut simplifié de la base de données"""
    try:
        users = await db.fetch_one("SELECT COUNT(*) AS count FROM users")
        requests = await db.fetch_one("SELECT COUNT(*) AS count FROM requests")
        is_connected = await db.is_connected()

        return {
            "status": "success",
            "connected": is_connected,
            "users": users["count"],
            "requests": requests["count"]
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "message": str(e)
        }


@app.get("/health")
async def health_check():
    """Endpoint de santé pour Render"""
    try:
        is_connected = await db.is_connected()
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "database": "connected" if is_connected else "disconnected",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


# --------------------------------------------------------
# Run (dev local)
# --------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)