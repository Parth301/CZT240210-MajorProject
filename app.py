from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset (replace with actual paths)
movies_file = r'C:\Users\jaypa\OneDrive\Desktop\Movie_Recommend\movie.csv'
ratings_file = r'C:\Users\jaypa\OneDrive\Desktop\Movie_Recommend\rating.csv'


movies_df = pd.read_csv(movies_file)
ratings_df = pd.read_csv(ratings_file)

# Clean the data
movies_df.dropna(subset=['title', 'genres'], inplace=True)
ratings_df.dropna(subset=['userId', 'movieId', 'rating'], inplace=True)

# Merge datasets
movie_ratings = pd.merge(ratings_df, movies_df, on='movieId')

# Function to recommend movies based on genres and ratings
def recommend_movies(genres):
    # Filter movies by selected genres
    filtered_movies = movies_df[movies_df['genres'].str.contains('|'.join(genres), case=False, na=False)]
    
    # Merge the filtered movies with ratings data
    movie_ratings_filtered = pd.merge(ratings_df[ratings_df['movieId'].isin(filtered_movies['movieId'])], 
                                      filtered_movies, on='movieId')

    # Group by movieId and get the average rating
    avg_ratings = movie_ratings_filtered.groupby('movieId')['rating'].mean()

    # Sort movies by rating and return top 10
    top_movies = avg_ratings.sort_values(ascending=False).head(10)
    top_movie_titles = movies_df[movies_df['movieId'].isin(top_movies.index)]['title'].tolist()
    
    return top_movie_titles

# Flask Routes
@app.route('/')
def index():
    # Get unique genres from the movies dataset
    genres = movies_df['genres'].str.split('|').explode().unique()
    return render_template('index.html', genres=genres)

@app.route('/recommend', methods=['POST'])
def recommend():
    selected_genres = request.form.getlist('genres')
    if not selected_genres:
        return render_template('error.html', error="Please select at least one genre.")
    
    recommended_movies = recommend_movies(selected_genres)
    
    if recommended_movies:
        return render_template('recommendations.html', movies=recommended_movies)
    else:
        return render_template('error.html', error="No recommendations found for the selected genres.")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
