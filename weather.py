import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import time
import nest_asyncio

# библиотеки которые обязательны для работы программы и телеграмм бота

nest_asyncio.apply()

API_KEY = '53e4968511c54b6c8f2122515250105'  # тут находится ключ API от сайта с погодой

# эта функция осуществляет получение прогноза погоды на 3 дня
async def get_week_weather():
    url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q=Novosibirsk&days=3'
    
    try:
        response = await asyncio.to_thread(requests.get, url)
        data = response.json()

        if response.status_code != 200:
            return f"Ошибка: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"

        week_weather = []
        for day in data['forecast']['forecastday']:
            date = day['date']
            day_name = day['day']['condition']['text']
            temp_max = day['day']['maxtemp_c']
            temp_min = day['day']['mintemp_c']

            day_of_week = time.strftime('%A', time.strptime(date, '%Y-%m-%d'))
            formatted_date = f"{int(date.split('-')[2])} {time.strftime('%B', time.strptime(date, '%Y-%m-%d'))} ({day_of_week})"
            
            if 'rain' in day_name.lower():
                weather_icon = "🌧️"
            elif 'cloudy' in day_name.lower():
                weather_icon = "☁️"
            elif 'sun' in day_name.lower():
                weather_icon = "☀️"
            else:
                weather_icon = "🌤️"

            week_weather.append(f"{formatted_date}: {weather_icon} {day_name}, Макс: {temp_max}°C, Мин: {temp_min}°C")

        return "\n".join(week_weather)
    
    except Exception as e:
        return f"Ошибка при получении данных от API. Код ошибки: {e}"
    
    # эта функция позволяет получить почасовой прогноз погоды на сегодняшний день
async def get_today_weather():
    url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q=Novosibirsk&hours=24'
    
    try:
        response = await asyncio.to_thread(requests.get, url) 
        data = response.json()

        if response.status_code != 200:
            return f"Ошибка: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"

        today_weather = []
        for hour in data['forecast']['forecastday'][0]['hour']:
            time_hour = time.strftime('%H:%M', time.strptime(hour['time'], '%Y-%m-%d %H:%M'))
            condition = hour['condition']['text']
            temp = hour['temp_c']
            today_weather.append(f"{time_hour}: {condition}, {temp}°C")

        return "\n".join(today_weather)
    
    except Exception as e:
        return f"Ошибка при получении данных от API. Код ошибки: {e}"

# эта команда /start в боте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я твой бот! 🌞 Используй команду /weather, чтобы увидеть прогноз погоды на 3 дня, или /today, чтобы узнать почасовой прогноз на сегодня.")

# при использовании этой команды бот вышлет вам прогноз погоды на 3 дня
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weather_text = await get_week_weather()
        await update.message.reply_text(f"*Прогноз на 3 дня:*\n\n{weather_text}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении погоды: {e}")
        
        # при использовании этой команды бот вышлет вам почасовой прогноз погоды на сегодняшний день
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today_weather_text = await get_today_weather()
        await update.message.reply_text(f"*Почасовой прогноз на сегодня:*\n\n{today_weather_text}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении почасового прогноза: {e}")

# скрипт для запуска бота
async def main():
    app = ApplicationBuilder().token('7801669044:AAE_F44eIXMf35Uhuznqpsh15ddbfj2n_kY').build() # - здесь находится токен от телеграмм бота

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("today", today))

    await app.run_polling()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()

        if loop.is_running():
            loop.create_task(main())
        else:
            asyncio.run(main())

    except Exception as e:
        print(f"Произошла ошибка: {e}")