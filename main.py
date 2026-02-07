from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import math

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

# --- CORS SETTINGS ---
# This allows your GitHub Pages site to talk to this Render server
# --- CORS SETTINGS ---
app.add_middleware(
    CORSMiddleware,
    # Allow both your local testing and your live portfolio
    allow_origins=[
        "https://conchoe.github.io", 
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], # Standard web methods
    allow_headers=["*"], # Allow all standard browser headers
)

# --- YOUR LOGIC FUNCTIONS (Unchanged) ---

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def get_geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(url, params=params).json()
    if response["status"] == "OK":
        return response["results"][0]["geometry"]["location"]["lat"], response["results"][0]["geometry"]["location"]["lng"]
    raise Exception(f"Geocoding Error: {response['status']}")

def fetch_nearby_bars(lat, lng, radius=1500):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "radius": radius, "type": "bar", "key": API_KEY}
    response = requests.get(url, params=params).json()
    return [{
        "name": p["name"],
        "lat": p["geometry"]["location"]["lat"],
        "lng": p["geometry"]["location"]["lng"],
        "rating": p.get("rating", "N/A")
    } for p in response.get("results", [])]

def build_route(start_lat, start_lng, bars, max_stops):
    route = []
    current_lat, current_lng = start_lat, start_lng
    available_bars = bars.copy()
    while available_bars and len(route) < max_stops:
        next_bar = min(available_bars, key=lambda b: haversine(current_lat, current_lng, b["lat"], b["lng"]))
        next_bar["dist_from_last"] = haversine(current_lat, current_lng, next_bar["lat"], next_bar["lng"])
        route.append(next_bar)
        available_bars.remove(next_bar)
        current_lat, current_lng = next_bar["lat"], next_bar["lng"]
    return route

# --- FASTAPI ENDPOINT ---

@app.get("/generate-route")
def generate_route(address: str, stops: int = 3):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured on server")
    
    try:
        lat, lng = get_geocode(address)
        bars = fetch_nearby_bars(lat, lng)
        
        if not bars:
            return {"error": "No bars found in this area."}
            
        route = build_route(lat, lng, bars, stops)
        
        # Generate the Google Maps Link
        points = "/".join([f"{b['lat']},{b['lng']}" for b in route])
        maps_url = f"https://www.google.com/maps/dir/{lat},{lng}/{points}"
        
        return {
            "status": "success",
            "route": route,
            "map_url": maps_url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)