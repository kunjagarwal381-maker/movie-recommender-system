import time
import streamlit as st
import pickle
import requests

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Title */
    h1 {
        text-align: center;
        font-size: 3rem !important;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #aaa;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #1e1e2e !important;
        color: white !important;
        border: 1px solid #f7971e !important;
        border-radius: 10px !important;
    }

    /* Button */
    .stButton > button {
        display: block;
        margin: 0 auto;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: black;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.6rem 2.5rem;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
    }

    /* Movie card */
    .movie-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        transition: transform 0.3s;
        backdrop-filter: blur(5px);
    }
    .movie-card:hover {
        transform: translateY(-8px);
        border-color: #f7971e;
    }
    .movie-card img {
        border-radius: 10px;
        width: 100%;
    }
    .movie-title {
        color: white;
        font-weight: bold;
        font-size: 0.95rem;
        margin-top: 8px;
    }

    /* Section header */
    .section-title {
        text-align: center;
        color: #ffd200;
        font-size: 1.4rem;
        margin: 2rem 0 1rem 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_list = pickle.load(open('movies.pkl', 'rb'))
movies = movie_list["title"].values

# ── Fetch poster ─────────────────────────────────────────
def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": "a6a8769d3b738557ffd00e4fc71ccd42", "language": "en-US"}
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            return "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
        except:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return "https://via.placeholder.com/500x750?text=Error"

# ── Recommend ─────────────────────────────────────────────
def recommend(movie_name):
    idx = movie_list[movie_list["title"] == movie_name].index[0]
    distances = similarity[idx]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    names, posters = [], []
    for i in movies_list:
        movie_id = movie_list.iloc[i[0]].movie_id
        names.append(movie_list.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        time.sleep(0.3)
    return names, posters

# ── UI ────────────────────────────────────────────────────
st.markdown("<h1>🎬 Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover movies you\'ll love based on your favorites</p>', unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    selected_movie_name = st.selectbox("🎥 Choose a movie", movies)
    st.markdown("")
    recommend_btn = st.button("✨ Recommend Movies")
if recommend_btn:
    with st.spinner("Finding the best picks for you..."):
        names, posters = recommend(selected_movie_name)

    st.markdown('<p class="section-title">⭐ Top Picks For You</p>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{posters[i]}" alt="{names[i]}"/>
                <div class="movie-title">{names[i]}</div>
            </div>
            """, unsafe_allow_html=True)