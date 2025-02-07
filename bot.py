import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
PRIVATE = "Private"
PUBLIC = "Public"
from database import get_balance  # Import the function from database.py
from config import TELEGRAM_TOKEN



async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your bot. How can I help?")

async def echo(update: Update, context):
    """Replies with the same message sent by the user."""
    await update.message.reply_text(update.message.text)

async def help_command(update: Update, context):
    """Handles the /help command."""
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show this message\n/about - About the bot\n/balance - Check account balance")

async def about_command(update: Update, context):
    """Handles the /about command."""
    await update.message.reply_text("I am a simple bot created with Python and python-telegram-bot library!")

async def balance_command(update: Update, context):
    """Shows a menu to select an account balance."""
    keyboard = [
        [InlineKeyboardButton(PRIVATE +" Account", callback_data="balance_1")],
        [InlineKeyboardButton(PUBLIC +" Account", callback_data="balance_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select an account to check balance:", reply_markup=reply_markup)

async def button_click(update: Update, context):
    """Handles button clicks for account selection."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    chat_id = query.message.chat.id

    # (Optional) Re-display the inline keyboard; catch the error if nothing has changed.
    keyboard = [
        [InlineKeyboardButton(PRIVATE +" Account", callback_data="balance_1")],
        [InlineKeyboardButton(PUBLIC +" Account", callback_data="balance_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await query.message.edit_text("Select an account to check balance:", reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            pass  # Ignore if the message content is unchanged.
        else:
            raise

    # Determine which account was selected.
    if query.data == "balance_1":
        account_id = 1
    elif query.data == "balance_2":
        account_id = 2
    else:
        account_id = None

    if account_id is not None:
        # Retrieve the balance from the MySQL database in a non-blocking way.
        balance = await asyncio.to_thread(get_balance, account_id)
        if balance is not None:
            type_of_account = PRIVATE if account_id == 1 else PUBLIC
            await context.bot.send_message(chat_id, f"The balance for  {type_of_account} Account is: {balance[1]},Last updated on: {balance[0]}")
        else:
            await context.bot.send_message(chat_id, f"Account {account_id} not found or no balance available.")
    else:
        await context.bot.send_message(chat_id, "Invalid account selection.")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CallbackQueryHandler(button_click))  # Handles button clicks

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()