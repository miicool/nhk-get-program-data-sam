import pprint
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.request import urlopen
import json
import jpholiday


@dataclass
class NHKTvProgramSingleData:
    id: int
    service_name: str
    program_title: str
    program_subtitle: str
    program_content: str
    program_act: str
    start_time: str
    end_time: str
    genres: list


class NHKTvProgramList:
    def __init__(
        self,
        tv_service_code,
        genre_codes,
        exec_date,
        api_key,
    ):
        self.tv_service_code = tv_service_code
        self.genre_codes = genre_codes
        self.exec_date = exec_date
        self.api_key = api_key

    def get_specific_genre_program_list(self) -> list[NHKTvProgramSingleData]:
        response = NHKTvProgramList.create_dataclass_list(
            self.get_tv_program_by_specific_genre_code(
                self.get_tv_program_data_from_api(self.create_request_url())
            )
        )
        return response

    def get_tv_program_data_from_api(self, request_url) -> list[dict]:
        try:
            raw_json = urlopen(request_url)
        except Exception as e:
            print("[An Exception Has Occurred]: {0}".format(e))
        json_loads = json.loads(raw_json.read())
        tv_program_list = self.get_necessary_item_from_rawdata(json_loads)
        return tv_program_list

    def get_necessary_item_from_rawdata(self, json_loads):
        tv_program_list = []
        # APIのreturnが空でない場合は、番組データをdictに格納する
        if json_loads["list"] is not None:
            data_json = json_loads["list"][self.tv_service_code]
            for raw_data in data_json:
                single_tv_program = {
                    "id": raw_data["id"],
                    "service_name": raw_data["service"]["name"],
                    "program_title": raw_data["title"],
                    "program_subtitle": raw_data["subtitle"],
                    "program_content": raw_data["content"],
                    "program_act": raw_data["act"],
                    "start_time": raw_data["start_time"],
                    "end_time": raw_data["end_time"],
                    "genres": raw_data["genres"],
                }
                tv_program_list.append(single_tv_program)
        else:
            pass
        return tv_program_list

    def create_request_url(self):
        dt_now = self.exec_date
        today = dt_now.strftime("%Y-%m-%d")
        request_url = (
            "https://api.nhk.or.jp/v2/pg/list/140/"
            + self.tv_service_code
            + "/"
            + today
            + ".json?key="
            + self.api_key
        )
        return request_url

    def get_tv_program_by_specific_genre_code(self, tv_program_list):
        return [
            single_tv_program
            for single_tv_program in tv_program_list
            if self.is_target_genre_code(single_tv_program) is True
        ]

    def is_target_genre_code(self, single_tv_program):
        result = []
        for genre_code in self.genre_codes:
            if genre_code in single_tv_program["genres"]:
                result.append(True)
            else:
                result.append(False)
        return any(result)

    @staticmethod
    def create_dataclass_list(data: list[dict]) -> list[NHKTvProgramSingleData]:
        return list(
            NHKTvProgramSingleData(**tv_program_data) for tv_program_data in data
        )


def process_tv_program_data(parameter, TvService) -> list[NHKTvProgramSingleData]:
    exclude_parameter = {}
    if is_business_day(parameter) is True:
        print("process_tv_program_data(): 平日のため、除外時間処理を実施します。")
        exclude_parameter["exclude_time_period"] = parameter["exclude_time_period"][
            "business_day"
        ]
        response = exclude_program_data_by_time(exclude_parameter, TvService)
    elif is_business_day(parameter) is False:
        print("process_tv_program_data(): 土日祝日のため、休日の除外時間処理を実施します。")
        exclude_parameter["exclude_time_period"] = parameter["exclude_time_period"][
            "holiday"
        ]
        response = exclude_program_data_by_time(exclude_parameter, TvService)
    else:
        response = TvService
    pprint.pprint(response)
    return response


def is_business_day(parameter):
    date = parameter["exec_date"]
    # 実行時が平日であればTrueを返す
    return False if date.weekday() >= 5 or jpholiday.is_holiday(date) else True


def exclude_program_data_by_time(parameter, TvService) -> list[NHKTvProgramSingleData]:
    return [
        single_tv_program
        for single_tv_program in TvService
        if is_program_data_in_exclude_time(parameter, single_tv_program) is False
    ]


def is_program_data_in_exclude_time(parameter, single_tv_program):
    check_booleans_list = []
    ymd = re.search(r"\d{4}-\d{2}-\d{2}", single_tv_program.start_time).group()
    for period in parameter["exclude_time_period"]:
        dt_exclude_start_time = create_datetime_object_by_regex(
            period, ymd, "^\d{2}:\d{2}"
        )
        dt_exclude_end_time = create_datetime_object_by_regex(
            period, ymd, "\d{2}:\d{2}$"
        )

        dt_data_start_time = datetime.strptime(
            single_tv_program.start_time, "%Y-%m-%dT%H:%M:%S%z"
        )
        if dt_exclude_start_time <= dt_data_start_time < dt_exclude_end_time:
            check_booleans_list.append(True)
        else:
            check_booleans_list.append(False)
    # 番組の開始時間が1つでも除外時間帯に含まれている場合、Trueを返す
    return any(check_booleans_list)


def create_datetime_object_by_regex(period, ymd, regex_string):
    r = re.search(regex_string, period).group()
    datetime_string = ymd + "T" + r + ":00+09:00"
    datetime_object = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    return datetime_object
