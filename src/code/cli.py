from importlib.resources import contents
import boto3
import json
from .get_nhk_tv_program_list import NHKTvProgramList, process_tv_program_data
from .send_slack import send_slack_app
from datetime import datetime, timezone, timedelta


def main():
    nhk_api_key, slack_bot_token, raw_parameters = set_execute_parameters()
    print(raw_parameters)
    raw_parameters["api_key"] = nhk_api_key
    raw_parameters["exec_date"] = set_execute_date()

    service_code_list = raw_parameters["tv_service_codes"]
    slack_channel_ids = raw_parameters["slack_channel_ids"]
    channel_parameters = raw_parameters
    for service_code in service_code_list:
        send_slack_app(
            (
                create_custom_tv_program_list(
                    channel_parameters, service_code, slack_channel_ids
                )
            ),
            slack_bot_token,
            raw_parameters["slack_channel_id"],
        )


def set_execute_parameters():
    ssm = boto3.client("ssm")
    nhk_api_key = get_ssm_parameter_value(
        ssm, ssm_parameter_name="nhk_get_programlist_nhkapikey"
    )
    slack_bot_token = get_ssm_parameter_value(
        ssm, ssm_parameter_name="nhk_get_programlist_slackbottoken"
    )
    raw_parameters = json.loads(
        get_ssm_parameter_value(
            ssm, ssm_parameter_name="nhk_get_programlist_execparameter"
        )
    )
    return nhk_api_key, slack_bot_token, raw_parameters


def get_ssm_parameter_value(ssm, ssm_parameter_name) -> str:
    response = ssm.get_parameter(Name=ssm_parameter_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def set_execute_date():
    # 実行対象の日を設定する/通常は実行時
    return datetime.now(timezone(timedelta(hours=+9)))


def create_custom_tv_program_list(channel_parameters, service_code, slack_channel_ids):
    channel_parameters["tv_service_code"] = str(service_code)
    channel_parameters["slack_channel_id"] = slack_channel_ids[service_code]
    TvService = NHKTvProgramList(
        channel_parameters["tv_service_code"],
        channel_parameters["genre_codes"],
        channel_parameters["exec_date"],
        channel_parameters["api_key"],
    )
    # pprint.pprint(TvService)
    custom_tv_program_list = process_tv_program_data(
        channel_parameters, (TvService.get_specific_genre_program_list())
    )
    return custom_tv_program_list
