
import os
import sqlite3
import uuid
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
DB = os.getenv("DB_PATH", "files.db")

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS files (
                code TEXT PRIMARY KEY,
                file_id TEXT,
                file_type TEXT
            )
        """)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        with sqlite3.connect(DB) as con:
            item = con.execute(
                "SELECT file_id, file_type FROM files WHERE code=?",
                (code,)
            ).fetchone()

        if not item:
            await update.message.reply_text("فایل پیدا نشد.")
            return

        file_id, file_type = item
        if file_type == "video":
            await context.bot.send_video(update.effective_chat.id, file_id)
        elif file_type == "audio":
            await context.bot.send_audio(update.effective_chat.id, file_id)
        else:
            await context.bot.send_document(update.effective_chat.id, file_id)
        return

    await update.message.reply_text(
        "به ربات دانلود VibeNoirX خوش آمدید 🖤"
    )

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("دسترسی مجاز نیست.")
        return

    msg = update.message

    if msg.video:
        file_id, file_type = msg.video.file_id, "video"
    elif msg.audio:
        file_id, file_type = msg.audio.file_id, "audio"
    elif msg.document:
        file_id, file_type = msg.document.file_id, "document"
    else:
        return

    code = uuid.uuid4().hex[:10]

    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO files VALUES (?, ?, ?)",
            (code, file_id, file_type)
        )

    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start={code}"

    await msg.reply_text(
        f"فایل ثبت شد 🖤\n\nلینک دانلود:\n{link}"
    )

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.VIDEO | filters.AUDIO | filters.Document.ALL,
            receive_file
        )
    )
    app.run_polling()

if __name__ == "__main__":
    main()
