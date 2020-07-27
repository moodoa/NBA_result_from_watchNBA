# Get NBA statistics from Watch NBA 
![alt text](https://i.imgur.com/iXNVCRo.jpg)

## NBA_BOX.py
#### get_today_games_url
* 以 selenium 進入 watch NBA( https://watch.nba.com/ )，並取得今日賽程URL。
* 回傳值範例如下：`['https://watch.nba.com/game/20200726/PHIOKC', 'https://watch.nba.com/game/20200726/HOUMEM']`。

#### url_to_page_source
* 將 `get_today_games_url` 取得的URL傳入，並取得 `比賽得分`、`主場數據`、`客場數據` 的 page_source。

#### pagesource_to_dataframe
* 嵌入在 `soup_to_json`這支 function，負責將 `主場數據`、`客場數據` 的 page_source 轉換成 dataframe。

#### page_source_to_json
* 將`比賽得分`、`主場數據`、`客場數據`整理成 json 檔後輸出。


## Requirements
python 3

## Usage
`NBA_box.py`

```
1.get URL:

game_today = get_today_games_url()


2:

for url in game_today:
    game_result,home_stat,away_stat = url_to_page_source(url)
    json_output = page_source_to_json(game_result,home_stat,away_stat)


```

## Installation
* `pip install -r requriements.txt`
* 注意 `selenium` 的 driver 是否與 Chrome 版本相符。


