import httpx

def create_post(base_url, header):
    async def post(url, data={}, params={}, json={}):
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(base_url + url, headers=header, data=data, params=params, json=json)
                return res.json()
            except Exception as e:
                return {"code": 1, "msg": "请求失败", "data": e}
    return post

def create_get(base_url, header):
    async def get(url, params={}):
        async with httpx.AsyncClient() as client:
            res = await client.get(base_url + url, headers=header, params=params)
            return res.json()
    return get