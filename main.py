import os
import discord
import random
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord import app_commands
import math

# =========================
# 데이터 저장 시스템
# =========================

import json

DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = "/data/data.json"

DATA_KEYS = [
    "money_data",
    "daily_claims",
    "roulette_logs",
    "talk_states",
    "talk_counts",
    "cooldowns",
    "fish_tanks",
    "fish_dex",
    "fishing_cooldowns",
    "farm_data",
    "crop_dex",
    "crop_prices",
    "bank_data"
]

data = {key: {} for key in DATA_KEYS}


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, set):
        return list(obj)

    raise TypeError(f"{type(obj)} is not serializable")


def to_int_key_dict(raw):
    result = {}

    for key, value in raw.items():
        try:
            new_key = int(key)
        except (ValueError, TypeError):
            new_key = key

        result[new_key] = value

    return result


def restore_datetime(value):
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return value

    return value


def bind_storage_globals():
    global money_data, daily_claims, roulette_logs
    global talk_states, talk_counts, cooldowns
    global fish_tanks, fish_dex, fishing_cooldowns
    global farm_data, crop_dex, crop_prices
    global bank_data

    money_data = data["money_data"]
    daily_claims = data["daily_claims"]
    roulette_logs = data["roulette_logs"]
    bank_data = data["bank_data"]
    
    talk_states = data["talk_states"]
    talk_counts = data["talk_counts"]
    cooldowns = data["cooldowns"]

    fish_tanks = data["fish_tanks"]
    fish_dex = data["fish_dex"]
    fishing_cooldowns = data["fishing_cooldowns"]

    farm_data = data["farm_data"]
    crop_dex = data["crop_dex"]
    crop_prices = data["crop_prices"]

def sync_storage_globals():
    data["money_data"] = money_data
    data["daily_claims"] = daily_claims
    data["roulette_logs"] = roulette_logs

    data["talk_states"] = talk_states
    data["talk_counts"] = talk_counts
    data["cooldowns"] = cooldowns

    data["fish_tanks"] = fish_tanks
    data["fish_dex"] = fish_dex
    data["fishing_cooldowns"] = fishing_cooldowns

    data["farm_data"] = farm_data
    data["crop_dex"] = crop_dex
    data["crop_prices"] = crop_prices

    data["bank_data"] = bank_data


def load_data():
    global data

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        for key in DATA_KEYS:
            data[key] = loaded.get(key, {})

    for key in [
        "money_data",
        "daily_claims",
        "roulette_logs",
        "talk_states",
        "talk_counts",
        "cooldowns",
        "fish_tanks",
        "fish_dex",
        "fishing_cooldowns",
        "farm_data",
        "crop_dex",
    ]:
        data[key] = to_int_key_dict(data[key])

    for user_id, value in list(data["daily_claims"].items()):
        data["daily_claims"][user_id] = restore_datetime(value)

    for user_id, value in list(data["cooldowns"].items()):
        data["cooldowns"][user_id] = restore_datetime(value)

    for user_id, value in list(data["fishing_cooldowns"].items()):
        data["fishing_cooldowns"][user_id] = restore_datetime(value)

    for user_id, value in list(data["talk_states"].items()):
        if isinstance(value, dict) and "expires" in value:
            value["expires"] = restore_datetime(value["expires"])

    for user_id, value in list(data["fish_dex"].items()):
        data["fish_dex"][user_id] = set(value)

    for user_id, value in list(data["crop_dex"].items()):
        data["crop_dex"][user_id] = set(value)

    for user_id, farm in list(data["farm_data"].items()):
        if not isinstance(farm, dict):
            continue

        for plot in farm.get("field", []):
            if isinstance(plot, dict):
                if "planted_at" in plot:
                    plot["planted_at"] = restore_datetime(plot["planted_at"])
                if "harvest_time" in plot:
                    plot["harvest_time"] = restore_datetime(plot["harvest_time"])

    bind_storage_globals()
    save_data()


def save_data():
    sync_storage_globals()

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
                default=serialize_datetime
            )

        print("저장 성공")

    except Exception as e:
        print("저장 실패:", e)
    
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1502532691495751731
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

auto_message_started = False

CHOSUNG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNGSUNG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ",
    "ㅗ", "ㅘ", "ㅙ", "ㅚ",
    "ㅛ",
    "ㅜ", "ㅝ", "ㅞ", "ㅟ",
    "ㅠ",
    "ㅡ", "ㅢ", "ㅣ"
]

JONGSUNG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ",
    "ㄷ",
    "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
    "ㅁ",
    "ㅂ", "ㅄ",
    "ㅅ", "ㅆ",
    "ㅇ",
    "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

# =========================
# 쿼티 도로어 1.0.1 규칙
# =========================
KOR_TO_QWERTY_DORO = {
    # 자음
    "ㄱ": "DD", "ㄲ": "DO", "ㅋ": "DR",
    "ㄴ": "Dd", "ㄹ": "Do", "ㅁ": "Dr",

    "ㄷ": "OD", "ㄸ": "OO", "ㅌ": "OR",

    "ㅂ": "Rd", "ㅃ": "Ro", "ㅍ": "Rr",

    "ㅅ": "RD", "ㅆ": "RO", "ㅇ": "RR",

    "ㅈ": "dD", "ㅉ": "dO", "ㅊ": "dR",

    "ㅎ": "dd",

    # 모음
    "ㅏ": "do", "ㅑ": "dr",

    "ㅓ": "od", "ㅕ": "oo",

    "ㅗ": "or", "ㅛ": "ro",

    "ㅜ": "rd", "ㅠ": "rr",

    "ㅡ": "so", "ㅣ": "os",

    "ㅐ": "rs", "ㅔ": "sr",

    "ㅒ": "sd", "ㅖ": "ds",
}
# 주의: oo, or, rd, ro, rr 같은 토큰은 중복이라 완전 복원이 불가능함.
# 그래서 역변환은 먼저 등록된 글자를 우선 사용함.
QWERTY_DORO_TO_KOR = {}
for kor, doro in KOR_TO_QWERTY_DORO.items():
    if doro not in QWERTY_DORO_TO_KOR:
        QWERTY_DORO_TO_KOR[doro] = kor

QWERTY_DORO_TOKENS = sorted(QWERTY_DORO_TO_KOR.keys(), key=len, reverse=True)

# =========================
# 기존 천지인식 도로어 규칙
# =========================
KOR_TO_CHEONJIIN_DORO = {
    "ㅣ": "d",
    ".": "o",
    "ㅡ": "r",

    "ㄱ": "D",
    "ㅋ": "^D",
    "ㄲ": "^^D",

    "ㅂ": "D.",
    "ㅍ": "^D.",
    "ㅃ": "^^D.",

    "ㄴ": "R:",
    "ㄹ": "^R:",

    "ㅅ": "R.",
    "ㅎ": "^R.",
    "ㅆ": "^^R.",

    "ㅇ": "R",
    "ㅁ": "^R",

    "ㄷ": "O",
    "ㅌ": "^O",
    "ㄸ": "^^O",

    "ㅈ": "O.",
    "ㅊ": "^O.",
    "ㅉ": "^^O.",
}

CHEONJIIN_DORO_TO_KOR = {v: k for k, v in KOR_TO_CHEONJIIN_DORO.items()}
CHEONJIIN_DORO_TOKENS = sorted(CHEONJIIN_DORO_TO_KOR.keys(), key=len, reverse=True)

# =========================
# 천지인 모음 규칙
# =========================
VOWEL_TO_CHEONJIIN = {
    "ㅏ": "ㅣ.",
    "ㅓ": ".ㅣ",
    "ㅗ": ".ㅡ",
    "ㅜ": "ㅡ.",
    "ㅡ": "ㅡ",
    "ㅣ": "ㅣ",

    "ㅑ": "ㅣ..",
    "ㅕ": "..ㅣ",
    "ㅛ": "..ㅡ",
    "ㅠ": "ㅡ..",

    "ㅐ": "ㅣ.ㅣ",
    "ㅔ": ".ㅣㅣ",

    "ㅘ": ".ㅡㅣ.",
    "ㅚ": ".ㅡㅣ",
    "ㅝ": "ㅡ..ㅣ",
    "ㅟ": "ㅡ.ㅣ",
    "ㅢ": "ㅡㅣ",
}

CHEONJIIN_TO_VOWEL = {v: k for k, v in VOWEL_TO_CHEONJIIN.items()}

# =========================
# 복합 모음 / 겹받침
# =========================
COMPLEX_VOWEL_DECOMPOSE = {
    "ㅘ": "ㅗㅏ",
    "ㅙ": "ㅗㅐ",
    "ㅚ": "ㅗㅣ",
    "ㅝ": "ㅜㅓ",
    "ㅞ": "ㅜㅔ",
    "ㅟ": "ㅜㅣ",
    "ㅢ": "ㅡㅣ",
}

COMPLEX_VOWEL_COMPOSE = {
    "ㅗㅏ": "ㅘ",
    "ㅗㅐ": "ㅙ",
    "ㅗㅣ": "ㅚ",
    "ㅜㅓ": "ㅝ",
    "ㅜㅔ": "ㅞ",
    "ㅜㅣ": "ㅟ",
    "ㅡㅣ": "ㅢ",
}

DOUBLE_JONG = {
    "ㄳ": "ㄱㅅ",
    "ㄵ": "ㄴㅈ",
    "ㄶ": "ㄴㅎ",
    "ㄺ": "ㄹㄱ",
    "ㄻ": "ㄹㅁ",
    "ㄼ": "ㄹㅂ",
    "ㄽ": "ㄹㅅ",
    "ㄾ": "ㄹㅌ",
    "ㄿ": "ㄹㅍ",
    "ㅀ": "ㄹㅎ",
    "ㅄ": "ㅂㅅ",
}

