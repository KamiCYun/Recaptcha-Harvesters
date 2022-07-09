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

@app.get('/recaptcha/{site}/{version}', status_code=status.HTTP_200_OK)
async def getwebhook(site: str, version: str, response: Response):
    try:
        return tokens[site][version]
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False}


uvicorn.run(app, port=5000)


