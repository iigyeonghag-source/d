import os
import discord
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1502532691495751731
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

auto_message_started = False


# =========================
# 채널별 자동 메시지 설정
# =========================

CHANNELS = [
    {
        "id": 1502532692275625985,
        "messages": [
            "도로롱!",
            "\"DORO\"",
            "날 숭배하라.",
            "DORO 바보",
            "DORO 천재",
            "오늘의 날씨는 DORO합니다.",
            "DORODORODORODORODORODORODORO",
            "다들 뭐함?",
            "뭔 겜하지",
            "케케케",
            "도로롱!",
            "내가 가는 길이 곧 DORO야!",
            "배고프다.",
            "진짜 기분 like 종훈이",
            "야이 씨발아",
            "뭘봐",
            "ㅋ",
            "ㅋㅋㅋㅋ",
            "내 이름은 DORO",
            "졸리다.",
            "니들 뭔 겜함?",
            "내가 진짜 도로다!",
            "와 도로!",
            "@naigyejeongjugum",
            "@_1doro1_",
            "뭐임마",
            "나랑 놀자",
            "끝말잇기 시~작!"
        ],
        "min_time": 30,
        "max_time": 120
    },
    {
        "id": 1503162390735228928,
        "messages": [
            "도박 망했냐?",
            "어케 했냐 ㄷㄷ"
        ],
        "min_time": 60,
        "max_time": 600
    },
    {
        "id": 1502533312902598799,
        "messages": [
            "내가 DORO다!",
            "날 숭배하라.",
            "도멘",
            "솔직히 기독교 보단 도로교가 더 멋지다고 생각해요"
        ],
        "min_time": 120,
        "max_time": 360
    },
    {
        "id": 1502535053245284482,
        "messages": [
            "이 서버는 내꺼다 케케케",
            "관리자 해치웠나?",
            "테러를 시작하지 케케케"
        ],
        "min_time": 180,
        "max_time": 720
    }
]


# =========================
# 자동 메시지 루프
# =========================

async def random_message_loop(channel_data):
    await bot.wait_until_ready()

    while not bot.is_closed():
        channel = bot.get_channel(channel_data["id"])

        if channel:
            await channel.send(random.choice(channel_data["messages"]))

        wait_minutes = random.randint(
            channel_data["min_time"],
            channel_data["max_time"]
        )

        print(f"{channel_data['id']} 채널 → {wait_minutes}분 후 다음 메시지")

        await asyncio.sleep(wait_minutes * 60)


# =========================
# 봇 준비 완료
# =========================

@bot.event
async def on_ready():
    global auto_message_started

    synced = await bot.tree.sync(guild=GUILD)

    print(f"{len(synced)}개 명령어 동기화됨")
    print(f"{bot.user} 로그인 완료!")

    if auto_message_started:
        return

    auto_message_started = True

    for channel_data in CHANNELS:
        bot.loop.create_task(random_message_loop(channel_data))


# =========================
# 명령어
# =========================

@bot.tree.command(name="도로어", description="한국어를 쿼티 도로어로 번역", guild=GUILD)
async def doro(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)


@bot.tree.command(name="한국어", description="쿼티 도로어를 한국어로 번역", guild=GUILD)
async def korean(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)


@bot.tree.command(name="dorodoro", description="DORODORODORODORO", guild=GUILD)
async def doro_spam(interaction: discord.Interaction):
    await interaction.response.send_message("DORODORODORODORO")


@bot.tree.command(name="소개", description="봇 소개", guild=GUILD)
async def intro(interaction: discord.Interaction):
    await interaction.response.send_message("My name is DORO")


@bot.tree.command(name="짖기", description="짱센 도로가 울부짖었따", guild=GUILD)
async def bark(interaction: discord.Interaction):
    await interaction.response.send_message("도르르릉 롱롱!!")


last_message = None

@bot.tree.command(name="현재상태", description="현재 도로롱의 상태 출력", guild=GUILD)
async def status(interaction: discord.Interaction):
    global last_message

    messages = [
        "졸리다.",
        "배고프다.",
        "심심하다.",
        "뭘봐 씨발아",
        "도로롱!",
        "도로롱?",
        "즐겁다.",
        "우울하다."
    ]

    available = [m for m in messages if m != last_message]
    msg = random.choice(available)
    last_message = msg

    await interaction.response.send_message(msg)


# =========================
# 말걸기 명령어
# =========================

from datetime import datetime, timedelta

talk_states = {}
talk_counts = {}

TALK_TIMEOUT = timedelta(minutes=5)

def reset_talk(user_id):
    if user_id in talk_states:
        del talk_states[user_id]


@bot.tree.command(name="카운트", description="현재 대화 카운트 확인", guild=GUILD)
async def count(interaction: discord.Interaction):
    user_id = interaction.user.id

    current = talk_counts.get(user_id, 0)

    await interaction.response.send_message(
        f"현재 대화 카운트: {current}"
    )

@bot.tree.command(name="말걸기", description="도로롱에게 말을 건다", guild=GUILD)
async def talk(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_name = interaction.user.display_name
    now = datetime.now()

    # 카운트 증가
    talk_counts[user_id] = talk_counts.get(user_id, 0) + 1

    state_data = talk_states.get(user_id)

    # 5분 지나면 초기화
    if state_data and now > state_data["expires"]:
        reset_talk(user_id)
        state_data = None

    # 첫 대화
    if not state_data:
        msg = random.choice(["뭐", "왜", "ㅗ"])

        if msg in ["뭐", "왜"]:
            talk_states[user_id] = {
                "state": "first_normal",
                "expires": now + TALK_TIMEOUT
            }

        else:
            reset_talk(user_id)

        await interaction.response.send_message(msg)
        return

    state = state_data["state"]

    # 뭐 / 왜 이후
    if state == "first_normal":
        msg = random.choice([
            "말 걸지마 씨발",
            "왜 그래"
        ])

        if msg == "왜 그래":
            talk_states[user_id] = {
                "state": "why",
                "expires": now + TALK_TIMEOUT
            }

        else:
            reset_talk(user_id)

        await interaction.response.send_message(msg)
        return

    # 왜 그래 이후
    if state == "why":
        msg = random.choice([
            "나? 내 이름은 DORO, 도로롱이죠.",
            "너랑 말 안해"
        ])

        if msg == "나? 내 이름은 DORO, 도로롱이죠.":
            talk_states[user_id] = {
                "state": "introduced",
                "expires": now + TALK_TIMEOUT
            }

        else:
            reset_talk(user_id)

        await interaction.response.send_message(msg)
        return

    # 자기소개 이후
    if state == "introduced":
        msg = random.choice([
            "나 오늘 바빠",
            "넌 자기소개 안함?",
            "밥 먹고 옴"
        ])

        if msg == "넌 자기소개 안함?":
            talk_states[user_id] = {
                "state": "ask_name",
                "expires": now + TALK_TIMEOUT
            }

        else:
            reset_talk(user_id)

        await interaction.response.send_message(msg)
        return

    # 이름 묻기
    if state == "ask_name":
        talk_states[user_id] = {
            "state": "know_name",
            "expires": now + TALK_TIMEOUT
        }

        await interaction.response.send_message(
            f"ㅇㅋ 니 이름은 {user_name}이구나? 반갑다"
        )
        return

    # 마지막
    if state == "know_name":
        talk_counts[user_id] = 0

        reset_talk(user_id)
        
        await interaction.response.send_message(
            "다음에 또 대화하자."
        )
        return
        
bot.run(TOKEN)
