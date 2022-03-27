import requests
import json
import pickle

with open('cookie.dump', 'rb') as f:
    cookies = pickle.load(f)
default_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'origin': 'https://tr.tradingview.com',
    'referer': ''
}
with requests.Session() as ses:
    ses.cookies = cookies

    login_data = {'user':'filthy-jew-5671','name':'zagovory.america.thailand@gmail.com','pass':'s5V3EfiqDnfWitZ'}
    main_page = ses.get('https://www.tradingview.com/', headers=default_header)
    print(main_page)

    res_1 = ses.get('https://www.tradingview.com/chart/?symbol=BINANCE:NEARUSDT')
    print(res_1)
    headers_2 = {
    'accept':'* / *',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
    'content-length': '117484',
    'origin': 'https://www.tradingview.com',
    'referer': 'https://www.tradingview.com/chart/?symbol=BINANCE:NEARUSDT',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': default_header['user-agent'],
    'x-language': 'en',
    'x-requested-with': 'XMLHttpRequest',
    }

    data = {"event":"report_stash","params":{"chartevents_http_status":[{"v":200,"a":{"source":"ChartEvents"}}],"chartevents_response_time_frame":[{"v":399,"a":{"source":"ChartEvents"}}],"chartevents_ok":[{"c":1}]}}
    headers = res_1.headers
    res_2 = ses.post('https://telemetry.tradingview.com/calendars/report', data=data, headers=default_header, stream=True)

    data = {
    'asyncSave': 'true',
    'timezone': 'Etc/UTC',
    'symbol': 'BINANCE:NEARUSDT',
    'preparedImage': '(binary)',
    }
    res = ses.post('https://www.tradingview.com/snapshot/', data=data, headers=headers_2, stream=True)

    print(res)

    #data.tradingview.com