DOUBLE_JONG_REVERSE = {v: k for k, v in DOUBLE_JONG.items()}

# =========================
# 한글 분해
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

    jung_char = JUNGSUNG[jung]
    result += COMPLEX_VOWEL_DECOMPOSE.get(jung_char, jung_char)

    jong_char = JONGSUNG[jong]
    if jong_char:
        result += DOUBLE_JONG.get(jong_char, jong_char)

    return result

# =========================
# 천지인식 한글 분해
# =========================
def decompose_hangul_cheonjiin(char):
    code = ord(char)

    if not (0xAC00 <= code <= 0xD7A3):
        return char

    base = code - 0xAC00

    cho = base // 588
    jung = (base % 588) // 28
    jong = base % 28

    result = CHOSUNG[cho] + VOWEL_TO_CHEONJIIN[JUNGSUNG[jung]]

    if JONGSUNG[jong]:
        result += DOUBLE_JONG.get(JONGSUNG[jong], JONGSUNG[jong])

    return result

# =========================
# 한글 조합
# =========================
def compose_hangul(cho, jung, jong=""):
    cho_i = CHOSUNG.index(cho)
    jung_i = JUNGSUNG.index(jung)
    jong_i = JONGSUNG.index(jong)

    return chr(0xAC00 + cho_i * 588 + jung_i * 28 + jong_i)

# =========================
# 쿼티 도로어: 한국어 -> 도로어
# =========================
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

# =========================
# 쿼티 도로어: 도로어 -> 자모
# =========================
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

# =========================
# 쿼티 도로어: 도로어 -> 한국어
# =========================
def qwerty_doro_to_korean(text):
    words = text.split("   ")
    final_result = []

    for word in words:
        syllables = word.split(" ")
        result = []

        for syllable in syllables:
            jamos = qwerty_doro_to_jamo(syllable)

            if len(jamos) < 2 or jamos[0] not in CHOSUNG or jamos[1] not in JUNGSUNG:
                result.append("".join(jamos))
                continue

            cho = jamos[0]
            jung = jamos[1]
            jong = ""

            # 복합 모음 처리: ㅗ+ㅏ, ㅜ+ㅓ 같은 것
            index_after_vowel = 2
            if len(jamos) >= 3:
                two_vowels = jamos[1] + jamos[2]
                if two_vowels in COMPLEX_VOWEL_COMPOSE:
                    jung = COMPLEX_VOWEL_COMPOSE[two_vowels]
                    index_after_vowel = 3

            remain = jamos[index_after_vowel:]

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
# 기존 천지인식: 한국어 -> 도로어
# =========================
def korean_to_cheonjiin_doro(text):
    result = []

    for word in text.split(" "):
        chars = []

        for ch in word:
            decomposed = decompose_hangul_cheonjiin(ch)
            doro = ""

            for jamo in decomposed:
                doro += KOR_TO_CHEONJIIN_DORO.get(jamo, jamo)

            chars.append(doro)

        result.append(" ".join(chars))

    return "   ".join(result)

# =========================
# 기존 천지인식: 도로어 -> 자모
# =========================
def cheonjiin_doro_to_jamo(text):
    result = []
    i = 0

    while i < len(text):
        if text[i] == " ":
            i += 1
            continue

        matched = False

        for token in CHEONJIIN_DORO_TOKENS:
            if text.startswith(token, i):
                result.append(CHEONJIIN_DORO_TO_KOR[token])
                i += len(token)
                matched = True
                break

        if not matched:
            result.append(text[i])
            i += 1

    return result

# =========================
# 기존 천지인식: 도로어 -> 한국어
# =========================
def cheonjiin_doro_to_korean(text):
    words = text.split("   ")
    final_result = []

    for word in words:
        syllables = word.split(" ")
        jamos = []

        for s in syllables:
            jamos.extend(cheonjiin_doro_to_jamo(s))

        result = []
        i = 0

        while i < len(jamos):
            if jamos[i] not in CHOSUNG:
                result.append(jamos[i])
                i += 1
                continue

            cho = jamos[i]
            i += 1

            vowel_buffer = ""

            while i < len(jamos) and jamos[i] in ["ㅣ", ".", "ㅡ"]:
                vowel_buffer += jamos[i]
                i += 1

            if vowel_buffer not in CHEONJIIN_TO_VOWEL:
                result.append(cho)
                continue

            jung = CHEONJIIN_TO_VOWEL[vowel_buffer]
            jong = ""

            if i < len(jamos) and jamos[i] in CHOSUNG:
                jong = jamos[i]
                i += 1

            result.append(compose_hangul(cho, jung, jong))

        final_result.append("".join(result))

    return " ".join(final_result)
    
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

    if not crop_price_loop.is_running():
        if not crop_prices:
            update_crop_prices()
        crop_price_loop.start()

    for channel_data in CHANNELS:
        bot.loop.create_task(random_message_loop(channel_data))


# =========================
# 명령어
# =========================

