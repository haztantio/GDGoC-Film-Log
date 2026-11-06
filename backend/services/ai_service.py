import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_movie_recommendation(prompt: str, movie_catalog: str) -> dict:
    system_instruction = f"""
    Bertindaklah sebagai ahli rekomendasi film yang profesional.
    Berikut adalah SATU-SATUNYA list film yang tersedia:
    {movie_catalog}

    User meminta rekomendasi film seperti ini: "{prompt}"

    Pahami permintaan user, tugasmu adalah memilih SATU film dari daftar di atas.
    Balas HANYA dengan format JSON murni:
    {{
        "movie_id": 1,
        "reasoning": "Film ini cocok buat kamu karena..."
    }}
    """

    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    response = model.generate_content(system_instruction)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        print(f"\n--- DEBUG: AI TIDAK MERESPONS JSON ---\n{clean_text}\n---")
        return {"movie_id": None, "reasoning": f"Sistem memilihkan default. (Pesan asli: {clean_text})"}