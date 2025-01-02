import streamlit as st
import pickle
import pandas as pd
import requests

# Fetch the movie poster using TMDB API
def fetch_poster(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=376527df971bb65acc40692ba43ac544&language=en-US')
        data = response.json()
        # If poster path exists in the response, return the image URL
        if 'poster_path' in data:
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            # Return a placeholder image if no poster is available
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except Exception:
        # In case of any exception, return a placeholder image
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"

# Get recommended movies based on the selected movie
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    # Get the top 5 most similar movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    # Fetch recommended movies and their posters
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_movies_posters

# Load pre-saved data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI components
st.title('Movies Recommendation System')

# Movie selection dropdown
selected_movie_name = st.selectbox(
    'How would you like to get recommended movies?',
    movies['title'].values,
    index=None,
    help="Select a movie to get recommendations based on it",
)

# Recommend button functionality
if st.button('Recommend'):
    if selected_movie_name:
        with st.spinner('Fetching recommendations...'):
            names, posters = recommend(selected_movie_name)
            
            # Ensure only 5 recommendations are displayed
            names, posters = names[:5], posters[:5]

            # Display movie recommendations in columns
            cols = st.columns(len(names))
            for i in range(len(names)):
                with cols[i]:
                    st.text(names[i])
                    st.image(posters[i])
    else:
        st.write("Please select a movie.")
