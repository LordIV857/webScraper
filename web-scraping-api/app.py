from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin  # Importation de urljoin pour résoudre les URL relatives

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

    # Extraction des liens, titres et images des articles contenant les mots-clés spécifiés
    articles = []
    seen_links = set()  # Ensemble pour garder une trace des liens uniques déjà ajoutés

    # Recherche des éléments <a> et <img>
    for link in soup.find_all('a', href=True):  # Rechercher toutes les balises <a> avec un attribut href
        title = link.get_text(strip=True)  # Extraire le texte (titre) de la balise <a>
        href = link['href']  # Extraire le lien (href) de la balise <a>
        
        # Utiliser urljoin pour convertir le lien relatif en absolu
        href = urljoin(url, href)

        # Vérifie si le titre ou le lien contient un des mots-clés
        if any(keyword in title.lower() or keyword in href.lower() for keyword in keywords):
            # Chercher l'image associée à ce lien dans le même conteneur (comme <div>)
            parent = link.find_parent()  # Trouver le parent de <a> (généralement une <div> ou <section>)
            image = None
            
            if parent:
                # Chercher une image dans le parent, vérifier les variantes de src
                img_tag = parent.find('img')
                if img_tag:
                    # Vérifier plusieurs variantes de l'URL de l'image (src, data-src, srcset)
                    image_url = img_tag.get('data-src') or img_tag.get('src') or img_tag.get('srcset')
                    
                    if image_url:
                        # Si l'image est dans srcset, on prend la première URL valide
                        if 'srcset' in img_tag.attrs:
                            # Récupérer toutes les URLs du srcset et les diviser par la virgule
                            srcset_urls = img_tag['srcset'].split(',')
                            # Extraire la première URL dans srcset
                            image_url = srcset_urls[0].split(' ')[0].strip()
                        
                        # Utiliser urljoin pour convertir l'URL de l'image relative en absolue
                        image = urljoin(url, image_url)

            # Vérifie si le lien est unique et si l'image est valide
            if href not in seen_links and image:
                articles.append({
                    "title": title,
                    "link": href,
                    "image": image  # Inclure l'image uniquement si elle est valide
                })
                seen_links.add(href)  # Ajouter le lien à l'ensemble des liens vus

    return jsonify(articles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
