import threading
import time
import ujson
import asyncio
from fastapi import FastAPI, Response, status, Request
import uvicorn
import requests

tokens = {
    "yeezysupply":{
        "v2": [],
        "v3": []
    },
    "google": {
        "v2": [],
        "v3": []
    }
}

globalpixel = []

app = FastAPI(openapi_url="")
LOCK = asyncio.Lock()

async def timer(site, version, token):
    await asyncio.sleep(60)
    async with LOCK:
        tokens[site][version].remove(token)


@app.post('/recaptcha/add', status_code=status.HTTP_200_OK)
async def savewebhooks(response: Response, request: Request):
    try:
        form = await request.body()
        form = form.decode('utf-8')
        print(form)
        data = ujson.loads(form)

        token = data["token"]
        site = data["site"]
        version = data["version"]

        async with LOCK:
            tokens[site][version].append(token)
        loop = asyncio.get_event_loop()
        loop.create_task(timer(site, version, token))
        return {"success": True}
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False}

@app.post('/pixel', status_code=status.HTTP_200_OK)
async def pixel(response: Response, request: Request):
    try:
        form = await request.body()
        form = form.decode('utf-8')
        data = ujson.loads(form)

        sensordata = data["pixel"]

        headers = {
            'Host': 'www.yeezysupply.com',
            'x-instana-t': '82f6b836dbac05d',
            'content-type': 'application/x-www-form-urlencoded',
            'x-instana-s': '82f6b836dbac05d',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'x-instana-l': '1,correlationType=web;correlationId=82f6b836dbac05d',
            'accept': '*/*',
            'origin': 'https://www.yeezysupply.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.yeezysupply.com/',
            'accept-language': 'en-US,en;q=0.9',
        }

        data = sensordata

        response = requests.post('https://www.yeezysupply.com/akam/11/pixel_59f27564', headers=headers, data=data)
        print(response.text)

        # globalpixel.append(sensordata)
        return {"success": True}
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False}


@app.get('/recaptcha/{site}/{version}', status_code=status.HTTP_200_OK)
async def getwebhook(site: str, version: str, response: Response):
    try:
        return tokens[site][version]
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False}


uvicorn.run(app, port=5000)


