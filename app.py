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
st.markdown('''*:blue[Created by]* **:red[Deep Kansagara]**''')

# Movie selection dropdown
selected_movie_name = st.selectbox(
    'How would you like to get recommended movies?',
    movies['title'].values,
    index=None,
    help="Select a movie to get recommendations based on it",
)

# Fetch movie details and trailer using TMDB API
def fetch_movie_details_and_trailer(movie_id):
    try:
        # Fetch movie details
        details_response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=376527df971bb65acc40692ba43ac544&language=en-US')
        details_data = details_response.json()

        # Fetch movie trailer
        trailer_response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=376527df971bb65acc40692ba43ac544&language=en-US')
        trailer_data = trailer_response.json()

        # Extract trailer key from response
        trailer_key = None
        for video in trailer_data.get('results', []):
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                trailer_key = video['key']
                break

        # Construct YouTube trailer URL
        trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None

        return details_data, trailer_url
    except Exception as e:
        return None, None

# Update the Streamlit app to show movie details and trailers
if st.button('Recommend'):
    if selected_movie_name:
        with st.spinner('Fetching recommendations...'):
            names, posters = recommend(selected_movie_name)

            # Ensure only 5 recommendations are displayed
            names, posters = names[:5], posters[:5]
            
            cols = st.columns(len(names))
            for i in range(len(names)):
                with cols[i]:
                    st.text(names[i])
                    st.image(posters[i])

                    # Add a button to view details and trailer
                    if st.button(f"Details & Trailer: {names[i]}"):
                        # Fetch and display movie details and trailer
                        movie_id = movies[movies['title'] == names[i]].iloc[0].movie_id
                        details, trailer_url = fetch_movie_details_and_trailer(movie_id)

                        if details:
                            st.subheader(details['title'])
                            st.write(f"**Overview:** {details['overview']}")
                            st.write(f"**Release Date:** {details['release_date']}")
                            st.write(f"**Genres:** {', '.join([genre['name'] for genre in details['genres']])}")

                            if trailer_url:
                                st.video(trailer_url)
                            else:
                                st.write("Trailer not available.")
                        else:
                            st.write("Failed to fetch movie details.")
    else:
        st.write("Please select a movie.")
