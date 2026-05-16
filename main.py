import os
import discord
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord import app_commands

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

    state_data = talk_states.get(user_id)

    if state_data and now > state_data["expires"]:
        reset_talk(user_id)
        state_data = None

    def set_state(next_state):
        talk_states[user_id] = {
            "state": next_state,
            "expires": now + TALK_TIMEOUT
        }

    async def reply_50(positive_msgs, negative_msgs, next_state):
        is_positive = random.choice([True, False])

        if is_positive:
            msg = random.choice(positive_msgs)
            set_state(next_state)
        else:
            msg = random.choice(negative_msgs)
            cooldowns[user_id] = now + COOLDOWN_TIME
            reset_talk(user_id)

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

# 유저 돈 데이터
money_data = {}

# 배율 설정
JACKPOT_MULTIPLIER = {
    "🍒": 2,
    "🍋": 3,
    "🍉": 4,
    "⭐": 5,
    "💎": 7,
    "7️⃣": 10
}

@bot.tree.command(name="룰렛", description="슬롯머신을 돌린다", guild=GUILD)
@app_commands.describe(베팅="최소 500원 이상 입력")
async def roulette(interaction: discord.Interaction, 베팅: int):

    user_id = interaction.user.id

    # 돈 없으면 기본 지급
    if user_id not in money_data:
        money_data[user_id] = 5000

    # 최소 베팅 체크
    if 베팅 < 500:
        await interaction.response.send_message(
            "❌ 최소 베팅은 500원부터 가능함.",
            ephemeral=True
        )
        return

    # 돈 부족
    if money_data[user_id] < 베팅:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n현재 잔액: {money_data[user_id]}원",
            ephemeral=True
        )
        return

    # 돈 차감
    money_data[user_id] -= 베팅

    await interaction.response.send_message("🎰 슬롯머신 돌리는 중...")

    msg = await interaction.original_response()

    slots = ["❔", "❔", "❔"]

    # 돌아가는 연출
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

    # 최종 결과
    slots = [
        random.choice(SLOT_SYMBOLS),
        random.choice(SLOT_SYMBOLS),
        random.choice(SLOT_SYMBOLS)
    ]

    result_text = f"🎰 슬롯머신 결과 🎰\n\n| {' | '.join(slots)} |\n\n"

    # 3개 일치
    if slots[0] == slots[1] == slots[2]:

        multiplier = JACKPOT_MULTIPLIER[slots[0]]
        reward = 베팅 * multiplier

        money_data[user_id] += reward

        result_text += (
            f"🔥 JACKPOT 🔥\n"
            f"{slots[0]} 3개 일치!\n"
            f"{multiplier}배 지급!\n\n"
            f"💰 +{reward}원"
        )

    # 2개 일치
    elif (
        slots[0] == slots[1]
        or slots[1] == slots[2]
        or slots[0] == slots[2]
    ):

        reward = int(베팅 * 0.5)

        money_data[user_id] += reward

        result_text += (
            f"✨ 2개 일치!\n"
            f"베팅금 절반 반환.\n\n"
            f"💰 +{reward}원"
        )

    # 실패
    else:

        result_text += (
            f"☠️ 실패...\n"
            f"💸 -{베팅}원"
        )

    result_text += f"\n\n현재 잔액: {money_data[user_id]}원"

    await msg.edit(content=result_text)

bot.run(TOKEN)
