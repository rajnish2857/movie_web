import streamlit as st
import pickle,gzip
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Safe requests session with retry ---
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=af165e8e2feaea9c07ff82141ef2bd46&language=en-US"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "poster_path" in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        print("Error fetching poster:", e)
        return "https://via.placeholder.com/500x750?text=Error"


# --- Load similarity and movies ---
with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)
movie_list = pickle.load(open('movies.pkl', 'rb'))
movie = pd.DataFrame(movie_list)
movie_titles = movie['title'].values


# --- Recommendation logic ---
def recommend(movie_name):
    movie_index = movie[movie['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    movie_lst = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_lst:
        movie_id = movie.iloc[i[0]].movie_id
        recommended_movies.append(movie.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters


# --- Streamlit UI ---
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Choose a movie you like:",
    movie_titles
)

if st.button("Recommend", type="primary"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])