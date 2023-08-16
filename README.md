# nhk-get-program-data-sam

## 単体実行
```
sam build

sam local invoke --profile default
```

## デプロイ
```
sam deploy
```

## 実行パラメータ
- Systems Manager Parameter Storeに格納
- `slack API token`、`NHK API token`はそれぞれ個別にSecurestringで格納
- その他の実行パラメータは、下記json Stringの形で単一のStoreに格納

```
{
    "tv_service_codes": [
        "g1",
        "e1",
        "s1",
        "s3"
    ],
    "genre_codes": [
        "0005",
        "0202",
        "0205",
        "0502",
        "0505",
        "0800",
        "0801",
        "0802",
        "0804",
        "0807",
        "1000",
        "1002"
    ],
    "exclude_time_period": {
        "business_day": [
            "00:00-19:30",
            "23:00-23:59"
        ],
        "holiday": [
            "01:00-11:00"
        ]
    },
    "slack_channel_ids": {
		"g1": "xxxxxxxxxxx",
		"e1": "xxxxxxxxxxx",
		"s1": "xxxxxxxxxxx",
		"s3": "xxxxxxxxxxx"
	}
}
```

# unitttest実行
```
python -m unittest
```