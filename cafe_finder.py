from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

def get_cafes(location):
    # Geocode location using Nominatim (OSM)
    geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=3"
    response = requests.get(geocode_url, headers={"User-Agent": "CafeFinder/1.0 (nehal@example.com)"})
    if response.status_code != 200 or not response.json():
        return "Bhai, location nahi mili!"

    # Take the most relevant location
    best_loc = max(response.json(), key=lambda x: float(x.get("importance", 0)))
    lat, lng = float(best_loc["lat"]), float(best_loc["lon"])

    # Search nearby cafes using Overpass API with 5km radius
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node["amenity"="cafe"](around:5000,{lat},{lng});
    out body;
    >;
    out skel qt;
    """
    response = requests.post(overpass_url, data=query, headers={"User-Agent": "CafeFinder/1.0 (nehal@example.com)"})
    if response.status_code != 200:
        return "Bhai, cafes nahi mile!"

    cafes_data = response.json()["elements"]
    cafes = []
    for cafe in cafes_data:
        name = cafe.get("tags", {}).get("name", "Unknown Cafe")
        lat_c = cafe["lat"]
        lon_c = cafe["lon"]
        address = cafe.get("tags", {}).get("addr:street", "Near " + location) + " " + cafe.get("tags", {}).get("addr:housenumber", "")
        cuisine = cafe.get("tags", {}).get("cuisine", "Not specified")
        maps_url = f"https://www.openstreetmap.org/?mlat={lat_c}&mlon={lon_c}#map=16/{lat_c}/{lon_c}"
        rating = "N/A (Check Google/Zomato)"
        photo = "N/A (Check Google/Zomato for photos)"
        category = "Nice"
        if cuisine in ["coffee_shop", "italian"]:
            category = "Good"
        if "popular" in name.lower() or lat_c == lat:
            category = "Best"

        cafes.append({"name": name, "address": address, "cuisine": cuisine, "maps_url": maps_url, "rating": rating, "photo": photo, "category": category})

    return cafes

@app.route("/", methods=["GET", "POST"])
def home():
    cafes = []
    if request.method == "POST":
        location = request.form["location"]
        cafes = get_cafes(location)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Cafe Finder Tech</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: #e0e0e0;
                font-family: 'Arial', sans-serif;
                overflow-x: hidden;
            }
            .tech-input {
                transition: all 0.3s ease-in-out;
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
            }
            .tech-input:focus {
                transform: scale(1.05);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
            }
            .cafe-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .cafe-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.7);
            }
            .fade-in {
                animation: fadeIn 0.5s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .neon-text {
                text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 15px #00ffff;
            }
        </style>
    </head>
    <body class="min-h-screen flex items-center justify-center flex-col">
        <h1 class="text-4xl md:text-5xl font-bold mb-6 neon-text">Bhai, Tech Cafe Finder!</h1>
        <form method="POST" class="mb-8">
            <input type="text" name="location" placeholder="City ya address (e.g., Mumbai)" required
                   class="tech-input p-3 rounded-lg text-black focus:outline-none">
            <input type="submit" value="Search" class="ml-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        </form>
        <div class="cafe-list grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-4xl px-4">
            {% if cafes %}
                <h2 class="text-2xl font-semibold mb-4 neon-text">Results:</h2>
                {% for cafe in cafes %}
                    <div class="cafe-card p-4 fade-in {{ cafe.category.lower() }}">
                        <h3 class="text-xl font-bold">{{ cafe.name }}</h3>
                        <p class="mt-2">Address: {{ cafe.address }}</p>
                        <p>Cuisine: {{ cafe.cuisine }}</p>
                        <p>Rating: {{ cafe.rating }}</p>
                        <p>Photo: {{ cafe.photo }}</p>
                        <a href="{{ cafe.maps_url }}" target="_blank" class="text-blue-400 hover:text-blue-600 mt-2 inline-block">OpenStreetMap</a>
                    </div>
                {% endfor %}
            {% elif cafes == 'Bhai, location nahi mili!' or cafes == 'Bhai, cafes nahi mile!' %}
                <p class="text-red-400 text-lg">{{ cafes }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, cafes=cafes)

if __name__ == "__main__":
    app.run(debug=True , port  = 5000)