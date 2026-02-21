import asyncio, httpx
async def t():
    async with httpx.AsyncClient() as c:
        d = await c.get("https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d=113/01/02&se=AL")
        print(d.json().keys())
        d2 = await c.get("https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=20240102&type=ALL")
        print(d2.json().keys())
asyncio.run(t())
