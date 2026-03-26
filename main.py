import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from dotenv import load_dotenv

from models import PerfilRequest, PerfilResponse, MatchingRequest, MatchingResponse

# Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI(
    title="TalentID API",
    description="API para generar perfiles psicométricos y matching con IA",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración inicial del cliente de Gemini
# El SDK toma automáticamente la variable de entorno GEMINI_API_KEY
try:
    client = genai.Client()
except Exception as e:
    print(f"Advertencia: No se pudo inicializar el cliente de Gemini. Verifica tu GEMINI_API_KEY. Error: {e}")
    client = None

@app.post("/api/perfil", response_model=PerfilResponse)
async def generar_perfil(request: PerfilRequest):
    if not client:
        raise HTTPException(status_code=500, detail="El cliente de Gemini no está configurado.")
        
    prompt = f"""
    Actúa como un psicólogo experto en evaluación de talento.
    Analiza al siguiente candidato para generar un Perfil de Talento psicométrico.
    
    Nombre: {request.nombre}
    Fecha de nacimiento: {request.fecha_nacimiento}
    Respuestas del cuestionario (Eneagrama/Psicométrico): {request.respuestas_eneagrama}

    Genera un perfil estructurado con:
    1. tipo_personalidad: El tipo de personalidad (ej. Eneatipo 3, INTJ, etc.)
    2. competencias: Exactamente 5 competencias clave con un valor de 0 a 100.
    3. estilo_liderazgo: Breve descripción de su estilo de liderazgo.
    4. compatibilidad: Qué tipo de cultura o líder hace mejor match con este perfil.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PerfilResponse,
                temperature=0.2, # Baja temperatura para respuestas más consistentes
            ),
        )
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar perfil: {str(e)}")

@app.post("/api/matching", response_model=MatchingResponse)
async def generar_matching(request: MatchingRequest):
    if not client:
        raise HTTPException(status_code=500, detail="El cliente de Gemini no está configurado.")
        
    prompt = f"""
    Actúa como un experto en recursos humanos y dinámica de equipos.
    Analiza los siguientes perfiles para determinar su compatibilidad laboral.
    
    Datos del Líder: {request.datos_lider}
    Datos del Candidato: {request.datos_candidato}

    Genera un Informe de Compatibilidad estructurado con:
    1. porcentaje_match: Un valor de 0 a 100 indicando la compatibilidad general.
    2. puntos_fuertes: Una lista de 3 a 5 puntos fuertes de esta combinación de trabajo.
    3. zonas_conflicto: Una lista de 2 a 3 posibles zonas de fricción o conflicto probable.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MatchingResponse,
                temperature=0.3,
            ),
        )
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar matching: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
