# database.py
import mysql.connector
from mysql.connector import Error

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
                formatted_date = balance_date.strftime('%d-%m-%Y')
                # Format balance as string with 2 decimal places
                formatted_balance = f"{float(balance_amount):.2f}"
                return ([formatted_date, formatted_balance])
    return None