from dotenv import load_dotenv
import os
import requests
import math
load_dotenv()  # This finds the .env file and sets the variables automatically


# --- CONFIGURATION ---
# Ensure you run `export GOOGLE_API_KEY='your_key_here'` in your terminal
API_KEY = os.getenv("GOOGLE_API_KEY")

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the Earth in miles.
    """
    R = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_geocode(address):
    """Converts a string address to lat/lng coordinates."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(url, params=params).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise Exception(f"Geocoding Error: {response['status']}")

def fetch_nearby_bars(lat, lng, radius=1500):
    """Finds bars within a specific radius of the coordinates."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "bar",
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    
    bars = []
    for place in response.get("results", []):
        bars.append({
            "name": place["name"],
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"],
            "rating": place.get("rating", "N/A")
        })
    return bars

def build_route(start_lat, start_lng, bars, max_stops):
    """
    Greedy Nearest Neighbor Algorithm:
    Always picks the closest bar from the current location.
    """
    route = []
    current_lat, current_lng = start_lat, start_lng
    
    # We only care about the top bars available
    available_bars = bars.copy()
    
    while available_bars and len(route) < max_stops:
        # Find the bar with the minimum haversine distance from current location
        next_bar = min(
            available_bars, 
            key=lambda b: haversine(current_lat, current_lng, b["lat"], b["lng"])
        )
        
        # Calculate distance to this bar for our output
        dist = haversine(current_lat, current_lng, next_bar["lat"], next_bar["lng"])
        next_bar["dist_from_last"] = dist
        
        route.append(next_bar)
        available_bars.remove(next_bar)
        
        # Move our "current" position to the new bar
        current_lat, current_lng = next_bar["lat"], next_bar["lng"]
        
    return route

def main():
    print("--- 🍻 Google Places Bar Hopper ---")
    
    if not API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return

    address = input("Enter a starting address: ")
    try:
        max_bars = int(input("How many bars do you want to visit? "))
    except ValueError:
        print("Enter a number!")
        max_bars = int(input("How many bars do you want to visit?"))

    try:
        # 1. Geocode
        print(f"\nLocating '{address}'...")
        start_lat, start_lng = get_geocode(address)
        
        # 2. Fetch Bars
        print("Searching for nearby watering holes...")
        all_bars = fetch_nearby_bars(start_lat, start_lng)
        
        if not all_bars:
            print("No bars found in that area!")
            return

        # 3. Optimize Route
        print("Optimizing your walking route...")
        route = build_route(start_lat, start_lng, all_bars, max_bars)
        
        # 4. Output
        print("\n✅ YOUR OPTIMAL ROUTE:")
        total_dist = 0
        for i, bar in enumerate(route, 1):
            total_dist += bar['dist_from_last']
            print(f"{i}. {bar['name']} ({bar['rating']} ⭐)")
            print(f"   Move: {bar['dist_from_last']:.2f} miles from previous stop")
            
        print("-" * 30)
        print(f"Total Walking Distance: {total_dist:.2f} miles")
        # Create a URL for a multi-stop route
        base_url = "https://www.google.com/maps/dir/"
        points = "/".join([f"{b['lat']},{b['lng']}" for b in route])
        print(f"\nOpen your route in Maps: {base_url}{start_lat},{start_lng}/{points}")

        
    except Exception as e:
        print(f"An error occurred: {e}")

    
if __name__ == "__main__":
    main()

    