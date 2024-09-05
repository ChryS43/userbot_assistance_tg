import os
from pyrogram import Client
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# API ID e API Hash vengono presi dal file .env
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

async def main():
    # Crea un client temporaneo per generare la session string
    async with Client("userbot", api_id=API_ID, api_hash=API_HASH) as app:
        # Genera la session string
        session_string = await app.export_session_string()
        print("\nSession string:")
        print(session_string)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
