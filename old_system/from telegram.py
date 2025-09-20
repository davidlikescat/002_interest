from telegram.ext import Updater, MessageHandler, Filters

def get_chat_id(update, context):
    print("✅ Group Chat ID:", update.message.chat.id)
    print("📌 Group Title:", update.message.chat.title)

updater = Updater("7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4", use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_chat_id))

print("🤖 Bot is running... Send a message in the group.")
updater.start_polling()
updater.idle()