import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

RIOT_API_KEY = "RGAPI-9620a85d-270a-409f-9b4a-26d9ad817073" # 24시간마다 갱신 필요

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    riot_id_full = request.args.get('riot_id')
    if not riot_id_full or '#' not in riot_id_full:
        return "Riot ID를 '닉네임#태그' 형식으로 입력해주세요.", 400

    # Riot ID를 게임 이름과 태그로 분리
    game_name, tag_line = riot_id_full.split('#')
    
    # --- 1단계: Riot ID로 PUUID 조회하기 ---
    # ACCOUNT-V1 API는 아시아(asia) 서버를 통해 조회합니다.
    account_url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    account_response = requests.get(account_url, headers=headers)
    
    if account_response.status_code != 200:
        return f"Riot ID를 찾을 수 없습니다. (에러 코드: {account_response.status_code})", account_response.status_code
        
    puuid = account_response.json()['puuid']
    
    # --- 2단계: PUUID로 소환사 정보 조회하기 ---
    # SUMMONER-V4 API는 각 지역 서버(kr)에 요청해야 합니다.
    summoner_url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    
    summoner_response = requests.get(summoner_url, headers=headers)
    
    if summoner_response.status_code == 200:
        summoner_data = summoner_response.json()
        
        # DDragon 버전 정보 가져오기 (이전과 동일)
        ddragon_versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions_response = requests.get(ddragon_versions_url)
        latest_version = versions_response.json()[0]

        # 템플릿에 데이터 전달
        return render_template('summoner.html', 
                               summoner=summoner_data, 
                               version=latest_version)
    else:
        return f"소환사 정보를 가져오는 데 실패했습니다. (에러 코드: {summoner_response.status_code})", summoner_response.status_code

if __name__ == '__main__':
    app.run(debug=True)