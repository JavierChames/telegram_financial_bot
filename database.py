# database.py
import mysql.connector
from mysql.connector import Error
import logging

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.DEBUG
# )

from config import DB_CONFIG  # Import the DB configuration from config.py


def get_balance(account_id):
    """
    Connects to the MySQL database and retrieves the balance for a given account_id.
    Assumes that you have a table (e.g., 'accounts') with columns 'account_id' and 'balance'.
    """
    cnx = None
    cursor = None
    try:
        # Establish connection using the configuration details.
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        query = "SELECT date,balance FROM balance WHERE accountNumberid = %s"
        cursor.execute(query, (account_id,))
        result = cursor.fetchone()
    except Error as err:
        print("Database error: {}".format(err))
        result = None
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

    # Return the balance if found; otherwise, return None.
    if result:
        balance_date, balance_amount = result
        # Format date as string (YYYY-MM-DD)
        formatted_date = balance_date.strftime("%d-%m-%Y")
        # Format balance as string with 2 decimal places
        formatted_balance = f"{float(balance_amount):.2f}"
        return [formatted_date, formatted_balance]
    return None


def get_card_usage_current_month(account_id):
    """
    Connects to the MySQL database and retrieves the balance for a given account_id.
    Assumes that you have a table (e.g., 'accounts') with columns 'account_id' and 'balance'.
    """
    cnx = None
    cursor = None
    try:
        # Establish connection using the configuration details.
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        query = """select cards.card_number,cards_des.description,abs(sum(cards.charged_amount)) from cards_transactions cards
                join cards cards_des on cards_des.card4digits=cards.card_number
  AND YEAR(date) = YEAR(CURRENT_DATE())
  AND MONTH(date) = MONTH(CURRENT_DATE())
  AND (note != 'credit' OR note IS NULL)
        and cards.account = %s

  group by card_number"""
        cursor.execute(query, (account_id,))
        result = cursor.fetchall()
    except Error as err:
        print("Database error: {}".format(err))
        result = None
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

    # Return the balance if found; otherwise, return None.
    if result:
        new_data = []
        for entry in result:
            card_id, card_name, amount = entry
            # Convert the Decimal to a string
            amount_str = str(amount)
            new_data.append((card_id, card_name, amount_str))
        return new_data
    return None
