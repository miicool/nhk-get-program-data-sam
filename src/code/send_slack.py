import json

# import ssl
from slack_sdk.web import WebClient

# ssl._create_default_https_context = ssl._create_unverified_context


def send_slack_app(contents, slack_bot_token, channel_id):
    client = WebClient(token=slack_bot_token)
    if len(contents) > 0:
        # slack block 用のリストを初期化
        program_count = str(len(contents))
        block_list = create_block_list_basic_header(program_count)
        # 番組データごとに slack block payload用の辞書を生成してリストに追加
        for program in contents:
            single_program_section = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*『{program.program_title}』* \n:tv:{program.service_name} \n:sunrise:{program.start_time} :night_with_stars:{program.end_time} \n```{program.program_content}```",
                },
            }
            block_list.append(single_program_section)

        # 最終行にdividerを追加
        block_list.append({"type": "divider"})
        # print(block_list)
    else:
        # slack block 用のリスト
        block_list = create_no_program_item_block_list()

    # 送信処理
    response = client.chat_postMessage(
        text="NHK Program List Notify",
        blocks=block_list,
        channel=channel_id,
    )
    # print(json.dumps(response.data))


def create_block_list_basic_header(program_count):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*今日の番組表です。{program_count}件の番組が該当しました。*",
            },
        },
        {
            "type": "divider",
        },
    ]


def create_no_program_item_block_list():
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*今日は該当する番組はありませんでした。*",
            },
        },
        {
            "type": "divider",
        },
    ]
