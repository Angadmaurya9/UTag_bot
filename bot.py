import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ChatMemberHandler
)
from dotenv import load_dotenv
from db import add_or_update_user, get_recent_users, clean_old_users

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
admin_ids = set()

async def is_admin(update: Update, user_id: int) -> bool:
    if update.effective_chat.type == "private":
        return False
    try:
        chat_admins = await update.effective_chat.get_administrators()
        return any(admin.user.id == user_id for admin in chat_admins)
    except Exception as e:
        print(f"Error in is_admin(): {e}")
        return False

async def update_admin_list(update: Update):
    global admin_ids
    try:
        chat_admins = await update.effective_chat.get_administrators()
        admin_ids = {admin.user.id for admin in chat_admins}
    except Exception as e:
        print(f"Error in update_admin_list(): {e}")
        admin_ids = set()

async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        user = update.effective_user
        added = add_or_update_user(user.id, user.first_name)
        if added:
            print(f"Tracking: {user.first_name} ({user.id})")

async def mention_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ This command only works in groups.")
        return

    chat = update.effective_chat
    bot_member = await chat.get_member(context.bot.id)

    if bot_member.status != "administrator" or not bot_member.can_manage_chat:
        await update.message.reply_text("🔒 Please promote me to admin, sir 🙏")
        return

    await update_admin_list(update)
    if not admin_ids:
        await update.message.reply_text("⚠️ No admins found.")
        return

    mentions = [f"[Admin {i+1}](tg://user?id={uid})" for i, uid in enumerate(admin_ids)]
    await update.message.reply_text(
        f"📢 Calling admins:
{' '.join(mentions)}",
        parse_mode='Markdown'
    )

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ This command only works in groups.")
        return

    user_id = update.effective_user.id
    if not await is_admin(update, user_id):
        await update.message.reply_text("❌ Only admins can use @all or /all.")
        return

    clean_old_users(days=15)
    users = get_recent_users(days=15)
    if not users:
        await update.message.reply_text("⚠️ No active users in the last 15 days.")
        return

    extra_message = ' '.join(context.args) if context.args else ''
    mentions = [f"[User {i+1}](tg://user?id={uid})" for i, (uid, _) in enumerate(users)]

    await update.message.reply_text(
        f"{extra_message}

📣 {' '.join(mentions)}",
        parse_mode='Markdown'
    )

async def private_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to a Group", url="https://t.me/learn_mention_bot?startgroup=true")]
    ])
    text = (
        "👋 Hello! I'm your MentionBot.\n\n"
        "📌 Use me in groups to:\n"
        "• `/admin` or `@admin` → Tag all admins\n"
        "• `/all` or `@all` → Admins tag all active users\n\n"
        "✅ I only mention users who have sent a message in the group."
    )
    await update.message.reply_text(text, reply_markup=keyboard)

async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_status = update.my_chat_member.new_chat_member.status
    chat = update.effective_chat
    if new_status == 'member':
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                "👋 Thank you for adding me!\n\n"
                "Here’s what I can do:\n"
                "• `/admin` or `@admin` → Tag all admins\n"
                "• `/all` or `@all` → Admins tag all active users\n\n"
                "Make me admin to use all features!"
            )
        )
    elif new_status == 'administrator':
        await context.bot.send_message(
            chat_id=chat.id,
            text="🛡 Thanks for making me admin! I'm fully functional now 😎"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("admin", mention_admins))
app.add_handler(CommandHandler("all", mention_all))
app.add_handler(CommandHandler("start", private_start))
app.add_handler(MessageHandler(filters.Regex(r'@admin'), mention_admins))
app.add_handler(MessageHandler(filters.Regex(r'@all'), mention_all))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_users))
app.add_handler(ChatMemberHandler(bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
print("🚀 MentionBot is now running...")
app.run_polling()