@bot.tree.command(name="도로어", description="한국어를 쿼티 도로어로 번역", guild=GUILD)
async def doro(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(korean_to_qwerty_doro(text))


@bot.tree.command(name="한국어", description="쿼티 도로어를 한국어로 번역", guild=GUILD)
async def korean(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(qwerty_doro_to_korean(text))


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

import random
from datetime import datetime, timedelta

talk_states = {}
talk_counts = {}
cooldowns = {}

TALK_TIMEOUT = timedelta(minutes=5)
COOLDOWN_TIME = timedelta(seconds=15)


def reset_talk(user_id):
    if user_id in talk_states:
        del talk_states[user_id]
        save_data()


@bot.tree.command(name="카운트", description="현재 대화 카운트 확인", guild=GUILD)
async def count(interaction: discord.Interaction):
    user_id = interaction.user.id
    current = talk_counts.get(user_id, 0)

    await interaction.response.send_message(f"현재 대화 카운트: {current}")


@bot.tree.command(name="말걸기", description="도로롱에게 말을 건다", guild=GUILD)
async def talk(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_name = interaction.user.display_name
    now = datetime.now()

    cooldown = cooldowns.get(user_id)

    if cooldown and now < cooldown:
        remain = int((cooldown - now).total_seconds())
        await interaction.response.send_message(f"도로롱이 무시중임... ({remain}초)")
        return

    talk_counts[user_id] = talk_counts.get(user_id, 0) + 1
    save_data()

    state_data = talk_states.get(user_id)

    if state_data and now > state_data["expires"]:
        reset_talk(user_id)
        state_data = None

    def set_state(next_state):
        talk_states[user_id] = {
            "state": next_state,
            "expires": now + TALK_TIMEOUT
        }
        save_data()

    async def reply_50(positive_msgs, negative_msgs, next_state):
        is_positive = random.choice([True, False])

        if is_positive:
            msg = random.choice(positive_msgs)
            set_state(next_state)
        else:
            msg = random.choice(negative_msgs)
            cooldowns[user_id] = now + COOLDOWN_TIME
            reset_talk(user_id)
            save_data()

        await interaction.response.send_message(msg)

    if not state_data:
        await reply_50(
            ["뭐", "왜"],
            ["ㅗ", "말 걸지마"],
            "first_normal"
        )
        return

    state = state_data["state"]

    dialogue = {
        "first_normal": (
            ["왜 그래", "심심함?"],
            ["말 걸지마 씨발", "꺼져"],
            "why"
        ),
        "why": (
            ["나? 내 이름은 DORO, 도로롱이죠.", "일단 들어는 드릴게"],
            ["너랑 말 안해", "듣기 귀찮아"],
            "introduced"
        ),
        "introduced": (
            ["닌 왜 이름 안말해", "니 이름 뭐냐"],
            ["나 오늘 바빠", "ㄱㄷ 밥 먹고 옴"],
            "ask_name"
        ),
        "ask_name": (
            [
                f"ㅇㅋ 니 이름은 {user_name}이구나? 친추 받아라",
                f"{user_name}? 이름 기억했다"
            ],
            ["아 ㅈㄲ;", "응 니 이름 안들어 ㅅㄱ"],
            "know_name"
        ),
        "know_name": (
            ["왜케 많이 와", "단골이 따로 없네"],
            ["작작해라", "안질리냐?"],
            "friendly"
        ),
        "friendly": (
            ["나쁘진 않네 니", "너 짱 ㅇㅇ"],
            ["아니다 니 ㅄ임", "너임마종훈 ㅗㅗ"],
            "trust"
        ),
        "trust": (
            ["니 오니까 심심하진 않네", "니 나쁘진 않은 듯?"],
            ["취소 니 ㅈㄴ 귀찮아", "응 니 별로임 ㅅㄱ"],
            "small_talk"
        ),
        "small_talk": (
            ["요즘 뭐하고 사냐", "밥은 먹고 다니냐?"],
            ["안물안궁 ㅗ", "아 물어본 내가 바보지 ㅅㅂ"],
            "care"
        ),
        "care": (
            ["굶지 마라 밥 사드릴게", "내가 특별히 걱정해드림"],
            ["몰라 뒤지던지 말덙;", "응 걱정 안해 ㅅㄱ"],
            "compliment"
        ),
        "compliment": (
            ["끈기 있는 청년; 대단하다", "여기까지 온 거 보면 인정 ㅇㅇ"],
            ["말이 많다 닥쳐라", "칭찬하기도 아깝다 ㅄ아"],
            "secret"
        ),
        "secret": (
            ["사실 나도 대화하는 거 싫진 않음", "이건 비밀인데 니 ㅈㄴ 웃김"],
            ["아 근데 비밀 말하기 귀찮음 ㅅㄱ", "비밀 없는데? 꼽냐?"],
            "bond"
        ),
        "bond": (
            ["이러다가 90살 먹어서도 너랑 대화하겠네", "ㅇㅋ 너한테 친추 보낼게"],
            ["친구는 무슨", "아직 그 정도는 아님"],
            "closer"
        ),
        "closer": (
            ["니 말하는 거 왜케 웃기냐 ㅋㅋ", "솔직히 이제 좀 익숙해졌다"],
            ["니 너무 끈질겨 ㄲㅈ", "진 빠진다 ㅅㅂ"],
            "soft"
        ),
        "soft": (
            ["가끔 와서 말 거는 건 허락해줌", "뭐... 심심하면 와도 됨"],
            ["허락 취소함", "방금 말은 없던 걸로"],
            "promise"
        ),
        "promise": (
            ["ㅇㅋ 받아드림", "기분 좋으니까 특별히 받아는 드릴게"],
            ["응 안돼 ㅗ", "근데 귀찮아"],
            "almost_end"
        ),
        "almost_end": (
            ["오늘 대화 나쁘지 않았다", "내가 니 인정한다"],
            ["아 갑자기 귀찮아짐;", "더 말하기 싫어짐 ㅅㄱ"],
            "ending_ready"
        ),
        "ending_ready": (
            ["다음에 또 와라", "이번만큼은 봐드릴게"],
            ["아니 근데 슬슬 질림 ㅅㄱ", "슬슬 꺼져라"],
            "ending"
        )
    }

    if state in dialogue:
        positive_msgs, negative_msgs, next_state = dialogue[state]
        await reply_50(positive_msgs, negative_msgs, next_state)
        return

    if state == "ending":
        talk_counts[user_id] = 0
        reset_talk(user_id)
        save_data()
        await interaction.response.send_message("다음에 또 대화하자.")
        return

    reset_talk(user_id)
    return
        
@bot.tree.command(name="메뉴추천", description="랜덤으로 맛있는 메뉴 추천", guild=GUILD)
async def recommend_menu(interaction: discord.Interaction):
    menus = [

        # 한식
        "김치찌개", "된장찌개", "부대찌개", "순두부찌개",
        "청국장", "동태찌개", "고추장찌개", "참치김치찌개",
        "제육볶음", "불고기", "삼겹살", "목살", "항정살",
        "돼지갈비", "소갈비", "LA갈비", "갈비찜",
        "닭갈비", "찜닭", "닭볶음탕", "백숙",
        "보쌈", "족발", "냉채족발",
        "국밥", "돼지국밥", "순대국밥", "소머리국밥",
        "설렁탕", "갈비탕", "곰탕", "해장국",
        "감자탕", "뼈해장국", "육개장",
        "비빔밥", "돌솥비빔밥", "김치볶음밥",
        "새우볶음밥", "계란볶음밥",
        "오징어볶음", "낙지볶음", "쭈꾸미볶음",
        "코다리찜", "아귀찜",
        "칼국수", "수제비", "잔치국수",
        "비빔국수", "냉면", "막국수",
        "떡국", "만둣국",
        "김밥", "참치김밥", "치즈김밥",
        "떡볶이", "로제떡볶이", "라볶이",
        "순대", "튀김", "어묵", "핫바",
        "토스트", "길거리토스트",

        # 중식
        "짜장면", "간짜장", "삼선짜장",
        "짬뽕", "백짬뽕", "고추짬뽕",
        "탕수육", "깐풍기", "깐쇼새우",
        "유산슬", "양장피", "마파두부",
        "마라탕", "마라샹궈", "꿔바로우",
        "훠궈", "계란볶음밥",

        # 일식
        "초밥", "연어초밥", "광어초밥",
        "우동", "냉우동", "라멘",
        "돈까스", "치즈돈까스", "냉모밀",
        "규동", "가츠동", "오야코동",
        "사케동", "텐동",
        "회덮밥", "장어덮밥",

        # 양식
        "파스타", "로제 파스타", "크림 파스타",
        "토마토 파스타", "알리오올리오",
        "봉골레 파스타", "리조또",
        "스테이크", "함박스테이크",
        "피자", "페퍼로니 피자", "고구마 피자",
        "치즈 피자", "불고기 피자",
        "햄버거", "치즈버거", "새우버거",
        "핫도그", "샌드위치",
        "시저샐러드", "연어샐러드",

        # 패스트푸드 & 야식
        "치킨", "양념치킨", "후라이드치킨",
        "간장치킨", "마라치킨",
        "닭강정", "피자", "햄버거",
        "감자튀김", "치즈볼",
        "불닭볶음면", "짜파게티", "신라면",
        "컵라면", "치즈라면",

        # 아시안
        "쌀국수", "팟타이", "분짜",
        "나시고렝", "카오팟",
        "커리", "버터치킨커리",
        "탄두리치킨", "케밥", "타코",
        "브리또", "퀘사디아",

        # 디저트
        "붕어빵", "와플", "크로플",
        "케이크", "치즈케이크",
        "마카롱", "도넛", "츄러스",
        "빙수", "아이스크림",
        "초코 케이크", "허니브레드",

        # 술안주
        "닭발", "무뼈닭발",
        "곱창", "대창", "막창",
        "오돌뼈", "먹태", "골뱅이소면",
        "두부김치", "계란말이",
        "콘치즈", "치즈계란찜"
    ]

    menu = random.choice(menus)

    await interaction.response.send_message(
        f"오늘의 추천 메뉴는 **{menu}**"
    )

SLOT_SYMBOLS = [
    "🍒",
    "🍋",
    "🍉",
    "⭐",
    "💎",
    "7️⃣"
]
SLOT_SYMBOLS = [
    "🍒",
    "🍋",
    "🍉",
    "⭐",
    "💎",
    "7️⃣"
]

money_data = {}
daily_claims = {}
roulette_logs = {}

DAILY_COOLDOWN = timedelta(hours=24)

JACKPOT_MULTIPLIER = {
    "🍒": 2,
    "🍋": 3,
    "🍉": 4,
    "⭐": 5,
    "💎": 7,
    "7️⃣": 10
}


def get_wallet(user_id):
    if user_id not in money_data:
        money_data[user_id] = 5000
        return True
    return False


def get_log(user_id):
    if user_id not in roulette_logs:
        roulette_logs[user_id] = {
            "symbols": {symbol: 0 for symbol in SLOT_SYMBOLS},
            "spent": 0,
            "earned": 0,
            "plays": 0
        }
        return True
    return False


@bot.tree.command(name="돈받기", description="24시간마다 1000원을 받는다", guild=GUILD)
async def claim_money(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)

    last_claim = daily_claims.get(user_id)

    if last_claim and now < last_claim + DAILY_COOLDOWN:
        remain = (last_claim + DAILY_COOLDOWN) - now
        hours = remain.seconds // 3600
        minutes = (remain.seconds % 3600) // 60

        await interaction.response.send_message(
            f"용돈\n남은 시간: **{hours}시간 {minutes}분**",
            ephemeral=True
        )
        return

    money_data[user_id] += 1000
    daily_claims[user_id] = now
    save_data()

    await interaction.response.send_message(
        f"💰 1000원 받음!\n현재 잔액: **{money_data[user_id]}원**"
    )


@bot.tree.command(name="지갑", description="현재 잔액을 확인한다", guild=GUILD)
async def wallet(interaction: discord.Interaction):
    await interaction.response.defer()

    user_id = interaction.user.id
    created = get_wallet(user_id)

    await interaction.followup.send(
        f"👛 현재 잔액: **{money_data[user_id]}원**"
    )

    if created:
        save_data()


@bot.tree.command(name="로그", description="룰렛 기록을 확인한다", guild=GUILD)
async def roulette_log(interaction: discord.Interaction):
    await interaction.response.defer()

    user_id = interaction.user.id

    created = get_log(user_id)
    log = roulette_logs[user_id]

    symbol_text = "\n".join(
        f"{symbol}: {count}개"
        for symbol, count in log["symbols"].items()
    )

    await interaction.followup.send(
        f"📊 **룰렛 로그**\n\n"
        f"🎰 룰렛 횟수: **{log['plays']}회**\n"
        f"💸 쓴 금액: **{log['spent']}원**\n"
        f"💰 딴 금액: **{log['earned']}원**\n\n"
        f"나온 심볼 개수:\n{symbol_text}"
    )

    if created:
        save_data()


@bot.tree.command(name="룰렛", description="슬롯머신을 돌린다", guild=GUILD)
@app_commands.describe(베팅="최소 500원 이상 입력")
async def roulette(interaction: discord.Interaction, 베팅: int):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_log(user_id)

    if 베팅 < 500:
        await interaction.response.send_message(
            "❌ 최소 베팅은 500원부터 가능함.",
            ephemeral=True
        )
        return

    if money_data[user_id] < 베팅:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n현재 잔액: {money_data[user_id]}원",
            ephemeral=True
        )
        return

    money_data[user_id] -= 베팅
    roulette_logs[user_id]["spent"] += 베팅
    roulette_logs[user_id]["plays"] += 1
    save_data()

    await interaction.response.send_message("🎰 슬롯머신 돌리는 중...")

    msg = await interaction.original_response()

    for i in range(12):
        temp_slots = [
            random.choice(SLOT_SYMBOLS),
            random.choice(SLOT_SYMBOLS),
            random.choice(SLOT_SYMBOLS)
        ]

        await msg.edit(
            content=f"🎰 슬롯머신 🎰\n\n| {' | '.join(temp_slots)} |"
        )

        await asyncio.sleep(0.15 + (i * 0.02))

    slots = [
        random.choice(SLOT_SYMBOLS),
        random.choice(SLOT_SYMBOLS),
        random.choice(SLOT_SYMBOLS)
    ]

    for symbol in slots:
        roulette_logs[user_id]["symbols"][symbol] += 1

    save_data()

    result_text = f"🎰 슬롯머신 결과 🎰\n\n| {' | '.join(slots)} |\n\n"

    if slots[0] == slots[1] == slots[2]:
        multiplier = JACKPOT_MULTIPLIER[slots[0]]
        reward = 베팅 * multiplier

        money_data[user_id] += reward
        roulette_logs[user_id]["earned"] += reward
        save_data()

        result_text += (
            f"🔥 JACKPOT 🔥\n"
            f"{slots[0]} 3개 일치!\n"
            f"{multiplier}배 지급!\n\n"
            f"💰 +{reward}원"
        )

    elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
        reward = int(베팅 * 0.5)

        money_data[user_id] += reward
        roulette_logs[user_id]["earned"] += reward
        save_data()

        result_text += (
            f"✨ 2개 일치!\n"
            f"베팅금 절반 반환.\n\n"
            f"💰 +{reward}원"
        )

    else:
        result_text += (
            f"☠️ 실패...\n"
            f"💸 -{베팅}원"
        )

    result_text += f"\n\n현재 잔액: **{money_data[user_id]}원**"

    await msg.edit(content=result_text)

@bot.tree.command(name="송금", description="다른 유저에게 돈을 보낸다", guild=GUILD)
@app_commands.describe(
    대상="돈을 받을 유저",
    금액="송금할 금액"
)
async def transfer(
    interaction: discord.Interaction,
    대상: discord.Member,
    금액: int
):
    sender_id = interaction.user.id
    target_id = 대상.id

    get_wallet(sender_id)
    get_wallet(target_id)

    # 자기 자신 송금 방지
    if sender_id == target_id:
        await interaction.response.send_message(
            "❌ 자기 자신에게는 송금 못함.",
            ephemeral=True
        )
        return

    # 최소 금액
    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1원 이상 입력해야 함.",
            ephemeral=True
        )
        return

    # 돈 부족
    if money_data[sender_id] < 금액:
        await interaction.response.send_message(
            f"❌ 잔액 부족.\n현재 잔액: {money_data[sender_id]}원",
            ephemeral=True
        )
        return

    # 송금
    money_data[sender_id] -= 금액
    money_data[target_id] += 금액
    save_data()

    await interaction.response.send_message(
        f"💸 송금 완료!\n\n"
        f"보낸 사람: {interaction.user.mention}\n"
        f"받는 사람: {대상.mention}\n"
        f"금액: **{금액}원**\n\n"
        f"현재 잔액: **{money_data[sender_id]}원**"
    )

@bot.tree.command(
    name="돈",
    description="관리자 전용 돈 지급",
    guild=GUILD
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="돈 받을 유저",
    금액="지급할 금액"
)
async def add_money(
    interaction: discord.Interaction,
    유저: discord.Member,
    금액: int
):
    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1원 이상 입력해야 함.",
            ephemeral=True
        )
        return

    user_id = 유저.id

    get_wallet(user_id)

    money_data[user_id] += 금액
    save_data()

    await interaction.response.send_message(
        f"💰 지급 완료!\n\n"
        f"대상: {유저.mention}\n"
        f"지급 금액: **{금액:,}원**\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )


@add_money.error
async def add_money_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ 관리자 전용 명령어임.",
            ephemeral=True
        )
        
