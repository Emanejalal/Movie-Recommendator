from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Charger les données
users = pd.read_csv('users.csv', sep='\t', encoding='latin-1', usecols=['user_id', 'gender', 'zipcode', 'age_desc', 'occ_desc'])
movies = pd.read_csv('Ratting.csv', usecols=['movie_id','title','genres','rating'])


# Préparer la matrice TF-IDF
movies['genres'] = movies['genres'].str.split('|')
movies['genres'] = movies['genres'].fillna("").astype('str')

# Correction du paramètre min_df pour TfidfVectorizer
tf = TfidfVectorizer(analyzer='word', token_pattern=r"(?u)\b\w[\w-]*\w\b", ngram_range=(1, 1), min_df=1, stop_words='english')
tfidf_matrix = tf.fit_transform(movies['genres'])

# Calculer la similitude cosinus
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim_df = pd.DataFrame(cosine_sim, index=movies['title'], columns=movies['title'])

# Fonction de recommandation de genre
def genre_recommendations(title, M, items, k=10):
    if title not in M.index:
        return "Film non trouvé."
    ix = M.loc[:, title].to_numpy().argpartition(range(-1, -k, -1))
    closest = M.columns[ix[-1:-(k+2):-1]]
    closest = closest.drop(title, errors='ignore')
    return pd.DataFrame(closest).merge(items).head(k)

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def get_movie_image_url(movie_name):
    base_url = "https://www.imdb.com"
    
    # Search for the movie
    search_url = f"{base_url}/find?q={movie_name}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Modify this part based on the current HTML structure
        result = soup.find("div", class_="result_item")  # Change class or element as needed
        
        if result:
            movie_url = result.find('a')['href']
            movie_page_url = f"{base_url}{movie_url}"
            
            # Access the movie page
            movie_response = requests.get(movie_page_url)
            
            if movie_response.status_code == 200:
                movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
                
                # Modify this part based on the current HTML structure
                image_tag = movie_soup.find("div", class_="ipc-media--poster-27x40")  # Change class or element as needed
                
                if image_tag:
                    image_url = image_tag.find('img')['src']
                    return 'https://m.media-amazon.com/images/M/MV5BMzBmOGQ0NWItOTZjZC00ZDAxLTgyOTEtODJiYWQ2YWNiYWVjXkEyXkFqcGdeQXVyNTE1NjY5Mg@@._V1_QL75_UX190_CR0,1,190,281_.jpg'
    
    return None





@app.route('/', methods=['GET', 'POST'])
def home():
     top_rated_movies = movies.sort_values(by='rating', ascending=False).head(5)
     print(top_rated_movies)
     return render_template('index.html', top_rated_movies=top_rated_movies)






   

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
       if request.method == 'POST':
            movie_title = request.form['movie_title']
            recommendations = genre_recommendations(movie_title, cosine_sim_df, movies[['title', 'genres']])
            movie_image_url = get_movie_image_url("clueless")
            print(recommendations)

            return render_template('recommendations.html', recommendations=recommendations, movie_title=movie_title, movie_image_url=movie_image_url)
       return render_template('recommendations.html', recommendations=None)



@app.route('/about-us', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)