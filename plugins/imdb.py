import aiohttp

API_KEY = "ae495bd1"


# =========================
# GET MOVIE
# =========================
async def get_movie(query):

    try:

        url = f"http://www.omdbapi.com/" f"?t={query}&apikey={API_KEY}"

        async with aiohttp.ClientSession() as session:

            async with session.get(url) as response:

                data = await response.json()

        if data.get("Response") == "False":

            return None

        poster = data.get("Poster")

        if poster == "N/A":
            poster = None

        caption = (
            f"<b>🎬 Movie:</b> {data.get('Title', 'Unknown')}\n\n"
            f"<b>📅 Year:</b> {data.get('Year', 'N/A')}\n"
            f"<b>⭐ IMDb Rating:</b> {data.get('imdbRating', 'N/A')}/10\n"
            f"<b>🎭 Genre:</b> {data.get('Genre', 'N/A')}\n"
            f"<b>⏳ Runtime:</b> {data.get('Runtime', 'N/A')}\n"
            f"<b>🌍 Language:</b> {data.get('Language', 'N/A')}\n"
            f"<b>🎬 Director:</b> {data.get('Director', 'N/A')}\n"
            f"<b>🏆 Awards:</b> {data.get('Awards', 'N/A')}\n\n"
            f"<b>📖 Plot:</b>\n"
            f"{data.get('Plot', 'N/A')}"
        )

        return {"poster": poster, "caption": caption}

    except Exception as e:

        print("IMDb Error:", e)

        return None
