# -*- coding: utf-8 -*-
import os
import time
from random import randint
from datetime import datetime
from playsound import playsound
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, WebDriverException

from srt_reservation.exceptions import InvalidStationNameError, InvalidDateError, InvalidDateFormatError, InvalidTimeFormatError
from srt_reservation.validation import station_list

# Chromedriver 없을 시 처음에는 자동으로 설치합니다.
chromedriver_path = os.path.join(os.path.dirname(__file__), os.pardir, 'chrome_driver')


class SRT:
    def __init__(self, dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check=2, num_trains_to_ignore=0, want_reserve=False, notify_sound_file_path=None, telegram_client=None, num_passenger=None):
        """
        :param dpt_stn: SRT 출발역
        :param arr_stn: SRT 도착역
        :param dpt_dt: 출발 날짜 YYYYMMDD 형태 ex) 20220115
        :param dpt_tm: 출발 시간 hh 형태, 반드시 짝수 ex) 06, 08, 14, ...
        :param num_trains_to_check: 검색 결과 중 예약 가능 여부 확인할 기차의 수 ex) 2일 경우 상위 2개 확인
        :param num_trains_to_ignore: 검색 결과 중 예약 가능 여부 무시할 기차의 수 ex) 2일 경우 상위 2개 무시
        :param want_reserve: 예약 대기가 가능할 경우 선택 여부
        :param notify_sound_file_path: 예약 완료시 재생할 음원 파일 경로
        :param telegram_client: 예약 완료시 메세지 발송할 telegram client
        :param num_passenger: 성인 예약 인원
        """
        self.login_id = None
        self.login_psw = None

        self.dpt_stn = dpt_stn
        self.arr_stn = arr_stn
        self.dpt_dt = dpt_dt
        self.dpt_tm = dpt_tm
        self.num_passenger = num_passenger

        self.num_trains_to_check = num_trains_to_check
        self.num_trains_to_ignore = num_trains_to_ignore
        self.want_reserve = want_reserve
        self.notify_sound_file_path = notify_sound_file_path
        self.telegram_client = telegram_client
        self.driver = None

        self.is_booked = False  # 예약 완료 되었는지 확인용
        self.cnt_refresh = 0  # 새로고침 회수 기록

        self.check_input()

    def check_input(self):
        if self.dpt_stn not in station_list:
            raise InvalidStationNameError(f"출발역 오류. '{self.dpt_stn}' 은/는 목록에 없습니다.")
        if self.arr_stn not in station_list:
            raise InvalidStationNameError(f"도착역 오류. '{self.arr_stn}' 은/는 목록에 없습니다.")
        if not str(self.dpt_dt).isnumeric():
            raise InvalidDateFormatError("날짜는 숫자로만 이루어져야 합니다.")
        try:
            datetime.strptime(str(self.dpt_dt), '%Y%m%d')
        except ValueError:
            raise InvalidDateError("날짜가 잘못 되었습니다. YYYYMMDD 형식으로 입력해주세요.")

    def set_log_info(self, login_id, login_psw):
        self.login_id = login_id
        self.login_psw = login_psw

    def run_driver(self):
        ChromeDriverManager().install()
        self.driver = webdriver.Chrome()


    def login(self):
        self.driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do')

        self.driver.implicitly_wait(15)
        self.driver.find_element(By.ID, 'srchDvNm01').send_keys(str(self.login_id))
        self.driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(str(self.login_psw))
        self.driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
        self.driver.implicitly_wait(5)
        return self.driver

    def check_login(self):
        menu_text = self.driver.find_element(By.CSS_SELECTOR, "#wrap > div.header.header-e > div.global.clear > div").text
        if "환영합니다" in menu_text:
            return True
        else:
            return False



    def go_search(self):

        # 기차 조회 페이지로 이동
        self.driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
        self.driver.implicitly_wait(5)

        # 출발지 입력
        elm_dpt_stn = self.driver.find_element(By.ID, 'dptRsStnCdNm')
        elm_dpt_stn.clear()
        elm_dpt_stn.send_keys(self.dpt_stn)

        # 도착지 입력
        elm_arr_stn = self.driver.find_element(By.ID, 'arvRsStnCdNm')
        elm_arr_stn.clear()
        elm_arr_stn.send_keys(self.arr_stn)

        # 출발 날짜 입력
        elm_dpt_dt = self.driver.find_element(By.ID, "dptDt")
        self.driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dpt_dt)
        Select(self.driver.find_element(By.ID, "dptDt")).select_by_value(self.dpt_dt)

        # 출발 시간 입력
        elm_dpt_tm = self.driver.find_element(By.ID, "dptTm")
        self.driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dpt_tm)
        Select(self.driver.find_element(By.ID, "dptTm")).select_by_visible_text(self.dpt_tm)

        # 인원 정보 입력
        psg_info = self.driver.find_element(By.NAME, "psgInfoPerPrnb1")
        self.driver.execute_script("arguments[0].setAttribute('style','display: True;')", psg_info)
        Select(self.driver.find_element(By.NAME, "psgInfoPerPrnb1")).select_by_value(self.num_passenger)

        print("기차를 조회합니다")
        print(f"출발역:{self.dpt_stn} , 도착역:{self.arr_stn}\n날짜:{self.dpt_dt}, 시간: {self.dpt_tm}시 이후\n{self.num_trains_to_ignore} ~ {self.num_trains_to_check}개의 기차 중 예약")
        print(f"예약 대기 사용: {self.want_reserve}")

        # 조회하기 버튼 클릭
        self.driver.find_element(By.XPATH, "//input[@value='조회하기']").click()
        self.driver.implicitly_wait(5)
        time.sleep(1)

    def after_success(self):
        if self.notify_sound_file_path:
            try:
                playsound(self.notify_sound_file_path)
            except Exception as err:
                print(err)
        if self.telegram_client:
            try:
                self.telegram_client.send_message(f'예약완료!\n출발:{self.dpt_stn}\n도착:{self.arr_stn}\n날짜:{self.dpt_dt}\n시간:대략{self.dpt_tm}')
            except Exception as err:
                print(err)

    def refresh_search_result(self):
        while True:
            for i in range(1 + self.num_trains_to_ignore, self.num_trains_to_check + 1):
                try:
                    standard_seat = self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text
                    reservation = self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(8)").text
                except StaleElementReferenceException:
                    standard_seat = "매진"
                    reservation = "매진"

                if "예약하기" in standard_seat:
                    print("예약 가능 클릭")

                    # Error handling in case that click does not work
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7) > a").click()
                    except ElementClickInterceptedException as err:
                        print(err)
                        self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7) > a").send_keys(Keys.ENTER)
                    finally:
                        self.driver.implicitly_wait(3)

                    # 예약이 성공하면
                    if self.driver.find_elements(By.ID, 'isFalseGotoMain'):
                        is_booked = True
                        print("예약 성공")
                        self.after_success()
                        return self.driver
                    else:
                        print("잔여석 없음. 다시 검색")
                        self.driver.back()  # 뒤로가기
                        self.driver.implicitly_wait(5)

                if self.want_reserve:
                    if "신청하기" in reservation:
                        print("예약 대기 완료")
                        self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(8) > a").click()
                        is_booked = True
                        return self.driver

            if not self.is_booked:
                time.sleep(randint(2, 4))  # 2~4초 랜덤으로 기다리기

                # 다시 조회하기
                submit = self.driver.find_element(By.XPATH, "//input[@value='조회하기']")
                self.driver.execute_script("arguments[0].click();", submit)
                self.cnt_refresh += 1
                print(f"새로고침 {self.cnt_refresh}회")
                self.driver.implicitly_wait(10)
                time.sleep(0.5)
            else:
                return self.driver

    def run(self, login_id, login_psw):
        self.run_driver()
        self.set_log_info(login_id, login_psw)
        self.login()
        self.go_search()
        self.refresh_search_result()


# if __name__ == "__main__":
#     srt_id = os.environ.get('srt_id')
#     srt_psw = os.environ.get('srt_psw')
#
#     srt = SRT("동탄", "동대구", "20220119", "08")
#     srt.run(srt_id, srt_psw)