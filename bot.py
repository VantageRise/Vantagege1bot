import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from solana.publickey import PublicKey

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_URL = "https://t.me/vantagerise7"
GROUP_URL = "https://t.me/vantagerise24"
TWITTER_URL = "https://twitter.com/VantageDecrypt"
FACEBOOK_URL = "https://facebook.com/agboolatunmise"

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///airdrop.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    sol_wallet = Column(String)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Vantagerise Airdrop Bot 🌟\n\n"
        "Complete these tasks:\n"
        "1. Join our Telegram channels\n"
        "2. Follow our social media\n"
        "3. Submit your SOL wallet\n\n"
        "Click /tasks to begin!"
    )

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("Join Group", url=GROUP_URL)],
        [InlineKeyboardButton("Follow Twitter", url=TWITTER_URL)],
        [InlineKeyboardButton("Like Facebook", url=FACEBOOK_URL)],
        [InlineKeyboardButton("Submit SOL Wallet", callback_data="submit_wallet")]
    ]
    await update.message.reply_text(
        "✅ Complete these tasks:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        PublicKey(update.message.text)  # Validate SOL address
        await update.message.reply_text("🎉 Congratulations, 10 SOL is on its way to your address!")
    except:
        await update.message.reply_text("❌ Invalid SOL address! Try again.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tasks", show_tasks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    application.add_handler(CallbackQueryHandler(lambda u,c: u.answer("Please submit your wallet address via message")))
    
    application.run_polling()

if __name__ == "__main__":
    main()
