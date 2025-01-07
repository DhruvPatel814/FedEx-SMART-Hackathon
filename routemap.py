import tkinter as tk
import customtkinter as ctk
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from datetime import datetime
import math

class RouteOptimizer:
    def __init__(self):
        self.emission_factors = {
            'car': 0.2,  # kg CO2/km
            'van': 0.3,
            'truck': 0.8
        }
        self.weather_impacts = {
            'Rain': 1.2,
            'Snow': 1.4,
            'Thunderstorm': 1.3,
            'Clear': 1.0
        }

    def calculate_emissions(self, distance, vehicle_type, weather_condition):
        base_emission = distance * self.emission_factors[vehicle_type]
        weather_factor = self.weather_impacts.get(weather_condition, 1.0)
        return base_emission * weather_factor

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/route_map.html'
        
        try:
            if self.path == '/route_map.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode())
            elif self.path == '/update_route':
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                with open('route_data.js', 'r') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Server error: {e}")

class RoutingApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Dynamic Route Planner")
        self.window.geometry("800x800")
        
        self.tomtom_key = "BFM8H20WdTfnxhnpdQjhCrJ3QCPd4KcQ"
        self.weather_key = "ca3e450ba3f2b1ea74302f72cb9b78f6"
        
        self.optimizer = RouteOptimizer()
        self.server = WebServer()
        self.server.start()
        self._create_widgets()
        webbrowser.open('http://localhost:8000/route_map.html')

    def _create_widgets(self):
        # Left panel for inputs and info
        left_frame = ctk.CTkFrame(self.window, width=300)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Input section
        input_frame = ctk.CTkFrame(left_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Start Location").pack(pady=5)
        self.start_entry = ctk.CTkEntry(input_frame, width=250)
        self.start_entry.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Destination").pack(pady=5)
        self.dest_entry = ctk.CTkEntry(input_frame, width=250)
        self.dest_entry.pack(pady=5)

        # Vehicle selection
        vehicle_frame = ctk.CTkFrame(left_frame)
        vehicle_frame.pack(fill="x", padx=5, pady=5)
        
        self.vehicle_var = tk.StringVar(value="car")
        ctk.CTkLabel(vehicle_frame, text="Vehicle Type:").pack()
        
        for vehicle in ["car", "van", "truck"]:
            ctk.CTkRadioButton(
                vehicle_frame,
                text=vehicle.capitalize(),
                variable=self.vehicle_var,
                value=vehicle
            ).pack(pady=2)

        # Info displays
        self.info_frame = ctk.CTkFrame(left_frame)
        self.info_frame.pack(fill="x", padx=5, pady=5)
        
        self.weather_label = ctk.CTkLabel(self.info_frame, text="Weather Info")
        self.weather_label.pack(pady=5)
        
        self.traffic_label = ctk.CTkLabel(self.info_frame, text="Traffic Info")
        self.traffic_label.pack(pady=5)
        
        self.emissions_label = ctk.CTkLabel(self.info_frame, text="Emissions Info")
        self.emissions_label.pack(pady=5)
        
        self.eta_label = ctk.CTkLabel(self.info_frame, text="ETA")
        self.eta_label.pack(pady=5)

        # Calculate button
        ctk.CTkButton(
            left_frame,
            text="Calculate Optimal Route",
            command=self.calculate_optimal_route
        ).pack(pady=20)

    def calculate_optimal_route(self):
        start_coords = self._geocode(self.start_entry.get())
        end_coords = self._geocode(self.dest_entry.get())
        
        if start_coords and end_coords:
            # Get route and traffic
            route_data = self._get_route(start_coords, end_coords)
            weather_data = self._get_weather(end_coords)
            
            if route_data and weather_data:
                # Calculate metrics
                distance = route_data['distance'] / 1000  # Convert to km
                duration = route_data['duration'] / 60    # Convert to minutes
                
                # Calculate emissions
                emissions = self.optimizer.calculate_emissions(
                    distance,
                    self.vehicle_var.get(),
                    weather_data['main']
                )
                
                # Update display
                self.weather_label.configure(
                    text=f"Weather: {weather_data['temp']}°C\n"
                         f"Condition: {weather_data['description']}"
                )
                
                self.traffic_label.configure(
                    text=f"Distance: {distance:.1f} km\n"
                         f"Current Traffic: {route_data['traffic_delay']/60:.0f} min delay"
                )
                
                self.emissions_label.configure(
                    text=f"Estimated CO2: {emissions:.1f} kg\n"
                         f"Weather Impact: {weather_data['impact']:.1f}x"
                )
                
                self.eta_label.configure(
                    text=f"ETA: {duration:.0f} minutes\n"
                         f"Arrival: {datetime.now().strftime('%H:%M')}"
                )
                
                # Update map
                with open('route_data.js', 'w') as f:
                    f.write(f'updateRoute({json.dumps(start_coords)}, '
                           f'{json.dumps(end_coords)}, '
                           f'{json.dumps(route_data["points"])});')

    def _get_route(self, start, end):
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{start[0]},{start[1]}:{end[0]},{end[1]}/json"
        params = {
            "key": self.tomtom_key,
            "traffic": "true",
            "vehicleHeading": "90",
            "sectionType": "traffic"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            route = data['routes'][0]
            
            return {
                'points': [[p['latitude'], p['longitude']] for p in route['legs'][0]['points']],
                'distance': route['summary']['lengthInMeters'],
                'duration': route['summary']['travelTimeInSeconds'],
                'traffic_delay': route['summary'].get('trafficDelayInSeconds', 0)
            }
        except Exception as e:
            print(f"Routing error: {e}")
            return None

    def _get_weather(self, coords):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": coords[0],
            "lon": coords[1],
            "appid": self.weather_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            weather_main = data['weather'][0]['main']
            return {
                'temp': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'main': weather_main,
                'impact': self.optimizer.weather_impacts.get(weather_main, 1.0)
            }
        except Exception as e:
            print(f"Weather error: {e}")
            return None

    def _geocode(self, location):
        url = f"https://api.tomtom.com/search/2/geocode/{location}.json"
        params = {"key": self.tomtom_key}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["results"]:
                pos = data["results"][0]["position"]
                return [pos["lat"], pos["lon"]]
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def run(self):
        self.window.mainloop()

class WebServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        
    def start(self):
        self.server = HTTPServer(('localhost', self.port), CustomHandler)
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dynamic Route Planner</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link rel="icon" href="data:,">
    <style>
        #map { height: 100vh; width: 100%; }
        body { margin: 0; }
        .info-box {
            padding: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([20.5937, 78.9629], 5);
        
        // Base map layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Traffic layer
        var trafficLayer = L.tileLayer('https://{s}.api.tomtom.com/traffic/map/4/tile/flow/{z}/{x}/{y}.png?key=BFM8H20WdTfnxhnpdQjhCrJ3QCPd4KcQ', {
            subdomains: ['1', '2', '3', '4'],
            opacity: 0.7
        }).addTo(map);

        var routeLayer;
        var markers = [];

        function updateRoute(start, end, route) {
            // Clear existing route and markers
            if (routeLayer) map.removeLayer(routeLayer);
            markers.forEach(m => map.removeLayer(m));
            markers = [];

            // Add new markers
            markers.push(L.marker(start).addTo(map).bindPopup('Start'));
            markers.push(L.marker(end).addTo(map).bindPopup('Destination'));

            // Add new route
            routeLayer = L.polyline(route, {
                color: 'blue',
                weight: 3,
                opacity: 0.8
            }).addTo(map);
            
            // Fit map to show entire route
            map.fitBounds(L.latLngBounds([start, end]));
        }

        // Periodic route updates
        setInterval(() => {
            fetch('/update_route')
                .then(response => response.text())
                .then(text => {
                    if (text) eval(text);
                })
                .catch(err => console.log('Route update error:', err));
        }, 1000);
        // Add zoom controls to the map
        L.control.zoom({
            position: 'topright'
        }).addTo(map);
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app = RoutingApp()
    app.run()