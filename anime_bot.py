from dotenv import load_dotenv
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== CONFIG ==========
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "AnimeGloryStreams"   # Your channel username
BASE_URL = "https://anitown4u.com/tag/hindi/"

# ========== CLIENT ==========
bot = Client(
    "GloryHub", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN
)

# ========== GREETING ==========
@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌟 Join Anime Glory Streams", url=f"https://t.me/{CHANNEL_USERNAME}")]]
    )
    await message.reply_text(
        "━━━━━━━━━━━━━━━\n"
        "✨ 𝓦𝓮𝓵𝓬𝓸𝓶𝓮 𝓽𝓸 𝓖𝓵𝓸𝓻𝔂 𝓗𝓾𝓫 ✨\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👋 Your one-stop guide to Hindi Dubbed Anime.\n"
        "🎬 Type any Anime name below to start.\n"
        "But first, join our community channel 👇",
        reply_markup=keyboard
    )

# ========== CHANNEL CHECK ==========
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if member.status in [enums.ChatMemberStatus.MEMBER,
                             enums.ChatMemberStatus.OWNER,
                             enums.ChatMemberStatus.ADMINISTRATOR]:
            return True
        return False
    except Exception:
        return False

# ========== SCRAPER ==========
async def fetch_anime(query: str):
    search_url = f"https://anitown4u.com/?s={query}&tag=hindi"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            html_text = await resp.text()
            soup = BeautifulSoup(html_text, "html.parser")
            results = soup.find_all("h2", class_="title")
            if not results:
                return None, None

            first_result = results[0].find("a")
            anime_title = first_result.text.strip()
            anime_link = first_result["href"]

            async with session.get(anime_link) as r2:
                html2 = await r2.text()
                soup2 = BeautifulSoup(html2, "html.parser")
                eps = soup2.find_all("li", class_="dooplay_episodes")
                episodes = []
                for ep in eps:
                    a_tag = ep.find("a")
                    if a_tag:
                        ep_title = a_tag.text.strip()
                        ep_link = a_tag["href"]
                        episodes.append((ep_title, ep_link))
                return anime_title, episodes

# ========== HANDLE TEXT ==========
@bot.on_message(filters.text & ~filters.command("start"))
async def search_anime(client, message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        await message.reply_text(
            f"⚠️ Access Denied!\nPlease join our channel first 👉 @{CHANNEL_USERNAME}"
        )
        return

    query = message.text.strip()
    anime_title, episodes = await fetch_anime(query)
    if not anime_title:
        await message.reply_text("❌ Sorry, no Hindi Dubbed Anime found for your query.")
        return

    # Inline buttons (3 per row)
    buttons = []
    row = []
    for i, (ep_title, ep_link) in enumerate(episodes, start=1):
        row.append(InlineKeyboardButton(f"Ep {i}", callback_data=f"ep|{anime_title}|{ep_link}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    await message.reply_text(
        f"━━━━━━━━━━━━━━━\n"
        f"🎬 Anime Found: {anime_title} (Hindi Dub)\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📺 Episodes Available: {len(episodes)}\n"
        f"👇 Select your episode below 👇",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ========== HANDLE BUTTON ==========
@bot.on_callback_query()
async def episode_handler(client, callback_query):
    data = callback_query.data
    if data.startswith("ep|"):
        _, anime_title, ep_link = data.split("|", 2)
        await callback_query.message.reply_text(
            f"━━━━━━━━━━━━━━━\n"
            f"📺 {anime_title} (Hindi Dub)\n"
            f"✨ Selected Episode\n\n"
            f"👉 Watch Here: {ep_link}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💠 Source: AniTown4U.com"
        )
        await callback_query.answer()

# ========== START BOT ==========
print("🤖 Glory Hub Bot is running...")
bot.run()
