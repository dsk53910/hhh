import asyncio
import httpx

async def get_categories():
    async with httpx.AsyncClient(base_url="https://api.hh.ru") as client:
        # Get professional roles dictionaries
        resp = await client.get("/dictionaries/professional_roles")
        if resp.status_code == 200:
            data = resp.json()
            for cat in data.get('categories', []):
                print(f"[{cat.get('id')}] {cat.get('name')}")
                
        print("\n---")
        # Check standard specializations (old way)
        resp = await client.get("/specializations")
        if resp.status_code == 200:
            data = resp.json()
            for cat in data:
                print(f"[{cat.get('id')}] {cat.get('name')}")

if __name__ == "__main__":
    asyncio.run(get_categories())
