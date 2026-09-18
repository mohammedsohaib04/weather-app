from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
  0: ("Clear sky","☀️"),1:("Mainly clear","🌤️"),2:("Partly cloudy","⛅"),3:("Overcast","☁️"),
  45:("Fog","🌫️"),48:("Rime fog","🌫️"),51:("Light drizzle","🌦️"),53:("Drizzle","🌦️"),55:("Heavy drizzle","🌧️"),
  61:("Light rain","🌦️"),63:("Rain","🌧️"),65:("Heavy rain","🌧️"),71:("Light snow","🌨️"),73:("Snow","❄️"),
  75:("Heavy snow","❄️"),80:("Rain showers","🌦️"),81:("Rain showers","🌧️"),82:("Heavy showers","⛈️"),
  95:("Thunderstorm","⛈️"),96:("Thunderstorm + hail","⛈️"),99:("Thunderstorm + hail","⛈️")
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/weather")
def weather():
    city = request.args.get("city","").strip()
    if not city:
        return jsonify({"error":"Please enter a city name."}), 400
    try:
        geo = requests.get(GEOCODING_URL, params={"name":city,"count":1,"language":"en","format":"json"}, timeout=10)
        geo.raise_for_status()
        locations = geo.json().get("results",[])
        if not locations:
            return jsonify({"error":f"Could not find '{city}'."}), 404
        loc = locations[0]
        data = requests.get(WEATHER_URL, params={
          "latitude":loc["latitude"],"longitude":loc["longitude"],
          "current":"temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
          "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
          "timezone":"auto","forecast_days":5
        }, timeout=10)
        data.raise_for_status()
        w = data.json()
        cur = w["current"]
        desc, icon = WEATHER_CODES.get(cur["weather_code"],("Unknown","🌡️"))
        forecast=[]
        for i,date in enumerate(w["daily"]["time"]):
            fd,fi=WEATHER_CODES.get(w["daily"]["weather_code"][i],("Unknown","🌡️"))
            forecast.append({"date":date,"description":fd,"icon":fi,"max":round(w["daily"]["temperature_2m_max"][i]),"min":round(w["daily"]["temperature_2m_min"][i]),"rain":w["daily"]["precipitation_probability_max"][i]})
        return jsonify({
          "location":f'{loc["name"]}, {loc.get("country","")}',
          "current":{"temperature":round(cur["temperature_2m"]),"feels_like":round(cur["apparent_temperature"]),"humidity":cur["relative_humidity_2m"],"wind":round(cur["wind_speed_10m"]),"description":desc,"icon":icon},
          "forecast":forecast,"updated":cur["time"]
        })
    except requests.RequestException:
        return jsonify({"error":"Weather service is temporarily unavailable. Please try again."}),502

if __name__=="__main__":
    app.run(debug=True)
