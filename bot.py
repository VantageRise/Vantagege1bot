import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import solana.publickey as solana_key

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_URL = "https://t.me/vantagerise7"
GROUP_URL = "https://t.me/vantagerise24"
TWITTER_URL = "https://twitter.com/VantageDecrypt"
FACEBOOK_URL = "https://facebook.com/agboolatunmise"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///airdrop.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    joined_channel = Column(Boolean, default=False)
    joined_group = Column(Boolean, default=False)
    twitter_username = Column(String, default=None)
    facebook_profile = Column(String, default=None)
    sol_wallet = Column(String, default=None)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_msg = (
        "🌟 Welcome to Vantagerise Airdrop Bot! 🌟\n\n"
        "Complete these simple tasks to qualify for our SOL airdrop:\n\n"
        "1. Join our Telegram Channel\n"
        "2. Join our Telegram Group\n"
        "3. Follow us on Twitter\n"
        "4. Like our Facebook Page\n"
        "5. Submit your Solana wallet address\n\n"
        "Click /verify to get started!"
    )
    
    # Save user to DB
    with Session() as session:
        if not session.query(User).filter_by(user_id=user.id).first():
            new_user = User(user_id=user.id, username=user.username)
            session.add(new_user)
            session.commit()
    
    await update.message.reply_text(welcome_msg)

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("Join Channel", url=CHANNEL_URL),
            InlineKeyboardButton("✅ I Joined", callback_data="channel_done")
        ],
        [
            InlineKeyboardButton("Join Group", url=GROUP_URL),
            InlineKeyboardButton("✅ I Joined", callback_data="group_done")
        ],
        [
            InlineKeyboardButton("Follow Twitter", url=TWITTER_URL),
            InlineKeyboardButton("✅ I Followed", callback_data="submit_twitter")
        ],
        [
            InlineKeyboardButton("Like Facebook", url=FACEBOOK_URL),
            InlineKeyboardButton("✅ I Liked", callback_data="submit_facebook")
        ],
        [
            InlineKeyboardButton("Submit SOL Wallet", callback_data="submit_wallet")
        ]
    ]
    
    with Session() as session:
        db_user = session.query(User).filter_by(user_id=user.id).first()
        status = (
            f"📋 Your Verification Status:\n\n"
            f"1. Channel Joined: {'✅' if db_user.joined_channel else '❌'}\n"
            f"2. Group Joined: {'✅' if db_user.joined_group else '❌'}\n"
            f"3. Twitter Followed: {'✅' if db_user.twitter_username else '❌'}\n"
            f"4. Facebook Liked: {'✅' if db_user.facebook_profile else '❌'}\n"
            f"5. Wallet Submitted: {'✅' if db_user.sol_wallet else '❌'}\n\n"
            f"Complete all steps to qualify!"
        )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(status, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    with Session() as session:
        db_user = session.query(User).filter_by(user_id=user.id).first()
        
        if query.data == "channel_done":
            db_user.joined_channel = True
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ Channel join recorded! Well done, hope you didn't cheat the system!"
            )
        
        elif query.data == "group_done":
            db_user.joined_group = True
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ Group join recorded! Well done, hope you didn't cheat the system!"
            )
        
        elif query.data == "submit_twitter":
            await context.bot.send_message(
                chat_id=user.id,
                text="Please send me your Twitter username (without @):"
            )
            context.user_data["awaiting_input"] = "twitter"
        
        elif query.data == "submit_facebook":
            await context.bot.send_message(
                chat_id=user.id,
                text="Please send me your Facebook profile name:"
            )
            context.user_data["awaiting_input"] = "facebook"
        
        elif query.data == "submit_wallet":
            await context.bot.send_message(
                chat_id=user.id,
                text="Please send me your Solana wallet address:"
            )
            context.user_data["awaiting_input"] = "wallet"
        
        session.commit()
        await check_completion(context, user.id)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    task = context.user_data.get("awaiting_input")
    
    if not task:
        return
    
    with Session() as session:
        db_user = session.query(User).filter_by(user_id=user.id).first()
        
        if task == "twitter":
            db_user.twitter_username = text
            await update.message.reply_text(
                f"✅ Twitter handle @{text} saved! Well done, hope you didn't cheat the system!"
            )
        
        elif task == "facebook":
            db_user.facebook_profile = text
            await update.message.reply_text(
                f"✅ Facebook profile '{text}' saved! Well done, hope you didn't cheat the system!"
            )
        
        elif task == "wallet":
            try:
                solana_key.PublicKey(text)
                db_user.sol_wallet = text
                await update.message.reply_text(
                    "🎉 Congratulations, 10 SOL is on its way to your address!"
                )
            except:
                await update.message.reply_text(
                    "❌ Invalid Solana address! Please check and resubmit."
                )
                return
        
        session.commit()
        context.user_data.pop("awaiting_input", None)
        await check_completion(context, user.id)

async def check_completion(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    with Session() as session:
        db_user = session.query(User).filter_by(user_id=user_id).first()
        
        if db_user and all([
            db_user.joined_channel,
            db_user.joined_group,
            db_user.twitter_username,
            db_user.facebook_profile,
            db_user.sol_wallet
        ]) and not db_user.completed:
            db_user.completed = True
            session.commit()
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\n\n"
                     "You've successfully completed all tasks for the Vantagerise airdrop!\n"
                     "100 SOL will be sent to your wallet shortly.\n\n"
                     "Thank you for participating!"
            )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
