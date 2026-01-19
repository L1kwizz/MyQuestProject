import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКА ИИ ---
# Твой ключ я уже вставила сюда, всё четко
genai.configure(api_key="AIzaSyBD94mYsRDhb_E0QW8LBpOenfMQBBKvlLE")

# АВТОМАТИЧЕСКИЙ ПОИСК МОДЕЛИ
model_name = 'gemini-1.5-flash' # запасной вариант
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # Находим самую свежую модель
            model_name = m.name
            break
    print(f"--- УСПЕХ: Используем модель {model_name} ---")
except Exception as e:
    print(f"--- ОШИБКА ПОИСКА МОДЕЛИ: {e} ---")

model = genai.GenerativeModel(model_name)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    lecture = data.get('lecture', '')
    count = data.get('count', 5)
    diff = data.get('difficulty', 'normal')

    prompt = f"""
    Ты — строгий генератор квизов. На основе этого текста лекции: "{lecture}"
    Создай ровно {count} вопросов. Сложность: {diff}.
    Для каждого вопроса придумай 3 варианта ответа, где только ОДИН правильный.
    
    ОТВЕТЬ ТОЛЬКО В ФОРМАТЕ JSON:
    {{
      "questions": [
        {{
          "id": 1,
          "question": "текст вопроса",
          "choices": [
            {{"text": "вариант 1", "is_correct": true}},
            {{"text": "вариант 2", "is_correct": false}},
            {{"text": "вариант 3", "is_correct": false}}
          ]
        }}
      ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Убираем лишние знаки, если ИИ их добавит
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_json)
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return jsonify({"error": "ИИ закапризничал"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)