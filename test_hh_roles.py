import asyncio
import httpx

async def get_roles():
    async with httpx.AsyncClient(base_url="https://api.hh.ru") as client:
        resp = await client.get("/professional_roles")
        if resp.status_code == 200:
            data = resp.json()
            for cat in data.get('categories', []):
                print(f"[{cat.get('id')}] {cat.get('name')}")
                if "информацион" in cat.get('name').lower() or "it" in cat.get('name').lower():
                    print("  --> FOUND IT CATEGORY!")

if __name__ == "__main__":
    asyncio.run(get_roles())
