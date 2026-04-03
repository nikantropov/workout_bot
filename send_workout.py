#!/usr/bin/env python3
"""
Telegram Workout Bot - Отправка программы тренировок
Вторник: Грудь + Бицепс
Четверг: Спина + Трицепс
Суббота: Ноги + Плечи (приоритетный день)

Система прогрессии: +2.5 кг каждые 2 недели
"""

import urllib.request
import json
from datetime import datetime, timedelta

# Конфигурация
BOT_TOKEN = "8280175118:AAGs7RDHMDKNtjgcT9f-aCsEiwGvBmIeUJk"
CHAT_ID = "1214258573"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Дата старта программы
PROGRAM_START_DATE = datetime(2025, 4, 8)

# Базовые веса (кг) - стартовая точка для ВТОРНИКА и СУББОТЫ
BASE_WEIGHTS = {
    # ВТОРНИК - ГРУДЬ + БИЦЕПС
    "tuesday": {
        "Жим штанги лёжа": 60,
        "Жим гантелей наклон": 20,
        "Разводка гантелями": 12,
        "Брусья": 20,
        "Подъём штанги": 25,
        "Молотки": 10,
    },
    # СУББОТА - НОГИ + ПЛЕЧИ
    "saturday": {
        "Присед": 70,
        "Жим ногами": 100,
        "Сгибание ног": 35,
        "Разгибание ног": 40,
        "Икры": 50,
        "Жим гантелей": 12,
        "Разведения в стороны": 8,
        "Задняя дельта": 10,
        "Face Pull": 20,
    }
}

# ЧЕТВЕРГ - рабочие веса (max) - без прогрессии
THURSDAY_WORKOUT = [
    ("🏋️ ОСНОВНЫЕ УПРАЖНЕНИЯ:", True, [
        ("Тяга верхнего блока", 35, "Широкий хват"),
        ("Тяга горизонтального блока", 40, "К верху живота"),
        ("Тяга узким хватом", 40, "Акцент на ширину"),
        ("Гиперэкстензии", 15, "С доп. весом"),
    ]),
    ("💪 ТРИЦЕПС:", True, [
        ("Жим узким хватом", 30, "Штанга"),
        ("Канат", 30, "Разводка вниз"),
        ("Французский жим", 7, "Гантель"),
    ]),
    ("❤️ КАРДИО ИНТЕРВАЛЫ: 16 мин", False, [
        ("Интервалы", 16, "1 мин 12км / 2 мин 6км"),
    ]),
]

