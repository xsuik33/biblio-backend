from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel

app = FastAPI()

# Permitir que tu GitHub Pages se conecte a este Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA CON TUS LLAVES
url = "https://tu-proyecto.supabase.co"
key = "tu-anon-key"
supabase: Client = create_client(url, key)

class Registro(BaseModel):
    curp: str
    nombre: str
    user: str
    password: str
    tipo: str
    id_escolar: str

@app.get("/libros")
async def get_libros():
    # Traer libros para el catálogo de ESCOM
    res = supabase.table("libros").select("*").execute()
    return res.data

@app.post("/registrar")
async def registrar(datos: Registro):
    try:
        # 1. Auth de Supabase
        user = supabase.auth.sign_up({"email": f"{datos.user}@escom.ipn.mx", "password": datos.password})
        uid = user.user.id
        
        # 2. Insertar en Supertipo (profiles)
        supabase.table("profiles").insert({
            "id": uid, "curp": datos.curp, "nombre_completo": datos.nombre, "username": datos.user, "tipo": datos.tipo
        }).execute()
        
        # 3. Insertar en Subtipo
        tabla = "alumnos" if datos.tipo == "alumno" else "profesores"
        col = "boleta" if datos.tipo == "alumno" else "no_empleado"
        supabase.table(tabla).insert({"id": uid, col: datos.id_escolar}).execute()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
