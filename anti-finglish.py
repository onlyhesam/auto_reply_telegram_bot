import re
import random

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from auth import ACCESS_TOKEN
import settings
import words

def is_finglish(text: str) -> bool:
    text = re.sub("@[^ ]+", "", text.lower())
    text = re.sub(
        r"(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?",
        "",
        text
    )
    text = " ".join(text.split())
    text_english_characters = re.sub("[^a-z]", " ", text)
    text_english_characters = " ".join(text_english_characters.split())
    

    try:
        if len(text_english_characters) / len(text) < 0.6:
            return False
    except ZeroDivisionError:
        return False

    text_all_words = text_english_characters.split()
    legit_english_words = [t for t in text_all_words if t in words.english_words]

    try:
        if len(legit_english_words) / len(text_all_words) < 0.6:
            return True
    except ZeroDivisionError:
        return False

    return False


def reply(update: Update, context: CallbackContext) -> None:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    print(f"Handling message {message.message_id} in {chat.id} from {user.name} ({user.id})")

    if not settings.filter_users or ((user.username in settings.usernames) or (user.id in settings.ids)):
        if is_finglish(message.text):
            reply = random.choice(settings.replies)
            context.bot.sendMessage(chat_id=chat.id, text=reply, reply_to_message_id=message.message_id)
    else:
        print(f"Skipping {message.message_id} in {chat.id} as {user.name} ({user.id}) is not in our list")


def main() -> None:
    updater = Updater(ACCESS_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

    updater.start_polling()

    updater.idle()

    print("Bot started...")

if __name__ == '__main__':
    main()
