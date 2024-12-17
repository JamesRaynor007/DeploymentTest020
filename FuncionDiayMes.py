from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import os

# Define the paths for the CSV files
file_path_monthly = os.path.join(os.path.dirname(__file__), 'PeliculasPorMesListo.csv')
file_path_daily = os.path.join(os.path.dirname(__file__), 'PeliculasPorDiaListo.csv')

# Create a dictionary to map Spanish months to English months
meses_map = {
    'enero': 'January',
    'febrero': 'February',
    'marzo': 'March',
    'abril': 'April',
    'mayo': 'May',
    'junio': 'June',
    'julio': 'July',
    'agosto': 'August',
    'septiembre': 'September',
    'octubre': 'October',
    'noviembre': 'November',
    'diciembre': 'December'
}

# Create a dictionary to map Spanish days to English days
dias_map = {
    'lunes': 'Monday',
    'martes': 'Tuesday',
    'miercoles': 'Wednesday',
    'jueves': 'Thursday',
    'viernes': 'Friday',
    'sabado': 'Saturday',
    'domingo': 'Sunday',
}

app = FastAPI()

class MessageResponse(BaseModel):
    mensaje: str  # Mensaje personalizado

# Load datasets
try:
    df_monthly = pd.read_csv(file_path_monthly)
    df_daily = pd.read_csv(file_path_daily)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al cargar los archivos: {str(e)}")

# Ensure required columns are present
for df, required_columns in [(df_monthly, ['title', 'month']), (df_daily, ['title', 'day_of_week'])]:
    if not all(column in df.columns for column in required_columns):
        raise HTTPException(status_code=500, detail="El DataFrame no contiene las columnas esperadas.")

# Convert columns to lowercase
df_monthly.columns = df_monthly.columns.str.lower()
df_daily.columns = df_daily.columns.str.lower()

@app.get("/", response_model=dict)
def read_root(request: Request):
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "Mensaje": "Bienvenido a la API de películas.",
        "Instrucciones Mes y Dia": (
            "Usa los endpoints:",
            "/peliculas/mes/?mes=nombre_del_mes",
            "/peliculas/dia/?dia=nombre_del_dia para obtener datos."
        ),
        "Links Ejemplo": [
            {"Para Mes": list(meses_map.keys())[0], "url": f"{base_url}/peliculas/mes/?mes={list(meses_map.keys())[0]}"},
            {"Para Dia": list(dias_map.keys())[0], "url": f"{base_url}/peliculas/dia/?dia={list(dias_map.keys())[0]}"}
        ]
    }

@app.get("/peliculas/mes/", response_model=MessageResponse)
def get_peliculas_mes(mes: str):
    mes = mes.lower()
    if mes not in meses_map:
        raise HTTPException(status_code=400, detail="Mes no válido. Por favor ingrese un mes en español.")

    mes_en_ingles = meses_map[mes]
    resultado = df_monthly[df_monthly['month'] == mes_en_ingles]
    cantidad = resultado['title'].count() if not resultado.empty else 0

    return MessageResponse(
        mensaje=f"Cantidad de películas que fueron estrenadas en el mes de {mes_en_ingles}: {cantidad}"
    )

@app.get("/peliculas/dia/", response_model=MessageResponse)
def get_peliculas_dia(dia: str):
    dia = dia.lower()
    if dia not in dias_map:
        raise HTTPException(status_code=400, detail="Día no válido. Por favor ingrese un día en español.")

    dia_en_ingles = dias_map[dia]
    cantidad = df_daily[df_daily['day_of_week'] == dia_en_ingles].shape[0]

    return MessageResponse(
        mensaje=f"Cantidad de películas que fueron estrenadas en el día {dia_en_ingles}: {cantidad}"
    )
