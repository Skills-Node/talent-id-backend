# TalentID Backend

Python FastAPI backend for the TalentID platform. Provides AI-powered psychometric profiling and candidate matching services using Google Gemini API.

## Features

- **Psychometric Profile Generation**: AI-powered personality analysis based on Enneagram responses
- **Leader-Candidate Matching**: Compatibility analysis between hiring managers and candidates
- **Bilingual Support**: Full Spanish API responses
- **RESTful API**: Fast and efficient FastAPI implementation
- **CORS Enabled**: Seamless integration with Next.js frontend
- **Type Safety**: Pydantic models for request/response validation

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI**: Google Gemini API
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Environment**: python-dotenv

## Getting Started

### Prerequisites

- Python 3.10+
- pip or poetry

### Installation

```bash
# Clone the repository
git clone https://github.com/N4ch0VS/talent-id-backend.git
cd talent-id-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

### Run Development Server

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

### POST /api/perfil

Generate a psychometric talent profile in Spanish.

**Request Body:**
```json
{
  "nombre": "Juan Pérez",
  "fecha_nacimiento": "1990-05-15",
  "respuestas_eneagrama": "P1:4,P2:3,P3:5..."
}
```

**Response:**
```json
{
  "tipo_personalidad": "Eneatipo 3 - El Optimizador",
  "competencias": [
    {"nombre": "Liderazgo", "valor": 85},
    {"nombre": "Comunicación", "valor": 90},
    {"nombre": "Resolución de Problemas", "valor": 80},
    {"nombre": "Adaptabilidad", "valor": 75},
    {"nombre": "Pensamiento Estratégico", "valor": 88}
  ],
  "estilo_liderazgo": "Orientado a resultados con enfoque en logros",
  "compatibilidad": "Ambiente de alto rendimiento con metas claras"
}
```

### POST /api/matching

Generate compatibility analysis between leader and candidate.

**Request Body:**
```json
{
  "datos_lider": "Líder tipo 3, orientado a resultados, estilo directo",
  "datos_candidato": "Candidato tipo 5, analítico, independiente"
}
```

**Response:**
```json
{
  "porcentaje_match": 85,
  "puntos_fuertes": [
    "Complementariedad en estilos de comunicación",
    "Orientación compartida hacia resultados",
    "Valores alineados"
  ],
  "zonas_conflicto": [
    "Ritmo de trabajo diferente",
    "Enfoques distintos ante conflictos"
  ]
}
```

## Project Structure

```
talent-id-backend/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for request/response
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when added)
pytest
```

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and run:
```bash
docker build -t talent-id-backend .
docker run -p 8000:8000 --env-file .env talent-id-backend
```

## Environment Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

Get your API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

Error responses include detail message:
```json
{
  "detail": "Error message here"
}
```

## Related Projects

- [talent-id-frontend](https://github.com/N4ch0VS/talent-id-frontend) - Next.js React frontend
- [talent-id-bnb-chain](https://github.com/N4ch0VS/talent-id-bnb-chain) - Solidity smart contracts

## License

MIT