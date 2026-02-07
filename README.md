BarHopper uses the Google Places API to search and locate bars near a given address with Geocoding and gives you a walkable bar-hopping route. 
It also gives you a Google Maps route, console output of your route, and the walking distance calculated using the Haversine formula.

The application utilizes the requests module to handle HTTP communication with the Google Places APIs and the python-dotenv module to securely manage API credentials. 
For geocoding, pass a plaintext address to the Geocoding API, which returns a JSON object containing coordinate pairs (floats). 
For the bar search, provide the location (lat/lng), radius, and type parameters to the Places API, which returns a list of dictionaries representing nearby establishments.
To calculate the walking distance, I used the math module to implement the Haversine formula. 

Either use the script in findBars.py, or use the implementation in the "Projects" section of my portfolio to see it in action!

*NOTE BarHopper uses a free version of Render which takes ~45 seconds to deploy if it has not been called in over 30 minutes. Thus the first bar search may take a sec!

TO OBTAIN A GOOGLE API KEY:
1. Visit the Google Cloud Console.

2. Create a new project and enable the Geocoding API and Places API.

3. Navigate to Credentials and generate an API Key.

4. Create a .env file in the root directory of this project.

5. Add your key to the .env file: GOOGLE_API_KEY=your_key_here.
