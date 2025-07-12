import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/')
        await client.admin.command('ping')
        print('MongoDB is connected!')
        client.close()
        return True
    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb())
