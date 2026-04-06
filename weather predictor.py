import requests
from datetime import datetime

# Lakewood, Ohio coordinates
LAT = 41.4820
LON = -81.7982

def get_weather_data():
    # Step 1: Get NOAA grid info
    points_url = f"https://api.weather.gov/points/{LAT},{LON}"
    points = requests.get(points_url, headers={"User-Agent": "SnowDayPredictor"}).json()

    forecast_url = points["properties"]["forecastHourly"]
    forecast = requests.get(forecast_url, headers={"User-Agent": "SnowDayPredictor"}).json()

    return forecast["properties"]["periods"]


def analyze_weather(periods):
    snow_inches = 0
    ice_inches = 0
    coldest_temp = 100
    max_wind = 0
    overnight_snow = False
    snow_during_commute = False

    for p in periods[:12]:  # next 12 hours
        temp = p["temperature"]
        wind = int(p["windSpeed"].split()[0])
        forecast = p["shortForecast"].lower()
        hour = datetime.fromisoformat(p["startTime"]).hour

        coldest_temp = min(coldest_temp, temp)
        max_wind = max(max_wind, wind)

        if "snow" in forecast:
            snow_inches += 0.75  # NOAA doesn't give inches → estimate
            if hour <= 6:
                overnight_snow = True
            if 6 <= hour <= 9:
                snow_during_commute = True

        if "ice" in forecast or "freezing rain" in forecast:
            ice_inches += 0.1

    return {
        "snow": snow_inches,
        "ice": ice_inches,
        "temp": coldest_temp,
        "wind": max_wind,
        "overnight": overnight_snow,
        "commute": snow_during_commute
    }


def snow_day_algorithm(weather, principal_mood):
    score = 0

    # Snow
    score += min(weather["snow"] * 8, 40)

    # Ice
    score += min(weather["ice"] * 100, 40)

    # Temperature
    if weather["temp"] <= 10:
        score += 20
    elif weather["temp"] <= 20:
        score += 10
    elif weather["temp"] <= 32:
        score += 5

    # Wind
    if weather["wind"] >= 25:
        score += 10
    elif weather["wind"] >= 15:
        score += 5

    # Timing
    if weather["overnight"]:
        score += 10
    if weather["commute"]:
        score += 20

    # Principal mood
    score += principal_mood * 10

    # Lakewood / Ohio toughness
    score -= 15

    score = max(0, min(score, 100))

    if score >= 70:
        decision = "SNOW DAY VERY LIKELY ❄️"
    elif score >= 50:
        decision = "POSSIBLE SNOW DAY 🤔"
    elif score >= 30:
        decision = "UNLIKELY 😕"
    else:
        decision = "NO SNOW DAY 🏫"

    return score, decision


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Principal mood scale:")
    print("-2 = very strict | 0 = neutral | +2 = very chill")
    principal_mood = int(input("Enter principal mood (-2 to 2): "))

    periods = get_weather_data()
    weather = analyze_weather(periods)

    probability, result = snow_day_algorithm(weather, principal_mood)

    print("\n--- Snow Day Report (St. Edward, Lakewood OH) ---")
    print(f"Estimated Snow: {weather['snow']:.1f} in")
    print(f"Ice Risk: {weather['ice']:.2f} in")
    print(f"Coldest Temp: {weather['temp']}°F")
    print(f"Max Wind: {weather['wind']} mph")
    print(f"Snow During Commute: {weather['commute']}")
    print(f"Overnight Snow: {weather['overnight']}")
    print(f"\nSnow Day Probability: {probability}%")
    print(f"Prediction: {result}")
