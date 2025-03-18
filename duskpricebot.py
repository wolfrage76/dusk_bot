import discord
import os
import requests
import asyncio
from discord.ext import tasks
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True  # Ensure guild intents are enabled
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n✅ Logged in as {client.user} (ID: {client.user.id})")
    
    # Log the servers the bot has joined
    print(f"🛡️ The bot is in {len(client.guilds)} guilds:")
    for guild in client.guilds:
        print(f" - {guild.name} (ID: {guild.id})")

    if not myLoop.is_running():
        myLoop.start()

@tasks.loop(seconds=61)
async def myLoop():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "dusk-network",
                "vs_currencies": "usd,btc,eth",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            },
            timeout=10
        )

        if response.status_code != 200:
            print(f"⚠️ API Error: {response.status_code}")
            return

        data = response.json()
        if "dusk-network" not in data:
            print("⚠️ API data missing 'dusk-network'")
            return

        coin = data["dusk-network"]

        usd = coin.get("usd", 0)
        change = coin.get("usd_24h_change", 0)
        mcap = coin.get("usd_market_cap", 0)
        vol = coin.get("usd_24h_vol", 0)

        btc = coin.get("btc", 0)
        btc_change = coin.get("btc_24h_change", 0)

        eth = coin.get("eth", 0)
        eth_change = coin.get("eth_24h_change", 0)

        usd_str = f"${usd:.3f} USD {'↓' if change < 0 else '↑'}"
        for guild in client.guilds:
            if guild.me.guild_permissions.change_nickname:
                await guild.me.edit(nick=usd_str)

        # Updating bot's presence
        statuses = [
            f"24hr Chg: {change:.2f}% {'↓' if change < 0 else '↑'}",
            f"MCAP: ${mcap / 1e9:.1f}B USD",
            f"24hr Vol: ${vol / 1e6:.2f}M",
            f"{btc:.8f} BTC {'↓' if btc_change < 0 else '↑'}",
            f"{eth:.8f} ETH {'↓' if eth_change < 0 else '↑'}"
        ]

        for status in statuses:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name='custom', state=status))
            await asyncio.sleep(14)

    except Exception as e:
        print(f"❌ Exception in myLoop: {e}")

# Run the bot
client.run(DISCORD_TOKEN)
