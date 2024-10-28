from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
CORS(app)

# En-têtes pour imiter un navigateur réel
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Fonction pour récupérer le contenu HTML d'un site web
def fetch_html(url):
    response = requests.get(url, headers=headers)
    return response.text

# Route pour faire du web scraping
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')  # Récupère l'URL depuis les paramètres de la requête
    html_content = fetch_html(url)

    # Analyse le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraction des titres h1, h2, h3
    headers = soup.find_all(['h1', 'h2', 'h3'])
    extracted_headers = []
    for header in headers:
        extracted_headers.append({
            "tag": header.name,
            "text": header.get_text(strip=True)
        })

    return jsonify(
        #"headers": extracted_headers, 
        html_content
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
