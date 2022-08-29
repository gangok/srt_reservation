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
        login_id = str(config['login_id'])
        login_psw = str(config['login_psw'])
        dpt_stn = config['dpt_stn']
        arr_stn = config['arr_stn']
        dpt_dt = str(config['dpt_dt'])
        dpt_tm = str(config['dpt_tm'])
        num_passenger = str(config['num_passenger'])

        num_trains_to_check = int(config['num_trains_to_check'])
        want_reserve = bool(config['want_reserve'])
        notify_sound_file_path = config['notify_sound_file_path']

        telegram_token = config['telegram_token']
        telegram_chat_id = config['telegram_chat_id']
        if telegram_token and telegram_chat_id:
            telegram_client = TelegramClient(telegram_token, telegram_chat_id)
        else:
            telegram_client = None
    else:
        login_id = cli_args.user
        login_psw = cli_args.psw
        dpt_stn = cli_args.dpt
        arr_stn = cli_args.arr
        dpt_dt = cli_args.dt
        dpt_tm = cli_args.tm

        num_trains_to_check = cli_args.num
        want_reserve = cli_args.reserve
        notify_sound_file_path = os.path.join(os.path.dirname(__file__), 'mp3', '예약이준비되었습니다_papago.mp3')

    srt = SRT(dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check, want_reserve, notify_sound_file_path, telegram_client, num_passenger)
    srt.run(login_id, login_psw)
