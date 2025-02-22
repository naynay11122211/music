from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from AnonXMusic.misc import SUDOERS
from AnonXMusic import app

# MongoDB setup
gmute_collection = MongoClient()["mongodb+srv://botmaker9675208:botmaker9675208@cluster0.sc9mq8b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"]["gmute_collection"]

# Function to check if a user is sudo
def is_sudo(user_id: int) -> bool:
    return user_id in SUDO_USERS  # Define SUDO_USERS as a list of allowed sudo users

# Database functions
def add_gmuted_user(user_id: int):
    gmute_collection.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

def remove_gmuted_user(user_id: int):
    gmute_collection.delete_one({"user_id": user_id})

def is_gmuted(user_id: int) -> bool:
    return gmute_collection.find_one({"user_id": user_id}) is not None

# Commands
@app.on_message(filters.command("gmute") & filters.user(SUDO_USERS))
def gmute(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        message.reply_text("❌ Please specify a user ID or reply to a user's message.")
        return
    
    target_user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]
    try:
        target_user_id = int(target_user_id)
    except ValueError:
        message.reply_text("❌ Invalid user ID. Please provide a valid numeric ID.")
        return
    
    add_gmuted_user(target_user_id)
    message.reply_text(f"✅ User `{target_user_id}` has been globally muted.", parse_mode="markdown")

@app.on_message(filters.command("ungmute") & filters.user(SUDO_USERS))
def ungmute(client: Client, message: Message):
    if len(message.command) < 2:
        message.reply_text("❌ Please specify a user ID to unmute.")
        return
    
    try:
        target_user_id = int(message.command[1])
    except ValueError:
        message.reply_text("❌ Invalid user ID. Please provide a valid numeric ID.")
        return
    
    if not is_gmuted(target_user_id):
        message.reply_text(f"ℹ️ User `{target_user_id}` is not globally muted.", parse_mode="markdown")
        return
    
    remove_gmuted_user(target_user_id)
    message.reply_text(f"✅ User `{target_user_id}` has been globally unmuted.", parse_mode="markdown")

@app.on_message(filters.text & filters.group)
def delete_gmuted_messages(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    
    user_id = user.id
    chat_id = message.chat.id
    user_mention = f"[@{user.username}](tg://user?id={user_id})" if user.username else f"[User](tg://user?id={user_id})"
    
    if is_gmuted(user_id):
        try:
            message.delete()
            keyboard = [[InlineKeyboardButton("📩 Contact Support", url="https://t.me/deadlineTechSupport")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            client.send_message(
                chat_id,
                f"🚫 {user_mention}, **you are blacklisted from using this bot.**\n❓ If you believe this is a mistake, contact support.",
                parse_mode="markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Failed to delete message from {user_id}: {e}")
