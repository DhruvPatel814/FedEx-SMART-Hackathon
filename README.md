# FedEx-SMART-Hackathon

Dynamic Route Optimizer is an advanced Python application that combines the power of multiple APIs to provide users with real-time route planning and environmental insights. Designed for efficiency and usability, it calculates optimal routes, accounts for traffic and weather conditions, and estimates CO2 emissions based on vehicle type and route characteristics.

---

## 🌟 Features

### 🔍 Real-Time Data Integration
- **Traffic Updates**: Leverages the TomTom API for live traffic insights.
- **Weather Conditions**: Uses OpenWeatherMap to assess meteorological factors impacting travel.

### 🛣️ Route Optimization
- Calculates optimal routes and estimated arrival times.
- Provides travel distance and duration with traffic impact considerations.

### 🌱 Environmental Insights
- Vehicle-specific CO2 emission estimates.
- Dynamic adjustments based on weather conditions.

### 🌍 Interactive Map
- Visualize routes and traffic layers using Leaflet.js.
- Markers for start and destination points with real-time updates.

---

## 🛠️ Technologies Used

- **Programming Language**: Python
- **Frameworks and Libraries**: 
  - `customtkinter` for the GUI.
  - `requests` for API interactions.
- **APIs**:
  - [TomTom Routing API](https://developer.tomtom.com/)
  - [OpenWeatherMap API](https://openweathermap.org/api)
- **Frontend**: Leaflet.js for map rendering and interaction.
- **Server**: Local HTTP server for real-time updates.

---

## 📋 Prerequisites

Before setting up the project, ensure the following:
1. **Python 3.8+** is installed on your system.
2. API keys:
   - [TomTom Routing API](https://developer.tomtom.com/)
   - [OpenWeatherMap API](https://openweathermap.org/).

---

## 🚀 Installation Guide

### Step 1: Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/yourusername/RouteOptimizer.git
cd RouteOptimizer
