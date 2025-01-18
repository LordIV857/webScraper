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

# Route pour faire du web scraping avec un filtre de mots-clés
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')  # Récupère l'URL depuis les paramètres de la requête
    keywords = request.args.get('type', '').lower().split(',')  # Récupère les mots-clés et les transforme en liste
    html_content = fetch_html(url)

    # Analyse le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraction des liens et titres des articles contenant les mots-clés spécifiés dans <a>
    articles = []
    seen_links = set()  # Ensemble pour garder une trace des liens uniques déjà ajoutés
    for link in soup.find_all('a', href=True):  # Rechercher toutes les balises <a> avec un attribut href
        title = link.get_text(strip=True)  # Extraire le texte (titre) de la balise <a>
        href = link['href']  # Extraire le lien (href) de la balise <a>
        
        # Vérifie si le titre contient un des mots-clés
        if any(keyword in title.lower() for keyword in keywords):
            # Vérifie si le lien est unique pour éviter les doublons
            if href not in seen_links:
                articles.append({
                    "title": title,
                    "link": href
                })
                seen_links.add(href)  # Ajouter le lien à l'ensemble des liens vus

    return jsonify(articles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
