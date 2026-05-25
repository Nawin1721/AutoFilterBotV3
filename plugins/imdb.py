import aiohttp

API_KEY = "ae495bd1"


# =========================
# GET MOVIE
# =========================
async def get_movie(query):

    try:

        url = (
            f"http://www.omdbapi.com/"
            f"?t={query}&apikey={API_KEY}"
        )

        async with aiohttp.ClientSession() as session:

            async with session.get(url) as response:

                data = await response.json()

        if data.get("Response") == "False":

            return None

        poster = data.get("Poster")

        if poster == "N/A":
            poster = None

        caption = (
            f"🎬 {data.get('Title', 'Unknown')} "
            f"({data.get('Year', 'N/A')})\n"

            f"⭐ Rating: "
            f"{data.get('imdbRating', 'N/A')}/10\n"

            f"🎭 Genre: "
            f"{data.get('Genre', 'N/A')}"
        )

        return {

            "poster": poster,

            "caption": caption

        }

    except Exception as e:

        print("IMDb Error:", e)

        return None
