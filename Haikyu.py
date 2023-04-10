import os
import json
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

DAYS = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "domingo": 6
}

DAYS_NAMES = {
    0: "Lunes",
    1: "Martes",
    2: "Miercoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sabado",
    6: "Domingo"
}


def extract_date_time(message: str):
    words = message.split()
    date_str, time_str = None, None
    for word in words:
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', word):
            date_str = word

    matches = re.finditer(
        r"(?P<hour>(?:0?[1-9]|1[0-2])):(?P<minute>[0-5][0-9])\s?(?P<meridiem>[AP]M)", message)
    for match in matches:
        time_str = match.group(
            "hour") + ":" + match.group("minute") + " " + match.group("meridiem")

    print(time_str)
    return date_str, time_str


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    date_str, time_str = extract_date_time(msg)

    if date_str and time_str:
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            time = datetime.strptime(time_str, "%I:%M %p")

            game = {
                "date": date.strftime("%d/%m/%Y"),
                "time": time.strftime("%I:%M %p"),
                "participants": []
            }

            if not os.path.exists("games.json"):
                with open("games.json", "w") as f:
                    json.dump([], f)

            with open("games.json", "r+") as f:
                games = json.load(f)
                games.append(game)
                f.seek(0)
                f.truncate()
                json.dump(games, f)

            await update.message.reply_text("All done, are you ready? 😎")
        except Exception as e:
            await update.message.reply_text(
                "Sorry, I couldn't understand your instruction 😅")
    else:
        await update.message.reply_text(
            "Sorry, I couldn't understand your instruction 😅")


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    words = msg.split()

    day_found = None

    for word in words:
        day_found = find_day(word)

    if day_found is None:
        await update.message.reply_text(
            "Sorry, I couldn't understand your instruction 😅")
        return

    name = "@"+update.message.from_user.username
    day = day_found

    if day is None:
        await update.message.reply_text(
            "Sorry, I couldn't understand your instruction 😅")
        return

    if not os.path.exists("games.json"):
        await update.message.reply_text(
            "Sorry, There is a problem 🔥, please blame the guy who did this bot.")
        return

    with open("games.json", "r+") as f:
        games = json.load(f)

        game_found = False
        for game in reversed(games):
            game_date = datetime.strptime(game["date"], "%d/%m/%Y")
            if game_date.weekday() == day:
                if name not in game["participants"]:
                    game["participants"].append(name)
                    game_found = True
                break

        if game_found:
            f.seek(0)
            f.truncate()
            json.dump(games, f)

            day_name = DAYS_NAMES.get(day)
            await update.message.reply_text(
                f"Be ready for {day_name} 😎"
            )
        else:
            await update.message.reply_text(
                "I couldn't find a game for that day 😅"
            )


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    words = msg.split()
    invited_name = words[1]
    day_found = None

    for word in words:
        day_found = find_day(word)

    if day_found is None:
        await update.message.reply_text(
            "Sorry, I couldn't understand your instruction 😅")
        return

    name = invited_name + " Invitado por " + \
        "@" + update.message.from_user.username
    day = day_found

    if day is None:
        await update.message.reply_text(
            "Sorry, I couldn't understand your instruction 😅")
        return

    if not os.path.exists("games.json"):
        await update.message.reply_text(
            "Sorry, There is a problem 🔥, please blame the guy who did this bot.")
        return

    with open("games.json", "r+") as f:
        games = json.load(f)

        game_found = False
        for game in reversed(games):
            game_date = datetime.strptime(game["date"], "%d/%m/%Y")
            if game_date.weekday() == day:
                if name not in game["participants"]:
                    game["participants"].append(name)
                    game_found = True
                break

        if game_found:
            f.seek(0)
            f.truncate()
            json.dump(games, f)

            day_name = DAYS_NAMES.get(day)
            await update.message.reply_text(
                f"Be ready for {day_name} 😎"
            )
        else:
            await update.message.reply_text(
                "I couldn't find a game for that day 😅"
            )


