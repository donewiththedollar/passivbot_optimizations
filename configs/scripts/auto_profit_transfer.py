import os
import ta
import ccxt
if "NOJIT" not in os.environ:
    os.environ["NOJIT"] = "true"
import traceback
import argparse
from njit_funcs import round_dynamic
import logging
import logging.config
import pybit
from pybit import usdt_perpetual
from pybit.usdt_perpetual import HTTP
from uuid import uuid4
from config import *
import time

exchange = ccxt.bybit(
    {
        'apiKey':api_key,
        'secret':api_secret
    }
)

ws_perp = usdt_perpetual.WebSocket(
    test=False,
    api_key=api_key,
    api_secret=api_secret,
    domain=domain
)

def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    parser = argparse.ArgumentParser(
        prog="auto profit transfer Bybit",
        description="automatically transfer any funds of the limit from futures wallet to spot wallet, on Bybit",
    )
    parser.add_argument(
         "limit",
         type=float,
         default=150,
         help="the desired amount of funds to be kept in the futures wallet",
     )
    args = parser.parse_args()


    try:
        session = HTTP(
            endpoint="https://api.bybit.com",
            api_key=api_key,
            api_secret=api_secret,
        )
    except:
        logging.error(f"failed to connect with Bybit")
        logging.error(f"{traceback.format_exc()}")
        return

    try:
        usdt_balance = session.get_wallet_balance()['result']['USDT']['wallet_balance']
    except:
        logging.error(f"failed to get USDT balance")
        logging.error(f"{traceback.format_exc()}")
        return

    amount_to_transfer = round_dynamic(usdt_balance - args.limit, 4)

    if amount_to_transfer < 1:
        logging.info(f"No extra funds to transfer. Current USDT balance: {usdt_balance}")
        return

    logging.info(f"Transferring {amount_to_transfer} USDT to spot wallet. Old USDT balance: {usdt_balance},"
                 f" new balance: {usdt_balance - amount_to_transfer}.")

    try:
        session.create_internal_transfer(
            transfer_id=str(uuid4()),
            coin="USDT",
            amount=str(amount_to_transfer),
            from_account_type="CONTRACT",
            to_account_type="SPOT"
        )

        logging.info(f"Transferring was successful. {amount_to_transfer} USDT was transferred to the spot wallet.")
    except:
        logging.error(f"failed to transfer funds")
        logging.error(f"{traceback.format_exc()}")
        return

if __name__ == "__main__":
    #main()

    while True:
        time.sleep(5)
        print("Checking..")
        main()