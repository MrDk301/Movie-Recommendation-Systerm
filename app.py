import streamlit as st
import pickle
import pandas as pd
import requests

# TMDB API Key
TMDB_API_KEY = '376527df971bb65acc40692ba43ac544'

def fetch_movie_details(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params={
                'api_key': TMDB_API_KEY,
                'append_to_response': 'videos',
                'language': 'en-US'
            }
        )
        response.raise_for_status()
        
        data = response.json()
        details = {
            "title": data.get("title", "N/A"),
            "overview": data.get("overview", "No description available."),
            "release_date": data.get("release_date", "N/A"),
            "rating": data.get("vote_average", "N/A"),
            "runtime": data.get("runtime", "N/A"),
            "genres": data.get("genres", ["N/A"]),

            "trailer": None,
        }

        # Extract trailer
        videos = data.get("videos", {}).get("results", [])
        for video in videos:
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                details["trailer"] = f"https://www.youtube.com/watch?v={video['key']}"
                break
        return details
    except requests.exceptions.RequestException as e:
        return {"error": f"Request Exception: {e}"}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}"}


def fetch_poster(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US')
        data = response.json()
        if 'poster_path' in data:
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except Exception:
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []
    movies_id = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_details.append(fetch_movie_details(movie_id))
        movies_id.append(movie_id)

    return recommended_movies, recommended_movies_posters, recommended_movies_details, movies_id


# Load pre-saved data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI components
st.title('Movies Recommendation System')
st.markdown('''*:blue[Created by]* **:red[Deep Kansagara]**''')

# Movie selection dropdown
selected_movie_name = st.selectbox(
    'How would you like to get recommended movies?',
    movies['title'].values,
    index=None,
    help="Select a movie to get recommendations based on it",
)

# Session state to store selected movie details
if 'movie_details' not in st.session_state:
    st.session_state.movie_details = {}

if 'recommended_movies' not in st.session_state:
    st.session_state.recommended_movies = []
    st.session_state.recommended_movies_posters = []
    st.session_state.recommended_movies_details = []
    st.session_state.movies_id = []

if st.button('Recommend'):
    if selected_movie_name:
        with st.spinner('Fetching recommendations...'):
            names, posters, details, movies_id = recommend(selected_movie_name)
            st.session_state.recommended_movies = names[:5]
            st.session_state.recommended_movies_posters = posters[:5]
            st.session_state.recommended_movies_details = details[:5]
            st.session_state.movies_id = movies_id[:5]
    else:
        st.error('Please select a movie')

# Display recommended movies
if st.session_state.recommended_movies:
    cols = st.columns(len(st.session_state.recommended_movies))
    for i in range(len(st.session_state.recommended_movies)):
        with cols[i]:
            st.text(st.session_state.recommended_movies[i])
            st.image(st.session_state.recommended_movies_posters[i])

            # Store movie details in session state on button click
            def show_movie_details(movie_details=st.session_state.recommended_movies_details[i]):
                st.session_state.movie_details = movie_details

            st.button("Details", key=st.session_state.recommended_movies[i], on_click=show_movie_details)

# Display movie details if available
if st.session_state.movie_details:
    details = st.session_state.movie_details
    st.write(f"**Title**: {details['title']}")
    st.write(f"**Release Date**: {details['release_date']}")
    st.write(f"**Rating**: {details['rating']}")
    st.write(f"**Overview**: {details['overview']}")
    genres = ", ".join([genre['name'] for genre in details['genres']])  # Iterate over genres
    st.write(f"**Genres**: {genres}")
    st.write(f"**runtime**: {details['runtime']}")
    if details['trailer']:
        st.write(f"[Watch Trailer]({details['trailer']})")