HORSES = {
    1: "🐎 번개도로",
    2: "🐴 흑룡마",
    3: "🦄 도로콘",
    4: "🐐 염소련마"
}

@bot.tree.command(name="경마", description="말 한 마리에 올인하는 경마 게임", guild=GUILD)
@app_commands.describe(
    말번호="1~4번 말 중 하나 선택",
    베팅="베팅할 금액"
)
async def horse_race(
    interaction: discord.Interaction,
    말번호: int,
    베팅: int
):
    user_id = interaction.user.id

    get_wallet(user_id)

    if 말번호 not in HORSES:
        await interaction.response.send_message(
            "❌ 1~4번 말 중에서 골라야 함.",
            ephemeral=True
        )
        return

    if 베팅 < 500:
        await interaction.response.send_message(
            "❌ 최소 베팅은 500원부터 가능함.",
            ephemeral=True
        )
        return

    if money_data[user_id] < 베팅:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n현재 잔액: {money_data[user_id]}원",
            ephemeral=True
        )
        return

    money_data[user_id] -= 베팅
    save_data()

    await interaction.response.send_message(
        "🏇 경마 시작..."
    )

    msg = await interaction.original_response()

    race_track = ["🐎", "🐴", "🦄", "🐐"]

    for i in range(8):
        lines = []

        for horse in race_track:
            pos = random.randint(0, 20)
            lines.append(f"{'─' * pos}{horse}")

        await msg.edit(
            content="🏇 경마 진행중...\n\n" + "\n".join(lines)
        )

        await asyncio.sleep(0.7)

    winner = random.randint(1, 4)

    result = (
        f"🏁 우승 말: {HORSES[winner]}\n\n"
    )

    if 말번호 == winner:
        reward = 베팅 * 3
        money_data[user_id] += reward
        save_data()

        result += (
            f"🎉 적중!\n"
            f"💰 +{reward}원\n\n"
        )
    else:
        result += (
            f"☠️ 실패...\n"
            f"💸 -{베팅}원\n\n"
        )

    result += f"현재 잔액: **{money_data[user_id]}원**"

    await msg.edit(content=result)

@bot.tree.command(name="말목록", description="경마에 참가하는 말 목록 확인", guild=GUILD)
async def horse_list(interaction: discord.Interaction):

    horse_text = "\n".join(
        f"{number}번 - {name}"
        for number, name in HORSES.items()
    )

    await interaction.response.send_message(
        f"🏇 현재 참가중인 말 목록\n\n{horse_text}\n\n"
        f"/경마 [말번호] [베팅금액]"
    )

# =========================
# 낚시 시스템
# =========================

