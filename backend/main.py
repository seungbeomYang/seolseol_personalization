from typing import Optional
from fastapi import FastAPI
from sklearn.metrics.pairwise import cosine_similarity
import requests
import pandas as pd

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ✅ Allow Vue frontend
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)


# 🔥 Sample Artwork Data with Expanded Mapping
artworks_df = pd.DataFrame([
    {'title': 'Artwork A', 'style': '인상주의', 'genre': '풍경화',
        'medium': '회화', 'mood': '따뜻함', 'region': '서양', 'message': '감정 표현'},
    {'title': 'Artwork B', 'style': '팝아트', 'genre': '인물화', 'medium': '사진',
        'mood': '경쾌함', 'region': '동양', 'message': '사회 비판'},
    {'title': 'Artwork C', 'style': '초현실주의', 'genre': '추상화',
        'medium': '미디어아트', 'mood': '신비로움', 'region': '아프리카', 'message': '개념'},
    {'title': 'Artwork D', 'style': '미니멀리즘', 'genre': '정물화',
        'medium': '설치미술', 'mood': '차가움', 'region': '남미', 'message': '실험'},
])

# One-Hot Encoding
df_encoded = pd.get_dummies(artworks_df.drop(columns=['title']))
df_encoded.insert(0, 'title', artworks_df['title'])


def map_hospital_data(interior_tone, department, installation_space, patient_age, patient_gender, weather):
    mapping = {
        "interior_tone": {
            "화이트": "따뜻함",
            "베이지": "따뜻함",
            "브라운": "차가움",
            "블랙": "차가움"
        },
        "department": {
            "피부과": "인물화",
            "소아과": "풍경화",
            "성형외과": "인물화",
            "치과": "정물화",
            "산부인과": "미디어아트"
        },
        "installation_space": {
            "로비": "미디어아트",
            "대기실": "풍경화",
            "병실": "인물화",
            "복도": "설치미술"
        },
        "weather": {
            "Clear": "따뜻함",  # ☀️ Clear skies = warm feeling
            "Partly cloudy": "우울함",
            "Cloudy": "우울함",
            "Overcast": "우울함",
            "Mist": "신비로움",
            "Patchy rain possible": "신비로움",
            "Rain": "신비로움",
            "Light rain": "신비로움",
            "Heavy rain": "우울함",
            "Snow": "차가움",
            "Blizzard": "차가움",
            "Fog": "신비로움",
            "Thunderstorm": "신비로움"
        },
        "region": {
            "피부과": "서양",
            "소아과": "동양",
            "성형외과": "서양",
            "치과": "아프리카",
            "산부인과": "남미"
        },
        "message": {
            "피부과": "감정 표현",
            "소아과": "개념",
            "성형외과": "사회 비판",
            "치과": "실험",
            "산부인과": "개념"
        }
    }

    return {
        "mood": mapping["interior_tone"].get(interior_tone, "중립"),
        "genre": mapping["department"].get(department, "추상화"),
        "medium": mapping["installation_space"].get(installation_space, "미디어아트"),
        "mood_weather": mapping["weather"].get(weather, "중립"),
        "region": mapping["region"].get(department, "서양"),
        "message": mapping["message"].get(department, "감정 표현")
    }


# Weather API Configuration
API_KEY = "0e82a6e070924250b39101720250402"
CITY = "seoul"


def get_weather():

    url = f"http://api.weatherapi.com/v1/current.json?key={
        API_KEY}&q={CITY}&aqi=yes"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            # ✅ Corrected field
            return response.json()['current']['condition']['text']
        except KeyError:
            return "Unknown"
    return "Unknown"


@app.get("/recommend/")
def recommend_artwork(
    interior_tone: str,
    department: Optional[str] = "",
    installation_space: Optional[str] = "",
    patient_age: Optional[str] = "",
    patient_gender: Optional[str] = "",
    mood: Optional[str] = "중립",
    genre: Optional[str] = "추상화",
    medium: Optional[str] = "미디어아트",
    message: Optional[str] = "감정 표현"
):
    weather = get_weather()  # Get real-time weather

    # Map hospital and weather data to artwork features
    mapped_data = map_hospital_data(
        interior_tone, department, installation_space, patient_age, patient_gender, weather)

    input_conditions = {
        f"mood_{mapped_data['mood']}": 1,
        f"genre_{mapped_data['genre']}": 1,
        f"medium_{mapped_data['medium']}": 1,
        f"mood_{mapped_data['mood_weather']}": 1,
        f"style_{mapped_data['genre']}": 1,  # ✅ New Feature
        f"region_{mapped_data['region']}": 1,  # ✅ New Feature
        f"message_{mapped_data['message']}": 1,  # ✅ New Feature
    }

    input_df = pd.DataFrame([input_conditions])

    # ✅ Ensure all missing columns are filled with 0
    missing_cols = set(df_encoded.columns) - set(input_df.columns)
    for col in missing_cols:
        input_df[col] = 0
    input_df = input_df[df_encoded.columns[1:]]  # Ensure column order matches

    # ✅ Create a copy of df_encoded before modifying
    df_temp = df_encoded.copy()

    # ✅ Compute Cosine Similarity
    similarity_scores = cosine_similarity(input_df, df_temp.iloc[:, 1:])
    # ✅ Avoid modifying original df_encoded
    df_temp['similarity'] = similarity_scores[0]

    # ✅ Select Top 3 Artworks
    top_similar_artworks = df_temp.nlargest(3, 'similarity')

    return {"recommendations": top_similar_artworks[['title', 'similarity']].to_dict(orient="records")}
