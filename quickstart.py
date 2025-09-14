""" Quickstart script for InstaPy usage """

# imports
import os
from srt_reservation.main import SRT
from srt_reservation.telegram_client import TelegramClient
from srt_reservation.util import parse_cli_args, parse_yaml


if __name__ == "__main__":
    cli_args = parse_cli_args()

    if cli_args.config:
        config = parse_yaml(cli_args.config)
        dpt_stn = config['dpt_stn']
        arr_stn = config['arr_stn']
        dpt_dt = str(config['dpt_dt'])
        dpt_tm = str(config['dpt_tm'])
        num_passenger = str(config['num_passenger'])
        num_children_passenger = str(config['num_children_passenger'])

        num_trains_to_check = int(config['num_trains_to_check'])
        num_trains_to_ignore = int(config['num_trains_to_ignore'])
        want_reserve = bool(config['want_reserve'])

        telegram_token = config['telegram_token']
        telegram_chat_id = config['telegram_chat_id']
        if telegram_token and telegram_chat_id:
            telegram_client = TelegramClient(telegram_token, telegram_chat_id)
        else:
            telegram_client = None
    else:
        dpt_stn = cli_args.dpt
        arr_stn = cli_args.arr
        dpt_dt = cli_args.dt
        dpt_tm = cli_args.tm

        num_trains_to_check = cli_args.num
        num_trains_to_ignore = 0
        want_reserve = cli_args.reserve
        telegram_client = None

    srt = SRT(dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check, num_trains_to_ignore, want_reserve, telegram_client, num_passenger, num_children_passenger)
    srt.run()
