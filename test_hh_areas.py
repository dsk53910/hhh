import asyncio
import httpx

async def test_areas():
    async with httpx.AsyncClient(base_url="https://api.hh.ru") as client:
        resp = await client.get("/suggests/areas", params={"text": "алмат"})
        if resp.status_code == 200:
            print("Suggestions for 'алмат':")
            data = resp.json()
            for item in data.get('items', [])[:5]:
                print(f" - [{item.get('id')}] {item.get('text')}")
        else:
            print(f"Failed: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(test_areas())
