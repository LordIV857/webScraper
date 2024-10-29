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

    # Extraction des liens et titres des articles contenant le mot "article" dans l'intégralité de la balise <a>
    articles = []
    seen_links = set()  # Ensemble pour garder une trace des liens uniques déjà ajoutés
    for link in soup.find_all('a', href=True):  # Rechercher toutes les balises <a> avec un attribut href
        full_a_content = str(link)  # Obtenir tout le contenu HTML de la balise <a>

        # Vérifie si le mot "article" est présent dans le contenu complet de <a>
        if "article" in full_a_content.lower():
            title = link.get_text(strip=True)  # Extraire le texte (titre) de la balise <a>
            href = link['href']  # Extraire le lien (href) de la balise <a>
            
            # Vérifie si le lien a déjà été ajouté pour éviter les doublons
            if href not in seen_links:
                articles.append({
                    "title": title,
                    "link": href
                })
                seen_links.add(href)  # Ajouter le lien à l'ensemble des liens vus

    # Récupère le type de réponse demandée
    response_type = request.args.get('type', default='all')  # 'all' par défaut

    if response_type == 'titles':
        return jsonify([article['title'] for article in articles])  # Retourne seulement les titres
    elif response_type == 'links':
        return jsonify([article['link'] for article in articles])  # Retourne seulement les liens
    else:
        return jsonify(articles)  # Retourne les articles complets (titres et liens)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
