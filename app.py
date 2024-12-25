from src import Location
from flask import Flask, render_template, request
from api_keys import ACCUWEATHER_API_KEY, YANDEX_API_KEY

def get_return(data):
    return f"Температура °C:  {data['temperature']}\nВлажность %:  {data['humidity']}\nСкорость ветра м/с:  {data['wind_speed']}\nВероятность осадков %:  {data['precipitation_prob']}"

app = Flask(__name__)

point = Location(ACCUWEATHER_API_KEY, YANDEX_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        start_city = request.form.get("start_city")
        end_city = request.form.get("end_city")

        start_weather_comment, start_weather_data = point.get_weather(start_city)
        end_weather_comment, end_weather_data = point.get_weather(end_city)

        result = f"Погода в городе {start_city}:\n\n{get_return(start_weather_data)}\n\nОценка: {start_weather_comment}\n\nПогода в городе {end_city}:\n\n{get_return(end_weather_data)}\n\nОценка: {end_weather_comment}"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)