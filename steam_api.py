import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

SGDB_API_KEY = config["api_key"]
BASE_URL = "https://www.steamgriddb.com/api/v2"

def get_sgdb_id(game_name):
    url = f"{BASE_URL}/search/autocomplete/{game_name}"
    headers = {"Authorization": f"Bearer {SGDB_API_KEY}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if data.get('success') and data['data']:
            return data['data'][0]['id']
    except Exception as e:
        print(f"Search error: {e}")
    return None

def get_game_assets(game_id):
    headers = {"Authorization": f"Bearer {SGDB_API_KEY}"}
    assets = {"cover": None, "hero": None}
    try:
        grid_url = f"{BASE_URL}/grids/game/{game_id}?dimensions=600x900"
        g_res = requests.get(grid_url, headers=headers).json()
        if g_res.get('success') and g_res['data']:
            assets['cover'] = g_res['data'][0]['url']

        hero_url = f"{BASE_URL}/heroes/game/{game_id}"
        h_res = requests.get(hero_url, headers=headers).json()
        if h_res.get('success') and h_res['data']:
            assets['hero'] = h_res['data'][0]['url']
    except Exception as e:
        print(f"Asset fetch error: {e}")
    return assets

def enrich_game_data(game_list):
    for game in game_list:
        sgdb_id = get_sgdb_id(game['title'])
        if sgdb_id:
            assets = get_game_assets(sgdb_id)
            game['cover'] = assets['cover']
            game['hero'] = assets['hero']
    return game_list
