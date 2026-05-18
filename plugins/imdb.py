import requests

API_KEY = "ae495bd1"


async def get_movie(query):

    try:

        url = f"http://www.omdbapi.com/?t={query}&apikey={API_KEY}"

        response = requests.get(url)

        data = response.json()

        if data["Response"] == "False":

            return None

        poster = data["Poster"]

        caption = (
            f"🎬 {data['Title']} ({data['Year']})\n"
            f"⭐ Rating: {data['imdbRating']}/10\n"
            f"🎭 Genre: {data['Genre']}"
        )

        return {
            "poster": poster,
            "caption": caption
        }

    except Exception as e:

        print("IMDb Error:", e)

        return None