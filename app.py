# Import necessary libraries
import streamlit as st  # Streamlit for building the web application
import pickle  # For loading pre-saved data (such as movie data and similarity matrix)
import pandas as pd  # For data manipulation and DataFrame operations
import requests  # For making HTTP requests to the TMDB API

# TMDB API Key for accessing movie details
TMDB_API_KEY = '376527df971bb65acc40692ba43ac544'

# Function to fetch detailed information about a movie
def fetch_movie_details(movie_id):
    try:
        # Making a request to TMDB API to get detailed movie information
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params={
                'api_key': TMDB_API_KEY,
                'append_to_response': 'videos',  # Request video (trailer) details as well
                'language': 'en-US'
            }
        )
        # Raise an error if the request fails
        response.raise_for_status()

        # Extract the movie details from the API response
        data = response.json()
        details = {
            "title": data.get("title", "N/A"),  # Movie title
            "overview": data.get("overview", "No description available."),  # Movie description
            "release_date": data.get("release_date", "N/A"),  # Release date
            "rating": data.get("vote_average", "N/A"),  # Movie rating
            "runtime": data.get("runtime", "N/A"),  # Movie runtime in minutes
            "genres": data.get("genres", ["N/A"]),  # Movie genres
            "trailer": None,  # Initialize trailer as None
        }

        # Extract the trailer URL from the response (if available)
        videos = data.get("videos", {}).get("results", [])
        for video in videos:
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                details["trailer"] = f"https://www.youtube.com/watch?v={video['key']}"
                break

        return details  # Return the movie details
    except requests.exceptions.RequestException as e:
        return {"error": f"Request Exception: {e}"}  # Handle request exceptions
    except Exception as e:
        return {"error": f"Unexpected Error: {e}"}  # Handle other unexpected errors

# Function to fetch the poster image for a movie
def fetch_poster(movie_id):
    try:
        # Making a request to TMDB API to get the movie poster
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US')
        data = response.json()
        
        # Check if poster path exists and return the appropriate poster URL
        if 'poster_path' in data:
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"  # Return a placeholder if no poster is found
    except Exception:
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"  # Return placeholder on error

# Function to recommend movies based on similarity
def recommend(movie):
    # Find the index of the selected movie from the movie list
    movie_index = movies[movies['title'] == movie].index[0]
    
    # Get the similarity scores for the selected movie
    distances = similarity[movie_index]
    
    # Sort movies by similarity score (excluding the movie itself) and get top 5 recommendations
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []
    movies_id = []

    # Loop through the sorted list and get details for the top 5 recommended movies
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))  # Fetch the movie poster
        recommended_movies_details.append(fetch_movie_details(movie_id))  # Fetch movie details
        movies_id.append(movie_id)  # Store movie ID

    # Return the recommended movie names, posters, details, and movie IDs
    return recommended_movies, recommended_movies_posters, recommended_movies_details, movies_id


# Load the pre-saved movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))  # Load movie data (title, ID, etc.)
movies = pd.DataFrame(movies_dict)  # Convert movie data into a DataFrame for easier manipulation
similarity = pickle.load(open('similarity.pkl', 'rb'))  # Load similarity matrix for movie recommendations

# Streamlit UI components
st.title('Movies Recommendation System')  # Set the title of the web app
st.markdown('''*:blue[Created by]* **:red[Deep Kansagara]**''')  # Display the creator's name

# Movie selection dropdown
selected_movie_name = st.selectbox(
    'How would you like to get recommended movies?',  # Label of the dropdown
    movies['title'].values,  # List of available movie titles
    index=None,  # Default selected index
    help="Select a movie to get recommendations based on it",  # Tooltip text
)

# Initialize session state to store data across user interactions
if 'movie_details' not in st.session_state:
    st.session_state.movie_details = {}  # Store movie details in session state

if 'recommended_movies' not in st.session_state:
    # Store the list of recommended movies and their details in session state
    st.session_state.recommended_movies = []
    st.session_state.recommended_movies_posters = []
    st.session_state.recommended_movies_details = []
    st.session_state.movies_id = []

# When the 'Recommend' button is clicked
if st.button('Recommend'):
    if selected_movie_name:
        with st.spinner('Fetching recommendations...'):  # Show a loading spinner
            # Call the recommend function and update session state with recommendations
            names, posters, details, movies_id = recommend(selected_movie_name)
            st.session_state.recommended_movies = names[:5]  # Top 5 recommended movies
            st.session_state.recommended_movies_posters = posters[:5]  # Movie posters
            st.session_state.recommended_movies_details = details[:5]  # Movie details
            st.session_state.movies_id = movies_id[:5]  # Movie IDs
    else:
        st.error('Please select a movie')  # Show error if no movie is selected

# Display the recommended movies (with posters)
if st.session_state.recommended_movies:
    cols = st.columns(len(st.session_state.recommended_movies))  # Create columns to display movies
    for i in range(len(st.session_state.recommended_movies)):
        with cols[i]:
            # Display the movie name and poster
            st.text(st.session_state.recommended_movies[i])
            st.image(st.session_state.recommended_movies_posters[i])

            # Function to display movie details when the "Details" button is clicked
            def show_movie_details(movie_details=st.session_state.recommended_movies_details[i]):
                st.session_state.movie_details = movie_details  # Store the selected movie's details in session state

            # Display the "Details" button for each movie
            st.button("Details", key=st.session_state.recommended_movies[i], on_click=show_movie_details)

# If movie details are available, display them
if st.session_state.movie_details:
    details = st.session_state.movie_details
    st.write(f"**Title**: {details['title']}")  # Display movie title
    st.write(f"**Release Date**: {details['release_date']}")  # Display release date
    st.write(f"**Rating**: {details['rating']}")  # Display movie rating
    st.write(f"**Overview**: {details['overview']}")  # Display movie overview
    genres = ", ".join([genre['name'] for genre in details['genres']])  # Format genres as a comma-separated list
    st.write(f"**Genres**: {genres}")  # Display genres
    st.write(f"**runtime**: {details['runtime']}")  # Display runtime
    if details['trailer']:
        st.write(f"[Watch Trailer]({details['trailer']})")  # Display a link to the trailer if available