# YouTube Shorts ссылки
EXERCISE_VIDEOS = {
    "Жим штанги лёжа": {"url": "https://www.youtube.com/shorts/Nc8EfHYnurY", "tip": "Сведи лопатки, ноги в упоре"},
    "Жим гантелей наклон": {"url": "https://www.youtube.com/shorts/PTzUJkPrrDw", "tip": "Угол наклона 30-45°"},
    "Разводка гантелями": {"url": "https://www.youtube.com/shorts/YR8J987tK8M", "tip": "Лёгкий изгиб в локтях"},
    "Брусья": {"url": "https://www.youtube.com/shorts/2z8JmcrW-As", "tip": "Наклон корпуса вперёд"},
    "Подъём штанги": {"url": "https://www.youtube.com/shorts/54x2WF1_Suc", "tip": "Локти назад"},
    "Молотки": {"url": "https://www.youtube.com/shorts/Ej1oJ1r5qR4", "tip": "Параллельный хват"},
    "Тяга верхнего блока": {"url": "https://www.youtube.com/shorts/hnSqbBk15tw", "tip": "Тяни к груди"},
    "Тяга горизонтального блока": {"url": "https://www.youtube.com/shorts/qD1WZ5pSuvk", "tip": "Корпус чуть назад"},
    "Тяга узким хватом": {"url": "https://www.youtube.com/shorts/0rzMziYkK7k", "tip": "Широкий хват"},
    "Гиперэкстензии": {"url": "https://www.youtube.com/shorts/R8y16opVx9c", "tip": "Прямая спина"},
    "Жим узким хватом": {"url": "https://www.youtube.com/shorts/OLePvpxQEGk", "tip": "Локти прижаты"},
    "Канат": {"url": "https://www.youtube.com/shorts/aHfbuBf1TJk", "tip": "Разводи вниз и в стороны"},
    "Французский жим гантель": {"url": "https://www.youtube.com/shorts/v2fMq8RjNBw", "tip": "Локти смотрят вверх"},
    "Присед": {"url": "https://www.youtube.com/shorts/Ak1iHbEeeY8", "tip": "Колени по стопам"},
    "Жим ногами": {"url": "https://www.youtube.com/shorts/EotSw18oR9w", "tip": "Не выпрямляй ноги"},
    "Сгибание ног": {"url": "https://www.youtube.com/shorts/WKFzO6U6lE4", "tip": "Полностью сгибай"},
    "Разгибание ног": {"url": "https://www.youtube.com/shorts/Tae3aeJe5Ks", "tip": "Задержи наверху 1 сек"},
    "Икры": {"url": "https://www.youtube.com/shorts/hG0n41Svdf0", "tip": "Полный диапазон"},
    "Жим гантелей": {"url": "https://www.youtube.com/shorts/OLePvpxQEGk", "tip": "Локти в линию"},
    "Разведения в стороны": {"url": "https://www.youtube.com/shorts/Myim1WH6Qec", "tip": "Мизинец выше"},
    "Задняя дельта": {"url": "https://www.youtube.com/shorts/LsT-bR_zxLo", "tip": "Сведи лопатки"},
    "Face Pull": {"url": "https://www.youtube.com/shorts/qEyoBOpvqR4", "tip": "Тяни к лицу"},
}


