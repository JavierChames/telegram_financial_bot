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
from database import (
    get_balance,
    get_card_usage_current_month,
)  # Import the function from database.py
from config import TELEGRAM_TOKEN


def format_table(data, title):
    # Headers for the table
    headers = ["ID", "Card Name", "Usage"]

    # Build a table by calculating the maximum width for each column.
    # Combine headers with the data rows
    rows = [headers] + [list(map(str, row)) for row in data]
    # Calculate the maximum width for each column.
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]

    # Build the header line.
    header_line = " | ".join(
        f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers))
    )
    # Build a separator line.
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    # Build each data row.
    data_lines = []
    for row in data:
        data_lines.append(
            " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        )

    # Combine everything into a final string.
    table = f"{title}:\n\n{header_line}\n{separator}\n" + "\n".join(data_lines)
    return table


# When sending via Telegram, wrap the table in <pre> tags for fixed-width formatting.
# For example, in an async Telegram bot handler:


async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your bot. How can I help?")


async def echo(update: Update, context):
    """Replies with the same message sent by the user."""
    await update.message.reply_text(update.message.text)


async def help_command(update: Update, context):
    """Handles the /help command."""
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/about - About the bot\n"
        "/balance - Check account balance\n"
        "/credit_card - Check current credit card usage"
    )
    await update.message.reply_text(help_text)


async def about_command(update: Update, context):
    """Handles the /about command."""
    await update.message.reply_text(
        "I am a simple bot created with Python and python-telegram-bot library!"
    )


async def credit_card_command(update: Update, context):
    """Handles the /credit_card command."""
    await update.message.reply_text("This is the credit card command.")


async def balance_command(update: Update, context):
    """Shows a menu to select an account balance."""
    keyboard = [
        [InlineKeyboardButton(PUBLIC + " Account", callback_data="balance_1")],
        [InlineKeyboardButton(PRIVATE + " Account", callback_data="balance_2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select an account to check balance:", reply_markup=reply_markup
    )


async def button_click(update: Update, context):
    """Handles button clicks for account selection."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    chat_id = query.message.chat.id

    # (Optional) Re-display the inline keyboard; catch the error if nothing has changed.
    if query.data.startswith("balance_"):

        keyboard = [
            [InlineKeyboardButton(PUBLIC + " Account", callback_data="balance_1")],
            [InlineKeyboardButton(PRIVATE + " Account", callback_data="balance_2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.message.edit_text(
                "Select an account to check balance:", reply_markup=reply_markup
            )
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
                await context.bot.send_message(
                    chat_id,
                    f"The balance for  {type_of_account} Account is: {balance[1]},Last updated on: {balance[0]}",
                )
            else:
                await context.bot.send_message(
                    chat_id, f"Account {account_id} not found or no balance available."
                )
        else:
            await context.bot.send_message(chat_id, "Invalid account selection.")
    elif query.data.startswith("card_usage_"):
        # Optionally, re-display the inline keyboard for credit card usage.
        keyboard = [
            [InlineKeyboardButton(PUBLIC + " Cards", callback_data="card_usage_1")],
            [InlineKeyboardButton(PRIVATE + " Cards", callback_data="card_usage_2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.message.edit_text(
                "Select a credit card to check current usage:",
                reply_markup=reply_markup,
            )
        except BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            else:
                raise

        # Determine which credit card was selected.
        if query.data == "card_usage_1":
            card_id = 1
        elif query.data == "card_usage_2":
            card_id = 2
        else:
            card_id = None

        if card_id is not None:
            # Retrieve the current month’s card usage from the database.
            card_usage = await asyncio.to_thread(get_card_usage_current_month, card_id)
            if card_usage is not None:
                # Adjust the formatting based on what your function returns.
                type_of_account = PRIVATE if card_id == 2 else PUBLIC
                title = "Credit Card usage for Public account for the current month"

                table_text = format_table(card_usage, title)
                await context.bot.send_message(
                    chat_id,
                    # f"<pre>{table_text}</pre>",
                    f"<code>{table_text}</code>",

                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id, f"Card {card_id} not found or no usage available."
                )
        else:
            await context.bot.send_message(chat_id, "Invalid card selection.")


async def credit_card_command(update: Update, context):
    """Shows a menu to select a credit card for current usage."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Usage for usage for the public account", callback_data="card_usage_1"
            )
        ],
        [
            InlineKeyboardButton(
                "Usage for usage for the private account", callback_data="card_usage_2"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select an account to check credit card current moth usage:",
        reply_markup=reply_markup,
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("credit_card", credit_card_command))

    app.add_handler(CallbackQueryHandler(button_click))  # Handles button clicks

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
