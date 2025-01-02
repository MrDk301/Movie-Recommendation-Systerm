import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=376527df971bb65acc40692ba43ac544&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies,recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

st.title('Movies Recommendation System')

selected_movie_name = st.selectbox(
    'How would you like to get recommended movies?',
    movies['title'].values,
    index=None,
    help="Select a movie to get recommendations based on it",
)

if st.button('Recommend'):
    if selected_movie_name:
        names = recommend(selected_movie_name)
        # Ensure names and posters are returned as a list with at least 5 items
        names,posters = names[:5]
        posters = posters[:5]
        
        # Displaying movie recommendations in 5 columns
        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
                
    else:
        st.write("Please select a movie")