fish_tanks = {}
fish_dex = {}
FISH_DATA = {
    "붕어": {
        "min_kg": 0.3,
        "max_kg": 2.0,
        "habitat": "연못",
        "base_price": 300,
        "kg_price": 120,
        "chance": 35
    },

    "잉어": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "강",
        "base_price": 700,
        "kg_price": 180,
        "chance": 25
    },

    "메기": {
        "min_kg": 2.0,
        "max_kg": 15.0,
        "habitat": "늪 / 강바닥",
        "base_price": 1200,
        "kg_price": 250,
        "chance": 15
    },

    "송어": {
        "min_kg": 1.0,
        "max_kg": 6.0,
        "habitat": "계곡",
        "base_price": 1400,
        "kg_price": 300,
        "chance": 18
    },

    "배스": {
        "min_kg": 1.0,
        "max_kg": 10.0,
        "habitat": "강",
        "base_price": 1500,
        "kg_price": 260,
        "chance": 16
    },

    "가물치": {
        "min_kg": 3.0,
        "max_kg": 20.0,
        "habitat": "늪",
        "base_price": 2400,
        "kg_price": 350,
        "chance": 10
    },

    "피라미": {
        "min_kg": 0.1,
        "max_kg": 0.7,
        "habitat": "시냇물",
        "base_price": 120,
        "kg_price": 90,
        "chance": 40
    },

    "금붕어": {
        "min_kg": 0.2,
        "max_kg": 1.0,
        "habitat": "연못",
        "base_price": 500,
        "kg_price": 150,
        "chance": 20
    },

    "장어": {
        "min_kg": 1.0,
        "max_kg": 12.0,
        "habitat": "강 / 바다",
        "base_price": 3500,
        "kg_price": 450,
        "chance": 9
    },

    "철갑상어": {
        "min_kg": 20.0,
        "max_kg": 200.0,
        "habitat": "심해 강",
        "base_price": 12000,
        "kg_price": 800,
        "chance": 3
    },

    "비단잉어": {
        "min_kg": 2.0,
        "max_kg": 15.0,
        "habitat": "고급 연못",
        "base_price": 8000,
        "kg_price": 600,
        "chance": 5
    },

    "무지개송어": {
        "min_kg": 1.0,
        "max_kg": 7.0,
        "habitat": "차가운 계곡",
        "base_price": 2800,
        "kg_price": 350,
        "chance": 12
    },

    "연어": {
        "min_kg": 2.0,
        "max_kg": 18.0,
        "habitat": "강 / 바다",
        "base_price": 3000,
        "kg_price": 420,
        "chance": 14
    },

    "구피": {
        "min_kg": 0.05,
        "max_kg": 0.3,
        "habitat": "수족관",
        "base_price": 100,
        "kg_price": 50,
        "chance": 45
    },

    "고등어": {
        "min_kg": 0.5,
        "max_kg": 5.0,
        "habitat": "바다",
        "base_price": 900,
        "kg_price": 180,
        "chance": 25
    },

    "갈치": {
        "min_kg": 2.0,
        "max_kg": 12.0,
        "habitat": "심해",
        "base_price": 3200,
        "kg_price": 400,
        "chance": 12
    },

    "참치": {
        "min_kg": 20.0,
        "max_kg": 250.0,
        "habitat": "먼바다",
        "base_price": 5000,
        "kg_price": 80,
        "chance": 8
    },

    "광어": {
        "min_kg": 1.0,
        "max_kg": 10.0,
        "habitat": "바다",
        "base_price": 2600,
        "kg_price": 300,
        "chance": 14
    },

    "우럭": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "바다",
        "base_price": 2400,
        "kg_price": 280,
        "chance": 14
    },

    "놀래미": {
        "min_kg": 0.5,
        "max_kg": 4.0,
        "habitat": "바다",
        "base_price": 1700,
        "kg_price": 220,
        "chance": 18
    },

    "복어": {
        "min_kg": 1.0,
        "max_kg": 6.0,
        "habitat": "바다",
        "base_price": 4200,
        "kg_price": 500,
        "chance": 7
    },

    "대구": {
        "min_kg": 3.0,
        "max_kg": 25.0,
        "habitat": "심해",
        "base_price": 3800,
        "kg_price": 420,
        "chance": 11
    },

    "아귀": {
        "min_kg": 5.0,
        "max_kg": 40.0,
        "habitat": "심해",
        "base_price": 6000,
        "kg_price": 550,
        "chance": 6
    },

    "병어": {
        "min_kg": 0.5,
        "max_kg": 3.0,
        "habitat": "바다",
        "base_price": 1300,
        "kg_price": 170,
        "chance": 20
    },

    "민어": {
        "min_kg": 3.0,
        "max_kg": 20.0,
        "habitat": "바다",
        "base_price": 4500,
        "kg_price": 480,
        "chance": 9
    },

    "다금바리": {
        "min_kg": 10.0,
        "max_kg": 80.0,
        "habitat": "심해 암초",
        "base_price": 15000,
        "kg_price": 900,
        "chance": 2
    },

    "얼음 송어": {
        "min_kg": 3.0,
        "max_kg": 15.0,
        "habitat": "빙하 호수",
        "base_price": 22000,
        "kg_price": 1200,
        "chance": 1
    },

    "그림자 메기": {
        "min_kg": 5.0,
        "max_kg": 30.0,
        "habitat": "어둠의 늪",
        "base_price": 26000,
        "kg_price": 1400,
        "chance": 1
    },

    "전기 뱀장어": {
        "min_kg": 4.0,
        "max_kg": 25.0,
        "habitat": "폭풍 강",
        "base_price": 28000,
        "kg_price": 1500,
        "chance": 1
    },

    "무지개 고래어": {
        "min_kg": 100.0,
        "max_kg": 800.0,
        "habitat": "환상의 바다",
        "base_price": 100000,
        "kg_price": 2500,
        "chance": 0.3
    },

    "별빛 해파리": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "밤바다",
        "base_price": 75000,
        "kg_price": 2200,
        "chance": 0.5
    },

    "심연의 포식어": {
        "min_kg": 150.0,
        "max_kg": 900.0,
        "habitat": "심연",
        "base_price": 250000,
        "kg_price": 5000,
        "chance": 0.1
    },

    "아카브 심해종": {
        "min_kg": 200.0,
        "max_kg": 1200.0,
        "habitat": "아카브 심해",
        "base_price": 500000,
        "kg_price": 8000,
        "chance": 0.05
    },

    "낡은 신발": {
        "min_kg": 0.3,
        "max_kg": 1.5,
        "habitat": "하수구",
        "base_price": 50,
        "kg_price": 10,
        "chance": 18
    },

    "찢어진 양말": {
        "min_kg": 0.1,
        "max_kg": 0.5,
        "habitat": "하수구",
        "base_price": 20,
        "kg_price": 5,
        "chance": 15
    },

    "녹슨 깡통": {
        "min_kg": 0.2,
        "max_kg": 2.0,
        "habitat": "강바닥",
        "base_price": 80,
        "kg_price": 15,
        "chance": 16
    },

    "폐타이어": {
        "min_kg": 3.0,
        "max_kg": 15.0,
        "habitat": "강바닥",
        "base_price": 100,
        "kg_price": 20,
        "chance": 7
    },

    "비닐봉지": {
        "min_kg": 0.05,
        "max_kg": 0.3,
        "habitat": "물 위",
        "base_price": 10,
        "kg_price": 3,
        "chance": 20
    },

    "부러진 낚싯대": {
        "min_kg": 1.0,
        "max_kg": 4.0,
        "habitat": "호수",
        "base_price": 300,
        "kg_price": 40,
        "chance": 5
    },

    "해초": {
        "min_kg": 0.1,
        "max_kg": 1.0,
        "habitat": "얕은 바다",
        "base_price": 30,
        "kg_price": 8,
        "chance": 25
    },

    "젖은 종이": {
        "min_kg": 0.05,
        "max_kg": 0.2,
        "habitat": "강",
        "base_price": 5,
        "kg_price": 1,
        "chance": 15
    },

    "고장난 스마트폰": {
        "min_kg": 0.2,
        "max_kg": 0.6,
        "habitat": "강바닥",
        "base_price": 1000,
        "kg_price": 50,
        "chance": 2
    }
}

def get_tank(user_id):
    changed = False

    if user_id not in fish_tanks:
        fish_tanks[user_id] = []
        changed = True

    if user_id not in fish_dex:
        fish_dex[user_id] = set()
        changed = True

    return changed


def fish_price(fish_name, kg):
    fish = FISH_DATA[fish_name]
    return int(fish["base_price"] + kg * fish["kg_price"])


def pick_fish():
    names = list(FISH_DATA.keys())
    chances = [FISH_DATA[name]["chance"] for name in names]
    return random.choices(names, weights=chances, k=1)[0]

fishing_cooldowns = {}
FISHING_COOLDOWN = timedelta(seconds=5)


class FishingButtonView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=12)
        self.user_id = user_id
        self.can_catch = False
        self.clicked = False
        self.message = None

    @discord.ui.button(
        label="기다리는 중...",
        style=discord.ButtonStyle.gray
    )
    async def catch_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ 낚싯대가 다르다.",
                ephemeral=True
            )
            return

        if not self.can_catch:
            self.clicked = True
            button.label = "너무 빨랐다..."
            button.style = discord.ButtonStyle.red
            button.disabled = True

            await interaction.response.edit_message(
                content="🐟 낚싯대엔 아무것도 안잡혔다..",
                view=self
            )
            self.stop()
            return

        self.clicked = True
        button.disabled = True

        await fishing_success(interaction, button)
        self.stop()

    async def start_waiting(self):
        wait_time = random.randint(3, 10)
        await asyncio.sleep(wait_time)

        if self.clicked:
            return

        self.can_catch = True

        button = self.children[0]
        button.label = "지금이다!"
        button.style = discord.ButtonStyle.green

        await self.message.edit(
            content="🎣 찌가 흔들린다! 지금 버튼 누르자!",
            view=self
        )

    async def on_timeout(self):
        if self.clicked:
            return

        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(
                content="🐟 시간이 지나서 물고기가 도망갔다...",
                view=self
            )


async def fishing_success(interaction: discord.Interaction, button):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)

    if random.randint(1, 100) == 1:
        stolen = int(money_data[user_id] * 0.05)
        money_data[user_id] -= stolen
        save_data()

        await interaction.response.edit_message(
            content=(
                f"🐟💀 **간고등어 출현**\n\n"
                f"간고등어가 당신의 지갑을 물고 튀었다..\n"
                f"💸 -{stolen}원\n\n"
                f"현재 잔액: **{money_data[user_id]}원**"
            ),
            view=None
        )
        return

    fish_name = pick_fish()
    data = FISH_DATA[fish_name]

    kg = round(random.uniform(data["min_kg"], data["max_kg"]), 2)
    price = fish_price(fish_name, kg)

    fish_tanks[user_id].append({
        "name": fish_name,
        "kg": kg,
        "price": price
    })

    fish_dex[user_id].add(fish_name)
    save_data()

    await interaction.response.edit_message(
        content=(
            f"🎣 낚시 성공!\n\n"
            f"잡은 물고기: **{fish_name}**\n"
            f"무게: **{kg}kg**\n"
            f"예상 판매가: **{price}원**"
        ),
        view=None
    )


@bot.tree.command(name="낚시", description="버튼 타이밍에 맞춰 물고기를 낚는다", guild=GUILD)
async def fishing(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)
    get_tank(user_id)

    cooldown = fishing_cooldowns.get(user_id)

    if cooldown and now < cooldown:
        remain = int((cooldown - now).total_seconds())
        await interaction.response.send_message(
            f"🎣 아직 낚시 준비중임. {remain}초 남음.",
            ephemeral=True
        )
        return

    fishing_cooldowns[user_id] = now + FISHING_COOLDOWN
    save_data()

    view = FishingButtonView(user_id)

    await interaction.response.send_message(
        "🎣 낚싯대를 던졌다...\n버튼이 초록색이 되면 눌러!",
        view=view
    )

    view.message = await interaction.original_response()

    asyncio.create_task(view.start_waiting())