def get_current_week():
    days_since_start = (datetime.now() - PROGRAM_START_DATE).days
    return max(1, (days_since_start // 14) + 1)


def get_progression_indicator(week):
    if week <= 1:
        return "", False
    progress_kg = (week - 1) * 2.5
    return f"+{progress_kg:.1f} кг с начала программы", True


def calculate_weights(day_key, week):
    base = BASE_WEIGHTS[day_key]
    progression = (week - 1) * 2.5
    return {exercise: weight + progression for exercise, weight in base.items()}


def get_workout_data():
    weekday = datetime.now().weekday()
    week = get_current_week()
    is_progression, progression_text = get_progression_indicator(week)

    workouts = {
        1: ("tuesday", "📅 ВТОРНИК", "💪 ГРУДЬ + БИЦЕПС + КАРДИО"),
        3: ("thursday", "📅 ЧЕТВЕРГ", "💪 СПИНА + ТРИЦЕПС + ИНТЕРВАЛЫ"),
        5: ("saturday", "📅 СУББОТА", "💪 НОГИ + ПЛЕЧИ + КАРДИО"),
    }

    if weekday not in workouts:
        return None

    day_key, day_name, title = workouts[weekday]
    weights = calculate_weights(day_key, week)

    exercises = {
        "tuesday": [
            ("🏋️ ОСНОВНЫЕ УПРАЖНЕНИЯ:", [
                ("Жим штанги лёжа", "4 × 6-8", "75-80%", True),
                ("Жим гантелей наклон", "3 × 8-10", None, True),
                ("Разводка гантелями", "3 × 10-12", None, False),
                ("Брусья", "3 × 8-12", None, True),
            ]),
            ("💪 БИЦЕПС:", [
                ("Подъём штанги", "3 × 10", None, False),
                ("Молотки", "3 × 12", None, False),
            ]),
            ("❤️ КАРДИО: 20 минут (8-9 км/ч)", None),
        ],
        "thursday": THURSDAY_WORKOUT,
        "saturday": [
            ("🏋️ ОСНОВНЫЕ УПРАЖНЕНИЯ:", [
                ("Присед", "4 × 6-8", "75-80%", True),
                ("Жим ногами", "3 × 10-12", None, True),
                ("Сгибание ног", "4 × 10-12", None, True),
                ("Разгибание ног", "3 × 12-15", None, False),
                ("Икры", "4 × 12-15", None, False),
            ]),
            ("💪 ПЛЕЧИ:", [
                ("Жим гантелей", "3 × 8-10", None, True),
                ("Разведения в стороны", "4 × 12-15", None, False),
                ("Задняя дельта", "3 × 12-15", None, False),
                ("Face Pull", "3 × 12-15", None, False),
            ]),
            ("❤️ КАРДИО: 20-25 минут (наклон 6-8%)", None),
        ],
    }

    return {
        "day_name": day_name, "title": title, "exercises": exercises[day_key],
        "weights": weights, "week": week, "progression_text": progression_text,
        "is_increased": is_progression
    }


def format_workout_message(workout_data):
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(workout_data["day_name"])
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(workout_data["title"])

    if workout_data["is_increased"]:
        lines.append("")
        lines.append(f"🔼 <b>ВНИМАНИЕ! ВЕСА УВЕЛИЧЕНЫ!</b>")
        lines.append(f"📈 Неделя {workout_data['week']} ({workout_data['progression_text']})")

    lines.append("")
    lines.append("🎥 Нажми на упражнение для видео")
    lines.append("")

    for item in workout_data["exercises"]:
        if len(item) == 3:
            lines.append(item[0])
            lines.append("")
            for ex_data in item[2]:
                ex_name, weight, tip = ex_data
                lines.append(f"  <b>{ex_name}</b>: <b>{weight} кг</b> (max)")
            lines.append("")
        elif len(item) == 2:
            lines.append(item[0])
            if item[1]:
                lines.append("")
                for ex_data in item[1]:
                    ex_name, sets, intensity, is_main = ex_data
                    weight = workout_data["weights"].get(ex_name, 0)
                    weight_str = f"<b>{weight:.1f} кг</b>"
                    indicator = "⚡" if is_main else ""
                    intensity_str = f" ({intensity})" if intensity else ""
                    lines.append(f"  {indicator}<b>{ex_name}</b>: {sets} @ {weight_str}{intensity_str}")
                lines.append("")
        else:
            lines.append(item[0])

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("⏱️ <b>ОТДЫХ МЕЖДУ ПОДХОДАМИ:</b>")
    lines.append("• База: 90-120 сек")
    lines.append("• Средние: 60-90 сек")
    lines.append("• Изоляция: 45-60 сек")
    lines.append("")
    lines.append("💡 Оставляй 1-2 повтора в запасе (RIR 1-2)")
    lines.append("")
    lines.append("🏆 <b>ПРОГРЕССИЯ:</b> +2.5 кг каждые 2 недели")
    lines.append("━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def create_inline_keyboard(workout_data):
    keyboard = []
    for item in workout_data["exercises"]:
        if len(item) == 3:
            exercises_list = item[2]
        else:
            exercises_list = item[1] if item[1] else []

        if exercises_list:
            for ex_data in exercises_list:
                if len(ex_data) == 3:
                    ex_name = ex_data[0]
                else:
                    ex_name = ex_data[0]

                if ex_name in EXERCISE_VIDEOS:
                    video_info = EXERCISE_VIDEOS[ex_name]
                    keyboard.append([{"text": f"📹 {ex_name}", "url": video_info["url"]}])

    return keyboard


def send_message_with_buttons(text, keyboard):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps({"inline_keyboard": keyboard})
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('ok', False)
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


def send_message(text):
    url = f"{API_URL}/sendMessage"
    data = json.dumps({
        "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('ok', False)
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


def main():
    workout_data = get_workout_data()
    if workout_data:
        message = format_workout_message(workout_data)
        keyboard = create_inline_keyboard(workout_data)

        if keyboard:
            if send_message_with_buttons(message, keyboard):
                print(f"✅ Тренировка отправлена с видео: {workout_data['day_name']}")
                if workout_data['is_increased']:
                    print(f"🔼 Прогрессия: Неделя {workout_data['week']}")
            else:
                print("❌ Ошибка отправки")
        else:
            if send_message(message):
                print(f"✅ Тренировка отправлена: {workout_data['day_name']}")
            else:
                print("❌ Ошибка отправки")
    else:
        print("Сегодня не день тренировки")


if __name__ == "__main__":
    main()