async def remove_participant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    for word in message_text.split():
        day = find_day(message_text)

    if not os.path.exists("games.json"):
        await update.message.reply_text("I couldn't find a game for that day 😅")
        return

    with open("games.json", "r") as file:
        games = json.load(file)

    game_to_update = None
    for game in reversed(games):
        game_date = datetime.strptime(game["date"], "%d/%m/%Y")
        if game_date.weekday() == day:
            game_to_update = game
            break
    else:
        game_to_update = games[-1]

    if game_to_update:
        username = update.message.from_user.username
        player_entry = None
        for participant in game_to_update["participants"]:
            if f"@{username}" in participant and "invitado" not in participant:
                player_entry = participant
                break

        if player_entry:
            game_to_update["participants"].remove(player_entry)

            with open("games.json", "w") as file:
                json.dump(games, file)

            day_name = DAYS_NAMES.get(day)
            await update.message.reply_text(
                f"Sad you won't join us 😢")
        else:
            await update.message.reply_text(
                "I didn't find you on the player list, were you already signed up? 🤔")
    else:
        await update.message.reply_text(
            "I couldn't find a game for that day 😅"
        )


async def remove_invited_participant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    invited_name = message_text.split()[1]
    day = None
    for word in message_text.split():
        day = find_day(word)
        if day is not None:
            break

    if not os.path.exists("games.json"):
        await update.message.reply_text("No hay partidos programados 😅")
        return

    with open("games.json", "r") as file:
        games = json.load(file)

    game_to_update = None
    for game in reversed(games):
        game_date = datetime.strptime(game["date"], "%d/%m/%Y")
        if game_date.weekday() == day:
            game_to_update = game
            break
    else:
        game_to_update = games[-1]

    if game_to_update:
        username = update.message.from_user.username
        removed_entry = None
        for participant in game_to_update["participants"]:
            full_invited_name = f"{invited_name} Invitado por @{username}"
            print(full_invited_name)
            if full_invited_name in participant:
                removed_entry = participant
                game_to_update["participants"].remove(participant)
                break

        if removed_entry:
            with open("games.json", "w") as file:
                json.dump(games, file)

            await update.message.reply_text(
                f"Sad your guess won't join us on 😢")
        else:
            await update.message.reply_text(
                "I couldn't find the guess 🤔")
    else:
        await update.message.reply_text(
            "I couldn't find a game for that day 😅")


async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    day = None
    for word in message_text.split():
        day = find_day(word)
        if day is not None:
            break

    if day is None:
        await update.message.reply_text("I couldn't understand what you said 😅")
        return

    if not os.path.exists("games.json"):
        await update.message.reply_text("I couldn't find a game for that day 😅")
        return

    with open("games.json", "r") as file:
        games = json.load(file)

    game_to_list = None
    for game in reversed(games):
        game_date = datetime.strptime(game["date"], "%d/%m/%Y")
        if game_date.weekday() == day:
            game_to_list = game
            break

    if game_to_list:
        participants = game_to_list["participants"]
        if len(participants) == 0:
            await update.message.reply_text(
                "There are no players for the given day 😢")
        else:
            response = "Jugadores inscritos:\n\n"
            for i, participant in enumerate(participants, start=1):
                response += f"{i}. {participant}\n"
            await update.message.reply_text(response)
    else:
        await update.message.reply_text("I couldn't find a game for that day 😅 😅")


async def cleanup_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("games.json"):
        await update.message.reply_text("I couldn't find a game for that day 😅")
        return

    with open("games.json", "r") as file:
        games = json.load(file)

    current_date = datetime.now()
    updated_games = [game for game in games if datetime.strptime(
        game["date"], "%d/%m/%Y") > current_date]

    with open("games.json", "w") as file:
        json.dump(updated_games, file)

    await update.message.reply_text("All Clean Up! 🧹")


async def cleanup_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("games.json"):
        await update.message.reply_text("I couldn't find a game for that day 😅")
        return

    with open("games.json", "w") as file:
        json.dump([], file)

    await update.message.reply_text("All Clean Up! 🧹")


def spanish_day_to_weekday_index(day: str):
    return DAYS.get(day)


def find_day(day: str):
    day = day.lower().replace("á", "a").replace("é", "e").replace(
        "í", "i").replace("ó", "o").replace("ú", "u")
    return DAYS.get(day)


def main():
    dp = ApplicationBuilder().token(TOKEN).build()

    dp.add_handler(CommandHandler("agendar", schedule))
    dp.add_handler(CommandHandler("confirmo", confirm))
    dp.add_handler(CommandHandler("invitar", invite))
    dp.add_handler(CommandHandler("yanovoy", remove_participant))
    dp.add_handler(CommandHandler("yanova", remove_invited_participant))
    dp.add_handler(CommandHandler("quienesvan", list_participants))
    dp.add_handler(CommandHandler("limpiar", cleanup_games))
    dp.add_handler(CommandHandler("limpiartodo", cleanup_all))

    dp.run_polling()


if __name__ == '__main__':
    main()
