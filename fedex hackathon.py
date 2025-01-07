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
            'petrol_car': 0.2,
            'diesel_car': 0.18,
            'hybrid_car': 0.12,
            'small_van': 0.25,
            'large_van': 0.35,
            'truck': 0.8
        }
        self.fuel_efficiency = {
            'petrol_car': 12,    # km/L
            'diesel_car': 14,    # km/L
            'hybrid_car': 20,    # km/L
            'small_van': 10,     # km/L
            'large_van': 8,      # km/L
            'truck': 4          # km/L
        }
        self.fuel_prices = {
            'petrol': 102.0,     # ₹/L
            'diesel': 88.0,      # ₹/L
            'hybrid': 102.0      # ₹/L
        }
        self.weather_impacts = {
            'Rain': 1.2,
            'Snow': 1.4,
            'Thunderstorm': 1.3,
            'Clear': 1.0,
            'Cloudy': 1.1,
            'Fog': 1.25
        }
        self.fuel_api_key = "EkTi9xNhsVsqFek79byCcpsi01QCh0Fd5JvTw2RH"

    def get_fuel_consumption(self, distance, vehicle_type, traffic_delay, weather_condition):
        try:
            url = "https://api.carbon-footprint.com/v1/fuel-consumption"
            headers = {
                "Authorization": f"Bearer {self.fuel_api_key}",
                "Content-Type": "application/json"
            }
            
            # Calculate traffic impact (increased fuel consumption in traffic)
            traffic_factor = 1 + (traffic_delay / 3600) * 0.1  # 10% increase per hour of delay
            weather_factor = self.weather_impacts.get(weather_condition, 1.0)
            
            # Basic fuel consumption calculation
            base_efficiency = self.fuel_efficiency[vehicle_type]
            adjusted_efficiency = base_efficiency / (traffic_factor * weather_factor)
            
            fuel_consumption = distance / adjusted_efficiency
            
            # Determine fuel type and price
            if vehicle_type in ['petrol_car', 'small_van']:
                fuel_type = 'petrol'
            elif vehicle_type in ['diesel_car', 'large_van', 'truck']:
                fuel_type = 'diesel'
            else:  # hybrid
                fuel_type = 'hybrid'
            
            fuel_cost = fuel_consumption * self.fuel_prices[fuel_type]
            
            # Calculate CO2 emissions
            co2_emissions = distance * self.emission_factors[vehicle_type] * traffic_factor * weather_factor
            
            # API call for additional data
            payload = {
                "distance": distance,
                "vehicle_type": vehicle_type,
                "traffic_delay": traffic_delay,
                "weather": weather_condition,
                "fuel_type": fuel_type
            }
            
            response = requests.post(url, headers=headers, json=payload)
            api_data = response.json()
            
            # Combine local calculations with API data
            return {
                'fuel_consumption': fuel_consumption,
                'fuel_cost': fuel_cost,
                'co2_emissions': co2_emissions,
                'fuel_type': fuel_type,
                'efficiency': adjusted_efficiency,
                'traffic_impact': traffic_factor,
                'weather_impact': weather_factor,
                'api_data': api_data
            }
            
        except Exception as e:
            print(f"Fuel API error: {e}")
            return self._fallback_calculations(distance, vehicle_type, traffic_delay, weather_condition)

    def _fallback_calculations(self, distance, vehicle_type, traffic_delay, weather_condition):
        # Fallback calculations if API fails
        traffic_factor = 1 + (traffic_delay / 3600) * 0.1
        weather_factor = self.weather_impacts.get(weather_condition, 1.0)
        base_efficiency = self.fuel_efficiency[vehicle_type]
        adjusted_efficiency = base_efficiency / (traffic_factor * weather_factor)
        fuel_consumption = distance / adjusted_efficiency
        
        if vehicle_type in ['petrol_car', 'small_van']:
            fuel_type = 'petrol'
        elif vehicle_type in ['diesel_car', 'large_van', 'truck']:
            fuel_type = 'diesel'
        else:
            fuel_type = 'hybrid'
        
        fuel_cost = fuel_consumption * self.fuel_prices[fuel_type]
        co2_emissions = distance * self.emission_factors[vehicle_type] * traffic_factor * weather_factor
        
        return {
            'fuel_consumption': fuel_consumption,
            'fuel_cost': fuel_cost,
            'co2_emissions': co2_emissions,
            'fuel_type': fuel_type,
            'efficiency': adjusted_efficiency,
            'traffic_impact': traffic_factor,
            'weather_impact': weather_factor,
            'api_data': None
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
        self.window.geometry("1000x800")
        
        self.tomtom_key = "BFM8H20WdTfnxhnpdQjhCrJ3QCPd4KcQ"
        self.weather_key = "ca3e450ba3f2b1ea74302f72cb9b78f6"
        
        self.optimizer = RouteOptimizer()
        self.server = WebServer()
        self.server.start()
        self._create_widgets()
        webbrowser.open('http://localhost:8000/route_map.html')

    def _create_widgets(self):
        # Left panel for inputs and info
        left_frame = ctk.CTkFrame(self.window, width=350)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Input section
        input_frame = ctk.CTkFrame(left_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Start Location").pack(pady=5)
        self.start_entry = ctk.CTkEntry(input_frame, width=300)
        self.start_entry.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Destination").pack(pady=5)
        self.dest_entry = ctk.CTkEntry(input_frame, width=300)
        self.dest_entry.pack(pady=5)

        # Vehicle selection with more options
        vehicle_frame = ctk.CTkFrame(left_frame)
        vehicle_frame.pack(fill="x", padx=5, pady=5)
        
        self.vehicle_var = tk.StringVar(value="petrol_car")
        ctk.CTkLabel(vehicle_frame, text="Vehicle Type:").pack()
        
        vehicles = [
            ("Petrol Car", "petrol_car"),
            ("Diesel Car", "diesel_car"),
            ("Hybrid Car", "hybrid_car"),
            ("Small Van", "small_van"),
            ("Large Van", "large_van"),
            ("Truck", "truck")
        ]
        
        for vehicle_name, vehicle_value in vehicles:
            ctk.CTkRadioButton(
                vehicle_frame,
                text=vehicle_name,
                variable=self.vehicle_var,
                value=vehicle_value
            ).pack(pady=2)

        # Info displays with sections
        self.info_frame = ctk.CTkFrame(left_frame)
        self.info_frame.pack(fill="x", padx=5, pady=5)
        
        # Route Information Section
        route_section = ctk.CTkFrame(self.info_frame)
        route_section.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(route_section, text="Route Information", font=("Arial", 14, "bold")).pack()
        self.distance_label = ctk.CTkLabel(route_section, text="Distance: --")
        self.distance_label.pack(pady=2)
        self.eta_label = ctk.CTkLabel(route_section, text="ETA: --")
        self.eta_label.pack(pady=2)
        
        # Weather Information Section
        weather_section = ctk.CTkFrame(self.info_frame)
        weather_section.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(weather_section, text="Weather Information", font=("Arial", 14, "bold")).pack()
        self.weather_label = ctk.CTkLabel(weather_section, text="Current Weather: --")
        self.weather_label.pack(pady=2)
        
        # Traffic Information Section
        traffic_section = ctk.CTkFrame(self.info_frame)
        traffic_section.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(traffic_section, text="Traffic Information", font=("Arial", 14, "bold")).pack()
        self.traffic_label = ctk.CTkLabel(traffic_section, text="Traffic Status: --")
        self.traffic_label.pack(pady=2)
        
        # Fuel Information Section
        fuel_section = ctk.CTkFrame(self.info_frame)
        fuel_section.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(fuel_section, text="Fuel Analysis", font=("Arial", 14, "bold")).pack()
        self.fuel_consumption_label = ctk.CTkLabel(fuel_section, text="Fuel Consumption: --")
        self.fuel_consumption_label.pack(pady=2)
        self.fuel_efficiency_label = ctk.CTkLabel(fuel_section, text="Fuel Efficiency: --")
        self.fuel_efficiency_label.pack(pady=2)
        self.fuel_cost_label = ctk.CTkLabel(fuel_section, text="Fuel Cost: --")
        self.fuel_cost_label.pack(pady=2)
        
        # Emissions Section
        emissions_section = ctk.CTkFrame(self.info_frame)
        emissions_section.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(emissions_section, text="Environmental Impact", font=("Arial", 14, "bold")).pack()
        self.emissions_label = ctk.CTkLabel(emissions_section, text="CO2 Emissions: --")
        self.emissions_label.pack(pady=2)
        self.impact_label = ctk.CTkLabel(emissions_section, text="Environmental Impact: --")
        self.impact_label.pack(pady=2)

        # Calculate button
        ctk.CTkButton(
            left_frame,
            text="Calculate Route",
            command=self.calculate_optimal_route,
            height=40,
            font=("Arial", 14)
        ).pack(pady=20)

    def calculate_optimal_route(self):
        start_coords = self._geocode(self.start_entry.get())
        end_coords = self._geocode(self.dest_entry.get())
        
        if start_coords and end_coords:
            route_data = self._get_route(start_coords, end_coords)
            weather_data = self._get_weather(end_coords)
            
            if route_data and weather_data:
                distance = route_data['distance'] / 1000  # Convert to km
                duration = route_data['duration'] / 60    # Convert to minutes
                
                # Get comprehensive fuel data
                fuel_data = self.optimizer.get_fuel_consumption(
                    distance,
                    self.vehicle_var.get(),
                    route_data['traffic_delay'],
                    weather_data['main']
                )
                
                # Update all display labels with detailed information
                self.distance_label.configure(
                    text=f"Distance: {distance:.1f} km"
                )
                
                self.eta_label.configure(
                    text=f"ETA: {duration:.0f} min\n"
                         f"Arrival: {datetime.now().strftime('%H:%M')}"
                )
                
                self.weather_label.configure(
                    text=f"Temperature: {weather_data['temp']}°C\n"
                         f"Condition: {weather_data['description']}\n"
                         f"Impact on Fuel: +{((fuel_data['weather_impact'] - 1) * 100):.1f}%"
                )
                
                self.traffic_label.configure(
                    text=f"Delay: {route_data['traffic_delay']/60:.0f} min\n"
                         f"Impact on Fuel: +{((fuel_data['traffic_impact'] - 1) * 100):.1f}%"
                )
                
                self.fuel_consumption_label.configure(
                    text=f"Fuel Required: {fuel_data['fuel_consumption']:.1f} L\n"
                         f"Fuel Type: {fuel_data['fuel_type'].title()}"
                )
                
                self.fuel_efficiency_label.configure(
                    text=f"Average Efficiency: {fuel_data['efficiency']:.1f} km/L\n"
                         f"(Including traffic & weather effects)"
                )
                
                self.fuel_cost_label.configure(
                    text=f"Estimated Cost: ₹{fuel_data['fuel_cost']:.2f}\n"
                         f"Rate: ₹{self.optimizer.fuel_prices[fuel_data['fuel_type']]}/L"
                )
                
                self.emissions_label.configure(
                    text=f"CO2 Emissions: {fuel_data['co2_emissions']:.1f} kg\n"
                         f"Carbon Intensity: {(fuel_data['co2_emissions']/distance):.2f} kg/km"
                )
                
                self.impact_label.configure(
                    text=f"Weather Impact: {weather_data['impact']:.1f}x\n"
                         f"Traffic Impact: {fuel_data['traffic_impact']:.1f}x"
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
                'traffic_delay': route['summary']['trafficDelayInSeconds']
            }
        except Exception as e:
            print(f"Error fetching route data: {e}")
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
    <title>Enhanced Route Planner with Fuel Analysis</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <link rel="icon" href="data:,">
    <style>
        #map { height: 65vh; width: 100%; }
        body { margin: 0; font-family: Arial, sans-serif; background: #f5f5f5; }
        
        .controls {
            padding: 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 15px;
            display: flex;
            gap: 15px;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .controls input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .controls button {
            padding: 10px 20px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            transition: background 0.3s;
        }
        
        .controls button:hover {
            background: #45a049;
        }
        
        .info-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px;
        }
        
        .info-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .info-card h3 {
            margin: 0 0 10px 0;
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 5px;
        }
        
        .fuel-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        
        .metric {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #2196F3;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .legends {
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        
        .legend-color {
            width: 20px;
            height: 10px;
            margin-right: 10px;
            border-radius: 2px;
        }
        
        .eco-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .eco-score {
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="controls">
        <input type="text" id="start" placeholder="Start Location">
        <input type="text" id="end" placeholder="Destination">
        <select id="vehicleType">
            <option value="petrol_car">Petrol Car</option>
            <option value="diesel_car">Diesel Car</option>
            <option value="hybrid_car">Hybrid Car</option>
            <option value="small_van">Small Van</option>
            <option value="large_van">Large Van</option>
            <option value="truck">Truck</option>
        </select>
        <button onclick="findRoute()">Calculate Route</button>
        <button onclick="resetRoute()">Reset</button>
    </div>

    <div id="map"></div>

    <div class="info-panel">
        <div class="info-card">
            <h3>Route Information</h3>
            <div id="routeInfo"></div>
        </div>
        <div class="info-card">
            <h3>Fuel Analysis</h3>
            <div class="fuel-metrics">
                <div class="metric">
                    <div class="metric-value" id="fuelConsumption">--</div>
                    <div class="metric-label">Fuel Consumption (L)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="fuelCost">--</div>
                    <div class="metric-label">Estimated Cost (₹)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="fuelEfficiency">--</div>
                    <div class="metric-label">Efficiency (km/L)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="co2Emissions">--</div>
                    <div class="metric-label">CO2 Emissions (kg)</div>
                </div>
            </div>
        </div>
    </div>

    <div class="legends">
        <div><strong>Traffic & Efficiency</strong></div>
        <div class="legend-item">
            <div class="legend-color" style="background: #4CAF50;"></div>
            Optimal Efficiency
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #FFC107;"></div>
            Moderate Impact
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #F44336;"></div>
            High Consumption
        </div>
    </div>

    <div class="eco-indicator">
        <div>Eco Score</div>
        <div class="eco-score" id="ecoScore">--</div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script>
        let map;
        let routeLayer;
        let markers = [];
        
        function initMap() {
            map = L.map('map').setView([20.5937, 78.9629], 5);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            routeLayer = L.layerGroup().addTo(map);
        }

        async function findRoute() {
            const start = document.getElementById('start').value;
            const end = document.getElementById('end').value;
            const vehicleType = document.getElementById('vehicleType').value;

            if (!start || !end) {
                alert('Please enter both start and end locations');
                return;
            }

            resetRoute();

            try {
                // Get coordinates and route data
                const startCoords = await geocode(start);
                const endCoords = await geocode(end);
                const routeData = await getRouteData(startCoords, endCoords, vehicleType);
                
                // Display route on map
                displayRoute(routeData);
                
                // Update information panels
                updateRouteInfo(routeData);
                updateFuelMetrics(routeData);
                updateEcoScore(routeData);
                
                // Add markers
                addMarkers(startCoords, endCoords);
                
                // Fit map to route
                map.fitBounds(L.polyline(routeData.points).getBounds());
            } catch (error) {
                console.error('Route calculation error:', error);
                alert('Error calculating route. Please try again.');
            }
        }

        function displayRoute(routeData) {
            const { points, segments } = routeData;
            
            segments.forEach(segment => {
                const color = getSegmentColor(segment.efficiency);
                L.polyline(segment.points, {
                    color: color,
                    weight: 5,
                    opacity: 0.8
                }).addTo(routeLayer);
            });
        }

        function getSegmentColor(efficiency) {
            if (efficiency > 0.8) return '#4CAF50';
            if (efficiency > 0.5) return '#FFC107';
            return '#F44336';
        }

        function updateRouteInfo(routeData) {
            const routeInfo = document.getElementById('routeInfo');
            routeInfo.innerHTML = `
                <p><strong>Distance:</strong> ${(routeData.distance/1000).toFixed(1)} km</p>
                <p><strong>Duration:</strong> ${Math.round(routeData.duration/60)} minutes</p>
                <p><strong>Traffic Delay:</strong> ${Math.round(routeData.trafficDelay/60)} minutes</p>
                <p><strong>Weather:</strong> ${routeData.weather}</p>
            `;
        }

        function updateFuelMetrics(routeData) {
            document.getElementById('fuelConsumption').textContent = 
                routeData.fuel.consumption.toFixed(1);
            document.getElementById('fuelCost').textContent = 
                routeData.fuel.cost.toFixed(0);
            document.getElementById('fuelEfficiency').textContent = 
                routeData.fuel.efficiency.toFixed(1);
            document.getElementById('co2Emissions').textContent = 
                routeData.fuel.emissions.toFixed(1);
        }

        function updateEcoScore(routeData) {
            const score = calculateEcoScore(routeData);
            const ecoScore = document.getElementById('ecoScore');
            ecoScore.textContent = score + '/100';
            ecoScore.style.color = getEcoScoreColor(score);
        }

        function calculateEcoScore(routeData) {
            // Calculate eco score based on multiple factors
            const efficiencyScore = routeData.fuel.efficiency * 20;
            const emissionsScore = (1 - routeData.fuel.emissions/100) * 40;
            const trafficScore = (1 - routeData.trafficDelay/3600) * 20;
            const weatherScore = (1 - (routeData.weatherImpact - 1)) * 20;
            
            return Math.round(efficiencyScore + emissionsScore + trafficScore + weatherScore);
        }

        function getEcoScoreColor(score) {
            if (score >= 80) return '#4CAF50';
            if (score >= 60) return '#FFC107';
            return '#F44336';
        }

        function resetRoute() {
            routeLayer.clearLayers();
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
            
            document.getElementById('routeInfo').innerHTML = '';
            document.getElementById('fuelConsumption').textContent = '--';
            document.getElementById('fuelCost').textContent = '--';
            document.getElementById('fuelEfficiency').textContent = '--';
            document.getElementById('co2Emissions').textContent = '--';
            document.getElementById('ecoScore').textContent = '--';
        }

        initMap();
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app = RoutingApp()
    app.run() 
