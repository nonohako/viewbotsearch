import json
import requests
import datetime as dt
import os
import asyncio
from aiohttp import ClientSession

client_id = '클라이언트아이디'
client_secret = '클라이언트시크릿'

def get_app_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception('Failed to get App Token')

app_token = get_app_token(client_id, client_secret)
headers = {"Client-Id": client_id, "Authorization": "Bearer " + app_token}

t = bot = k = b = 0
follow = []
viewbot = []
botlist = []
search = input('스트리머 ID 입력 : ')
print()

x = dt.datetime.now()
chatters = requests.get(f'https://tmi.twitch.tv/group/user/{search}/chatters')  # 로그인 목록
chatters_data = chatters.json()['chatters']['broadcaster'] + chatters.json()['chatters']['vips'] + chatters.json()['chatters']['moderators'] + chatters.json()['chatters']['staff'] + chatters.json()['chatters']['admins'] + chatters.json()['chatters']['global_mods'] + chatters.json()['chatters']['viewers']
host = requests.get(f'https://api.twitch.tv/helix/streams?user_login={search}', headers=headers)

if host.json()['data'] == []:
    req = requests.get(f'https://api.twitch.tv/helix/users?login={search}', headers=headers)
    host_id = req.json()['data'][0]['id']
else:
    host_id = host.json()['data'][0]['user_id']

req = requests.get('https://api.twitchinsights.net/v1/bots/all')

for i in req.json()['bots']:
    botlist.append(i[0])


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def fetch_all(urls, loop):
    async with ClientSession() as session:
        results = await asyncio.gather(
            *[fetch(session, url, headers) for url in urls],
            return_exceptions=True
        )
        return results


async def main(chatters_data):
    global t, bot, k, b, viewbot

    user_info_urls = [f'https://api.twitch.tv/helix/users?login={i}' for i in chatters_data]
    user_info_responses = await fetch_all(user_info_urls, asyncio.get_event_loop())
    user_info_data = [json.loads(response) for response in user_info_responses if json.loads(response) != {'data': []}]

    for req_data in user_info_data:
        k_count = k2_count = e_count = 0
        lst = []

        if req_data['data'][0]['login'] in botlist:
            bot += 1
        else:
            display_name = req_data['data'][0]['display_name']
            for c in display_name:  # 한국어 체크
                if ord('가') <= ord(c) <= ord('힣'):
                    k_count += 1
            if k_count >= 1:  # 한국어 카운터
                k += 1
            else:
                id = req_data['data'][0]['id']  # id 반환
                follow_req_url = f'https://api.twitch.tv/helix/users/follows?from_id={id}&frist=100'

                async with ClientSession() as session:
                    follow_req_response = await fetch(session, follow_req_url, headers)

                follow_req_data = json.loads(follow_req_response)

                if follow_req_data['data'] == []:
                    viewbot.append(req_data['data'][0]['login'])
                else:
                    for y in follow_req_data['data']:
                        lst.append(y['to_name'])
                    for z in str(lst):  # 팔로우 한국어 체크
                        if ord('가') <= ord(z) <= ord('힣'):
                            k2_count += 1
                        elif ord('a') <= ord(z) <= ord('z'):
                            e_count += 1
                    if k2_count * 85 > e_count * 15:
                        b += 1
                        follow.append(req_data['data'][0]['login'])
                    else:
                        viewbot.append(req_data['data'][0]['login'])

        t += 1
        print("[", t, "/", chatters.json()['chatter_count'], "]", sep='')
        print("아이디:", req_data['data'][0]['login'], ", 닉네임:", req_data['data'][0]['display_name'], sep='')
        print("통계용 봇 = ", bot)
        print("한국어 닉네임 = ", k)
        print("한국어 팔로우 = ", b)
        print("뷰봇 의심 = ", t - k - b - bot)
        print("로그인 시청자 수 = ", t, end='\n\n')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main(chatters_data))
except Exception as e:
    print("Error:", e)
    os.system("pause")
    exit()


print(x)
print(host.json()['data'][0]['user_name'], "(", host.json()['data'][0]['user_login'], ")", sep='', end='\n\n')
print("통계용 봇 = ", bot)
print("한국어 닉네임 = ", k)
print("한국어 팔로우 = ", b)
print("뷰봇 의심 = ", t - k - b - bot)
print("로그인 시청자 수 = ", t)
print("트위치 시청자 수 = ", host.json()['data'][0]['viewer_count'], end='\n\n')
print("뷰봇 의심 아이디")
print(viewbot, end='\n\n')

print("영어 닉네임 목록")
print(follow, end='\n\n')