@bot.tree.command(name="어항", description="내가 잡은 물고기 목록 확인", guild=GUILD)
async def fish_tank(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_tank(user_id)

    tank = fish_tanks[user_id]

    if not tank:
        await interaction.response.send_message("🐠 어항이 비어있다.")
        return

    count_data = {}

    for fish in tank:
        name = fish["name"]

        if name not in count_data:
            count_data[name] = {
                "count": 0,
                "total_kg": 0,
                "total_price": 0
            }

        count_data[name]["count"] += 1
        count_data[name]["total_kg"] += fish["kg"]
        count_data[name]["total_price"] += fish["price"]

    text = "\n".join(
        f"{name}: {data['count']}마리 / 총 {round(data['total_kg'], 2)}kg / 총 {data['total_price']}원"
        for name, data in count_data.items()
    )

    await interaction.response.send_message(
        f"🐠 **내 어항**\n\n{text}"
    )


@bot.tree.command(name="팔기", description="물고기를 판매한다.", guild=GUILD)
@app_commands.describe(
    물고기="판매할 물고기 이름",
    갯수="판매할 갯수"
)
async def sell_fish(interaction: discord.Interaction, 물고기: str, 갯수: int):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1마리 이상 팔아야 한다.", ephemeral=True)
        return

    owned = [fish for fish in fish_tanks[user_id] if fish["name"] == 물고기]

    if len(owned) < 갯수:
        await interaction.response.send_message(
            f"❌ {물고기} 부족함.\n"
            f"보유: {len(owned)}마리",
            ephemeral=True
        )
        return

    sell_list = owned[:갯수]
    total_price = sum(fish["price"] for fish in sell_list)

    removed = 0
    new_tank = []

    for fish in fish_tanks[user_id]:
        if fish["name"] == 물고기 and removed < 갯수:
            removed += 1
            continue

        new_tank.append(fish)

    fish_tanks[user_id] = new_tank
    money_data[user_id] += total_price
    save_data()

    await interaction.response.send_message(
        f"💰 판매 완료!\n\n"
        f"판매 물고기: **{물고기}**\n"
        f"판매 수량: **{갯수}마리**\n"
        f"획득 금액: **{total_price}원**\n\n"
        f"현재 잔액: **{money_data[user_id]}원**"
    )


@bot.tree.command(name="도감", description="내가 잡아본 물고기 도감 확인", guild=GUILD)
async def fish_book(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_tank(user_id)

    if not fish_dex[user_id]:
        await interaction.response.send_message("📖 아직 도감에 등록된 물고기가 없음.")
        return

    text = "\n".join(
        f"✅ {fish_name}"
        for fish_name in fish_dex[user_id]
    )

    await interaction.response.send_message(
        f"📖 **물고기 도감**\n\n{text}"
    )


@bot.tree.command(name="물고기정보", description="물고기 정보를 확인한다", guild=GUILD)
@app_commands.describe(물고기="정보를 볼 물고기 이름")
async def fish_info(interaction: discord.Interaction, 물고기: str):
    if 물고기 not in FISH_DATA:
        await interaction.response.send_message(
            "❌ 그런 물고기는 없음.",
            ephemeral=True
        )
        return

    data = FISH_DATA[물고기]

    await interaction.response.send_message(
        f"🐟 **{물고기} 정보**\n\n"
        f"무게 범위: **{data['min_kg']}kg ~ {data['max_kg']}kg**\n"
        f"서식지: **{data['habitat']}**\n"
        f"기본 판매가격: **{data['base_price']}원**\n"
        f"kg당 추가 가격: **{data['kg_price']}원**\n\n"
        f"판매가 계산식:\n"
        f"`기본 가격 + kg × kg당 가격`"
    )

@bot.tree.command(name="전체팔기", description="어항에 있는 모든 물고기를 판매한다.", guild=GUILD)
async def sell_all_fish(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)

    tank = fish_tanks[user_id]

    if not tank:
        await interaction.response.send_message("🐠 어항이 비어있다.", ephemeral=True)
        return

    total_price = sum(fish["price"] for fish in tank)
    total_count = len(tank)

    count_data = {}

    for fish in tank:
        name = fish["name"]
        count_data[name] = count_data.get(name, 0) + 1

    fish_tanks[user_id] = []
    money_data[user_id] += total_price
    save_data()

    sold_text = "\n".join(
        f"{name}: {count}마리"
        for name, count in count_data.items()
    )

    await interaction.response.send_message(
        f"💰 **전체 판매 완료!**\n\n"
        f"{sold_text}\n\n"
        f"판매 수량: **{total_count}마리**\n"
        f"획득 금액: **{total_price}원**\n\n"
        f"현재 잔액: **{money_data[user_id]}원**"
    )
# =========================
# 농사 시스템
# =========================

farm_data = {}
crop_dex = {}
crop_prices = {}

FARM_SIZE = 9
FERTILIZER_PRICE = 1500

SEED_DATA = {
    "감자": {
        "seed_price": 500,
        "base_price": 900,
        "grow_min": 60,
        "grow_max": 180
    },
    "당근": {
        "seed_price": 700,
        "base_price": 1300,
        "grow_min": 120,
        "grow_max": 300
    },
    "토마토": {
        "seed_price": 1200,
        "base_price": 2200,
        "grow_min": 300,
        "grow_max": 600
    },
    "딸기": {
        "seed_price": 2500,
        "base_price": 5000,
        "grow_min": 600,
        "grow_max": 1200
    },
    "황금옥수수": {
        "seed_price": 10000,
        "base_price": 25000,
        "grow_min": 1800,
        "grow_max": 3600
    },
    "만년초": {
    "seed_price": 50000,
    "base_price": 100000,
    "grow_min": 1800,
    "grow_max": 3600
    },

    "킹갓제너럴암튼겁나대단한킹왕짱히루루크도울고갈레전설의채소": {
    "seed_price": 1000000,
    "base_price": 2500000,
    "grow_min": 129600,
    "grow_max": 129600
    }
}


def get_farm(user_id):
    changed = False

    if user_id not in farm_data:
        farm_data[user_id] = {
            "seeds": {name: 0 for name in SEED_DATA},
            "fertilizer": 0,
            "field": [None for _ in range(FARM_SIZE)],
            "crops": {name: 0 for name in SEED_DATA}
        }
        changed = True

    for name in SEED_DATA:
        if name not in farm_data[user_id]["seeds"]:
            farm_data[user_id]["seeds"][name] = 0
            changed = True

        if name not in farm_data[user_id]["crops"]:
            farm_data[user_id]["crops"][name] = 0
            changed = True

    if user_id not in crop_dex:
        crop_dex[user_id] = set()
        changed = True

    return changed


def update_crop_prices():
    for crop_name, data in SEED_DATA.items():
        if crop_name not in crop_prices:
            crop_prices[crop_name] = data["base_price"]

        current = crop_prices[crop_name]
        base = data["base_price"]

        change_rate = random.randint(1, 7) / 100

        if random.choice([True, False]):
            current = int(current * (1 + change_rate))
        else:
            current = int(current * (1 - change_rate))

        min_price = int(base * 0.3)
        max_price = int(base * 1.5)

        crop_prices[crop_name] = max(min_price, min(max_price, current))

    save_data()


@tasks.loop(hours=1)
async def crop_price_loop():
    update_crop_prices()


# on_ready 안에 이거 추가해야 함
# if not crop_price_loop.is_running():
#     update_crop_prices()
#     crop_price_loop.start()


@bot.tree.command(name="상점", description="씨앗과 비료를 구매한다", guild=GUILD)
@app_commands.describe(
    아이템="구매할 씨앗 이름 또는 비료",
    갯수="구매할 갯수"
)
async def farm_shop(interaction: discord.Interaction, 아이템: str = None, 갯수: int = 1):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)

    if 아이템 is None:
        seed_lines = []

        for name, data in SEED_DATA.items():
            seed_lines.append(
                f"🌱 {name}\n"
                f"씨앗 가격: {data['seed_price']}원\n"
                f"기준 판매가: {data['base_price']}원\n"
                f"성장 시간: {data['grow_min']}초 ~ {data['grow_max']}초"
            )

        shop_text = "\n\n".join(seed_lines)

        await interaction.response.send_message(
            f"🏪 **농사 상점**\n\n"
            f"{shop_text}\n\n"
            f"🧪 비료\n"
            f"가격: {FERTILIZER_PRICE}원\n"
            f"효과: 성장 시간 50% 감소\n\n"
            f"구매 예시:\n"
            f"`/상점 감자 3`\n"
            f"`/상점 비료 2`"
        )
        return

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1개 이상 사야 함.", ephemeral=True)
        return

    if 아이템 == "비료":
        price = FERTILIZER_PRICE * 갯수

        if money_data[user_id] < price:
            await interaction.response.send_message("❌ 돈 부족.", ephemeral=True)
            return

        money_data[user_id] -= price
        farm_data[user_id]["fertilizer"] += 갯수
        save_data()

        await interaction.response.send_message(
            f"🧪 비료 {갯수}개 구매 완료!\n"
            f"현재 비료: **{farm_data[user_id]['fertilizer']}개**\n"
            f"현재 잔액: **{money_data[user_id]}원**"
        )
        return

    if 아이템 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 아이템은 상점에 없음.", ephemeral=True)
        return

    price = SEED_DATA[아이템]["seed_price"] * 갯수

    if money_data[user_id] < price:
        await interaction.response.send_message("❌ 돈 부족.", ephemeral=True)
        return

    money_data[user_id] -= price
    farm_data[user_id]["seeds"][아이템] += 갯수
    save_data()

    await interaction.response.send_message(
        f"🌱 {아이템} 씨앗 {갯수}개 구매 완료!\n"
        f"현재 보유: **{farm_data[user_id]['seeds'][아이템]}개**\n"
        f"현재 잔액: **{money_data[user_id]}원**"
    )


@bot.tree.command(name="농밭", description="내 농밭 상태 확인", guild=GUILD)
async def farm_field(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    lines = []

    for i, plot in enumerate(farm_data[user_id]["field"], start=1):
        if plot is None:
            lines.append(f"{i}번 밭: 비어있음")
            continue

        if now >= plot["harvest_time"]:
            lines.append(f"{i}번 밭: 🌾 {plot['crop']} 수확 가능")
        else:
            remain = int((plot["harvest_time"] - now).total_seconds())
            minutes = remain // 60
            seconds = remain % 60
            lines.append(f"{i}번 밭: 🌱 {plot['crop']} 성장중 ({minutes}분 {seconds}초)")

    await interaction.response.send_message(
        "🚜 **내 농밭**\n\n" + "\n".join(lines)
    )


@bot.tree.command(name="심기", description="농밭에 씨앗을 심는다", guild=GUILD)
@app_commands.describe(
    칸="1~9번 밭 칸",
    씨앗="심을 씨앗 이름",
    비료사용="비료 사용 여부"
)
async def plant_seed(
    interaction: discord.Interaction,
    칸: int,
    씨앗: str,
    비료사용: bool = False
):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    if 칸 < 1 or 칸 > FARM_SIZE:
        await interaction.response.send_message("❌ 밭 칸은 1~9번만 가능.", ephemeral=True)
        return

    index = 칸 - 1

    if farm_data[user_id]["field"][index] is not None:
        await interaction.response.send_message("❌ 이미 뭐가 심어져 있음.", ephemeral=True)
        return

    if 씨앗 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 씨앗 없음.", ephemeral=True)
        return

    if farm_data[user_id]["seeds"][씨앗] <= 0:
        await interaction.response.send_message("❌ 씨앗 없음. `/상점`에서 사셈.", ephemeral=True)
        return

    grow_time = random.randint(
        SEED_DATA[씨앗]["grow_min"],
        SEED_DATA[씨앗]["grow_max"]
    )

    used_fertilizer = False

    if 비료사용:
        if farm_data[user_id]["fertilizer"] <= 0:
            await interaction.response.send_message("❌ 비료 없음.", ephemeral=True)
            return

        farm_data[user_id]["fertilizer"] -= 1
        grow_time //= 2
        used_fertilizer = True

    farm_data[user_id]["seeds"][씨앗] -= 1

    farm_data[user_id]["field"][index] = {
        "crop": 씨앗,
        "planted_at": now,
        "harvest_time": now + timedelta(seconds=grow_time),
        "fertilizer": used_fertilizer
    }
    save_data()

    await interaction.response.send_message(
        f"🌱 {칸}번 밭에 **{씨앗}** 심음!\n"
        f"예상 성장 시간: **{grow_time}초**\n"
        f"비료 사용: **{'O' if used_fertilizer else 'X'}**"
    )


@bot.tree.command(name="수확", description="다 자란 농작물을 수확한다", guild=GUILD)
@app_commands.describe(칸="수확할 밭 칸")
async def harvest_crop(interaction: discord.Interaction, 칸: int):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    if 칸 < 1 or 칸 > FARM_SIZE:
        await interaction.response.send_message("❌ 밭 칸은 1~9번만 가능.", ephemeral=True)
        return

    index = 칸 - 1
    plot = farm_data[user_id]["field"][index]

    if plot is None:
        await interaction.response.send_message("❌ 이 칸은 비어있음.", ephemeral=True)
        return

    if now < plot["harvest_time"]:
        remain = int((plot["harvest_time"] - now).total_seconds())
        await interaction.response.send_message(
            f"❌ 아직 덜 자람. {remain}초 남음.",
            ephemeral=True
        )
        return

    crop_name = plot["crop"]

    farm_data[user_id]["crops"][crop_name] += 1
    crop_dex[user_id].add(crop_name)
    farm_data[user_id]["field"][index] = None
    save_data()

    await interaction.response.send_message(
        f"🌾 수확 완료!\n"
        f"획득 농작물: **{crop_name} 1개**"
    )


@bot.tree.command(name="판매", description="농작물을 판매한다", guild=GUILD)
@app_commands.describe(
    농작물="판매할 농작물 이름",
    갯수="판매할 갯수"
)
async def sell_crop(interaction: discord.Interaction, 농작물: str, 갯수: int):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)

    if 농작물 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 농작물 없음.", ephemeral=True)
        return

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1개 이상 팔아야 함.", ephemeral=True)
        return

    if farm_data[user_id]["crops"][농작물] < 갯수:
        await interaction.response.send_message(
            f"❌ {농작물} 부족함.\n"
            f"보유: {farm_data[user_id]['crops'][농작물]}개",
            ephemeral=True
        )
        return

    if not crop_prices:
        update_crop_prices()

    price = crop_prices[농작물]
    total = price * 갯수

    farm_data[user_id]["crops"][농작물] -= 갯수
    money_data[user_id] += total
    save_data()

    await interaction.response.send_message(
        f"💰 판매 완료!\n\n"
        f"농작물: **{농작물}**\n"
        f"수량: **{갯수}개**\n"
        f"현재 단가: **{price}원**\n"
        f"총 판매가: **{total}원**\n\n"
        f"현재 잔액: **{money_data[user_id]}원**"
    )


@bot.tree.command(name="변동가", description="현재 농작물 시세 확인", guild=GUILD)
async def crop_price_info(interaction: discord.Interaction):
    if not crop_prices:
        update_crop_prices()

    text = "\n".join(
        f"{name}: {crop_prices[name]}원 "
        f"(기준가 {data['base_price']}원)"
        for name, data in SEED_DATA.items()
    )

    await interaction.response.send_message(
        f"📈 **현재 농작물 변동가**\n\n{text}\n\n"
        f"시세는 1시간마다 1%~7% 변동됨."
    )


@bot.tree.command(name="도감2", description="농작물 도감 확인", guild=GUILD)
async def crop_book(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_farm(user_id)

    lines = []

    for name, data in SEED_DATA.items():
        discovered = "✅" if name in crop_dex[user_id] else "❌"

        lines.append(
            f"{discovered} **{name}**\n"
            f"씨앗 가격: {data['seed_price']}원\n"
            f"기준 판매가: {data['base_price']}원\n"
            f"성장 시간: {data['grow_min']}초 ~ {data['grow_max']}초"
        )

    await interaction.response.send_message(
        "📖 **농작물 도감**\n\n" + "\n\n".join(lines)
    )
@bot.tree.command(name="전체심기", description="빈 밭에 같은 씨앗을 전부 심는다", guild=GUILD)
@app_commands.describe(
    씨앗="심을 씨앗 이름",
    비료사용="비료를 가능한 만큼 사용할지 여부"
)
async def plant_all_seed(
    interaction: discord.Interaction,
    씨앗: str,
    비료사용: bool = False
):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    if 씨앗 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 씨앗 없음.", ephemeral=True)
        return

    empty_indexes = [
        i for i, plot in enumerate(farm_data[user_id]["field"])
        if plot is None
    ]

    if not empty_indexes:
        await interaction.response.send_message("❌ 빈 밭이 없음.", ephemeral=True)
        return

    seed_count = farm_data[user_id]["seeds"][씨앗]

    if seed_count <= 0:
        await interaction.response.send_message(f"❌ {씨앗} 씨앗이 없음.", ephemeral=True)
        return

    plant_count = min(len(empty_indexes), seed_count)

    planted = 0
    used_fertilizer_count = 0

    for index in empty_indexes[:plant_count]:
        grow_time = random.randint(
            SEED_DATA[씨앗]["grow_min"],
            SEED_DATA[씨앗]["grow_max"]
        )

        used_fertilizer = False

        if 비료사용 and farm_data[user_id]["fertilizer"] > 0:
            farm_data[user_id]["fertilizer"] -= 1
            grow_time //= 2
            used_fertilizer = True
            used_fertilizer_count += 1

        farm_data[user_id]["seeds"][씨앗] -= 1

        farm_data[user_id]["field"][index] = {
            "crop": 씨앗,
            "planted_at": now,
            "harvest_time": now + timedelta(seconds=grow_time),
            "fertilizer": used_fertilizer
        }

        planted += 1

    save_data()

    await interaction.response.send_message(
        f"🌱 **전체 심기 완료!**\n\n"
        f"심은 작물: **{씨앗}**\n"
        f"심은 개수: **{planted}개**\n"
        f"사용한 비료: **{used_fertilizer_count}개**\n"
        f"남은 씨앗: **{farm_data[user_id]['seeds'][씨앗]}개**"
    )


@bot.tree.command(name="전체수확", description="다 자란 농작물을 전부 수확한다", guild=GUILD)
async def harvest_all_crop(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    harvested = {}

    for i, plot in enumerate(farm_data[user_id]["field"]):
        if plot is None:
            continue

        if now < plot["harvest_time"]:
            continue

        crop_name = plot["crop"]

        farm_data[user_id]["crops"][crop_name] += 1
        crop_dex[user_id].add(crop_name)
        farm_data[user_id]["field"][i] = None

        harvested[crop_name] = harvested.get(crop_name, 0) + 1

    if not harvested:
        await interaction.response.send_message("🌱 수확 가능한 농작물이 없음.", ephemeral=True)
        return

    save_data()

    text = "\n".join(
        f"{name}: {count}개"
        for name, count in harvested.items()
    )

    await interaction.response.send_message(
        f"🌾 **전체 수확 완료!**\n\n{text}"
    )


@bot.tree.command(name="전체판매", description="보유한 농작물을 전부 판매한다", guild=GUILD)
async def sell_all_crop(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)

    if not crop_prices:
        update_crop_prices()

    sold = {}
    total_price = 0
    total_count = 0

    for crop_name, count in list(farm_data[user_id]["crops"].items()):
        if count <= 0:
            continue

        price = crop_prices[crop_name]
        total = price * count

        sold[crop_name] = {
            "count": count,
            "price": price,
            "total": total
        }

        total_price += total
        total_count += count
        farm_data[user_id]["crops"][crop_name] = 0

    if total_count <= 0:
        await interaction.response.send_message("❌ 팔 농작물이 없음.", ephemeral=True)
        return

    money_data[user_id] += total_price
    save_data()

    text = "\n".join(
        f"{name}: {data['count']}개 / 단가 {data['price']}원 / {data['total']}원"
        for name, data in sold.items()
    )

    await interaction.response.send_message(
        f"💰 **농작물 전체 판매 완료!**\n\n"
        f"{text}\n\n"
        f"판매 수량: **{total_count}개**\n"
        f"총 판매가: **{total_price}원**\n\n"
        f"현재 잔액: **{money_data[user_id]}원**"
    )
@bot.tree.command(name="거래", description="내가 잡은 물고기를 다른 유저에게 준다.", guild=GUILD)
@app_commands.describe(
    대상="물고기를 받을 유저",
    물고기="줄 물고기 이름",
    갯수="줄 물고기 갯수"
)
async def trade_fish(
    interaction: discord.Interaction,
    대상: discord.Member,
    물고기: str,
    갯수: int
):
    sender_id = interaction.user.id
    target_id = 대상.id

    get_tank(sender_id)
    get_tank(target_id)

    if sender_id == target_id:
        await interaction.response.send_message(
            "❌ 자기 자신에게는 거래 못함.",
            ephemeral=True
        )
        return

    if 대상.bot:
        await interaction.response.send_message(
            "❌ 봇한테는 물고기 못 줌.",
            ephemeral=True
        )
        return

    if 갯수 <= 0:
        await interaction.response.send_message(
            "❌ 1마리 이상 줘야 함.",
            ephemeral=True
        )
        return

    owned = [fish for fish in fish_tanks[sender_id] if fish["name"] == 물고기]

    if len(owned) < 갯수:
        await interaction.response.send_message(
            f"❌ {물고기} 부족함.\n보유: {len(owned)}마리",
            ephemeral=True
        )
        return

    trade_list = owned[:갯수]

    removed = 0
    new_tank = []

    for fish in fish_tanks[sender_id]:
        if fish["name"] == 물고기 and removed < 갯수:
            removed += 1
            continue

        new_tank.append(fish)

    fish_tanks[sender_id] = new_tank
    fish_tanks[target_id].extend(trade_list)

    for fish in trade_list:
        fish_dex[target_id].add(fish["name"])

    save_data()

    total_kg = round(sum(fish["kg"] for fish in trade_list), 2)
    total_price = sum(fish["price"] for fish in trade_list)

    await interaction.response.send_message(
        f"🤝 **물고기 거래 완료!**\n\n"
        f"보낸 사람: {interaction.user.mention}\n"
        f"받는 사람: {대상.mention}\n"
        f"물고기: **{물고기}**\n"
        f"수량: **{갯수}마리**\n"
        f"총 무게: **{total_kg}kg**\n"
        f"총 예상가: **{total_price}원**"
    )
@bot.tree.command(name="리더보드", description="서버 내 잔액 순위를 확인한다", guild=GUILD)
async def money_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    user_id = interaction.user.id
    get_wallet(user_id)

    ranking_data = sorted(
        money_data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if not ranking_data:
        await interaction.followup.send("📊 아직 리더보드에 표시할 유저가 없음.")
        return

    top_10 = ranking_data[:10]
    lines = []

    for rank, (member_id, money) in enumerate(top_10, start=1):
        member = interaction.guild.get_member(member_id)

        if member is None:
            try:
                member = await interaction.guild.fetch_member(member_id)
                name = member.display_name
            except:
                name = f"알 수 없음({member_id})"
        else:
            name = member.display_name

        medal = ""
        if rank == 1:
            medal = "🥇 "
        elif rank == 2:
            medal = "🥈 "
        elif rank == 3:
            medal = "🥉 "

        lines.append(f"{rank}위. {medal}{name} - **{money:,}원**")

    my_rank = None
    for rank, (member_id, money) in enumerate(ranking_data, start=1):
        if member_id == user_id:
            my_rank = rank
            break

    my_money = money_data.get(user_id, 0)

    await interaction.followup.send(
        f"🏆 **잔액 리더보드 TOP 10**\n\n"
        f"{chr(10).join(lines)}\n\n"
        f"📌 내 순위: **{my_rank}위** / 잔액: **{my_money:,}원**"
    )
# =========================
# 은행 시스템
# =========================

LOAN_MAX = 500000


def get_bank(user_id):

    if user_id not in bank_data:
        bank_data[user_id] = {
            "deposit": 0,
            "last_interest": datetime.now(),
            "loan": 0,
            "loan_interest": 0,
            "loan_time": None,
            "warning_added": False
        }

    return bank_data[user_id]


def update_bank(user_id):

    bank = get_bank(user_id)

    now = datetime.now()

    # 예금 이자
    passed_hours = int(
        (
            now - restore_datetime(bank["last_interest"])
        ).total_seconds() // 3600
    )

    if passed_hours > 0 and bank["deposit"] > 0:

        for _ in range(passed_hours):
            bank["deposit"] = int(bank["deposit"] * 1.02)

        bank["last_interest"] = now

    # 대출 이자 증가
    if bank["loan"] > 0 and bank["loan_time"]:

        passed = (
            now - restore_datetime(bank["loan_time"])
        ).total_seconds() / 3600

        if passed >= 32 and not bank["warning_added"]:

            bank["loan_interest"] += 2
            bank["warning_added"] = True

@bot.tree.command(name="대출", description="은행에서 돈을 빌린다", guild=GUILD)
@app_commands.describe(금액="빌릴 금액")
async def loan(interaction: discord.Interaction, 금액: int):

    user_id = interaction.user.id

    get_wallet(user_id)

    bank = get_bank(user_id)

    if bank["loan"] > 0:
        await interaction.response.send_message(
            "❌ 이미 대출중임.",
            ephemeral=True
        )
        return

    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1원 이상 가능.",
            ephemeral=True
        )
        return

    if 금액 > LOAN_MAX:
        await interaction.response.send_message(
            "❌ 최대 500000원까지 가능.",
            ephemeral=True
        )
        return

    interest = 5 + (금액 // 50000)

    bank["loan"] = 금액
    bank["loan_interest"] = interest
    bank["loan_time"] = datetime.now()
    bank["warning_added"] = False

    money_data[user_id] += 금액

    save_data()

    await interaction.response.send_message(
        f"🏦 대출 완료!\n\n"
        f"대출 금액: **{금액}원**\n"
        f"현재 이자: **{interest}%**"
    )


@bot.tree.command(name="상환", description="대출금을 갚는다", guild=GUILD)
async def repay(interaction: discord.Interaction):

    user_id = interaction.user.id

    get_wallet(user_id)

    bank = get_bank(user_id)

    update_bank(user_id)

    if bank["loan"] <= 0:
        await interaction.response.send_message(
            "❌ 대출 없음.",
            ephemeral=True
        )
        return

    total = int(
        bank["loan"] * (1 + bank["loan_interest"] / 100)
    )

    if money_data[user_id] < total:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n"
            f"상환 금액: **{total}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= total

    bank["loan"] = 0
    bank["loan_interest"] = 0
    bank["loan_time"] = None
    bank["warning_added"] = False

    save_data()

    await interaction.response.send_message(
        f"💰 상환 완료!\n"
        f"상환 금액: **{total}원**"
    )


@bot.tree.command(name="남은시간", description="대출 상태 확인", guild=GUILD)
async def left_time(interaction: discord.Interaction):

    user_id = interaction.user.id

    bank = get_bank(user_id)

    if bank["loan"] <= 0:
        await interaction.response.send_message(
            "❌ 대출 없음.",
            ephemeral=True
        )
        return

    loan_time = restore_datetime(bank["loan_time"])

    now = datetime.now()

    warning_1 = loan_time + timedelta(hours=32)
    warning_2 = loan_time + timedelta(hours=100)

    remain1 = warning_1 - now
    remain2 = warning_2 - now

    await interaction.response.send_message(
        f"🏦 대출 상태\n\n"
        f"현재 이자: **{bank['loan_interest']}%**\n"
        f"1차 경고까지: **{remain1}**\n"
        f"관리자 경고 기준까지: **{remain2}**"
    )


@bot.tree.command(name="돈넣기", description="은행에 돈 예금", guild=GUILD)
@app_commands.describe(금액="넣을 금액")
async def deposit(interaction: discord.Interaction, 금액: int):

    user_id = interaction.user.id

    get_wallet(user_id)

    bank = get_bank(user_id)

    update_bank(user_id)

    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1원 이상 가능.",
            ephemeral=True
        )
        return

    if money_data[user_id] < 금액:
        await interaction.response.send_message(
            "❌ 돈 부족.",
            ephemeral=True
        )
        return

    money_data[user_id] -= 금액
    bank["deposit"] += 금액

    save_data()

    await interaction.response.send_message(
        f"🏦 예금 완료!\n"
        f"현재 예금: **{bank['deposit']}원**"
    )


@bot.tree.command(name="돈빼기", description="은행에서 돈 출금", guild=GUILD)
@app_commands.describe(금액="뺄 금액")
async def withdraw(interaction: discord.Interaction, 금액: int):

    user_id = interaction.user.id

    get_wallet(user_id)

    bank = get_bank(user_id)

    update_bank(user_id)

    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1원 이상 가능.",
            ephemeral=True
        )
        return

    if bank["deposit"] < 금액:
        await interaction.response.send_message(
            "❌ 예금 부족.",
            ephemeral=True
        )
        return

    bank["deposit"] -= 금액
    money_data[user_id] += 금액

    save_data()

    await interaction.response.send_message(
        f"💸 출금 완료!\n"
        f"현재 예금: **{bank['deposit']}원**"
    )

print("저장 위치:", os.path.abspath(DATA_FILE))
print("파일 존재 여부:", os.path.exists(DATA_FILE))

load_data()
bot.run(TOKEN)
