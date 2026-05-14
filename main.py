import os
import discord
import random
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# 도로어 데이터
# =========================

CHOSUNG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNGSUNG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ",
    "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ",
    "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ",
    "ㅡ", "ㅢ", "ㅣ"
]

JONGSUNG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ",
    "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
    "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ",
    "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

KOR_TO_QWERTY_DORO = {
    "ㄱ": "DD", "ㄲ": "DO", "ㅋ": "DR",
    "ㄴ": "Dd", "ㄹ": "Do", "ㅁ": "Dr",
    "ㄷ": "OD", "ㄸ": "OO", "ㅌ": "OR",
    "ㅂ": "Rd", "ㅃ": "Ro", "ㅍ": "Rr",
    "ㅅ": "RD", "ㅆ": "RO", "ㅇ": "RR",
    "ㅈ": "dD", "ㅉ": "dO", "ㅊ": "dR",
    "ㅎ": "dd",

    "ㅏ": "doo", "ㅑ": "dro",
    "ㅓ": "odo", "ㅕ": "ooo",
    "ㅗ": "oaa", "ㅛ": "roo",
    "ㅜ": "rdd", "ㅠ": "rrd",
    "ㅡ": "oor", "ㅣ": "orr",
    "ㅐ": "rdo", "ㅔ": "rod",
    "ㅒ": "rro", "ㅖ": "rdr",

    "ㅘ": "oaadoo",
    "ㅙ": "oaardo",
    "ㅚ": "oaaorr",
    "ㅝ": "rddodo",
    "ㅞ": "rddrod",
    "ㅟ": "rddorr",
    "ㅢ": "oororr",
}

QWERTY_DORO_TO_KOR = {v: k for k, v in KOR_TO_QWERTY_DORO.items()}
QWERTY_DORO_TOKENS = sorted(QWERTY_DORO_TO_KOR.keys(), key=len, reverse=True)

DOUBLE_JONG = {
    "ㄳ": "ㄱㅅ", "ㄵ": "ㄴㅈ", "ㄶ": "ㄴㅎ",
    "ㄺ": "ㄹㄱ", "ㄻ": "ㄹㅁ", "ㄼ": "ㄹㅂ",
    "ㄽ": "ㄹㅅ", "ㄾ": "ㄹㅌ", "ㄿ": "ㄹㅍ",
    "ㅀ": "ㄹㅎ", "ㅄ": "ㅂㅅ",
}

DOUBLE_JONG_REVERSE = {v: k for k, v in DOUBLE_JONG.items()}


# =========================
# 번역 함수
# =========================

def decompose_hangul(char):
    code = ord(char)

    if not (0xAC00 <= code <= 0xD7A3):
        return char

    base = code - 0xAC00
    cho = base // 588
    jung = (base % 588) // 28
    jong = base % 28

    result = CHOSUNG[cho]
    result += JUNGSUNG[jung]

    jong_char = JONGSUNG[jong]
    if jong_char:
        result += DOUBLE_JONG.get(jong_char, jong_char)

    return result


def compose_hangul(cho, jung, jong=""):
    return chr(
        0xAC00
        + CHOSUNG.index(cho) * 588
        + JUNGSUNG.index(jung) * 28
        + JONGSUNG.index(jong)
    )


def korean_to_qwerty_doro(text):
    result = []

    for word in text.split(" "):
        chars = []

        for ch in word:
            decomposed = decompose_hangul(ch)
            doro = ""

            for jamo in decomposed:
                doro += KOR_TO_QWERTY_DORO.get(jamo, jamo)

            chars.append(doro)

        result.append(" ".join(chars))

    return "   ".join(result)


def qwerty_doro_to_jamo(text):
    result = []
    i = 0

    while i < len(text):
        if text[i] == " ":
            i += 1
            continue

        matched = False

        for token in QWERTY_DORO_TOKENS:
            if text.startswith(token, i):
                result.append(QWERTY_DORO_TO_KOR[token])
                i += len(token)
                matched = True
                break

        if not matched:
            result.append(text[i])
            i += 1

    return result


def qwerty_doro_to_korean(text):
    words = text.split("   ")
    final_result = []

    for word in words:
        syllables = word.split(" ")
        result = []

        for syllable in syllables:
            jamos = qwerty_doro_to_jamo(syllable)

            if len(jamos) < 2:
                result.append("".join(jamos))
                continue

            cho = jamos[0]
            jung = jamos[1]
            remain = jamos[2:]

            if cho not in CHOSUNG or jung not in JUNGSUNG:
                result.append("".join(jamos))
                continue

            jong = ""

            if remain:
                jong_text = "".join(remain)
                jong = DOUBLE_JONG_REVERSE.get(jong_text, remain[0])

            try:
                result.append(compose_hangul(cho, jung, jong))
            except ValueError:
                result.append("".join(jamos))

        final_result.append("".join(result))

    return " ".join(final_result)


# =========================
# 자동 랜덤 메시지
# =========================

AUTO_MESSAGES = [
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
    "와 도로!"
]

CHANNEL_ID = 1502532692275625985


async def random_message_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        channel = bot.get_channel(CHANNEL_ID)

        if channel:
            await channel.send(random.choice(AUTO_MESSAGES))

        # 20분 ~ 3시간 사이 랜덤
        wait_time = random.randint(20 * 60, 3 * 60 * 60)
        await asyncio.sleep(wait_time)



# =========================
# 봇 준비 완료
# =========================

@bot.event
async def on_ready():
    guild = discord.Object(id=1502532691495751731)

    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)

    if not random_message.is_running():
        random_message.start()

    print(f"{len(synced)}개 명령어 동기화됨")
    print(f"{bot.user} 로그인 완료!")
    
    bot.loop.create_task(random_message_loop())

# =========================
# 명령어
# =========================

@bot.tree.command(name="도로어", description="한국어를 쿼티 도로어로 번역")
async def doro(interaction: discord.Interaction, text: str):
    result = korean_to_qwerty_doro(text)
    await interaction.response.send_message(result)


@bot.tree.command(name="한국어", description="쿼티 도로어를 한국어로 번역")
async def korean(interaction: discord.Interaction, text: str):
    result = qwerty_doro_to_korean(text)
    await interaction.response.send_message(result)


@bot.tree.command(name="dorodoro", description="DORODORODORODORO")
async def doro_spam(interaction: discord.Interaction):
    await interaction.response.send_message("DORODORODORODORO")


@bot.tree.command(name="소개", description="봇 소개")
async def intro(interaction: discord.Interaction):
    await interaction.response.send_message("My name is DORO")


@bot.tree.command(name="짖기", description="짱센 도로가 울부짖었따")
async def bark(interaction: discord.Interaction):
    await interaction.response.send_message("도르르릉 롱롱!!")


last_message = None

@bot.tree.command(name="현재상태", description="현재 도로롱의 상태 출력")
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


bot.run(TOKEN)
