import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)
CORS(app) # Habilita o CORS para toda a aplicação

# --- Configuração da API Spoonacular ---
API_KEY = os.getenv('SPOONACULAR_API_KEY')
API_URL = "https://api.spoonacular.com/recipes/complexSearch"
RANDOM_API_URL = "https://api.spoonacular.com/recipes/random"

@app.route('/api/search')
def search_recipes():
    """
    Esta rota recebe um termo de busca do front-end,
    consulta a API da Spoonacular e retorna os resultados.
    """
    # Pega o termo de busca da URL (ex: /api/search?query=feijoada)
    query = request.args.get('query')

    # --- LÓGICA DE CARGA INICIAL (ALEATÓRIA) ---
    if not query:
        print("Nenhuma query fornecida. Buscando 12 receitas aleatórias...")
        try:
            random_params = {
                'apiKey': API_KEY,
                'number': 12
                # Removendo a tag 'brazilian' para buscar receitas aleatórias de todo o banco de dados.
            }
            response = requests.get(RANDOM_API_URL, params=random_params)
            response.raise_for_status()
            data = response.json()
            # O endpoint random retorna a chave 'recipes'
            results = data.get('recipes', [])

            if results:
                return jsonify(results)
            else:
                # Se a API não retornar nada, ativa o Plano B
                raise ValueError("A busca aleatória não retornou resultados.")
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Erro na busca aleatória, ativando fallback: {e}")
            return load_local_fallback()

    # --- LÓGICA DE BUSCA DO USUÁRIO ---
    print(f"Buscando por termo do usuário: '{query}'")
    params = {
        'apiKey': API_KEY,
        'query': query,
        'addRecipeInformation': True,
        'number': 12 # Aumentando para 12 também na busca normal
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status() # Lança erro para status 4xx/5xx
        data = response.json()
        results = data.get('results', [])

        return jsonify(results) # Retorna os resultados da API
    except requests.exceptions.RequestException as e:
        # Se a API da Spoonacular retornar um erro (ex: 401, 402, 500),
        # capturamos a mensagem de erro dela para retornar ao nosso front-end.
        error_message = f"Erro ao contatar a API externa: {e}"
        status_code = 500
        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_message = e.response.json().get('message', str(e))
            except ValueError: # Em caso de a resposta não ser JSON
                error_message = str(e)
        return jsonify({"error": error_message}), status_code

def load_local_fallback():
    """
    Função de fallback que carrega receitas do arquivo JSON local.
    """
    print("Usando fallback: carregando receitas do 'recipe.json' local.")
    try:
        with open('recipe.json', 'r', encoding='utf-8') as f:
            local_recipes = json.load(f)
        # Formata os dados locais para se parecerem com os da API
        formatted_recipes = [
            {
                'title': recipe.get('name'),
                'image': recipe.get('image_url'),
                'summary': recipe.get('description'),
                'readyInMinutes': 'N/A',
                'sourceUrl': recipe.get('recipe_url')
            } for recipe in local_recipes
        ]
        return jsonify(formatted_recipes)
    except Exception as local_error:
        print(f"Erro ao carregar o JSON local como fallback: {local_error}")
        return jsonify([])

if __name__ == '__main__':
    # Roda a aplicação em modo de depuração
    app.run(debug=True, port=5000)