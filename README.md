
# 🌤️ Weatherboard — Global Weather Dashboard

A modern, beautiful **card-based weather dashboard** built using **Streamlit**, **Open-Meteo API**, and **Astral**.
Enter any city in the world and get:

* 🌡️ Real-time temperature & feels-like
* 🌤️ Cloud cover & visibility
* 💨 Wind speed
* 💧 Humidity
* 📉 Pressure
* 🌅 Sunrise / 🌇 Sunset (Astral)
* 🕒 Hour-by-hour forecast (next 8 hours)
* 🎨 Clean glassmorphic blue UI (desktop & mobile friendly)



---

## 🚀 Feature

### ✔ Global City Search

Type any city name — the app automatically fetches latitude, longitude, country, and timezone using **Open-Meteo Geocoding API**.

### ✔ Live Current Weather

Fetched from **Open-Meteo Forecast API**, including:

* Temperature
* Feels Like
* Humidity
* Wind Speed
* Pressure
* Cloud Cover
* Visibility
* Condition (Clear/Cloudy)

### ✔ Sunrise & Sunset Times

Powered by **Astral**, using real geographic coordinates.

### ✔ Hourly Weather Forecast

Shows compact cards for the next 8 hours:

* Temperature
* Humidity
* Wind Speed

### ✔ Clean UI

Built with custom CSS:

* Blue gradient background
* Glass-style cards
* Hero temperature card
* Minimal & responsive design

---

## 🧩 Project Structure

```
WETHERFORECAST/
│
├── app.py                    # Main Streamlit application (UI + logic)
│
├── models/
│   ├── sun_times.py          # Astral-based sunrise/sunset calculator
│   └── ...                   # (Other backend modules if added)
│
└── README.md                 # Project documentation
```

*(Your app also dynamically calls remote APIs — no local data files required.)*

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weatherboard.git
cd weatherboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, create one with:

```
streamlit
pandas
requests
astral
```

---

## ▶️ Run the App

Inside the project folder:

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## 🔧 How It Works

### 1. City → Coordinates

Using:

```
https://geocoding-api.open-meteo.com/v1/search
```

Returns:

* lat / lon
* timezone
* city & country labels

### 2. Current Weather & Hourly Forecast

Using:

```
https://api.open-meteo.com/v1/forecast
```

Parameters include:

* temperature
* humidity
* wind
* visibility
* pressure

### 3. Sunrise & Sunset

Using Astral:

```python
SunTimes().get(city, lat, lon)
```

---

## 📸 Screenshots (Replace with your actual images)

> Add UI screenshots here once your design is complete.

---

## 🙌 Credits

* **Open-Meteo** — Free weather & geocoding APIs
* **Astral** — Sun & moon calculations
* **Streamlit** — Web framework for data apps

---



