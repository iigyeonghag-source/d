import os
import discord
import random
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from discord import app_commands
import math
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# 데이터 저장 시스템
# =========================

import json

def money(value):
    return f"{round(value):,}"


def get_item_display_name(item, fallback="알 수 없음"):
    if not isinstance(item, dict):
        return fallback
    return item.get("display_name") or item.get("name") or fallback

DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = "/data/data.json"

DATA_KEYS = [
    "watering_cooldowns",
    "owned_weapons",
    "equipped_weapon",
    "owned_armors",
    "equipped_armor",
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
    "bank_data",
    "owned_rods",
    "equipped_rods",
    "owned_baits",
    "equipped_baits",
    "loan_data",
    "farm_levels",
    "field_sizes",
    "ore_bags",
    "owned_pickaxes",
    "equipped_pickaxes",
    "mine_data",
    "mining_cooldowns",
    "owned_pendants",
    "equipped_pendants",
    "boss_data",
    "boss_tickets",
    "boss_materials"
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
    global owned_rods, equipped_rods, owned_baits, equipped_baits
    global loan_data
    global farm_levels, field_sizes
    global ore_bags, owned_pickaxes, equipped_pickaxes
    global mine_data, mining_cooldowns
    global owned_pendants, equipped_pendants
    global boss_data, boss_tickets, boss_materials
    global owned_weapons, equipped_weapon
    global owned_armors, equipped_armor
    global watering_cooldowns
    
    watering_cooldowns = data["watering_cooldowns"]

    owned_weapons = data["owned_weapons"]
    equipped_weapon = data["equipped_weapon"]

    owned_armors = data["owned_armors"]
    equipped_armor = data["equipped_armor"]
    
    boss_data = data["boss_data"]
    boss_tickets = data["boss_tickets"]
    boss_materials = data["boss_materials"]
    
    money_data = data["money_data"]
    daily_claims = data["daily_claims"]
    roulette_logs = data["roulette_logs"]
    bank_data = data["bank_data"]
    loan_data = data["loan_data"]
    
    talk_states = data["talk_states"]
    talk_counts = data["talk_counts"]
    cooldowns = data["cooldowns"]

    fish_tanks = data["fish_tanks"]
    fish_dex = data["fish_dex"]
    fishing_cooldowns = data["fishing_cooldowns"]

    farm_data = data["farm_data"]
    crop_dex = data["crop_dex"]
    crop_prices = data["crop_prices"]
    farm_levels = data["farm_levels"]
    field_sizes = data["field_sizes"]

    owned_rods = data["owned_rods"]
    equipped_rods = data["equipped_rods"]
    owned_baits = data["owned_baits"]
    equipped_baits = data["equipped_baits"]

    ore_bags = data["ore_bags"]
    owned_pickaxes = data["owned_pickaxes"]
    equipped_pickaxes = data["equipped_pickaxes"]
    mine_data = data["mine_data"]
    mining_cooldowns = data["mining_cooldowns"]
    owned_pendants = data["owned_pendants"]
    equipped_pendants = data["equipped_pendants"]
    
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
    data["farm_levels"] = farm_levels
    data["field_sizes"] = field_sizes

    data["bank_data"] = bank_data
    data["loan_data"] = loan_data

    data["owned_rods"] = owned_rods
    data["equipped_rods"] = equipped_rods
    data["owned_baits"] = owned_baits
    data["equipped_baits"] = equipped_baits

    data["ore_bags"] = ore_bags
    data["owned_pickaxes"] = owned_pickaxes
    data["equipped_pickaxes"] = equipped_pickaxes
    data["mine_data"] = mine_data
    data["mining_cooldowns"] = mining_cooldowns
    data["owned_pendants"] = owned_pendants
    data["equipped_pendants"] = equipped_pendants

    data["boss_data"] = boss_data
    data["boss_tickets"] = boss_tickets
    data["boss_materials"] = boss_materials

    data["owned_weapons"] = owned_weapons
    data["equipped_weapon"] = equipped_weapon

    data["owned_armors"] = owned_armors
    data["equipped_armor"] = equipped_armor

    data["watering_cooldowns"] = watering_cooldowns

def load_data():
    global data

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        for key in DATA_KEYS:
            data[key] = loaded.get(key, {})

    for key in [
        "watering_cooldowns",
        "owned_weapons",
        "equipped_weapon",
        "owned_armors",
        "equipped_armor",
        "boss_data",
        "boss_tickets",
        "boss_materials",
        "money_data",
        "bank_data",
        "loan_data",
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
        "owned_rods",
        "equipped_rods",
        "owned_baits",
        "equipped_baits",
        "farm_levels",
        "field_sizes",
        "ore_bags",
        "owned_pickaxes",
        "equipped_pickaxes",
        "mine_data",
        "mining_cooldowns",
        "owned_pendants",
        "equipped_pendants"
    ]:
        data[key] = to_int_key_dict(data[key])
    for user_id, value in list(data["watering_cooldowns"].items()):
        data["watering_cooldowns"][user_id] = restore_datetime(value)
    
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
    
    for user_id, bank in list(data["bank_data"].items()):
        if not isinstance(bank, dict):
            continue

        if "last_interest" in bank:
            bank["last_interest"] = restore_datetime(bank["last_interest"])

        if "loan_time" in bank:
            bank["loan_time"] = restore_datetime(bank["loan_time"])

    for user_id, farm in list(data["farm_data"].items()):
        if not isinstance(farm, dict):
            continue

        for plot in farm.get("field", []):
            if isinstance(plot, dict):
                if "planted_at" in plot:
                    plot["planted_at"] = restore_datetime(plot["planted_at"])

                if "harvest_time" in plot:
                    plot["harvest_time"] = restore_datetime(plot["harvest_time"])
                    
    for user_id, mine in list(data["mine_data"].items()):
        if not isinstance(mine, dict):
            continue

        if "last_collect" in mine:
            mine["last_collect"] = restore_datetime(mine["last_collect"])
    
    for user_id, value in list(data["mining_cooldowns"].items()):
        data["mining_cooldowns"][user_id] = restore_datetime(value)
        
    for user_id, value in list(data["mining_cooldowns"].items()):
        data["mining_cooldowns"][user_id] = restore_datetime(value)

    for user_id, mine in list(data["mine_data"].items()):
        if isinstance(mine, dict) and "last_collect" in mine:
            mine["last_collect"] = restore_datetime(mine["last_collect"])
    
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
intents.message_content = False

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# 봇 준비 완료
# =========================

@bot.event
async def on_ready():
    synced = await bot.tree.sync(guild=GUILD)

    print(f"{len(synced)}개 명령어 동기화됨")
    print(f"{bot.user} 로그인 완료!")

    if not crop_price_loop.is_running():
        if not crop_prices:
            update_crop_prices()
        crop_price_loop.start()


# =========================
# 명령어
# =========================

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
# 미연시 시스템
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

# =========================
# 메뉴 추천 시스템
# =========================
        
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

# =========================
# 룰렛 시스템
# =========================

SLOT_SYMBOLS = ["🍒", "🍋", "🍉", "⭐", "💎", "7️⃣"]

SLOT_WEIGHTS = {
    "🍒": 35,
    "🍋": 25,
    "🍉": 18,
    "⭐": 12,
    "💎": 7,
    "7️⃣": 3
}

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


def get_weighted_slot(luck_bonus=0):
    symbols = list(SLOT_WEIGHTS.keys())
    weights = []

    for symbol in symbols:
        weight = SLOT_WEIGHTS[symbol]

        if symbol in ["💎", "7️⃣"]:
            weight *= 1 + (luck_bonus / 120)
        elif symbol == "⭐":
            weight *= 1 + (luck_bonus / 180)
        elif symbol in ["🍒", "🍋"]:
            weight *= max(0.35, 1 - (luck_bonus / 350))

        weights.append(weight)

    return random.choices(symbols, weights=weights, k=1)[0]


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
            "plays": 0,
            "gauge": 0
        }
        return True

    if "gauge" not in roulette_logs[user_id]:
        roulette_logs[user_id]["gauge"] = 0

    return False

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
    get_pendant(user_id)

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

    luck = get_pendant_luck(user_id)

    for i in range(12):
        temp_slots = [
            get_weighted_slot(luck),
            get_weighted_slot(luck),
            get_weighted_slot(luck)
        ]

        await msg.edit(
            content=f"🎰 슬롯머신 🎰\n\n| {' | '.join(temp_slots)} |"
        )

        await asyncio.sleep(0.15 + (i * 0.02))

    gauge = roulette_logs[user_id]["gauge"]
    pity_activated = gauge >= 100

    if pity_activated:
        jackpot_symbol = get_weighted_slot(luck)

        slots = [
            jackpot_symbol,
            jackpot_symbol,
            jackpot_symbol
        ]

        roulette_logs[user_id]["gauge"] = 0

    else:
        slots = [
            get_weighted_slot(luck),
            get_weighted_slot(luck),
            get_weighted_slot()
        ]

    for symbol in slots:
        roulette_logs[user_id]["symbols"][symbol] += 1

    result_text = f"🎰 슬롯머신 결과 🎰\n\n| {' | '.join(slots)} |\n\n"

    if slots[0] == slots[1] == slots[2]:
        multiplier = JACKPOT_MULTIPLIER[slots[0]]
        reward = 베팅 * multiplier

        money_data[user_id] += reward
        roulette_logs[user_id]["earned"] += reward

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

        result_text += (
            f"✨ 2개 일치!\n"
            f"베팅금 절반 반환.\n\n"
            f"💰 +{reward}원"
        )

    else:
        gauge_add = random.randint(5, 20)
        roulette_logs[user_id]["gauge"] += gauge_add

        if roulette_logs[user_id]["gauge"] > 100:
            roulette_logs[user_id]["gauge"] = 100

        result_text += (
            f"☠️ 실패...\n"
            f"💸 -{베팅}원"
        )

    result_text += (
        f"\n\n현재 잔액: **{money_data[user_id]}원**"
    )

    save_data()

    await msg.edit(content=result_text)
    
@bot.tree.command(name="돈받기", description="24시간마다 50000원을 받는다", guild=GUILD)
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

    money_data[user_id] += 50000
    daily_claims[user_id] = now
    save_data()

    await interaction.response.send_message(
        f"💰 50000원 받음!\n현재 잔액: **{money_data[user_id]}원**"
    )


@bot.tree.command(name="지갑", description="현재 잔액을 확인한다", guild=GUILD)
async def wallet(interaction: discord.Interaction):
    await interaction.response.defer()

    user_id = interaction.user.id
    created = get_wallet(user_id)

    await interaction.followup.send(
        f"👛 현재 잔액: **{money_data[user_id]:,}원**"
    )

    if created:
        save_data()
        
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

    if sender_id == target_id:
        await interaction.response.send_message("❌ 자기 자신에게는 송금 못함.", ephemeral=True)
        return

    if 금액 <= 0:
        await interaction.response.send_message("❌ 1원 이상 입력해야 함.", ephemeral=True)
        return

    if money_data[sender_id] < 금액:
        await interaction.response.send_message(
            f"❌ 잔액 부족.\n현재 잔액: {money_data[sender_id]:,}원",
            ephemeral=True
        )
        return

    money_data[sender_id] -= 금액
    money_data[target_id] += 금액
    save_data()

    await interaction.response.send_message(
        f"💸 송금 완료!\n\n"
        f"보낸 사람: {interaction.user.mention}\n"
        f"받는 사람: {대상.mention}\n"
        f"금액: **{금액:,}원**\n\n"
        f"대상의 현재 잔액: **{money_data[target_id]:,}원**\n"
        f"자신의 현재 잔액: **{money_data[sender_id]:,}원**"
    )

@bot.tree.command(name="돈", description="관리자 전용 돈 지급", guild=GUILD)
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
    get_pendant(user_id)

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

    luck_bonus = get_pendant_luck(user_id)
    horse_weights = [100, 100, 100, 100]
    horse_weights[말번호 - 1] += luck_bonus
    winner = random.choices([1, 2, 3, 4], weights=horse_weights, k=1)[0]

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

FISH_TRAIT_CHANCE = 50

FISH_DATA = {

    # ===== 쓰레기 =====

    "젖은 종이": {
        "min_kg": 0.05,
        "max_kg": 0.2,
        "habitat": "강",
        "base_price": 5,
        "kg_price": 1,
        "chance": 15
    },

    "비닐봉지": {
        "min_kg": 0.05,
        "max_kg": 0.3,
        "habitat": "물 위",
        "base_price": 10,
        "kg_price": 3,
        "chance": 20
    },

    "찢어진 양말": {
        "min_kg": 0.1,
        "max_kg": 0.5,
        "habitat": "하수구",
        "base_price": 20,
        "kg_price": 5,
        "chance": 18
    },

    "해초": {
        "min_kg": 0.1,
        "max_kg": 1.0,
        "habitat": "얕은 바다",
        "base_price": 30,
        "kg_price": 8,
        "chance": 25
    },

    "낡은 신발": {
        "min_kg": 0.3,
        "max_kg": 1.5,
        "habitat": "하수구",
        "base_price": 50,
        "kg_price": 10,
        "chance": 20
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

    "구피": {
        "min_kg": 0.05,
        "max_kg": 0.3,
        "habitat": "수족관",
        "base_price": 250,
        "kg_price": 50,
        "chance": 47
    },

    "피라미": {
        "min_kg": 0.1,
        "max_kg": 0.7,
        "habitat": "시냇물",
        "base_price": 320,
        "kg_price": 90,
        "chance": 40
    },

    "부러진 낚싯대": {
        "min_kg": 1.0,
        "max_kg": 4.0,
        "habitat": "호수",
        "base_price": 300,
        "kg_price": 40,
        "chance": 5
    },

    "누군가의 지갑": {
        "min_kg": 0.1,
        "max_kg": 0.5,
        "habitat": "호수",
        "base_price": 500000,
        "kg_price": 500,
        "chance": 1
    },

    "잃어버린 카드": {
        "min_kg": 0.1,
        "max_kg": 0.1,
        "habitat": "호수",
        "base_price": 200000,
        "kg_price": 5000,
        "chance": 0.1
    },

    "카시오 시계": {
        "min_kg": 0.02,
        "max_kg": 0.04,
        "habitat": "호수",
        "base_price": 25000,
        "kg_price": 1000,
        "chance": 0.1
    },
    
    "붕어": {
        "min_kg": 0.3,
        "max_kg": 2.0,
        "habitat": "연못",
        "base_price": 500,
        "kg_price": 120,
        "chance": 35
    },

    "금붕어": {
        "min_kg": 0.2,
        "max_kg": 1.0,
        "habitat": "연못",
        "base_price": 680,
        "kg_price": 150,
        "chance": 20
    },

    "잉어": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "강",
        "base_price": 1300,
        "kg_price": 380,
        "chance": 25
    },

    "고등어": {
        "min_kg": 0.5,
        "max_kg": 5.0,
        "habitat": "바다",
        "base_price": 2500,
        "kg_price": 180,
        "chance": 25
    },

    "고장난 스마트폰": {
        "min_kg": 0.2,
        "max_kg": 0.6,
        "habitat": "강바닥",
        "base_price": 3000,
        "kg_price": 50,
        "chance": 2
    },

    "메기": {
        "min_kg": 2.0,
        "max_kg": 15.0,
        "habitat": "늪 / 강바닥",
        "base_price": 5200,
        "kg_price": 350,
        "chance": 15
    },

    "병어": {
        "min_kg": 0.5,
        "max_kg": 3.0,
        "habitat": "바다",
        "base_price": 5300,
        "kg_price": 370,
        "chance": 21
    },

    "송어": {
        "min_kg": 1.0,
        "max_kg": 6.0,
        "habitat": "계곡",
        "base_price": 6400,
        "kg_price": 400,
        "chance": 18
    },

    "배스": {
        "min_kg": 1.0,
        "max_kg": 10.0,
        "habitat": "강",
        "base_price": 8500,
        "kg_price": 560,
        "chance": 16
    },

    "놀래미": {
        "min_kg": 0.5,
        "max_kg": 4.0,
        "habitat": "바다",
        "base_price": 10700,
        "kg_price": 520,
        "chance": 20
    },

    "은어": {
    "min_kg": 0.3,
    "max_kg": 2.0,
    "habitat": "맑은 강",
    "base_price": 15100,
    "kg_price": 570,
    "chance": 24
    },

    "농어": {
        "min_kg": 1.0,
        "max_kg": 9.0,
        "habitat": "연안 바다",
        "base_price": 28000,
        "kg_price": 660,
        "chance": 18
    },

    "숭어": {
        "min_kg": 0.8,
        "max_kg": 6.0,
        "habitat": "강 하구",
        "base_price": 9500,
        "kg_price": 700,
        "chance": 22
    },

    "전어": {
        "min_kg": 0.2,
        "max_kg": 1.2,
        "habitat": "바다",
        "base_price": 42000,
        "kg_price": 750,
        "chance": 28
    },

    "도루묵": {
        "min_kg": 0.4,
        "max_kg": 2.5,
        "habitat": "차가운 바다",
        "base_price": 35600,
        "kg_price": 830,
        "chance": 20
    },

    "쏘가리": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "강 상류",
        "base_price": 55200,
        "kg_price": 1050,
        "chance": 9
    },

    "볼락": {
        "min_kg": 0.5,
        "max_kg": 3.0,
        "habitat": "암초 지대",
        "base_price": 22700,
        "kg_price": 840,
        "chance": 19
    },

    "문어": {
        "min_kg": 2.0,
        "max_kg": 15.0,
        "habitat": "깊은 바다",
        "base_price": 68800,
        "kg_price": 1900,
        "chance": 7
    },

    "해마": {
        "min_kg": 0.1,
        "max_kg": 0.8,
        "habitat": "산호초",
        "base_price": 43100,
        "kg_price": 980,
        "chance": 12
    },

    "가재": {
        "min_kg": 0.3,
        "max_kg": 2.0,
        "habitat": "민물 바닥",
        "base_price": 15500,
        "kg_price": 1050,
        "chance": 23
    },

    "청어": {
        "min_kg": 0.5,
        "max_kg": 4.0,
        "habitat": "차가운 바다",
        "base_price": 16300,
        "kg_price": 1090,
        "chance": 25
    },

    "붉은 해파리": {
        "min_kg": 0.8,
        "max_kg": 5.0,
        "habitat": "붉은 해역",
        "base_price": 43600,
        "kg_price": 1330,
        "chance": 11
    },

    "검은 농어": {
        "min_kg": 2.0,
        "max_kg": 12.0,
        "habitat": "폭풍 해안",
        "base_price": 76900,
        "kg_price": 1550,
        "chance": 6
    },

    "도미": {
        "min_kg": 2.0,
        "max_kg": 12.0,
        "habitat": "깊은 바다",
        "base_price": 30100,
        "kg_price": 1610,
        "chance": 14
    },

    "청새치": {
        "min_kg": 40.0,
        "max_kg": 300.0,
        "habitat": "원양",
        "base_price": 120000,
        "kg_price": 1850,
        "chance": 4
    },

    "황금 잉어": {
        "min_kg": 5.0,
        "max_kg": 25.0,
        "habitat": "전설의 연못",
        "base_price": 480000,
        "kg_price": 2400,
        "chance": 2
    },

    # ===== 중상급 =====

    "가물치": {
        "min_kg": 3.0,
        "max_kg": 20.0,
        "habitat": "늪",
        "base_price": 75000,
        "kg_price": 1200,
        "chance": 10
    },

    "우럭": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "바다",
        "base_price": 32000,
        "kg_price": 1100,
        "chance": 16
    },

    "광어": {
        "min_kg": 1.0,
        "max_kg": 10.0,
        "habitat": "바다",
        "base_price": 43000,
        "kg_price": 1400,
        "chance": 13
    },

    "연어": {
        "min_kg": 2.0,
        "max_kg": 18.0,
        "habitat": "강 / 바다",
        "base_price": 45000,
        "kg_price": 1350,
        "chance": 13
    },

    "갈치": {
        "min_kg": 2.0,
        "max_kg": 12.0,
        "habitat": "심해",
        "base_price": 35000,
        "kg_price": 1450,
        "chance": 12
    },

    "장어": {
        "min_kg": 1.0,
        "max_kg": 12.0,
        "habitat": "강 / 바다",
        "base_price": 35000,
        "kg_price": 1600,
        "chance": 9
    },

    "대구": {
        "min_kg": 3.0,
        "max_kg": 25.0,
        "habitat": "심해",
        "base_price": 45000,
        "kg_price": 1700,
        "chance": 10
    },

    "복어": {
        "min_kg": 1.0,
        "max_kg": 6.0,
        "habitat": "바다",
        "base_price": 65000,
        "kg_price": 900,
        "chance": 7
    },

    "민어": {
        "min_kg": 3.0,
        "max_kg": 20.0,
        "habitat": "바다",
        "base_price": 90000,
        "kg_price": 1250,
        "chance": 8
    },

    "참치": {
        "min_kg": 20.0,
        "max_kg": 250.0,
        "habitat": "먼바다",
        "base_price": 56000,
        "kg_price": 900,
        "chance": 7
    },

    "무지개송어": {
        "min_kg": 1.0,
        "max_kg": 7.0,
        "habitat": "차가운 계곡",
        "base_price": 75000,
        "kg_price": 1000,
        "chance": 8
    },

    "아귀": {
        "min_kg": 5.0,
        "max_kg": 40.0,
        "habitat": "심해",
        "base_price": 125000,
        "kg_price": 1500,
        "chance": 5
    },

    "비단잉어": {
        "min_kg": 2.0,
        "max_kg": 15.0,
        "habitat": "고급 연못",
        "base_price": 130000,
        "kg_price": 1500,
        "chance": 5
    },

    "철갑상어": {
        "min_kg": 20.0,
        "max_kg": 200.0,
        "habitat": "심해 강",
        "base_price": 260000,
        "kg_price": 1200,
        "chance": 2
    },

    "다금바리": {
        "min_kg": 10.0,
        "max_kg": 80.0,
        "habitat": "심해 암초",
        "base_price": 240000,
        "kg_price": 2200,
        "chance": 3
    },

    "얼음 송어": {
        "min_kg": 3.0,
        "max_kg": 15.0,
        "habitat": "빙하 호수",
        "base_price": 220000,
        "kg_price": 2500,
        "chance": 2
    },

    "그림자 메기": {
        "min_kg": 5.0,
        "max_kg": 30.0,
        "habitat": "어둠의 늪",
        "base_price": 320000,
        "kg_price": 3000,
        "chance": 1
    },

    "전기 뱀장어": {
        "min_kg": 4.0,
        "max_kg": 25.0,
        "habitat": "폭풍의 강",
        "base_price": 300000,
        "kg_price": 3200,
        "chance": 0.9
    },

    "별빛 해파리": {
        "min_kg": 1.0,
        "max_kg": 8.0,
        "habitat": "밤바다",
        "base_price": 450000,
        "kg_price": 6500,
        "chance": 0.4
    },

    "무지개 고래어": {
        "min_kg": 100.0,
        "max_kg": 800.0,
        "habitat": "환상의 바다",
        "base_price": 900000,
        "kg_price": 2500,
        "chance": 0.1
    },

    "심연의 포식어": {
        "min_kg": 150.0,
        "max_kg": 900.0,
        "habitat": "심연",
        "base_price": 1300000,
        "kg_price": 3500,
        "chance": 0.08
    },

    "아카브 심해종": {
        "min_kg": 200.0,
        "max_kg": 1200.0,
        "habitat": "아카브 심해",
        "base_price": 2200000,
        "kg_price": 5000,
        "chance": 0.005
    },

    # ===== 새 비싼 물고기 =====

    "심해룡": {
        "min_kg": 500.0,
        "max_kg": 3000.0,
        "habitat": "용의 해구",
        "base_price": 3200000,
        "kg_price": 6500,
        "chance": 0.003
    },

    "심연 크라운": {
        "min_kg": 800.0,
        "max_kg": 5000.0,
        "habitat": "왕의 심연",
        "base_price": 4500000,
        "kg_price": 8000,
        "chance": 0.0015
    },

    "공허의 포식자": {
        "min_kg": 3000.0,
        "max_kg": 20000.0,
        "habitat": "공허 해역",
        "base_price": 7000000,
        "kg_price": 90000,
        "chance": 0.0005
    },

    "메갈로돈": {
        "min_kg": 3000.0,
        "max_kg": 120000.0,
        "habitat": "고대의 심연",
        "base_price": 2800000,
        "kg_price": 500,
        "chance": 0.001
    },

    "크라켄": {
        "min_kg": 300.0,
        "max_kg": 1000.0,
        "habitat": "심연의 균열",
        "base_price": 3500000,
        "kg_price": 7000,
        "chance": 0.001
    }
}

FISH_TRAITS = {

    # =========================
    # 안 좋은 특성
    # =========================

    "상처난": {
        "price_mult": 0.75,
        "kg_mult": 0.9,
        "type": "bad",
        "chance": 35
    },

    "비린내 나는": {
        "price_mult": 0.8,
        "kg_mult": 1.0,
        "type": "bad",
        "chance": 30
    },

    "마른": {
        "price_mult": 0.9,
        "kg_mult": 0.75,
        "type": "bad",
        "chance": 25
    },

    "썩어가는": {
        "price_mult": 0.5,
        "kg_mult": 1.0,
        "type": "bad",
        "chance": 10
    },

    # =========================
    # 좋은 특성
    # =========================

    "싱싱한": {
        "price_mult": 1.2,
        "kg_mult": 1.1,
        "type": "good",
        "chance": 100
    },

    "윤기나는": {
        "price_mult": 1.25,
        "kg_mult": 1.0,
        "type": "good",
        "chance": 90
    },

    "튼실한": {
        "price_mult": 1.2,
        "kg_mult": 1.35,
        "type": "good",
        "chance": 85
    },

    "거대한": {
        "price_mult": 0.9,
        "kg_mult": 10,
        "type": "good",
        "chance": 60
    },

    "황금빛": {
        "price_mult": 2,
        "kg_mult": 1.0,
        "type": "good",
        "chance": 40
    },

    "무지개빛": {
        "price_mult": 2.0,
        "kg_mult": 1.0,
        "type": "good",
        "chance": 25
    },

    "심연의": {
        "price_mult": 2.6,
        "kg_mult": 1.2,
        "type": "good",
        "chance": 18
    },

    "고대의": {
        "price_mult": 3.5,
        "kg_mult": 1.15,
        "type": "good",
        "chance": 14
    },

    "축복받은": {
        "price_mult": 4.8,
        "kg_mult": 1.0,
        "type": "good",
        "chance": 10
    },

    "왕관을 쓴": {
        "price_mult": 3.5,
        "kg_mult": 1.1,
        "type": "good",
        "chance": 8
    },

    "폭풍을 머금은": {
        "price_mult": 3.2,
        "kg_mult": 1.15,
        "type": "good",
        "chance": 12
    },

    "별빛을 품은": {
        "price_mult": 3.6,
        "kg_mult": 1.15,
        "type": "good",
        "chance": 7
    },

    "공허에 물든": {
        "price_mult": 4.5,
        "kg_mult": 1.4,
        "type": "good",
        "chance": 4
    },

    "신의": {
        "price_mult": 6.0,
        "kg_mult": 1.0,
        "type": "good",
        "chance": 2
    },

    "혼돈의": {
        "price_mult": 10.0,
        "kg_mult": 1.5,
        "type": "good",
        "chance": 1
    }
}

ROD_DATA = {
    "기본 낚싯대": {
        "price": 0, "ores": {},
        "luck": 0, "time_reduce": 0,
        "double_chance": 0, "triple_chance": 0
    },
    "초급 낚싯대": {
        "price": 150000, "ores": {"돌": 10, "구리": 7},
        "luck": 5, "time_reduce": 5,
        "double_chance": 2, "triple_chance": 0.1
    },
    "중급 낚싯대": {
        "price": 600000, "ores": {"구리": 10, "철광석": 10},
        "luck": 12, "time_reduce": 12,
        "double_chance": 5, "triple_chance": 1
    },
    "고급 낚싯대": {
        "price": 1300000, "ores": {"철광석": 40, "은광석": 15},
        "luck": 23, "time_reduce": 25,
        "double_chance": 8, "triple_chance": 2
    },
    "개쩌는 낚싯대": {
        "price": 3000000, "ores": {"금광석": 25, "다이아몬드": 5},
        "luck": 37, "time_reduce": 25,
        "double_chance": 10, "triple_chance": 5
    },
    "최상의 낚싯대": {
        "price": 8000000, "ores": {"사파이어": 7, "다이아몬드": 5, "에메랄드": 3},
        "luck": 55, "time_reduce": 30,
        "double_chance": 15, "triple_chance": 7
    },
    "장인의 낚싯대": {
        "price": 20000000, "ores": {"네더라이트": 2, "다이아몬드": 5, "철광석": 20},
        "luck": 75, "time_reduce": 40,
        "double_chance": 18, "triple_chance": 10
    },
    "엘프의 낚싯대": {
        "price": 60000000, "ores": {"레인보우 다이아몬드": 1, "네더라이트": 3, "에메랄드": 2},
        "luck": 100, "time_reduce": 45,
        "double_chance": 20, "triple_chance": 12
    },
    "강태공의 낚싯대": {
        "price": 180000000, "ores": {"레인보우 다이아몬드": 3, "레드 다이아몬드": 5, "네더라이트": 3},
        "luck": 235, "time_reduce": 55,
        "double_chance": 35, "triple_chance": 15
    },
    "신의 낚싯대": {
        "price": 500000000, "ores": {"신기루": 3, "레인보우 다이아몬드": 10, "우라늄": 1, "레드 다이아몬드": 3},
        "luck": 450, "time_reduce": 60,
        "double_chance": 40, "triple_chance": 30
    },
    "도로롱의 낚싯대": {
        "price": 800000000, "ores": {"신기루": 30},
        "luck": 900, "time_reduce": 70,
        "double_chance": 25, "triple_chance": 75
    }
}

BAIT_DATA = {
    "미끼 없음": {
        "price": 0,
        "luck": 0
    },
    "장구벌레": {
        "price": 300,
        "luck": 5
    },
    "지렁이": {
        "price": 700,
        "luck": 10
    },
    "귀뚜라미": {
        "price": 1300,
        "luck": 18
    },
    "거미": {
        "price": 2300,
        "luck": 28
    },
    "영양볼": {
        "price": 4500,
        "luck": 45
    },
    "세계수 잎사귀": {
        "price": 12000,
        "luck": 65
    },
    "장인의 미끼": {
        "price": 15000,
        "luck": 85
    },
    "강태공의 미끼": {
        "price": 35000,
        "luck": 105
    },
    "신의 미끼": {
        "price": 150000,
        "luck": 185
    },
    "도로롱": {
        "price": 500000,
        "luck": 300
    }
}

BOSS_FISH = ["메갈로돈", "크라켄"]

# FISH_DATA chance는 한 번만 절반으로 줄어들게 처리
if not globals().get("_FISH_CHANCE_HALVED", False):
    for fish in FISH_DATA.values():
        fish["chance"] /= 2
    _FISH_CHANCE_HALVED = True


# =========================
# 낚시 전투 메시지
# =========================

FISH_BATTLE_PATTERNS = {
    "강하게 당기기": [
        "🐟 물고기가 중심을 잃는다!",
        "🎣 강하게 끌려오는 느낌이다!",
        "🐟 놈의 움직임이 둔해진다...",
        "🌊 수면 가까이 올라오기 시작한다!",
        "🎣 릴이 빠르게 감긴다!",
        "🐟 물고기가 버티지 못하고 끌려온다!",
        "💥 강한 힘이 그대로 전달된다!",
        "🌊 커다란 물보라가 튄다!",
        "🐟 힘겨운 저항이 느껴진다...",
        "🎣 낚싯대 끝이 크게 휘어진다!"
    ],

    "천천히 당기기": [
        "🐟 물고기가 조심스럽게 움직인다...",
        "🎣 일정한 긴장감이 유지된다...",
        "🌊 물결이 천천히 흔들린다...",
        "🐟 놈이 경계하며 방향을 튼다...",
        "🎣 릴이 안정적으로 돌아간다...",
        "🐟 물고기가 천천히 끌려온다...",
        "🌊 수면 위로 잔물결이 퍼진다...",
        "🎣 침착하게 거리를 좁힌다...",
        "🐟 놈이 아직 힘을 아끼는 듯하다...",
        "🌊 조용한 힘겨루기가 이어진다..."
    ],

    "줄을 풀기": [
        "🐟 물고기가 거칠게 날뛴다!",
        "🎣 줄이 빠르게 풀려나간다!",
        "💥 강한 저항이 전해진다!",
        "🌊 물살이 크게 출렁인다!",
        "🐟 놈이 멀리 달아나려 한다!",
        "🎣 릴에서 거친 소리가 난다!",
        "🐟 엄청난 힘으로 버틴다!",
        "🌊 수면이 거세게 흔들린다!",
        "💨 물고기가 깊은 곳으로 파고든다!",
        "🎣 손끝이 저릴 정도로 저항한다!"
    ]
}

# =========================
# 저장용 데이터
# =========================

fish_tanks = globals().get("fish_tanks", {})
fish_dex = globals().get("fish_dex", {})

owned_rods = globals().get("owned_rods", {})
equipped_rods = globals().get("equipped_rods", {})
owned_baits = globals().get("owned_baits", {})
equipped_baits = globals().get("equipped_baits", {})

fishing_cooldowns = {}
FISHING_COOLDOWN = timedelta(seconds=10)

fish_market = globals().get("fish_market", {})
last_market_update = globals().get("last_market_update", None)

MARKET_MIN = 0.70
MARKET_MAX = 2.00


# =========================
# 시세 시스템
# =========================

def init_fish_market():
    for fish_name in FISH_DATA.keys():
        if fish_name not in fish_market:
            fish_market[fish_name] = 1.0


def update_fish_market():
    global last_market_update

    init_fish_market()
    now = datetime.now()

    if last_market_update is not None:
        if (now - last_market_update).total_seconds() < 3600:
            return False

    for fish_name in FISH_DATA.keys():
        change = random.uniform(0.01, 0.07)

        if random.choice([True, False]):
            fish_market[fish_name] += change
        else:
            fish_market[fish_name] -= change

        fish_market[fish_name] = max(
            MARKET_MIN,
            min(MARKET_MAX, fish_market[fish_name])
        )

    last_market_update = now
    save_data()
    return True


def get_market_price(fish_name, price):
    init_fish_market()
    return int(price * fish_market.get(fish_name, 1.0))


def get_market_text(fish_name):
    init_fish_market()
    rate = fish_market.get(fish_name, 1.0)
    percent = int(rate * 100)

    if rate > 1:
        return f"📈 현재 시세: **{percent}%**"
    elif rate < 1:
        return f"📉 현재 시세: **{percent}%**"

    return "➖ 현재 시세: **100%**"


# =========================
# 기본 함수
# =========================

def get_tank(user_id):
    changed = False

    if user_id not in fish_tanks or not isinstance(fish_tanks[user_id], list):
        fish_tanks[user_id] = []
        changed = True


    if user_id not in fish_dex:
        fish_dex[user_id] = set()
        changed = True

    if changed:
        save_data()

    return changed


def fish_price(fish_name, kg):
    fish = FISH_DATA[fish_name]
    return int(fish["base_price"] + kg * fish["kg_price"])


def pick_fish(luck_bonus=0):
    names = list(FISH_DATA.keys())
    weights = []

    for name in names:
        fish = FISH_DATA[name]
        chance = fish["chance"]
        price_score = fish["base_price"] + fish["max_kg"] * fish["kg_price"]

        if price_score >= 100000:
            chance *= 1 + (luck_bonus / 45)
        elif price_score >= 30000:
            chance *= 1 + (luck_bonus / 70)
        elif price_score >= 10000:
            chance *= 1 + (luck_bonus / 100)
        else:
            chance *= max(0.2, 1 - (luck_bonus / 250))

        weights.append(chance)

    return random.choices(names, weights=weights, k=1)[0]


def weighted_trait_choice(traits):
    names = []
    weights = []

    for name in traits:
        names.append(name)
        weights.append(FISH_TRAITS[name]["chance"])

    return random.choices(names, weights=weights, k=1)[0]


def roll_fish_trait():
    if random.randint(1, 100) > FISH_TRAIT_CHANCE:
        return None

    bad_traits = [
        name for name, data in FISH_TRAITS.items()
        if data["type"] == "bad"
    ]

    good_traits = [
        name for name, data in FISH_TRAITS.items()
        if data["type"] == "good"
    ]

    if random.randint(1, 100) <= 80:
        return weighted_trait_choice(good_traits)

    return weighted_trait_choice(bad_traits)

def make_fish(user_id, fish_name):
    fish_data = FISH_DATA[fish_name]

    trait_name = roll_fish_trait()

    kg = random.uniform(
        fish_data["min_kg"],
        fish_data["max_kg"]
    )

    display_name = fish_name

    if trait_name:
        trait = FISH_TRAITS[trait_name]
        kg *= trait["kg_mult"]
        display_name = f"{trait_name} {fish_name}"

    kg = round(kg, 2)

    price = fish_price(fish_name, kg)

    if trait_name:
        price = int(price * FISH_TRAITS[trait_name]["price_mult"])

    fish = {
        "name": fish_name,
        "display_name": display_name,
        "trait": trait_name,
        "kg": kg,
        "price": price
    }

    fish_tanks[user_id].append(fish)
    fish_dex[user_id].add(fish_name)

    return fish


def get_fishing_gear(user_id):
    changed = False

    if user_id not in owned_rods:
        owned_rods[user_id] = ["기본 낚싯대"]
        changed = True

    if user_id not in equipped_rods:
        equipped_rods[user_id] = "기본 낚싯대"
        changed = True

    if user_id not in owned_baits:
        owned_baits[user_id] = {}
        changed = True

    if user_id not in equipped_baits:
        equipped_baits[user_id] = "미끼 없음"
        changed = True

    return changed


# =========================
# 기본 낚시 타이밍 버튼
# =========================

class FishingButtonView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=25)
        self.user_id = user_id
        self.can_catch = False
        self.clicked = False
        self.message = None
        self.timed_out = False
        

    @discord.ui.button(label="기다리는 중...", style=discord.ButtonStyle.gray)
    async def catch_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 낚싯대가 다르다.", ephemeral=True)
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

        await fishing_success(interaction)
        self.stop()

    async def start_waiting(self):
        rod_name = equipped_rods.get(self.user_id, "기본 낚싯대")
        rod = ROD_DATA.get(rod_name, ROD_DATA["기본 낚싯대"])

        base_wait = random.randint(3, 10)
        reduce_rate = rod["time_reduce"] / 100
        wait_time = max(1, int(base_wait * (1 - reduce_rate)))

        await asyncio.sleep(wait_time)

        if self.clicked or self.timed_out:
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

        self.timed_out = True

        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(
                content="🐟 시간이 지나서 물고기가 도망갔다...",
                view=self
            )


# =========================
# 일반 물고기 힘겨루기
# =========================
LOST_ITEM_REWARDS = ["누군가의 지갑", "잃어버린 카드", "카시오 시계"]


class LostItemReturnView(discord.ui.View):
    def __init__(self, user_id, fish):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.fish = fish

    @discord.ui.button(label="주인 찾기", style=discord.ButtonStyle.green)
    async def find_owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 니가 주운 거 아님.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True

        wait_time = random.randint(100, 300)

        await interaction.response.edit_message(
            content=(
                f"🔎 **{self.fish['display_name']}**의 주인을 찾는 중...\n\n"
                f"⏳ 예상 시간: **{wait_time}초**"
            ),
            view=self
        )

        await asyncio.sleep(wait_time)

        reward = random.randint(100000, 200000)

        get_wallet(self.user_id)
        money_data[self.user_id] += reward
        save_data()

        await interaction.edit_original_response(
            content=(
                f"🙇‍♂️ 주인이 찾아왔다!\n\n"
                f"“정말 감사합니다! 이거라도 받아주세요.”\n\n"
                f"🎁 보상금: **{money(reward)}원**\n"
                f"현재 잔액: **{money(money_data[self.user_id])}원**"
            ),
            view=None
        )

        self.stop()

    @discord.ui.button(label="그냥 보관하기", style=discord.ButtonStyle.gray)
    async def keep_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 니가 주운 거 아님.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=f"🎒 **{self.fish['display_name']}**을 그냥 어항에 보관했다.",
            view=None
        )

        self.stop()


class FishBattleView(discord.ui.View):
    def __init__(self, user_id, fish_list, rod_name, bait_name):
        super().__init__(timeout=35)

        self.user_id = user_id
        self.fish_list = fish_list
        self.rod_name = rod_name
        self.bait_name = bait_name

        self.required_rounds = random.randint(2, 5)
        self.current_round = 0
        self.fail_count = 0

        self.correct_action = None
        self.message = None

        buttons = ["강하게 당기기", "천천히 당기기", "줄을 풀기"]
        random.shuffle(buttons)

        for label in buttons:
            self.add_item(FishBattleButton(label))

    async def next_round(self):
        if self.current_round >= self.required_rounds:
            await self.success()
            return

        self.correct_action = random.choice(list(FISH_BATTLE_PATTERNS.keys()))
        battle_message = random.choice(FISH_BATTLE_PATTERNS[self.correct_action])

        for item in self.children:
            item.disabled = False

        await self.message.edit(
            content=(
                f"🎣 **물고기와 힘겨루기 중...**\n\n"
                f"{battle_message}\n\n"
                f"알맞은 행동을 골라!"
            ),
            view=self
        )

    async def success(self):
        caught_text = []
        caught_fish = []

        for fish_name in self.fish_list:
            fish = make_fish(self.user_id, fish_name)
            caught_fish.append(fish)

            trait_text = ""
            if fish["trait"]:
                trait_text = f"\n특성: **{fish['trait']}**"

            caught_text.append(
                f"잡은 물고기: **{fish['display_name']}**\n"
                f"무게: **{fish['kg']}kg**\n"
                f"기본 판매가: **{money(fish['price'])}원**\n"
                f"{get_market_text(fish['name'])}\n"
                f"현재 판매가: **{money(get_market_price(fish['name'], fish['price']))}원**"
                f"{trait_text}"
            )

        save_data()

        lost_items = [
            fish for fish in caught_fish
            if fish["name"] in LOST_ITEM_REWARDS
        ]

        if len(lost_items) == 1:
            lost_item = lost_items[0]
            view = LostItemReturnView(self.user_id, lost_item)

            await self.message.edit(
                content=(
                    f"🎣 **낚시 성공!**\n\n"
                    f"사용 낚싯대: **{self.rod_name}**\n"
                    f"사용 미끼: **{self.bait_name}**\n\n"
                    + "\n\n".join(caught_text)
                    + "\n\n📦 뭔가 귀중품 같다...\n"
                    f"**{lost_item['display_name']}**의 주인을 찾을까?"
                ),
                view=view
            )

            self.stop()
            return

        await self.message.edit(
            content=(
                f"🎣 **낚시 성공!**\n\n"
                f"사용 낚싯대: **{self.rod_name}**\n"
                f"사용 미끼: **{self.bait_name}**\n\n"
                + "\n\n".join(caught_text)
            ),
            view=None
        )

        self.stop()

    async def fail(self):
        await self.message.edit(
            content="🐟 물고기가 도망쳤다...",
            view=None
        )

        self.stop()

    async def on_timeout(self):
        await self.fail()

class FishBattleButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.blurple
        )

    async def callback(self, interaction: discord.Interaction):
        view: FishBattleView = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ 니 물고기 아님.", ephemeral=True)
            return

        for item in view.children:
            item.disabled = True

        if self.label == view.correct_action:
            view.current_round += 1

            await interaction.response.edit_message(
                content="✅ 제대로 대응했다!",
                view=view
            )

            await asyncio.sleep(1)
            await view.next_round()
            return

        view.fail_count += 1

        if view.fail_count >= 3:
            await interaction.response.defer()
            await view.fail()
            return

        fail_messages = [
            "⚠️ 물고기가 크게 날뛰기 시작한다...",
            "💥 낚싯줄이 위험하게 흔들린다...",
            "🌊 물고기가 더 깊은 곳으로 파고든다..."
        ]

        await interaction.response.edit_message(
            content=random.choice(fail_messages),
            view=view
        )

        await asyncio.sleep(1)
        await view.next_round()


# =========================
# 보스 낚시
# =========================

class BossFishingView(discord.ui.View):
    def __init__(self, user_id, boss_name, rod_name, bait_name):
        super().__init__(timeout=40)
        self.user_id = user_id
        self.boss_name = boss_name
        self.rod_name = rod_name
        self.bait_name = bait_name

        self.required_hits = random.randint(5, 12)
        self.current_hits = 0
        self.target_index = None
        self.failed = False
        self.message = None

        for i in range(9):
            self.add_item(BossFishingButton(i))

    async def start_round(self):
        while self.current_hits < self.required_hits and not self.failed:
            self.target_index = random.randint(0, 8)

            for item in self.children:
                item.label = "⬛"
                item.style = discord.ButtonStyle.gray
                item.disabled = False

            self.children[self.target_index].label = "🟩"
            self.children[self.target_index].style = discord.ButtonStyle.green

            await self.message.edit(
                content=(
                    f"🐲 **보스 출현: {self.boss_name}**\n\n"
                    f"초록 칸을 3초 안에 눌러!\n"
                    f"진행도: **{self.current_hits}/{self.required_hits}**"
                ),
                view=self
            )

            before = self.current_hits
            await asyncio.sleep(3)

            if self.current_hits == before:
                await self.fail_boss("시간 초과")
                return

        if not self.failed:
            await self.success_boss()

    async def fail_boss(self, reason):
        self.failed = True

        for item in self.children:
            item.disabled = True

        await self.message.edit(
            content=(
                f"💀 **{self.boss_name} 도주**\n\n"
                f"사유: **{reason}**\n"
                f"진행도: **{self.current_hits}/{self.required_hits}**"
            ),
            view=self
        )

        self.stop()

    async def success_boss(self):
        fish = make_fish(self.user_id, self.boss_name)

        save_data()

        for item in self.children:
            item.disabled = True

        trait_text = ""
        if fish["trait"]:
            trait_text = f"\n특성: **{fish['trait']}**"

        await self.message.edit(
            content=(
                f"🔥🐲 **보스 낚시 성공!**\n\n"
                f"잡은 보스: **{fish['display_name']}**\n"
                f"무게: **{fish['kg']}kg**\n"
                f"기본 판매가: **{money(fish['price'])}원**\n"
                f"{get_market_text(fish['name'])}\n"
                f"현재 판매가: **{money(get_market_price(fish['name'], fish['price']))}원**"
                f"{trait_text}\n\n"
                f"사용 낚싯대: **{self.rod_name}**\n"
                f"사용 미끼: **{self.bait_name}**"
            ),
            view=self
        )

        self.stop()


class BossFishingButton(discord.ui.Button):
    def __init__(self, index):
        super().__init__(
            label="⬛",
            style=discord.ButtonStyle.gray,
            row=index // 3
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: BossFishingView = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ 니 보스 아님.", ephemeral=True)
            return

        if self.index != view.target_index:
            await interaction.response.defer()
            await view.fail_boss("잘못된 칸 클릭")
            return

        view.current_hits += 1

        for item in view.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=(
                f"✅ 명중!\n\n"
                f"보스: **{view.boss_name}**\n"
                f"진행도: **{view.current_hits}/{view.required_hits}**"
            ),
            view=view
        )


# =========================
# 낚시 성공 처리
# =========================

async def fishing_success(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)
    get_fishing_gear(user_id)
    update_fish_market()

    if random.randint(1, 100) == 1:
        stolen = int(money_data[user_id] * 0.05)
        money_data[user_id] -= stolen
        save_data()

        await interaction.response.edit_message(
            content=(
                f"🐟💀 간고등어 출현\n\n"
                f"간고등어가 당신의 지갑을 물고 튀었다..\n"
                f"💸 -{money(stolen)}원\n\n"
                f"현재 잔액: **{money(money_data[user_id])}원**"
            ),
            view=None
        )
        return

    rod_name = equipped_rods.get(user_id, "기본 낚싯대")
    bait_name = equipped_baits.get(user_id, "미끼 없음")

    rod = ROD_DATA.get(rod_name, ROD_DATA["기본 낚싯대"])
    bait = BAIT_DATA.get(bait_name, BAIT_DATA["미끼 없음"])

    luck_bonus = rod["luck"] + bait["luck"] + get_pendant_luck(user_id)

    def use_bait():
        if bait_name != "미끼 없음":
            owned_baits[user_id][bait_name] -= 1

            if owned_baits[user_id][bait_name] <= 0:
                del owned_baits[user_id][bait_name]
                equipped_baits[user_id] = "미끼 없음"

    first_fish = pick_fish(luck_bonus)

    use_bait()
    save_data()

    if first_fish in BOSS_FISH:
        view = BossFishingView(user_id, first_fish, rod_name, bait_name)

        await interaction.response.edit_message(
            content=(
                f"🌊⚠️ **수면 아래에서 거대한 그림자가 움직인다...**\n\n"
                f"🐲 보스 몹 **{first_fish}** 출현!\n"
                f"잠시 후 9칸 보스전 시작."
            ),
            view=view
        )

        view.message = await interaction.original_response()
        asyncio.create_task(view.start_round())
        return

    catch_count = 1
    roll = random.uniform(0, 100)

    if roll <= rod.get("triple_chance", 0):
        catch_count = 3
    elif roll <= rod.get("triple_chance", 0) + rod["double_chance"]:
        catch_count = 2

    fish_list = [first_fish]

    for _ in range(catch_count - 1):
        fish_name = pick_fish(luck_bonus)

        while fish_name in BOSS_FISH:
            fish_name = pick_fish(luck_bonus)

        fish_list.append(fish_name)

    bonus_text = ""

    if catch_count == 3:
        bonus_text = "\n🌊🔥 **트리플 낚시 발동!**"
    elif catch_count == 2:
        bonus_text = "\n🔥 **더블 낚시 발동!**"

    view = FishBattleView(user_id, fish_list, rod_name, bait_name)

    await interaction.response.edit_message(
        content=(
            f"🌊 물고기가 걸렸다...{bonus_text}\n"
            f"상황에 맞게 대응해야 한다!"
        ),
        view=view
    )

    view.message = await interaction.original_response()
    await view.next_round()


# =========================
# 명령어
# =========================

@bot.tree.command(name="낚시", description="버튼 타이밍에 맞춰 물고기를 낚는다", guild=GUILD)
async def fishing(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)
    get_tank(user_id)
    get_fishing_gear(user_id)

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
    update_fish_market()

    tank = fish_tanks[user_id]

    if not tank:
        await interaction.response.send_message("🐠 어항이 비어있다.")
        return

    grouped = {}
    total_value = 0

    for fish in tank:
        base_name = fish.get("name", "알 수 없음")
        trait = fish.get("trait")
        display_name = fish.get("display_name") or (f"{trait} {base_name}" if trait else base_name)
        kg = fish.get("kg", 0)
        price = get_market_price(base_name, fish.get("price", 0))
        total_value += price

        key = (base_name, trait)
        if key not in grouped:
            grouped[key] = {
                "display_name": display_name,
                "count": 0,
                "kg": 0,
                "price": 0,
            }

        grouped[key]["count"] += 1
        grouped[key]["kg"] += kg
        grouped[key]["price"] += price

    lines = []

    for (base_name, trait), info in sorted(grouped.items(), key=lambda x: x[1]["display_name"]):
        lines.append(
            f"🐟 **{info['display_name']}** x{info['count']}마리 / "
            f"총 {info['kg']:.2f}kg / 현재 판매가 {money(info['price'])}원"
        )

    save_data()

    header = f"🐠 **내 어항** | 총 {len(tank)}마리 / 묶음 {len(grouped)}개 / 예상가 {money(total_value)}원\n\n"
    content = header + "\n".join(lines)

    if len(content) <= 2000:
        await interaction.response.send_message(content)
        return

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"fish_tank_{user_id}.txt"
    )
    await interaction.response.send_message("📄 어항 목록이 길어서 txt 파일로 뽑았음.", file=file)

@bot.tree.command(name="상세어항", description="물고기 상세 정보를 txt 파일로 확인한다", guild=GUILD)
async def detail_fish_tank(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_tank(user_id)
    update_fish_market()

    tank = fish_tanks[user_id]

    if not tank:
        await interaction.response.send_message("🐠 어항이 비어있다.")
        return

    lines = ["🐠 물고기 상세 어항", ""]

    for fish in tank:
        name = get_item_display_name(fish, fish.get("name", "알 수 없음"))
        trait = fish.get("trait") or "특성 없음"
        kg = fish.get("kg", 0)
        price = get_market_price(fish.get("name", name), fish.get("price", 0))

        lines.append(
            f"{name} | [{trait}] | {kg:.2f}kg | {money(price)}원"
        )

    save_data()
    content = "\n".join(lines)

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"fish_tank_detail_{user_id}.txt"
    )
    await interaction.response.send_message("📄 물고기 상세 어항을 txt 파일로 뽑았음.", file=file)


@bot.tree.command(name="팔기", description="물고기를 판매한다.", guild=GUILD)
@app_commands.describe(
    물고기="판매할 물고기 이름",
    갯수="판매할 갯수"
)
async def sell_fish(interaction: discord.Interaction, 물고기: str, 갯수: int):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)
    update_fish_market()

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1마리 이상 팔아야 한다.", ephemeral=True)
        return

    owned = [
        fish for fish in fish_tanks[user_id]
        if fish.get("display_name", fish["name"]) == 물고기
        or fish["name"] == 물고기
    ]

    if len(owned) < 갯수:
        await interaction.response.send_message(
            f"❌ {물고기} 부족함.\n보유: {len(owned)}마리",
            ephemeral=True
        )
        return

    sell_list = owned[:갯수]
    total_price = sum(
        get_market_price(fish["name"], fish["price"])
        for fish in sell_list
    )

    removed = 0
    new_tank = []

    for fish in fish_tanks[user_id]:
        same_fish = (
            fish.get("display_name", fish["name"]) == 물고기
            or fish["name"] == 물고기
        )

        if same_fish and removed < 갯수:
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
        f"획득 금액: **{money(total_price)}원**\n\n"
        f"현재 잔액: **{money(money_data[user_id])}원**"
    )


@bot.tree.command(name="전체팔기", description="어항에 있는 모든 물고기를 판매한다.", guild=GUILD)
async def sell_all_fish(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_tank(user_id)
    update_fish_market()

    tank = fish_tanks[user_id]

    if not tank:
        await interaction.response.send_message("🐠 어항이 비어있다.", ephemeral=True)
        return

    total_price = sum(
        get_market_price(fish["name"], fish["price"])
        for fish in tank
    )

    total_count = len(tank)

    count_data = {}

    for fish in tank:
        name = fish.get("display_name", fish["name"])
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
        f"획득 금액: **{money(total_price)}원**\n\n"
        f"현재 잔액: **{money(money_data[user_id])}원**"
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
    update_fish_market()

    if 물고기 not in FISH_DATA:
        await interaction.response.send_message("❌ 그런 물고기는 없음.", ephemeral=True)
        return

    data = FISH_DATA[물고기]

    await interaction.response.send_message(
        f"🐟 **{물고기} 정보**\n\n"
        f"무게 범위: **{data['min_kg']}kg ~ {data['max_kg']}kg**\n"
        f"서식지: **{data['habitat']}**\n"
        f"기본 판매가격: **{money(data['base_price'])}원**\n"
        f"kg당 추가 가격: **{money(data['kg_price'])}원**\n"
        f"{get_market_text(물고기)}\n\n"
        f"판매가 계산식:\n"
        f"`기본 가격 + kg × kg당 가격 × 현재 시세`"
    )


@bot.tree.command(name="어시장", description="현재 물고기 시세를 확인한다", guild=GUILD)
async def fish_market_command(interaction: discord.Interaction):
    update_fish_market()
    init_fish_market()

    sorted_market = sorted(
        fish_market.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top = sorted_market[:5]
    bottom = sorted_market[-5:]

    top_text = "\n".join(
        f"📈 **{name}**: {int(rate * 100)}%"
        for name, rate in top
    )

    bottom_text = "\n".join(
        f"📉 **{name}**: {int(rate * 100)}%"
        for name, rate in bottom
    )

    await interaction.response.send_message(
        f"🏪 **현재 어시장 시세**\n\n"
        f"## 떡상 어종\n{top_text}\n\n"
        f"## 떡락 어종\n{bottom_text}\n\n"
        f"시세는 1시간마다 1~7% 변동됨.\n"
        f"최소 70%, 최대 200%."
    )


@bot.tree.command(name="낚시상점", description="낚싯대와 미끼를 구매한다", guild=GUILD)
@app_commands.describe(
    종류="낚싯대 또는 미끼",
    이름="구매할 낚싯대/미끼 이름",
    갯수="미끼 구매 수량"
)
async def fishing_shop(
    interaction: discord.Interaction,
    종류: str,
    이름: str,
    갯수: int = 1
):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_fishing_gear(user_id)
    get_mining(user_id)

    if 종류 not in ["낚싯대", "미끼"]:
        await interaction.response.send_message(
            "❌ 종류는 `낚싯대` 또는 `미끼`로 입력해야 함.",
            ephemeral=True
        )
        return

    if 종류 == "낚싯대":
        if 이름 not in ROD_DATA or 이름 == "기본 낚싯대":
            await interaction.response.send_message("❌ 그런 낚싯대는 없음.", ephemeral=True)
            return

        if 이름 in owned_rods[user_id]:
            await interaction.response.send_message("❌ 이미 가진 낚싯대임.", ephemeral=True)
            return

        rod = ROD_DATA[이름]
        price = rod["price"]
        ore_costs = rod.get("ores", {})

        if money_data[user_id] < price:
            await interaction.response.send_message(
                f"❌ 돈 부족.\n필요 금액: {money(price)}원\n현재 잔액: {money(money_data[user_id])}원",
                ephemeral=True
            )
            return

        for ore_name, need_count in ore_costs.items():
            have_count = get_ore_count(user_id, ore_name)

            if have_count < need_count:
                await interaction.response.send_message(
                    f"❌ 광석 부족.\n"
                    f"필요: **{ore_name} x{need_count}**\n"
                    f"보유: **{have_count}개**",
                    ephemeral=True
                )
                return

        money_data[user_id] -= price

        for ore_name, need_count in ore_costs.items():
            remove_ore_from_bag(user_id, ore_name, need_count)

        owned_rods[user_id].append(이름)
        equipped_rods[user_id] = 이름
        save_data()

        ore_text = ", ".join(
            f"{ore} x{count}"
            for ore, count in ore_costs.items()
        )

        if not ore_text:
            ore_text = "없음"

        await interaction.response.send_message(
            f"🎣 낚싯대 구매 완료!\n\n"
            f"구매: **{이름}**\n"
            f"가격: **{money(price)}원**\n"
            f"사용 광석: **{ore_text}**\n"
            f"자동 장착됨.\n\n"
            f"현재 잔액: **{money(money_data[user_id])}원**"
        )
        return

    if 종류 == "미끼":
        if 이름 not in BAIT_DATA or 이름 == "미끼 없음":
            await interaction.response.send_message("❌ 그런 미끼는 없음.", ephemeral=True)
            return

        if 갯수 <= 0:
            await interaction.response.send_message("❌ 1개 이상 구매해야 함.", ephemeral=True)
            return

        price = BAIT_DATA[이름]["price"] * 갯수

        if money_data[user_id] < price:
            await interaction.response.send_message(
                f"❌ 돈 부족.\n필요 금액: {money(price)}원\n현재 잔액: {money(money_data[user_id])}원",
                ephemeral=True
            )
            return

        money_data[user_id] -= price
        owned_baits[user_id][이름] = owned_baits[user_id].get(이름, 0) + 갯수
        equipped_baits[user_id] = 이름
        save_data()

        await interaction.response.send_message(
            f"🪱 미끼 구매 완료!\n\n"
            f"구매: **{이름} x{갯수}개**\n"
            f"가격: **{money(price)}원**\n"
            f"자동 장착됨.\n\n"
            f"현재 잔액: **{money(money_data[user_id])}원**"
        )


@bot.tree.command(name="낚시상점목록", description="낚시상점 판매 목록 확인", guild=GUILD)
async def fishing_shop_list(interaction: discord.Interaction):
    rod_lines = []

    for name, data in ROD_DATA.items():
        if name == "기본 낚싯대":
            continue

        ore_text = ", ".join(
            f"{ore} x{count}"
            for ore, count in data.get("ores", {}).items()
        )

        if not ore_text:
            ore_text = "없음"

        rod_lines.append(
            f"**{name}**\n"
            f"가격: **{money(data['price'])}원**\n"
            f"재료: **{ore_text}**\n"
            f"운빨: **+{data['luck']}%**\n"
            f"시간 감소: **{data['time_reduce']}%**\n"
            f"더블 확률: **{data['double_chance']}%**\n"
            f"트리플 확률: **{data['triple_chance']}%**"
        )

    rod_text = "\n\n".join(rod_lines)

    bait_text = "\n".join(
        f"**{name}** - {money(data['price'])}원 / 희귀 확률 +{data['luck']}%"
        for name, data in BAIT_DATA.items()
        if name != "미끼 없음"
    )

    await interaction.response.send_message(
        f"🎣 **낚시상점 목록**\n\n"
        f"## 낚싯대\n{rod_text}\n\n"
        f"## 미끼\n{bait_text}\n\n"
        f"구매법: `/낚시상점 종류 이름 갯수`\n"
        f"예시: `/낚시상점 낚싯대 강태공의 낚싯대`\n"
        f"예시: `/낚시상점 미끼 지렁이 5`"
    )


@bot.tree.command(name="보유낚싯대", description="내가 가진 낚싯대를 확인한다", guild=GUILD)
async def my_rods(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_fishing_gear(user_id)

    equipped = equipped_rods[user_id]

    text = []

    for rod_name in owned_rods[user_id]:
        rod = ROD_DATA[rod_name]
        mark = "✅ 장착중" if rod_name == equipped else ""

        text.append(
            f"{mark} **{rod_name}**\n"
            f"운빨 증가: **{rod['luck']}%**\n"
            f"잡히는 시간 감소율: **{rod['time_reduce']}%**\n"
            f"더블 확률: **{rod['double_chance']}%**\n"
            f"트리플 확률: **{rod['triple_chance']}%**"
        )

    await interaction.response.send_message(
        "🎣 **보유 낚싯대**\n\n" + "\n\n".join(text)
    )


@bot.tree.command(name="낚싯대", description="보유한 낚싯대를 장착한다", guild=GUILD)
@app_commands.describe(이름="장착할 낚싯대 이름")
async def equip_rod(interaction: discord.Interaction, 이름: str):
    user_id = interaction.user.id
    get_fishing_gear(user_id)

    if 이름 not in owned_rods[user_id]:
        await interaction.response.send_message("❌ 그 낚싯대는 보유중이 아님.", ephemeral=True)
        return

    equipped_rods[user_id] = 이름
    save_data()

    await interaction.response.send_message(
        f"🎣 낚싯대 장착 완료!\n현재 낚싯대: **{이름}**"
    )


@bot.tree.command(name="미끼", description="보유한 미끼를 장착하거나 목록을 확인한다", guild=GUILD)
@app_commands.describe(이름="장착할 미끼 이름. 비워두면 목록 확인")
async def equip_bait(interaction: discord.Interaction, 이름: str = None):
    user_id = interaction.user.id
    get_fishing_gear(user_id)

    if 이름 is None:
        bait_items = owned_baits[user_id]

        if not bait_items:
            bait_text = "보유 미끼 없음."
        else:
            bait_text = "\n".join(
                f"**{name}**: {count}개 / 희귀 확률 +{BAIT_DATA[name]['luck']}%"
                for name, count in bait_items.items()
            )

        await interaction.response.send_message(
            f"🪱 **보유 미끼**\n\n"
            f"현재 장착: **{equipped_baits[user_id]}**\n\n"
            f"{bait_text}\n\n"
            f"미끼 해제는 `/미끼 미끼 없음`"
        )
        return

    if 이름 == "미끼 없음":
        equipped_baits[user_id] = "미끼 없음"
        save_data()

        await interaction.response.send_message("🪱 미끼를 해제함.")
        return

    if 이름 not in BAIT_DATA:
        await interaction.response.send_message("❌ 그 미끼는 없음.", ephemeral=True)
        return

    if owned_baits[user_id].get(이름, 0) <= 0:
        await interaction.response.send_message("❌ 그 미끼는 보유중이 아님.", ephemeral=True)
        return

    equipped_baits[user_id] = 이름
    save_data()

    await interaction.response.send_message(
        f"🪱 미끼 장착 완료!\n현재 미끼: **{이름}**"
    )

LOST_ITEM_REWARDS = ["누군가의 지갑", "잃어버린 카드", "카시오 시계"]


class LostItemReturnView(discord.ui.View):
    def __init__(self, user_id, fish):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.fish = fish
        self.message = None

    @discord.ui.button(label="주인 찾기", style=discord.ButtonStyle.green)
    async def find_owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 니가 주운 거 아님.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True

        wait_time = random.randint(100, 300)

        await interaction.response.edit_message(
            content=(
                f"🔎 **{self.fish['display_name']}**의 주인을 찾는 중...\n\n"
                f"⏳ 예상 시간: **{wait_time}초**"
            ),
            view=self
        )

        await asyncio.sleep(wait_time)

        reward = random.randint(100000, 200000)

        get_wallet(self.user_id)
        money_data[self.user_id] += reward
        save_data()

        await interaction.edit_original_response(
            content=(
                f"🙇‍♂️ 주인이 찾아왔다!\n\n"
                f"“정말 감사합니다! 이거라도 받아주세요.”\n\n"
                f"🎁 보상금: **{money(reward)}원**\n"
                f"현재 잔액: **{money(money_data[self.user_id])}원**"
            ),
            view=None
        )

        self.stop()

    @discord.ui.button(label="그냥 보관하기", style=discord.ButtonStyle.gray)
    async def keep_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 니가 주운 거 아님.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=f"🎒 **{self.fish['display_name']}**을 그냥 어항에 보관했다.",
            view=None
        )

        self.stop()

@bot.tree.command(name="어시장리셋", description="어시장 시세를 초기화한다", guild=GUILD)
@app_commands.checks.has_permissions(administrator=True)
async def reset_fish_market(interaction: discord.Interaction):

    init_fish_market()

    for fish_name in FISH_DATA.keys():
        fish_market[fish_name] = 1.0

    global last_market_update
    last_market_update = datetime.now()

    save_data()

    text = "\n".join(
        f"{name}: 100%"
        for name in list(FISH_DATA.keys())[:10]
    )

    await interaction.response.send_message(
        f"🔄 **어시장 시세 초기화 완료!**\n\n"
        f"모든 물고기 시세가 **100%**로 초기화됨."
    )


@reset_fish_market.error
async def reset_fish_market_error(
    interaction: discord.Interaction,
    error
):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ 관리자만 사용 가능.",
            ephemeral=True
        )
# =========================
# 농사 시스템
# =========================

farm_data = globals().get("farm_data", {})
crop_dex = globals().get("crop_dex", {})
crop_prices = globals().get("crop_prices", {})

FARM_SIZE = 9
FERTILIZER_PRICE = 1500
WATER_REDUCE_RATE = 0.20

FARM_REGIONS = [
    "동부 농장",
    "서부 농장",
    "남부 농장",
    "북부 농장"
]

REGION_EMOJI = {
    "풍년": "🌾",
    "보통": "➖",
    "흉년": "🥀"
}

REGION_EFFECTS = {
    "풍년": {
        "grow_mult": 0.85,
        "yield_mult": 1.50,
        "trait_bonus": 20,
        "bad_trait_bonus": -15,
        "wither_chance": 0
    },
    "보통": {
        "grow_mult": 1.00,
        "yield_mult": 1.00,
        "trait_bonus": 0,
        "bad_trait_bonus": 0,
        "wither_chance": 0
    },
    "흉년": {
        "grow_mult": 1.25,
        "yield_mult": 0.60,
        "trait_bonus": -20,
        "bad_trait_bonus": 25,
        "wither_chance": 8
    }
}

# 펜던트 농사 전용 보너스
# 기존 PENDANT_DATA의 luck도 같이 적용되고, 아래 이름이 장착되어 있으면 추가 효과가 붙음.
PENDANT_FARM_BONUS = {
    "돌 펜던트": {"trait_bonus": 1, "yield_bonus": 0.01, "grow_reduce": 0.00, "wither_reduce": 0},
    "금 펜던트": {"trait_bonus": 3, "yield_bonus": 0.02, "grow_reduce": 0.01, "wither_reduce": 0},
    "다이아 펜던트": {"trait_bonus": 5, "yield_bonus": 0.04, "grow_reduce": 0.02, "wither_reduce": 1},
    "루비 펜던트": {"trait_bonus": 8, "yield_bonus": 0.02, "grow_reduce": 0.01, "wither_reduce": 0},
    "사파이어 펜던트": {"trait_bonus": 4, "yield_bonus": 0.03, "grow_reduce": 0.04, "wither_reduce": 1},
    "에메랄드 펜던트": {"trait_bonus": 4, "yield_bonus": 0.10, "grow_reduce": 0.02, "wither_reduce": 1},
    "흑요석 펜던트": {"trait_bonus": 2, "yield_bonus": 0.03, "grow_reduce": 0.01, "wither_reduce": 6},
    "레드 다이아몬드 펜던트": {"trait_bonus": 10, "yield_bonus": 0.08, "grow_reduce": 0.04, "wither_reduce": 2},
    "레인보우 다이아몬드 펜던트": {"trait_bonus": 15, "yield_bonus": 0.15, "grow_reduce": 0.07, "wither_reduce": 4},
    "신기루 펜던트": {"trait_bonus": 25, "yield_bonus": 0.25, "grow_reduce": 0.12, "wither_reduce": 8}
}

SEED_DATA = {
    "감자": {"seed_price": 250, "base_price": 830, "grow_min": 60, "grow_max": 180, "min_yield": 1, "max_yield": 3},
    "당근": {"seed_price": 600, "base_price": 1500, "grow_min": 120, "grow_max": 300, "min_yield": 1, "max_yield": 3},
    "토마토": {"seed_price": 1300, "base_price": 3000, "grow_min": 300, "grow_max": 600, "min_yield": 1, "max_yield": 4},
    "딸기": {"seed_price": 3200, "base_price": 7000, "grow_min": 600, "grow_max": 1200, "min_yield": 1, "max_yield": 4},
    "황금옥수수": {"seed_price": 85000, "base_price": 23000, "grow_min": 900, "grow_max": 2100, "min_yield": 1, "max_yield": 3},
    "만년초": {"seed_price": 45000, "base_price": 800000, "grow_min": 1800, "grow_max": 3600, "min_yield": 1, "max_yield": 2},
    "킹갓제너럴암튼겁나대단한킹왕짱히루루크도울고갈레전설의채소": {
        "seed_price": 700000,
        "base_price": 1500000,
        "grow_min": 129600,
        "grow_max": 129600,
        "min_yield": 1,
        "max_yield": 1
    },
    "도로롱": {"seed_price": 5000000, "base_price": 25000000, "grow_min": 500000, "grow_max": 700000, "min_yield": 1, "max_yield": 1}
}

CROP_TRAITS = {
    # 좋은 특성
    "싱싱한": {"price_mult": 1.20, "yield_mult": 1.10, "type": "good", "chance": 100},
    "튼실한": {"price_mult": 1.15, "yield_mult": 1.30, "type": "good", "chance": 85},
    "거대한": {"price_mult": 1.50, "yield_mult": 1.50, "type": "good", "chance": 45},
    "황금빛": {"price_mult": 2.50, "yield_mult": 1.00, "type": "good", "chance": 18},
    "무지개빛": {"price_mult": 4.00, "yield_mult": 2.00, "type": "good", "chance": 5},
    "신의 축복을 받은": {"price_mult": 6.00, "yield_mult": 2.50, "type": "good", "chance": 1},

    # 나쁜 특성
    "시든": {"price_mult": 0.70, "yield_mult": 0.80, "type": "bad", "chance": 45},
    "벌레먹은": {"price_mult": 0.50, "yield_mult": 0.70, "type": "bad", "chance": 30},
    "말라비틀어진": {"price_mult": 0.40, "yield_mult": 0.60, "type": "bad", "chance": 15}
}


def get_farm_upgrade(user_id):
    changed = False

    if user_id not in farm_levels:
        farm_levels[user_id] = 1
        changed = True

    if user_id not in field_sizes:
        field_sizes[user_id] = 9
        changed = True

    return changed


def get_crop_upgrade_bonus(user_id):
    level = farm_levels.get(user_id, 1)
    return 1 + ((level - 1) * 0.2)


def safe_get_pendant_luck(user_id):
    try:
        get_pendant(user_id)
        return get_pendant_luck(user_id)
    except Exception:
        return 0


def get_equipped_pendants_safe(user_id):
    try:
        get_pendant(user_id)
        return equipped_pendants.get(user_id, [])
    except Exception:
        return []


def get_farm_pendant_bonus(user_id):
    luck = safe_get_pendant_luck(user_id)

    bonus = {
        "luck": luck,
        "trait_bonus": min(30, luck // 8),
        "yield_bonus": min(0.35, luck / 500),
        "grow_reduce": min(0.20, luck / 700),
        "wither_reduce": min(5, luck // 25)
    }

    for pendant in get_equipped_pendants_safe(user_id):
        extra = PENDANT_FARM_BONUS.get(pendant)
        if not extra:
            continue

        bonus["trait_bonus"] += extra.get("trait_bonus", 0)
        bonus["yield_bonus"] += extra.get("yield_bonus", 0)
        bonus["grow_reduce"] += extra.get("grow_reduce", 0)
        bonus["wither_reduce"] += extra.get("wither_reduce", 0)

    bonus["trait_bonus"] = min(50, bonus["trait_bonus"])
    bonus["yield_bonus"] = min(0.75, bonus["yield_bonus"])
    bonus["grow_reduce"] = min(0.40, bonus["grow_reduce"])
    bonus["wither_reduce"] = min(20, bonus["wither_reduce"])

    return bonus


def get_farm_today_key():
    # 서버 시간이 UTC여도 한국 날짜 기준으로 24시간마다 바뀌게 함.
    return (datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d")


def get_daily_region_status():
    # 저장 데이터 추가 없이도 하루 동안 같은 결과가 유지됨.
    rng = random.Random(get_farm_today_key())
    regions = FARM_REGIONS[:]
    rng.shuffle(regions)

    bad = regions[0]
    good_regions = regions[1:3]

    status = {}
    for region in FARM_REGIONS:
        if region == bad:
            status[region] = "흉년"
        elif region in good_regions:
            status[region] = "풍년"
        else:
            status[region] = "보통"

    return status


def get_region_status(region):
    return get_daily_region_status().get(region, "보통")


def get_plot_region(index):
    return FARM_REGIONS[index % len(FARM_REGIONS)]


def get_current_region(user_id):
    get_farm(user_id)

    if "current_region" not in farm_data[user_id]:
        farm_data[user_id]["current_region"] = FARM_REGIONS[0]
        save_data()

    return farm_data[user_id]["current_region"]


def fix_datetime(value):
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    return None


def weighted_choice_from_dict(data_dict, names):
    weights = [data_dict[name]["chance"] for name in names]
    return random.choices(names, weights=weights, k=1)[0]


def roll_crop_trait(user_id, region):
    status = get_region_status(region)
    effect = REGION_EFFECTS[status]
    pendant_bonus = get_farm_pendant_bonus(user_id)

    trait_chance = 50 + effect["trait_bonus"] + pendant_bonus["trait_bonus"]
    trait_chance = max(5, min(95, trait_chance))

    if random.randint(1, 100) > trait_chance:
        return None

    good_traits = [name for name, data in CROP_TRAITS.items() if data["type"] == "good"]
    bad_traits = [name for name, data in CROP_TRAITS.items() if data["type"] == "bad"]

    good_chance = 75 + pendant_bonus["trait_bonus"] - effect["bad_trait_bonus"]
    good_chance = max(25, min(95, good_chance))

    if random.randint(1, 100) <= good_chance:
        return weighted_choice_from_dict(CROP_TRAITS, good_traits)

    return weighted_choice_from_dict(CROP_TRAITS, bad_traits)


def get_farm(user_id):
    changed = False

    if get_farm_upgrade(user_id):
        changed = True

    if user_id not in farm_data or not isinstance(farm_data[user_id], dict):
        farm_data[user_id] = {}
        changed = True

    farm = farm_data[user_id]

    if "seeds" not in farm or not isinstance(farm["seeds"], dict):
        farm["seeds"] = {}
        changed = True

    if "fertilizer" not in farm:
        farm["fertilizer"] = 0
        changed = True

    if "current_region" not in farm or farm["current_region"] not in FARM_REGIONS:
        # 현재 선택한 재배 지역. /이동으로 바뀌고, /심기 때 이 지역 버프가 저장됨.
        farm["current_region"] = FARM_REGIONS[0]
        changed = True

    if "field" not in farm or not isinstance(farm["field"], list):
        farm["field"] = [None for _ in range(9)]
        changed = True

    target_size = field_sizes.get(user_id, 9)

    if target_size < 9:
        target_size = 9
        field_sizes[user_id] = 9
        changed = True

    while len(farm["field"]) < target_size:
        farm["field"].append(None)
        changed = True

    if len(farm["field"]) > target_size:
        farm["field"] = farm["field"][:target_size]
        changed = True

    if "crops" not in farm or not isinstance(farm["crops"], dict):
        farm["crops"] = {}
        changed = True

    # 새 헛간 구조: 농작물도 물고기/광석처럼 개별 아이템으로 관리한다.
    if "crop_items" not in farm or not isinstance(farm["crop_items"], list):
        farm["crop_items"] = []

        old_crops = farm.get("crops", {})
        if isinstance(old_crops, dict):
            for item_name, count in old_crops.items():
                if not isinstance(count, int) or count <= 0:
                    continue

                crop_name, trait_name = parse_crop_item_name(item_name)
                for _ in range(count):
                    farm["crop_items"].append({
                                        "name": crop_name or item_name,
                        "display_name": item_name,
                        "trait": trait_name,
                        "price": get_crop_price_for_user(user_id, item_name) or 0
                    })

        changed = True


    for name in SEED_DATA:
        if name not in farm["seeds"]:
            farm["seeds"][name] = 0
            changed = True

        if name not in farm["crops"]:
            farm["crops"][name] = 0
            changed = True

    # 기존 데이터 호환: 예전 작물에는 region/watered/yield 정보가 없을 수 있음.
    for index, plot in enumerate(farm["field"]):
        if not isinstance(plot, dict):
            continue

        if "region" not in plot:
            plot["region"] = get_plot_region(index)
            changed = True

        if "watered" not in plot:
            plot["watered"] = False
            changed = True

        if "yield" not in plot:
            plot["yield"] = 1
            changed = True

        if "trait" not in plot:
            plot["trait"] = None
            changed = True

        if "withered" not in plot:
            plot["withered"] = False
            changed = True

    if user_id not in crop_dex or not isinstance(crop_dex[user_id], set):
        crop_dex[user_id] = set(crop_dex.get(user_id, []))
        changed = True

    if changed:
        save_data()

    return changed


def update_crop_prices():
    for crop_name, seed in SEED_DATA.items():
        if crop_name not in crop_prices:
            crop_prices[crop_name] = seed["base_price"]

        current = crop_prices[crop_name]
        base = seed["base_price"]

        change_rate = random.randint(1, 7) / 100

        if random.choice([True, False]):
            current = int(current * (1 + change_rate))
        else:
            current = int(current * (1 - change_rate))

        min_price = int(base * 0.7)
        max_price = int(base * 1.7)

        crop_prices[crop_name] = max(min_price, min(max_price, current))

    save_data()


@tasks.loop(hours=1)
async def crop_price_loop():
    update_crop_prices()


def parse_crop_item_name(item_name):
    # "황금빛 감자" 같은 특성 작물도 판매 가능하게 처리.
    if item_name in SEED_DATA:
        return item_name, None

    for crop_name in sorted(SEED_DATA.keys(), key=len, reverse=True):
        suffix = f" {crop_name}"
        if item_name.endswith(suffix):
            trait_name = item_name[:-len(suffix)]
            if trait_name in CROP_TRAITS:
                return crop_name, trait_name

    return None, None


def get_crop_price_for_user(user_id, item_name):
    crop_name, trait_name = parse_crop_item_name(item_name)

    if crop_name is None:
        return None

    if not crop_prices:
        update_crop_prices()

    base = crop_prices.get(crop_name, SEED_DATA[crop_name]["base_price"])
    price = base * get_crop_upgrade_bonus(user_id)

    if trait_name:
        price *= CROP_TRAITS[trait_name]["price_mult"]

    return int(price)


def get_crop_item_name(crop_name, trait_name):
    if trait_name:
        return f"{trait_name} {crop_name}"
    return crop_name


def make_crop_yield(user_id, crop_name, region, trait_name):
    if crop_name not in SEED_DATA:
        print(f"알 수 없는 작물: {crop_name}")
        return 1

    seed = SEED_DATA[crop_name]
    base_yield = random.randint(seed.get("min_yield", 1), seed.get("max_yield", 1))

    status = get_region_status(region)
    effect = REGION_EFFECTS[status]
    pendant_bonus = get_farm_pendant_bonus(user_id)

    total_yield = base_yield * effect["yield_mult"] * (1 + pendant_bonus["yield_bonus"])

    if trait_name:
        total_yield *= CROP_TRAITS[trait_name]["yield_mult"]

    return max(1, int(round(total_yield)))


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

        for name, seed in SEED_DATA.items():
            seed_lines.append(
                f"🌱 {name}\n"
                f"씨앗 가격: {seed['seed_price']}원\n"
                f"기준 판매가: {seed['base_price']}원\n"
                f"성장 시간: {seed['grow_min']}초 ~ {seed['grow_max']}초\n"
                f"기본 수확량: {seed.get('min_yield', 1)}개 ~ {seed.get('max_yield', 1)}개"
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
    
@bot.tree.command(name="농밭", description="현재 이동한 농밭 상태 확인", guild=GUILD)
async def farm_field(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    current_region = get_current_region(user_id)
    status = get_region_status(current_region)

    lines = []

    for i, plot in enumerate(farm_data[user_id]["field"]):
        display_num = i + 1

        if plot is None:
            lines.append(f"{display_num}번 밭: 비어있음")
            continue

        # 현재 지역만 표시
        if plot.get("region") != current_region:
            continue

        harvest_time = fix_datetime(plot.get("harvest_time"))

        if harvest_time is None:
            lines.append(f"{display_num}번 밭: ⚠️ 시간 오류")
            continue

        crop_name = plot["crop"]

        if now >= harvest_time:
            lines.append(f"{display_num}번 밭: 🌾 {crop_name} 수확 가능")
        else:
            remain = int((harvest_time - now).total_seconds())

            minutes = remain // 60
            seconds = remain % 60

            lines.append(
                f"{display_num}번 밭: 🌱 {crop_name} 성장중 "
                f"({minutes}분 {seconds}초)"
            )

    if not lines:
        lines.append("현재 지역에 심어진 작물이 없음.")

    await interaction.response.send_message(
        f"🚜 현재 지역: **{current_region}**\n"
        f"📍 상태: **{status}**\n\n"
        + "\n".join(lines)
    )
    
@bot.tree.command(name="심기", description="현재 이동한 지역에서 씨앗을 심는다", guild=GUILD)
@app_commands.describe(
    작물="심을 작물 이름",
    비료사용="비료를 사용할지 여부"
)
async def plant_crop(
    interaction: discord.Interaction,
    작물: str,
    비료사용: bool = False
):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    if 작물 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 작물 없음.", ephemeral=True)
        return

    if farm_data[user_id]["seeds"].get(작물, 0) <= 0:
        await interaction.response.send_message(f"❌ {작물} 씨앗 없음.", ephemeral=True)
        return

    if 비료사용 and farm_data[user_id].get("fertilizer", 0) <= 0:
        await interaction.response.send_message("❌ 비료가 없음.", ephemeral=True)
        return

    target_index = None

    for i, plot in enumerate(farm_data[user_id]["field"]):
        if plot is None:
            target_index = i
            break

    if target_index is None:
        await interaction.response.send_message("❌ 빈 밭이 없음.", ephemeral=True)
        return

    region = get_current_region(user_id)
    status = get_region_status(region)
    effect = REGION_EFFECTS[status]
    pendant_bonus = get_farm_pendant_bonus(user_id)

    seed = SEED_DATA[작물]
    grow_time = random.randint(seed["grow_min"], seed["grow_max"])
    grow_time = int(grow_time * effect["grow_mult"])
    grow_time = int(grow_time * (1 - pendant_bonus["grow_reduce"]))

    if 비료사용:
        grow_time = int(grow_time * 0.5)
        farm_data[user_id]["fertilizer"] -= 1

    farm_data[user_id]["seeds"][작물] -= 1

    farm_data[user_id]["field"][target_index] = {
        "crop": 작물,
        "planted_at": now,
        "harvest_time": now + timedelta(seconds=grow_time),
        "watered": False,
        "fertilizer": 비료사용,
        "region": region,
        "yield": 1,
        "trait": None,
        "withered": False
    }

    save_data()

    await interaction.response.send_message(
        f"🌱 **{작물}** 심었음!\n\n"
        f"밭 칸: **{target_index + 1}번**\n"
        f"심은 지역: **{region} / {status}**\n"
        f"비료 사용: **{'사용함' if 비료사용 else '안 씀'}**\n"
        f"수확까지: **{grow_time // 60}분 {grow_time % 60}초**"
    )

@bot.tree.command(name="전체심기", description="현재 이동한 지역에서 빈 밭 전체에 씨앗을 심는다", guild=GUILD)
@app_commands.describe(
    작물="심을 작물 이름",
    비료사용="비료를 사용할지 여부"
)
async def mass_plant(
    interaction: discord.Interaction,
    작물: str,
    비료사용: bool = False
):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    if 작물 not in SEED_DATA:
        await interaction.response.send_message("❌ 그런 작물 없음.", ephemeral=True)
        return

    owned = farm_data[user_id]["seeds"].get(작물, 0)

    if owned <= 0:
        await interaction.response.send_message(f"❌ {작물} 씨앗 없음.", ephemeral=True)
        return

    fertilizer_count = farm_data[user_id].get("fertilizer", 0)

    if 비료사용 and fertilizer_count <= 0:
        await interaction.response.send_message("❌ 비료가 없음.", ephemeral=True)
        return

    empty_plots = [
        i for i, plot in enumerate(farm_data[user_id]["field"])
        if plot is None
    ]

    if not empty_plots:
        await interaction.response.send_message("❌ 빈 밭이 없음.", ephemeral=True)
        return

    plant_count = min(len(empty_plots), owned)

    if 비료사용:
        plant_count = min(plant_count, fertilizer_count)

    region = get_current_region(user_id)
    status = get_region_status(region)
    effect = REGION_EFFECTS[status]
    pendant_bonus = get_farm_pendant_bonus(user_id)

    planted = 0

    for i in empty_plots[:plant_count]:
        seed = SEED_DATA[작물]
        grow_time = random.randint(seed["grow_min"], seed["grow_max"])
        grow_time = int(grow_time * effect["grow_mult"])
        grow_time = int(grow_time * (1 - pendant_bonus["grow_reduce"]))

        if 비료사용:
            grow_time = int(grow_time * 0.5)

        farm_data[user_id]["field"][i] = {
            "crop": 작물,
            "planted_at": now,
            "harvest_time": now + timedelta(seconds=grow_time),
            "watered": False,
            "fertilizer": 비료사용,
            "region": region,
            "yield": 1,
            "trait": None,
            "withered": False
        }

        planted += 1

    farm_data[user_id]["seeds"][작물] -= planted

    if 비료사용:
        farm_data[user_id]["fertilizer"] -= planted

    save_data()

    await interaction.response.send_message(
        f"🌱 **{작물} 전체심기 완료!**\n\n"
        f"심은 지역: **{region} / {status}**\n"
        f"심은 개수: **{planted}개**\n"
        f"비료 사용: **{'사용함' if 비료사용 else '안 씀'}**\n"
        f"남은 씨앗: **{farm_data[user_id]['seeds'][작물]}개**\n"
        f"남은 비료: **{farm_data[user_id]['fertilizer']}개**"
    )

@bot.tree.command(name="물주기", description="농밭에 물을 줘서 남은 성장 시간을 줄인다", guild=GUILD)
@app_commands.describe(칸="물을 줄 밭 칸")
async def water_crop(interaction: discord.Interaction, 칸: int):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    max_size = len(farm_data[user_id]["field"])

    if 칸 < 1 or 칸 > max_size:
        await interaction.response.send_message(f"❌ 밭 칸은 1~{max_size}번만 가능.", ephemeral=True)
        return

    index = 칸 - 1
    plot = farm_data[user_id]["field"][index]

    if plot is None:
        await interaction.response.send_message("❌ 이 칸은 비어있음.", ephemeral=True)
        return

    if plot.get("watered"):
        await interaction.response.send_message("❌ 이미 물 준 밭임.", ephemeral=True)
        return

    harvest_time = fix_datetime(plot.get("harvest_time"))

    if harvest_time is None:
        await interaction.response.send_message("⚠️ 작물 시간 데이터 오류.", ephemeral=True)
        return

    if now >= harvest_time:
        await interaction.response.send_message("🌾 이미 다 자라서 물 줄 필요 없음.", ephemeral=True)
        return

    remaining = harvest_time - now
    reduced_seconds = int(remaining.total_seconds() * WATER_REDUCE_RATE)
    plot["harvest_time"] = harvest_time - timedelta(seconds=reduced_seconds)
    plot["watered"] = True

    save_data()

    await interaction.response.send_message(
        f"💧 {칸}번 밭에 물을 줌!\n"
        f"성장 시간이 **{reduced_seconds}초** 단축됨."
    )


@bot.tree.command(name="전체물주기", description="물을 줄 수 있는 모든 밭에 물을 준다", guild=GUILD)
async def water_all_crop(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    watered_count = 0
    total_reduced = 0

    for plot in farm_data[user_id]["field"]:
        if plot is None or plot.get("watered"):
            continue

        harvest_time = fix_datetime(plot.get("harvest_time"))
        if harvest_time is None or now >= harvest_time:
            continue

        reduced_seconds = int((harvest_time - now).total_seconds() * WATER_REDUCE_RATE)
        plot["harvest_time"] = harvest_time - timedelta(seconds=reduced_seconds)
        plot["watered"] = True
        watered_count += 1
        total_reduced += reduced_seconds

    if watered_count <= 0:
        await interaction.response.send_message("💧 물 줄 수 있는 밭이 없음.", ephemeral=True)
        return

    save_data()

    await interaction.response.send_message(
        f"💧 **전체 물주기 완료!**\n\n"
        f"물 준 밭: **{watered_count}칸**\n"
        f"총 단축 시간: **{total_reduced}초**"
    )


def harvest_one_plot(user_id, index, now):
    plot = farm_data[user_id]["field"][index]

    if plot is None:
        return None

    harvest_time = fix_datetime(plot.get("harvest_time"))
    if harvest_time is None or now < harvest_time:
        return None

    crop_name = plot["crop"]
    region = plot.get("region", get_plot_region(index))
    status = get_region_status(region)
    effect = REGION_EFFECTS[status]
    pendant_bonus = get_farm_pendant_bonus(user_id)

    wither_chance = max(0, effect["wither_chance"] - pendant_bonus["wither_reduce"])
    withered = random.randint(1, 100) <= wither_chance

    trait_name = None if withered else roll_crop_trait(user_id, region)
    amount = 1 if withered else make_crop_yield(user_id, crop_name, region, trait_name)

    if withered:
        item_name = f"시든 {crop_name}"
        if "시든" in CROP_TRAITS:
            trait_name = "시든"
    else:
        item_name = get_crop_item_name(crop_name, trait_name)

    if "crop_items" not in farm_data[user_id] or not isinstance(farm_data[user_id]["crop_items"], list):
        farm_data[user_id]["crop_items"] = []

    unit_price = get_crop_price_for_user(user_id, item_name) or 0

    for _ in range(amount):
        farm_data[user_id]["crop_items"].append({
                "name": crop_name,
            "display_name": item_name,
            "trait": trait_name,
            "price": unit_price,
            "region": region,
            "status": status,
            "withered": withered
        })

    # 구버전 명령어 호환용 카운트도 유지.
    farm_data[user_id]["crops"][item_name] = farm_data[user_id]["crops"].get(item_name, 0) + amount
    crop_dex[user_id].add(crop_name)
    farm_data[user_id]["field"][index] = None

    return {
        "crop": crop_name,
        "item": item_name,
        "trait": trait_name,
        "amount": amount,
        "region": region,
        "status": status,
        "withered": withered
    }


@bot.tree.command(name="수확", description="다 자란 농작물을 수확한다", guild=GUILD)
@app_commands.describe(칸="수확할 밭 칸")
async def harvest_crop(interaction: discord.Interaction, 칸: int):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    max_size = len(farm_data[user_id]["field"])

    if 칸 < 1 or 칸 > max_size:
        await interaction.response.send_message(f"❌ 밭 칸은 1~{max_size}번만 가능.", ephemeral=True)
        return

    index = 칸 - 1
    plot = farm_data[user_id]["field"][index]

    if plot is None:
        await interaction.response.send_message("❌ 이 칸은 비어있음.", ephemeral=True)
        return

    harvest_time = fix_datetime(plot.get("harvest_time"))

    if harvest_time is None:
        await interaction.response.send_message("⚠️ 작물 시간 데이터 오류.", ephemeral=True)
        return

    if now < harvest_time:
        remain = int((harvest_time - now).total_seconds())
        await interaction.response.send_message(f"❌ 아직 덜 자람. {remain}초 남음.", ephemeral=True)
        return

    result = harvest_one_plot(user_id, index, now)
    save_data()

    trait_text = result["trait"] if result["trait"] else "없음"
    wither_text = "\n🥀 흉년 피해로 작물이 시들었음..." if result["withered"] else ""

    await interaction.response.send_message(
        f"🌾 수확 완료!\n"
        f"구역: **{result['region']} / {result['status']}**\n"
        f"특성: **{trait_text}**\n"
        f"획득 농작물: **{result['item']} {result['amount']}개**"
        f"{wither_text}"
    )


@bot.tree.command(name="전체수확", description="다 자란 농작물을 전부 수확한다", guild=GUILD)
async def harvest_all_crop(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    harvested = {}
    region_log = {}
    withered_count = 0

    for i, plot in enumerate(farm_data[user_id]["field"]):
        result = harvest_one_plot(user_id, i, now)
        if result is None:
            continue

        harvested[result["item"]] = harvested.get(result["item"], 0) + result["amount"]
        region_key = f"{result['region']} / {result['status']}"
        region_log[region_key] = region_log.get(region_key, 0) + 1

        if result["withered"]:
            withered_count += 1

    if not harvested:
        await interaction.response.send_message("🌱 수확 가능한 농작물이 없음.", ephemeral=True)
        return

    save_data()

    crop_text = "\n".join(f"{name}: {count}개" for name, count in harvested.items())
    region_text = "\n".join(f"{name}: {count}칸" for name, count in region_log.items())

    await interaction.response.send_message(
        f"🌾 **전체 수확 완료!**\n\n"
        f"{crop_text}\n\n"
        f"📍 **구역별 수확**\n{region_text}\n\n"
        f"🥀 시든 작물: **{withered_count}개**"
    )


@bot.tree.command(name="판매", description="농작물을 판매한다", guild=GUILD)
@app_commands.describe(
    농작물="판매할 농작물 이름. 예: 감자 / 황금빛 감자",
    갯수="판매할 갯수"
)
async def sell_crop(interaction: discord.Interaction, 농작물: str, 갯수: int):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1개 이상 팔아야 함.", ephemeral=True)
        return

    crop_items = farm_data[user_id].setdefault("crop_items", [])
    owned = [
        item for item in crop_items
        if get_item_display_name(item) == 농작물 or item.get("name") == 농작물
    ]

    if len(owned) < 갯수:
        await interaction.response.send_message(
            f"❌ {농작물} 부족함.\n보유: {len(owned)}개",
            ephemeral=True
        )
        return

    sell_list = owned[:갯수]
    total = 0

    for item in sell_list:
        item_name = get_item_display_name(item, 농작물)
        total += get_crop_price_for_user(user_id, item_name) or item.get("price", 0)

    for item in sell_list:
        crop_items.remove(item)
        item_name = get_item_display_name(item, 농작물)
        if item_name in farm_data[user_id]["crops"]:
            farm_data[user_id]["crops"][item_name] = max(0, farm_data[user_id]["crops"][item_name] - 1)

    money_data[user_id] += total
    save_data()

    await interaction.response.send_message(
        f"💰 판매 완료!\n\n"
        f"농작물: **{농작물}**\n"
        f"수량: **{갯수}개**\n"
        f"총 판매가: **{total:,}원**\n\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )


@bot.tree.command(name="전체판매", description="보유한 농작물을 전부 판매한다", guild=GUILD)
async def sell_all_crop(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)

    crop_items = farm_data[user_id].setdefault("crop_items", [])

    if not crop_items:
        await interaction.response.send_message("❌ 팔 농작물이 없음.", ephemeral=True)
        return

    sold = {}
    total_price = 0

    for item in crop_items:
        item_name = get_item_display_name(item)
        price = get_crop_price_for_user(user_id, item_name) or item.get("price", 0)
        total_price += price

        if item_name not in sold:
            sold[item_name] = {"count": 0, "total": 0}
        sold[item_name]["count"] += 1
        sold[item_name]["total"] += price

    total_count = len(crop_items)
    farm_data[user_id]["crop_items"] = []

    for key in list(farm_data[user_id]["crops"].keys()):
        farm_data[user_id]["crops"][key] = 0

    money_data[user_id] += total_price
    save_data()

    text = "\n".join(
        f"{name}: {data['count']}개 / {data['total']:,}원"
        for name, data in sold.items()
    )

    await interaction.response.send_message(
        f"💰 **농작물 전체 판매 완료!**\n\n"
        f"{text}\n\n"
        f"판매 수량: **{total_count}개**\n"
        f"총 판매가: **{total_price:,}원**\n\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )


@bot.tree.command(name="변동가", description="현재 농작물 시세 확인", guild=GUILD)
async def crop_price_info(interaction: discord.Interaction):
    if not crop_prices:
        update_crop_prices()

    text = "\n".join(
        f"{name}: {crop_prices[name]}원 (기준가 {seed['base_price']}원)"
        for name, seed in SEED_DATA.items()
    )

    await interaction.response.send_message(
        f"📈 **현재 농작물 변동가**\n\n{text}\n\n"
        f"시세는 1시간마다 1%~7% 변동됨. 특성 작물은 여기에 특성 배율이 추가로 붙음."
    )


@bot.tree.command(name="농작물업글", description="농작물 성장/판매가를 업그레이드한다", guild=GUILD)
async def crop_upgrade(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)
    get_farm_upgrade(user_id)

    level = farm_levels[user_id]

    if level >= 10:
        await interaction.response.send_message("❌ 이미 농작물 업그레이드 최대 단계임.")
        return

    cost = 5000 * (3 ** (level - 1))

    if money_data[user_id] < cost:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n필요 금액: **{cost:,}원**\n현재 잔액: **{money_data[user_id]:,}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= cost
    farm_levels[user_id] += 1

    save_data()

    await interaction.response.send_message(
        f"🌾 **농작물 업그레이드 완료!**\n\n"
        f"현재 단계: **{farm_levels[user_id]}단계**\n"
        f"사용 금액: **{cost:,}원**\n\n"
        f"효과:\n"
        f"판매가 증가 / 성장 시간 감소"
    )


@bot.tree.command(name="밭업글", description="밭 칸 수를 업그레이드한다", guild=GUILD)
async def field_upgrade(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_farm(user_id)
    get_farm_upgrade(user_id)

    current_size = field_sizes[user_id]

    if current_size < 9:
        current_size = 9
        field_sizes[user_id] = 9

    if current_size >= 50:
        await interaction.response.send_message("❌ 이미 밭 최대 크기임.")
        return

    upgrade_count = current_size - 9
    cost = int(3000 * (2 ** upgrade_count))

    if money_data[user_id] < cost:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n필요 금액: **{cost:,}원**\n현재 잔액: **{money_data[user_id]:,}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= cost
    field_sizes[user_id] += 1
    farm_data[user_id]["field"].append(None)

    save_data()

    await interaction.response.send_message(
        f"🟫 **밭 업그레이드 완료!**\n\n"
        f"현재 밭 크기: **{field_sizes[user_id]}칸**\n"
        f"사용 금액: **{cost:,}원**"
    )


@bot.tree.command(name="도감2", description="농작물 도감 확인", guild=GUILD)
async def crop_book(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_farm(user_id)

    lines = []

    for name, seed in SEED_DATA.items():
        discovered = "✅" if name in crop_dex[user_id] else "❌"

        lines.append(
            f"{discovered} **{name}**\n"
            f"씨앗 가격: {seed['seed_price']}원\n"
            f"기준 판매가: {seed['base_price']}원\n"
            f"성장 시간: {seed['grow_min']}초 ~ {seed['grow_max']}초\n"
            f"수확량: {seed.get('min_yield', 1)}개 ~ {seed.get('max_yield', 1)}개"
        )

    trait_text = "\n".join(
        f"- {name}: 가격 x{data['price_mult']} / 수확량 x{data['yield_mult']}"
        for name, data in CROP_TRAITS.items()
    )

    await interaction.response.send_message(
        "📖 **농작물 도감**\n\n" +
        "\n\n".join(lines) +
        f"\n\n✨ **작물 특성**\n{trait_text}"
    )

@bot.tree.command(name="헛간", description="수확해서 보관 중인 농작물을 확인한다", guild=GUILD)
async def barn(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_farm(user_id)

    crop_items = farm_data[user_id].setdefault("crop_items", [])

    if not crop_items:
        await interaction.response.send_message("🏚️ 헛간이 비어있음.", ephemeral=True)
        return

    grouped = {}
    total_value = 0

    for item in crop_items:
        base_name = item.get("name") or get_item_display_name(item)
        trait = item.get("trait")
        display_name = item.get("display_name") or (f"{trait} {base_name}" if trait else base_name)
        price = get_crop_price_for_user(user_id, display_name) or item.get("price", 0)
        total_value += price

        key = (base_name, trait)
        if key not in grouped:
            grouped[key] = {
                "display_name": display_name,
                "count": 0,
                "price": 0,
            }

        grouped[key]["count"] += 1
        grouped[key]["price"] += price

    lines = []

    for (base_name, trait), info in sorted(grouped.items(), key=lambda x: x[1]["display_name"]):
        lines.append(
            f"🌱 **{info['display_name']}** x{info['count']}개 / "
            f"예상가 {info['price']:,}원"
        )

    save_data()

    content = (
        f"🌾 **내 헛간** | 총 {len(crop_items)}개 / 묶음 {len(grouped)}개\n\n"
        + "\n".join(lines)
        + f"\n\n💰 예상 총 판매가: **{total_value:,}원**"
    )

    if len(content) <= 2000:
        await interaction.response.send_message(content)
        return

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"barn_{user_id}.txt"
    )
    await interaction.response.send_message("📄 헛간 목록이 길어서 txt 파일로 뽑았음.", file=file)

@bot.tree.command(name="상세헛간", description="농작물 상세 정보를 txt 파일로 확인한다", guild=GUILD)
async def detail_barn(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_farm(user_id)

    crop_items = farm_data[user_id].setdefault("crop_items", [])

    if not crop_items:
        await interaction.response.send_message("🏚️ 헛간이 비어있음.", ephemeral=True)
        return

    lines = ["🌾 농작물 상세 헛간", ""]

    for item in crop_items:
        item_name = get_item_display_name(item)
        trait = item.get("trait") or "특성 없음"
        price = get_crop_price_for_user(user_id, item_name) or item.get("price", 0)

        lines.append(
            f"{item_name} | [{trait}] | 예상가 {price:,}원"
        )

    save_data()
    content = "\n".join(lines)

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"barn_detail_{user_id}.txt"
    )
    await interaction.response.send_message("📄 농작물 상세 헛간을 txt 파일로 뽑았음.", file=file)

@bot.tree.command(name="땅", description="4개의 농장 지역 상태를 확인한다", guild=GUILD)
async def land_status(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_farm(user_id)

    current_region = get_current_region(user_id)
    region_status = get_daily_region_status()
    region_lines = []

    for region in FARM_REGIONS:
        state = region_status[region]
        emoji = REGION_EMOJI[state]
        effect = REGION_EFFECTS[state]

        growing_count = 0
        ready_count = 0

        for plot in farm_data[user_id]["field"]:
            if not isinstance(plot, dict):
                continue

            if plot.get("region") != region:
                continue

            harvest_time = fix_datetime(plot.get("harvest_time"))
            if harvest_time is None:
                continue

            if now >= harvest_time:
                ready_count += 1
            else:
                growing_count += 1

        selected = " ✅ 현재 위치" if region == current_region else ""

        region_lines.append(
            f"{emoji} **{region} / {state}**{selected}\n"
            f"성장 x{effect['grow_mult']} / 수확량 x{effect['yield_mult']} / 특성 {effect['trait_bonus']:+}%\n"
            f"성장중: {growing_count}칸 / 수확 가능: {ready_count}칸"
        )

    await interaction.response.send_message(
        f"🧑‍🌾 **농장 지역 상태** ({get_farm_today_key()})\n\n"
        + "\n\n".join(region_lines)
        + "\n\n이동 예시: `/이동 남부 농장`"
    )

@bot.tree.command(name="이동", description="농작물을 심을 농장 지역으로 이동한다", guild=GUILD)
@app_commands.describe(지역="이동할 지역 이름: 동부 농장 / 서부 농장 / 남부 농장 / 북부 농장")
async def move_region(interaction: discord.Interaction, 지역: str):
    user_id = interaction.user.id

    get_farm(user_id)

    if 지역 not in FARM_REGIONS:
        await interaction.response.send_message(
            "❌ 지역은 동부 농장 / 서부 농장 / 남부 농장 / 북부 농장 중 하나여야 함.",
            ephemeral=True
        )
        return

    farm_data[user_id]["current_region"] = 지역
    save_data()

    status = get_region_status(지역)
    emoji = REGION_EMOJI[status]

    await interaction.response.send_message(
        f"🚶 **{지역}**으로 이동함!\n"
        f"{emoji} 현재 상태: **{status}**\n"
        f"이제 `/심기`나 `/전체심기`를 쓰면 이 지역 효과로 심어짐."
    )

@bot.tree.command(name="변동가리셋", description="농작물 변동가를 기준가로 초기화한다", guild=GUILD)
@app_commands.checks.has_permissions(administrator=True)
async def reset_crop_prices(interaction: discord.Interaction):

    for crop_name, seed in SEED_DATA.items():
        crop_prices[crop_name] = seed["base_price"]

    save_data()

    text = "\n".join(
        f"{name}: {crop_prices[name]}원"
        for name in SEED_DATA
    )

    await interaction.response.send_message(
        f"🔄 **농작물 변동가 초기화 완료!**\n\n{text}"
    )


@reset_crop_prices.error
async def reset_crop_prices_error(
    interaction: discord.Interaction,
    error
):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ 관리자만 사용 가능.",
            ephemeral=True
        )

# =========================
# 거래 시스템
# =========================
        
@bot.tree.command(name="거래", description="물고기나 광석을 다른 유저에게 준다.", guild=GUILD)
@app_commands.describe(
    대상="받을 유저",
    종류="물고기 또는 광석",
    이름="줄 물고기/광석 이름",
    갯수="줄 갯수"
)
async def trade_item(
    interaction: discord.Interaction,
    대상: discord.Member,
    종류: str,
    이름: str,
    갯수: int
):
    sender_id = interaction.user.id
    target_id = 대상.id

    get_tank(sender_id)
    get_tank(target_id)
    get_mining(sender_id)
    get_mining(target_id)
    get_farm(sender_id)
    get_farm(target_id)

    if sender_id == target_id:
        await interaction.response.send_message("❌ 자기 자신에게는 거래 못함.", ephemeral=True)
        return

    if 대상.bot:
        await interaction.response.send_message("❌ 봇한테는 거래 못함.", ephemeral=True)
        return

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1개 이상 줘야 함.", ephemeral=True)
        return

    if 종류 == "물고기":
        owned = [fish for fish in fish_tanks[sender_id] if fish.get("name") == 이름 or get_item_display_name(fish) == 이름]

        if len(owned) < 갯수:
            await interaction.response.send_message(f"❌ {이름} 부족함.\n보유: {len(owned)}마리", ephemeral=True)
            return

        trade_list = owned[:갯수]
        for fish in trade_list:
            fish_tanks[sender_id].remove(fish)
            fish_tanks[target_id].append(fish)
            fish_dex[target_id].add(fish["name"])

        save_data()

        total_kg = round(sum(fish["kg"] for fish in trade_list), 2)
        total_price = sum(fish["price"] for fish in trade_list)

        await interaction.response.send_message(
            f"🤝 **물고기 거래 완료!**\n\n"
            f"보낸 사람: {interaction.user.mention}\n"
            f"받는 사람: {대상.mention}\n"
            f"물고기: **{이름}**\n"
            f"수량: **{갯수}마리**\n"
            f"총 무게: **{total_kg}kg**\n"
            f"총 예상가: **{total_price:,}원**\n"
        )
        return

    if 종류 == "광석":
        if 이름 not in ORE_DATA:
            await interaction.response.send_message("❌ 그런 광석은 없음.", ephemeral=True)
            return

        normalize_ore_bag(sender_id)
        normalize_ore_bag(target_id)

        owned_ores = ore_bags[sender_id].get(이름, [])
        owned_count = len(owned_ores)

        if owned_count < 갯수:
            await interaction.response.send_message(f"❌ {이름} 부족함.\n보유: {owned_count}개", ephemeral=True)
            return

        trade_list = owned_ores[:갯수]
        ore_bags[sender_id][이름] = owned_ores[갯수:]

        if len(ore_bags[sender_id][이름]) <= 0:
            del ore_bags[sender_id][이름]

        if 이름 not in ore_bags[target_id]:
            ore_bags[target_id][이름] = []

        ore_bags[target_id][이름].extend(trade_list)
        save_data()

        await interaction.response.send_message(
            f"🤝 **광석 거래 완료!**\n\n"
            f"보낸 사람: {interaction.user.mention}\n"
            f"받는 사람: {대상.mention}\n"
            f"광석: **{이름}**\n"
            f"수량: **{갯수}개**\n"
        )
        return

    await interaction.response.send_message(
        "❌ 종류는 `물고기` 또는 `광석`만 가능함.",
        ephemeral=True
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

@bot.tree.command(
    name="돈삭제",
    description="관리자 전용 돈 차감",
    guild=GUILD
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="돈 차감할 유저",
    금액="차감할 금액"
)
async def remove_money(
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

    # 현재 돈보다 많이 삭제 시 0원 처리
    money_data[user_id] = max(
        0,
        round(float(money_data[user_id])) - round(float(금액))
    )

    save_data()

    await interaction.response.send_message(
        f"💸 차감 완료!\n\n"
        f"대상: {유저.mention}\n"
        f"차감 금액: **{금액:,}원**\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )


@remove_money.error
async def remove_money_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ 관리자 전용 명령어임.",
            ephemeral=True
        )
# =========================
# 광산 시스템
# =========================

ore_bags = globals().get("ore_bags", {})
owned_pickaxes = globals().get("owned_pickaxes", {})
equipped_pickaxes = globals().get("equipped_pickaxes", {})
mine_data = globals().get("mine_data", {})
mining_cooldowns = globals().get("mining_cooldowns", {})
mining2_cooldowns = globals().get("mining2_cooldowns", {})

MAX_MINE_LEVEL = 12

ORE_DATA = {
    "돌": {"price": 500, "chance": 45, "min_kg": 0.2, "max_kg": 2.5, "base_price": 300, "kg_price": 120},
    "석탄": {"price": 1200, "chance": 30, "min_kg": 0.3, "max_kg": 3.0, "base_price": 700, "kg_price": 220},
    "구리": {"price": 2200, "chance": 22, "min_kg": 0.5, "max_kg": 4.0, "base_price": 1200, "kg_price": 350},
    "철광석": {"price": 3400, "chance": 15, "min_kg": 0.8, "max_kg": 6.0, "base_price": 1800, "kg_price": 450},
    "은광석": {"price": 7300, "chance": 9, "min_kg": 0.6, "max_kg": 5.0, "base_price": 4200, "kg_price": 900},
    "금광석": {"price": 15000, "chance": 5, "min_kg": 0.4, "max_kg": 4.0, "base_price": 9000, "kg_price": 1800},
    "돈봉투": {"price": 145000, "chance": 8, "min_kg": 0.1, "max_kg": 0.5, "base_price": 145000, "kg_price": 0},
    "티타늄": {"price": 55000, "chance": 3.5, "min_kg": 0.5, "max_kg": 4.5, "base_price": 30000, "kg_price": 6000},
    "다이아몬드": {"price": 100000, "chance": 1.2, "min_kg": 0.1, "max_kg": 1.2, "base_price": 80000, "kg_price": 18000},
    "루비": {"price": 130000, "chance": 1.5, "min_kg": 0.1, "max_kg": 1.0, "base_price": 95000, "kg_price": 25000},
    "사파이어": {"price": 170000, "chance": 1.2, "min_kg": 0.1, "max_kg": 1.0, "base_price": 120000, "kg_price": 30000},
    "에메랄드": {"price": 250000, "chance": 0.7, "min_kg": 0.1, "max_kg": 0.8, "base_price": 180000, "kg_price": 45000},
    "흑요석": {"price": 520000, "chance": 0.35, "min_kg": 0.4, "max_kg": 3.0, "base_price": 350000, "kg_price": 70000},
    "네더라이트": {"price": 900000, "chance": 0.18, "min_kg": 0.2, "max_kg": 1.5, "base_price": 650000, "kg_price": 130000},
    "레드 다이아몬드": {"price": 1500000, "chance": 0.08, "min_kg": 0.1, "max_kg": 1.0, "base_price": 1100000, "kg_price": 250000},
    "레인보우 다이아몬드": {"price": 3000000, "chance": 0.025, "min_kg": 0.1, "max_kg": 0.8, "base_price": 2400000, "kg_price": 400000},
    "우라늄": {"price": 5000000, "chance": 0.01, "min_kg": 0.1, "max_kg": 0.6, "base_price": 4200000, "kg_price": 600000},
    "신기루": {"price": 10000000, "chance": 0.003, "min_kg": 0.05, "max_kg": 0.3, "base_price": 9000000, "kg_price": 1500000}
}

PICKAXE_DATA = {
    "나무 곡괭이": {
        "price": 0,
        "ores": {},
        "luck": 0,
        "time_reduce": 0,
        "double_chance": 0,
        "triple_chance": 0
    },
    "돌 곡괭이": {
        "price": 25000,
        "ores": {"돌": 10},
        "luck": 3,
        "time_reduce": 3,
        "double_chance": 3,
        "triple_chance": 0.5
    },
    "구리 곡괭이": {
        "price": 75000,
        "ores": {"구리": 5, "석탄": 3},
        "luck": 8,
        "time_reduce": 7,
        "double_chance": 7,
        "triple_chance": 1
    },
    "철 곡괭이": {
        "price": 150000,
        "ores": {"철광석": 10, "석탄": 4},
        "luck": 12,
        "time_reduce": 10,
        "double_chance": 7,
        "triple_chance": 1
    },
    "금 곡괭이": {
        "price": 450000,
        "ores": {"금광석": 12, "은광석": 6, "석탄": 3},
        "luck": 23,
        "time_reduce": 17,
        "double_chance": 12,
        "triple_chance": 3
    },
    "티타늄 곡괭이": {
        "price": 1000000,
        "ores": {"다이아몬드": 1, "티타늄": 10, "철광석": 5, "석탄": 10},
        "luck": 15,
        "time_reduce": 10,
        "double_chance": 40,
        "triple_chance": 30
    },
    "다이아몬드 곡괭이": {
        "price": 1300000,
        "ores": {"다이아몬드": 5, "철광석": 7, "석탄": 12},
        "luck": 40,
        "time_reduce": 28,
        "double_chance": 19,
        "triple_chance": 6
    },
    "에메랄드 곡괭이": {
        "price": 2200000,
        "ores": {"에메랄드": 8, "다이아몬드": 3, "석탄": 15},
        "luck": 65,
        "time_reduce": 40,
        "double_chance": 28,
        "triple_chance": 10
    },
    "보석 곡괭이": {
        "price": 3100000,
        "ores": {"사파이어": 5, "루비": 5, "에메랄드": 5, "다이아몬드": 1, "석탄": 7},
        "luck": 150,
        "time_reduce": 25,
        "double_chance": 0,
        "triple_chance": 0
    },
    "흑요석 곡괭이": {
        "price": 22000000,
        "ores": {"흑요석": 5, "에메랄드": 2, "석탄": 17},
        "luck": 90,
        "time_reduce": 50,
        "double_chance": 38,
        "triple_chance": 12
    },
    "네더라이트 곡괭이": {
        "price": 60000000,
        "ores": {"네더라이트": 3, "흑요석": 3, "다이아몬드": 5},
        "luck": 140,
        "time_reduce": 55,
        "double_chance": 42,
        "triple_chance": 18
    },
    "신의 곡괭이": {
        "price": 300000000,
        "ores": {"레인보우 다이아몬드": 3, "레드 다이아몬드": 3, "네더라이트": 5, "우라늄": 1},
        "luck": 350,
        "time_reduce": 65,
        "double_chance": 55,
        "triple_chance": 30
    }
}


def calc_ore_price(ore_name, kg):
    ore = ORE_DATA[ore_name]
    price = ore["base_price"] + (kg * ore["kg_price"])
    return max(1, int(price))


def create_ore_item(ore_name, luck_bonus=0, old_item=False):
    ore = ORE_DATA[ore_name]

    if old_item:
        return {
            "kg": 1.0,
            "price": ore.get("price", ore.get("base_price", 0))
        }

    kg = round(random.uniform(ore["min_kg"], ore["max_kg"]), 2)

    return {
        "kg": kg,
        "price": calc_ore_price(ore_name, kg)
    }


def normalize_ore_bag(user_id):
    if user_id not in ore_bags or not isinstance(ore_bags[user_id], dict):
        ore_bags[user_id] = {}
        return

    bag = ore_bags[user_id]

    for ore_name in list(bag.keys()):
        if ore_name not in ORE_DATA:
            del bag[ore_name]
            continue

        value = bag[ore_name]

        if isinstance(value, int):
            if value <= 0:
                del bag[ore_name]
            else:
                bag[ore_name] = [
                    create_ore_item(ore_name, old_item=True)
                    for _ in range(value)
                ]

        elif isinstance(value, list):
            cleaned_items = []

            for item in value:
                if isinstance(item, dict):
                    kg = float(item.get("kg", 1.0))
                    price = int(item.get("price", calc_ore_price(ore_name, kg)))

                    cleaned_items.append({
                        "kg": kg,
                        "price": price
                    })

                elif isinstance(item, (int, float)):
                    cleaned_items.append(create_ore_item(ore_name, old_item=True))

            if cleaned_items:
                bag[ore_name] = cleaned_items
            else:
                del bag[ore_name]

        else:
            del bag[ore_name]


def get_ore_count(user_id, ore_name):
    normalize_ore_bag(user_id)
    return len(ore_bags[user_id].get(ore_name, []))


def add_ore_to_bag(user_id, ore_name, amount=1, luck_bonus=0):
    normalize_ore_bag(user_id)

    if ore_name not in ore_bags[user_id]:
        ore_bags[user_id][ore_name] = []

    new_items = [
        create_ore_item(ore_name, luck_bonus)
        for _ in range(amount)
    ]

    ore_bags[user_id][ore_name].extend(new_items)
    return new_items


def remove_ore_from_bag(user_id, ore_name, amount):
    normalize_ore_bag(user_id)

    if get_ore_count(user_id, ore_name) < amount:
        return False

    del ore_bags[user_id][ore_name][:amount]

    if not ore_bags[user_id][ore_name]:
        del ore_bags[user_id][ore_name]

    return True


def get_mining(user_id):
    changed = False

    get_pendant(user_id)

    if user_id not in ore_bags or not isinstance(ore_bags[user_id], dict):
        ore_bags[user_id] = {}
        changed = True

    normalize_ore_bag(user_id)

    if user_id not in owned_pickaxes or not isinstance(owned_pickaxes[user_id], list):
        owned_pickaxes[user_id] = ["나무 곡괭이"]
        changed = True

    if "나무 곡괭이" not in owned_pickaxes[user_id]:
        owned_pickaxes[user_id].insert(0, "나무 곡괭이")
        changed = True

    if user_id not in equipped_pickaxes or equipped_pickaxes[user_id] not in PICKAXE_DATA:
        equipped_pickaxes[user_id] = "나무 곡괭이"
        changed = True

    if equipped_pickaxes[user_id] not in owned_pickaxes[user_id]:
        equipped_pickaxes[user_id] = "나무 곡괭이"
        changed = True

    if user_id not in mine_data or not isinstance(mine_data[user_id], dict):
        mine_data[user_id] = {
            "level": 1,
            "money": 0,
            "last_collect": datetime.now()
        }
        changed = True

    mine = mine_data[user_id]

    if "level" not in mine:
        mine["level"] = 1
        changed = True

    if "money" not in mine:
        mine["money"] = 0
        changed = True

    if "last_collect" not in mine or not isinstance(mine["last_collect"], datetime):
        mine["last_collect"] = datetime.now()
        changed = True

    if user_id not in mining_cooldowns:
        mining_cooldowns[user_id] = None
        changed = True

    if user_id not in mining2_cooldowns:
        mining2_cooldowns[user_id] = None
        changed = True

    if changed:
        save_data()

    return changed


def pick_ore(luck_bonus=0):
    names = list(ORE_DATA.keys())
    weights = []

    for name in names:
        ore = ORE_DATA[name]
        chance = ore["chance"]
        price = ore["price"]

        if price >= 80000:
            chance *= 1 + (luck_bonus / 45)
        elif price >= 20000:
            chance *= 1 + (luck_bonus / 70)
        elif price >= 5000:
            chance *= 1 + (luck_bonus / 100)
        else:
            chance *= max(0.2, 1 - (luck_bonus / 250))

        weights.append(chance)

    return random.choices(names, weights=weights, k=1)[0]


def pick_ore_premium(luck_bonus=0):
    names = list(ORE_DATA.keys())
    weights = []

    for name in names:
        ore = ORE_DATA[name]
        chance = ore["chance"]
        price = ore["price"]

        if price >= 80000:
            chance *= 3.5 + (luck_bonus / 35)
        elif price >= 20000:
            chance *= 2.5 + (luck_bonus / 55)
        elif price >= 5000:
            chance *= 1.5 + (luck_bonus / 80)
        else:
            chance *= 0.45

        weights.append(chance)

    return random.choices(names, weights=weights, k=1)[0]


def calc_mine_income(level):
    return 3000 * level


def update_mine_money(user_id):
    get_mining(user_id)

    mine = mine_data[user_id]
    now = datetime.now()
    last = mine["last_collect"]

    if not isinstance(last, datetime):
        last = now
        mine["last_collect"] = now
        return

    passed = int((now - last).total_seconds() // 600)

    if passed <= 0:
        return

    mine["money"] += calc_mine_income(mine["level"]) * passed
    mine["last_collect"] = last + timedelta(minutes=10 * passed)
    save_data()


def get_pickaxe_bonus(user_id):
    get_mining(user_id)

    pickaxe_name = equipped_pickaxes.get(user_id, "나무 곡괭이")

    if pickaxe_name not in PICKAXE_DATA:
        pickaxe_name = "나무 곡괭이"
        equipped_pickaxes[user_id] = pickaxe_name

    return PICKAXE_DATA[pickaxe_name]


class MiningReadyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="⛏️ 지금!",
            style=discord.ButtonStyle.green
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ 니 광질 아님.", ephemeral=True)
            return

        if not view.ready:
            await interaction.response.send_message("❌ 아직 초록 칸 아님.", ephemeral=True)
            return

        for item in view.children:
            item.disabled = True

        pickaxe = get_pickaxe_bonus(view.user_id)

        need_count = random.randint(2, 4)

        if view.premium:
            need_count += 1

        block_view = MiningBlockView(
            view.user_id,
            need_count,
            pickaxe,
            premium=view.premium
        )

        await interaction.response.edit_message(
            content=(
                f"⛏️ 광맥 발견!\n"
                f"숨겨진 광석 칸 **{need_count}개**를 눌러!"
            ),
            view=block_view
        )

        block_view.message = await interaction.original_response()
        view.stop()


class MiningReadyView(discord.ui.View):
    def __init__(self, user_id, premium=False):
        super().__init__(timeout=20)
        self.user_id = user_id
        self.ready = False
        self.premium = premium

        pickaxe = get_pickaxe_bonus(user_id)
        self.pickaxe_name = equipped_pickaxes.get(user_id, "나무 곡괭이")

        self.wait_time = random.uniform(
            1,
            max(1.5, 15 * (1 - pickaxe["time_reduce"] / 100))
        )

        self.add_item(MiningReadyButton())

    async def start_waiting(self):
        await asyncio.sleep(self.wait_time)

        self.ready = True

        if self.message:
            await self.message.edit(
                content=(
                    f"🟩 **지금이다!**\n"
                    f"사용 곡괭이: **{self.pickaxe_name}**\n"
                    f"버튼 눌러!"
                ),
                view=self
            )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(
                content="⛏️ 광질 타이밍을 놓침.",
                view=self
            )


class MiningBlockButton(discord.ui.Button):
    def __init__(self, index):
        super().__init__(
            label="⬛",
            style=discord.ButtonStyle.gray,
            row=index // 3
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ 니 광질 아님.", ephemeral=True)
            return

        if self.index in view.opened:
            await interaction.response.send_message("❌ 이미 캔 칸임.", ephemeral=True)
            return

        view.opened.add(self.index)
        self.disabled = True
        self.label = "✅"
        self.style = discord.ButtonStyle.green

        user_id = view.user_id

        get_wallet(user_id)
        get_pendant(user_id)
        get_mining(user_id)

        pickaxe = view.pickaxe
        luck = get_pendant_luck(user_id) + pickaxe["luck"]

        if view.premium:
            ore_name = pick_ore_premium(luck)
        else:
            ore_name = pick_ore(luck)

        amount = 1

        if random.uniform(0, 100) < pickaxe["double_chance"]:
            amount = 2

        if random.uniform(0, 100) < pickaxe["triple_chance"]:
            amount = 3

        new_items = add_ore_to_bag(user_id, ore_name, amount, luck)
        save_data()

        total_kg = sum(item["kg"] for item in new_items)
        total_price = sum(item["price"] for item in new_items)

        view.results.append(
            f"⛏️ **{ore_name} x {amount}** | "
            f"총 **{total_kg:.2f}kg** | "
            f"총 **{total_price:,}원**"
        )

        if len(view.opened) >= view.need_count:
            for item in view.children:
                item.disabled = True

            await interaction.response.edit_message(
                content=(
                    f"✅ **광질 완료!**\n\n"
                    + "\n".join(view.results)
                ),
                view=view
            )
            view.stop()
            return

        await interaction.response.edit_message(
            content=(
                f"⛏️ 광질 중.\n"
                f"남은 칸: **{view.need_count - len(view.opened)}칸**\n\n"
                + "\n".join(view.results[-5:])
            ),
            view=view
        )


class MiningBlockView(discord.ui.View):
    def __init__(self, user_id, need_count, pickaxe, premium=False):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.need_count = need_count
        self.pickaxe = pickaxe
        self.premium = premium
        self.opened = set()
        self.results = []
        self.message = None

        indexes = random.sample(range(9), need_count)

        for i in range(9):
            if i in indexes:
                self.add_item(MiningBlockButton(i))
            else:
                btn = discord.ui.Button(
                    label="⬛",
                    style=discord.ButtonStyle.gray,
                    disabled=True,
                    row=i // 3
                )
                self.add_item(btn)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(
                content=(
                    "⛏️ 광질 시간이 끝남.\n\n"
                    + ("\n".join(self.results) if self.results else "캔 광물 없음.")
                ),
                view=self
            )


@bot.tree.command(name="광질", description="랜덤 타이밍에 광맥을 찾아 광물을 캔다", guild=GUILD)
async def mining(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)
    get_mining(user_id)

    cooldown = mining_cooldowns.get(user_id)

    if cooldown and now < cooldown:
        remain = int((cooldown - now).total_seconds())
        await interaction.response.send_message(
            f"⛏️ 아직 광질 준비중임. **{remain}초** 남음.",
            ephemeral=True
        )
        return

    mining_cooldowns[user_id] = now + timedelta(seconds=20)
    save_data()

    view = MiningReadyView(user_id)

    await interaction.response.send_message(
        f"⛏️ 광질 시작!\n"
        f"사용 곡괭이: **{view.pickaxe_name}**\n\n"
        f"1초~15초 안에 초록 칸이 뜨면 눌러!",
        view=view
    )

    view.message = await interaction.original_response()
    asyncio.create_task(view.start_waiting())


@bot.tree.command(name="광질2", description="5만원을 내고 5분마다 고급 광질을 한다", guild=GUILD)
async def mining_premium(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)
    get_pendant(user_id)
    get_mining(user_id)

    cost = 50000
    cooldown = mining2_cooldowns.get(user_id)

    if cooldown and now < cooldown:
        remain = int((cooldown - now).total_seconds())
        minute = remain // 60
        second = remain % 60

        await interaction.response.send_message(
            f"⛏️ 아직 고급 광질 준비중임.\n"
            f"남은 시간: **{minute}분 {second}초**",
            ephemeral=True
        )
        return

    if money_data[user_id] < cost:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n"
            f"필요 금액: **{cost:,}원**\n"
            f"현재 잔액: **{money_data[user_id]:,}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= cost
    mining2_cooldowns[user_id] = now + timedelta(minutes=5)
    save_data()

    view = MiningReadyView(user_id, premium=True)

    await interaction.response.send_message(
        f"💎 **고급 광질 시작!**\n"
        f"사용 비용: **{cost:,}원**\n"
        f"사용 곡괭이: **{view.pickaxe_name}**\n\n"
        f"일반 광질보다 희귀 광물 확률이 높음.\n"
        f"1초~15초 안에 초록 칸이 뜨면 눌러!",
        view=view
    )

    view.message = await interaction.original_response()
    asyncio.create_task(view.start_waiting())


@bot.tree.command(name="가방", description="내 광석 가방을 확인한다", guild=GUILD)
async def ore_bag(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_mining(user_id)
    normalize_ore_bag(user_id)

    bag = ore_bags[user_id]

    if not bag:
        await interaction.response.send_message("🎒 가방이 비어있다.")
        return

    lines = []

    for ore_name, items in bag.items():
        if not items:
            continue

        count = len(items)
        total_kg = sum(item.get("kg", 0) for item in items)
        total_price = sum(item.get("price", 0) for item in items)
        each_price = total_price // count if count > 0 else 0

        lines.append(
            f"⛏️ **{ore_name} x {count}** | "
            f"총 **{total_kg:.2f}kg** | "
            f"개당 **{each_price:,}원** | "
            f"총 **{total_price:,}원**"
        )

    content = "🎒 **내 광석 가방**\n\n" + "\n".join(lines)

    if len(content) <= 2000:
        await interaction.response.send_message(content)
        return

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"ore_bag_{user_id}.txt"
    )

    await interaction.response.send_message(
        "📄 가방 내용이 길어서 txt 파일로 뽑았음.",
        file=file
    )


@bot.tree.command(name="상세가방", description="광석 상세 정보를 txt 파일로 확인한다", guild=GUILD)
async def detail_ore_bag(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_mining(user_id)
    normalize_ore_bag(user_id)

    bag = ore_bags[user_id]

    if not bag:
        await interaction.response.send_message("🎒 가방이 비어있다.")
        return

    lines = ["🎒 광석 상세 가방", ""]

    for ore_name, items in bag.items():
        if not items:
            continue

        count = len(items)
        total_kg = sum(item.get("kg", 0) for item in items)
        total_price = sum(item.get("price", 0) for item in items)
        each_price = total_price // count if count > 0 else 0

        lines.append(
            f"⛏️ {ore_name} x {count} | "
            f"총 {total_kg:.2f}kg | "
            f"개당 {each_price:,}원 | "
            f"총 {total_price:,}원"
        )

        for idx, item in enumerate(items, start=1):
            lines.append(
                f"  {idx}. {item.get('kg', 0):.2f}kg / {item.get('price', 0):,}원"
            )

        lines.append("")

    content = "\n".join(lines)

    file = discord.File(
        BytesIO(content.encode("utf-8")),
        filename=f"ore_bag_{user_id}.txt"
    )

    await interaction.response.send_message(
        "📄 광석 상세 가방을 txt 파일로 뽑았음.",
        file=file
    )


@bot.tree.command(name="전체팔기2", description="가방의 모든 광석을 판매한다", guild=GUILD)
async def sell_all_ores(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)
    normalize_ore_bag(user_id)

    bag = ore_bags[user_id]

    if not bag:
        await interaction.response.send_message("🎒 팔 광석이 없다.")
        return

    total = 0
    sold_text = []

    for ore_name, items in list(bag.items()):
        if ore_name not in ORE_DATA or not items:
            continue

        ore_total = sum(item.get("price", 0) for item in items)
        ore_kg = sum(item.get("kg", 0) for item in items)
        total += ore_total

        sold_text.append(
            f"{ore_name} x{len(items)} / {ore_kg:.2f}kg = {ore_total:,}원"
        )

    if total <= 0:
        ore_bags[user_id] = {}
        save_data()
        await interaction.response.send_message("🎒 팔 수 있는 광석이 없다.")
        return

    ore_bags[user_id] = {}
    money_data[user_id] += total

    save_data()

    await interaction.response.send_message(
        f"💰 **전체 판매 완료!**\n\n"
        + "\n".join(sold_text[:20])
        + f"\n\n총 판매 금액: **{total:,}원**\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )


@bot.tree.command(name="제작", description="곡괭이를 제작하거나 장착한다", guild=GUILD)
@app_commands.describe(곡괭이="제작/장착할 곡괭이 이름")
async def craft_pickaxe(interaction: discord.Interaction, 곡괭이: str = None):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)

    if 곡괭이 is None:
        lines = []

        for name, pickaxe in PICKAXE_DATA.items():
            owned = "✅" if name in owned_pickaxes[user_id] else "❌"

            ore_cost = ", ".join(
                f"{ore} x{count}"
                for ore, count in pickaxe["ores"].items()
            )

            if not ore_cost:
                ore_cost = "없음"

            lines.append(
                f"{owned} **{name}**\n"
                f"가격: **{pickaxe['price']:,}원**\n"
                f"광석 재료: {ore_cost}\n"
                f"운빨 증가: {pickaxe['luck']}% / 시간 감소: {pickaxe['time_reduce']}%\n"
                f"더블: {pickaxe['double_chance']}% / 트리플: {pickaxe['triple_chance']}%"
            )

        await interaction.response.send_message(
            "⛏️ **곡괭이 목록**\n\n"
            + "\n\n".join(lines)
            + "\n\n`/제작 곡괭이이름` 으로 제작/장착"
        )
        return

    if 곡괭이 not in PICKAXE_DATA:
        await interaction.response.send_message("❌ 없는 곡괭이임.", ephemeral=True)
        return

    if 곡괭이 in owned_pickaxes[user_id]:
        equipped_pickaxes[user_id] = 곡괭이
        save_data()

        await interaction.response.send_message(
            f"⛏️ **{곡괭이}** 장착 완료!"
        )
        return

    pickaxe = PICKAXE_DATA[곡괭이]

    if money_data[user_id] < pickaxe["price"]:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n필요 돈: {pickaxe['price']:,}원\n현재 돈: {money_data[user_id]:,}원",
            ephemeral=True
        )
        return

    for ore, need_count in pickaxe["ores"].items():
        if get_ore_count(user_id, ore) < need_count:
            await interaction.response.send_message(
                f"❌ 재료 부족.\n"
                f"필요: {ore} x{need_count}\n"
                f"보유: {get_ore_count(user_id, ore)}개",
                ephemeral=True
            )
            return

    money_data[user_id] -= pickaxe["price"]

    for ore, need_count in pickaxe["ores"].items():
        remove_ore_from_bag(user_id, ore, need_count)

    owned_pickaxes[user_id].append(곡괭이)
    equipped_pickaxes[user_id] = 곡괭이

    save_data()

    await interaction.response.send_message(
        f"✅ 제작 완료!\n"
        f"**{곡괭이}** 제작 후 바로 장착함."
    )


@bot.tree.command(name="광산", description="광산에 쌓인 돈을 확인한다", guild=GUILD)
async def mine(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)

    update_mine_money(user_id)

    mine = mine_data[user_id]
    income = calc_mine_income(mine["level"])

    await interaction.response.send_message(
        f"⛏️ **내 광산**\n\n"
        f"광산 강화: **{mine['level']}강**\n"
        f"10분마다 수익: **{income:,}원**\n"
        f"현재 쌓인 돈: **{mine['money']:,}원**\n\n"
        f"회수하려면 `/회수` 사용"
    )


@bot.tree.command(name="광산업글", description="광산 수익을 강화한다", guild=GUILD)
async def mine_upgrade(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)

    update_mine_money(user_id)

    mine = mine_data[user_id]
    level = mine["level"]

    if level >= MAX_MINE_LEVEL:
        await interaction.response.send_message("❌ 이미 광산 최대 강화임.")
        return

    cost = 100000 * (2 ** (level - 1))

    if money_data[user_id] < cost:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n"
            f"필요 금액: **{cost:,}원**\n"
            f"현재 잔액: **{money_data[user_id]:,}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= cost
    mine["level"] += 1

    save_data()

    await interaction.response.send_message(
        f"✅ 광산 강화 성공!\n\n"
        f"현재 강화: **{mine['level']}강**\n"
        f"10분마다 수익: **{calc_mine_income(mine['level']):,}원**\n"
        f"사용 금액: **{cost:,}원**"
    )


@bot.tree.command(name="회수", description="광산에 쌓인 돈을 회수한다", guild=GUILD)
async def collect_mine(interaction: discord.Interaction):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)

    update_mine_money(user_id)

    mine = mine_data[user_id]

    if mine["money"] <= 0:
        await interaction.response.send_message("❌ 회수할 돈이 없음.")
        return

    gained = mine["money"]

    mine["money"] = 0
    money_data[user_id] += gained

    save_data()

    await interaction.response.send_message(
        f"💰 광산 돈 회수 완료!\n\n"
        f"회수 금액: **{gained:,}원**\n"
        f"현재 잔액: **{money_data[user_id]:,}원**"
    )
@bot.tree.command(name="광질2", description="5만원을 내고 5분마다 고급 광질을 한다", guild=GUILD)
async def mining_premium(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()

    get_wallet(user_id)
    get_pendant(user_id)
    get_mining(user_id)

    cost = 50000
    cooldown = mining2_cooldowns.get(user_id)

    if cooldown and now < cooldown:
        remain = int((cooldown - now).total_seconds())
        minute = remain // 60
        second = remain % 60

        await interaction.response.send_message(
            f"⛏️ 아직 고급 광질 준비중임.\n"
            f"남은 시간: **{minute}분 {second}초**",
            ephemeral=True
        )
        return

    if money_data[user_id] < cost:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n"
            f"필요 금액: **{cost:,}원**\n"
            f"현재 잔액: **{money_data[user_id]:,}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= cost
    mining2_cooldowns[user_id] = now + timedelta(minutes=5)
    save_data()

    view = MiningReadyView(user_id, premium=True)

    await interaction.response.send_message(
        f"💎 **고급 광질 시작!**\n"
        f"사용 비용: **{cost:,}원**\n"
        f"사용 곡괭이: **{view.pickaxe_name}**\n\n"
        f"일반 광질보다 희귀 광물 확률이 높음.\n"
        f"1초~15초 안에 초록 칸이 뜨면 눌러!",
        view=view
    )

    view.message = await interaction.original_response()
    asyncio.create_task(view.start_waiting())

@bot.tree.command(name="펜던트", description="보유/장착 펜던트를 확인하거나 장착한다", guild=GUILD)
@app_commands.describe(
    이름="장착할 펜던트 이름",
    칸="장착할 칸 번호 1~2"
)
async def pendant_info_or_equip(
    interaction: discord.Interaction,
    이름: str = None,
    칸: int = None
):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_mining(user_id)
    get_pendant(user_id)

    # 그냥 /펜던트 입력 시 목록 확인
    if 이름 is None:
        owned = owned_pendants[user_id]
        equipped = equipped_pendants[user_id]

        equipped_text = []

        for i in range(2):
            if i < len(equipped):
                pendant = equipped[i]
                luck = PENDANT_DATA[pendant]["luck"]
                equipped_text.append(f"{i + 1}번 칸: **{pendant}** / 운 +{luck}")
            else:
                equipped_text.append(f"{i + 1}번 칸: 비어있음")

        if owned:
            owned_text = "\n".join(
                f"✅ **{pendant}** / 운 +{PENDANT_DATA[pendant]['luck']}"
                for pendant in owned
            )
        else:
            owned_text = "보유한 펜던트 없음"

        total_luck = get_pendant_luck(user_id)

        await interaction.response.send_message(
            f"💍 **펜던트 정보**\n\n"
            f"현재 장착:\n"
            f"{chr(10).join(equipped_text)}\n\n"
            f"보유 펜던트:\n"
            f"{owned_text}\n\n"
            f"총 추가 운: **+{total_luck}**\n\n"
            f"장착 예시:\n"
            f"`/펜던트 돌 펜던트 1`\n"
            f"`/펜던트 금 펜던트 2`"
        )
        return

    # 장착 모드
    if 칸 is None:
        await interaction.response.send_message(
            "❌ 장착할 칸도 입력해야 함. 1번 또는 2번.",
            ephemeral=True
        )
        return

    if 칸 not in [1, 2]:
        await interaction.response.send_message(
            "❌ 펜던트 칸은 1번 또는 2번만 가능.",
            ephemeral=True
        )
        return

    if 이름 not in PENDANT_DATA:
        await interaction.response.send_message(
            "❌ 그런 펜던트 없음.",
            ephemeral=True
        )
        return

    if 이름 not in owned_pendants[user_id]:
        await interaction.response.send_message(
            "❌ 아직 안 만든 펜던트임. `/제작2`로 먼저 제작해야 함.",
            ephemeral=True
        )
        return

    # 같은 펜던트 중복 장착 방지
    if 이름 in equipped_pendants[user_id]:
        await interaction.response.send_message(
            "❌ 이미 장착 중인 펜던트임.",
            ephemeral=True
        )
        return

    index = 칸 - 1

    while len(equipped_pendants[user_id]) < 2:
        equipped_pendants[user_id].append(None)

    old_pendant = equipped_pendants[user_id][index]
    equipped_pendants[user_id][index] = 이름

    equipped_pendants[user_id] = [
        p for p in equipped_pendants[user_id]
        if p is not None
    ]

    save_data()

    old_text = old_pendant if old_pendant else "없음"

    await interaction.response.send_message(
        f"💍 **펜던트 장착 완료!**\n\n"
        f"장착 칸: **{칸}번**\n"
        f"이전 펜던트: **{old_text}**\n"
        f"새 펜던트: **{이름}**\n"
        f"추가 운: **+{PENDANT_DATA[이름]['luck']}**\n\n"
        f"현재 총 펜던트 운: **+{get_pendant_luck(user_id)}**"
    )

# =========================
# 간단 RPG 보스 시스템
# =========================

BOSS_TICKET_PRICE = 1_000_000

BOSS_DATA = {
    "고블린 킹": {
        "hp": 5000,
        "price": 1_000_000,
        "material": "고블린 왕관",
        "drop_min": 1,
        "drop_max": 3,
        "reward": 300_000
    },
    "심연의 골렘": {
        "hp": 88500,
        "price": 5_000_000,
        "material": "심연의 핵",
        "drop_min": 1,
        "drop_max": 2,
        "reward": 1_000_000
    },
    "레드 드래곤": {
        "hp": 300000,
        "price": 15_000_000,
        "material": "붉은 용비늘",
        "drop_min": 1,
        "drop_max": 2,
        "reward": 3_000_000
    },
    "공허의 군주": {
        "hp": 50000000,
        "price": 50_000_000,
        "material": "공허의 파편",
        "drop_min": 1,
        "drop_max": 1,
        "reward": 100_000_000
    }
}

BOSS_EQUIP_DATA = {
    "고블린 의 검": {
        "material": "고블린 왕관",
        "need": 10,
        "price": 2_000_000,
        "power": 500
    },
    "심연의 화살": {
        "material": "심연의 핵",
        "need": 12,
        "price": 8_000_000,
        "power": 1500
    },
    "레드 드래곤의 창": {
        "material": "붉은 용비늘",
        "need": 15,
        "price": 25_000_000,
        "power": 13000
    },
    "공허의 대검": {
        "material": "공허의 파편",
        "need": 20,
        "price": 100_000_000,
        "power": 150000
    }
}

# =========================
# 일반 상점 장비
# =========================

WEAPON_DATA = {
    "녹슨 단검": {
        "price": 50000,
        "power": 60
    },
    "훈련용 검": {
        "price": 120000,
        "power": 120
    },
    "철검": {
        "price": 350000,
        "power": 320
    },
    "강철 대검": {
        "price": 700000,
        "power": 460
    },
    "기사의 장검": {
        "price": 1500000,
        "power": 1100
    },
    "용병의 도끼": {
        "price": 3000000,
        "power": 3500
    },
    "마력의 지팡이": {
        "price": 5500000,
        "power": 8000
    },
    "암살자의 쌍검": {
        "price": 9000000,
        "power": 32000
    },
    "흑요석 검": {
        "price": 15000000,
        "power": 80000
    },
    "용사왕의 검": {
        "price": 25000000,
        "power": 105000
    },
    "천공의 창": {
        "price": 40000000,
        "power": 135000
    },
    "혼돈 파쇄자": {
        "price": 70000000,
        "power": 270000
    },
    "심연 절단자": {
        "price": 120000000,
        "power": 1000000
    },
    "별의 집행자": {
        "price": 250000000,
        "power": 3000000
    },
    "신멸의 대검": {
        "price": 500000000,
        "power": 4200000
    }
}

ARMOR_DATA = {
    "찢어진 천옷": {
        "price": 40000,
        "hp": 15
    },
    "가죽 갑옷": {
        "price": 100000,
        "hp": 35
    },
    "철 갑옷": {
        "price": 300000,
        "hp": 60
    },
    "강철 갑옷": {
        "price": 650000,
        "hp": 90
    },
    "기사 갑주": {
        "price": 1400000,
        "hp": 130
    },
    "중장 전투복": {
        "price": 2800000,
        "hp": 180
    },
    "마력 로브": {
        "price": 5000000,
        "hp": 240
    },
    "암흑 갑주": {
        "price": 8500000,
        "hp": 320
    },
    "흑요석 갑옷": {
        "price": 14000000,
        "hp": 420
    },
    "용비늘 갑옷": {
        "price": 23000000,
        "hp": 540
    },
    "천공 수호복": {
        "price": 38000000,
        "hp": 700
    },
    "심연 판금갑": {
        "price": 65000000,
        "hp": 920
    },
    "별빛 수호갑": {
        "price": 110000000,
        "hp": 1200
    },
    "공허의 갑주": {
        "price": 220000000,
        "hp": 1650
    },
    "신성 파괴자 갑옷": {
        "price": 450000000,
        "hp": 2400
    }
}

def get_boss_user(user_id):
    changed = False

    if user_id not in boss_tickets:
        boss_tickets[user_id] = {}
        changed = True

    if user_id not in boss_materials:
        boss_materials[user_id] = {}
        changed = True

    if user_id not in boss_data:
        boss_data[user_id] = {
            "equips": [],
            "equipped": None
        }
        changed = True

    boss_data[user_id].setdefault("equips", [])
    boss_data[user_id].setdefault("equipped", None)

    return changed


def get_boss_power(user_id):
    get_boss_user(user_id)

    equipped = boss_data[user_id].get("equipped")

    if not equipped:
        return 10

    return 10 + BOSS_EQUIP_DATA.get(equipped, {}).get("power", 0)


BOSS_ACTIONS = ["검 휘두르기", "활 쏘기", "막기", "마법 쓰기", "회피"]

# key가 value들을 이김
BOSS_ACTION_WIN = {
    "검 휘두르기": ["활 쏘기", "회피"],
    "활 쏘기": ["마법 쓰기", "회피"],
    "막기": ["검 휘두르기", "활 쏘기"],
    "마법 쓰기": ["막기", "검 휘두르기"],
    "회피": ["마법 쓰기", "막기"],
}


class BossActionButton(discord.ui.Button):
    def __init__(self, action):
        super().__init__(
            label=action,
            style=discord.ButtonStyle.primary
        )
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        view: BossRaidView = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ 니 보스전 아님.", ephemeral=True)
            return

        if len(view.player_actions) >= 3:
            await interaction.response.send_message("❌ 이미 3개 골랐음.", ephemeral=True)
            return

        view.player_actions.append(self.action)

        if len(view.player_actions) >= 3:
            await view.play_turn(interaction)
        else:
            await view.update_msg(
                interaction,
                f"선택한 행동: **{', '.join(view.player_actions)}**\n"
                f"남은 선택: **{3 - len(view.player_actions)}개**"
            )

class BossRaidView(discord.ui.View):
    def __init__(self, user_id, boss_name):
        super().__init__(timeout=40)

        self.user_id = user_id
        self.boss_name = boss_name
        self.boss = BOSS_DATA[boss_name]

        self.boss_hp = self.boss["hp"]

        self.max_hp = self.get_player_hp()
        self.player_hp = self.max_hp

        self.turn = 1
        self.player_actions = []
        self.message = None

        for action in BOSS_ACTIONS:
            self.add_item(BossActionButton(action))

    def get_player_hp(self):
        get_rpg_equipment(self.user_id)

        armor = equipped_armor[self.user_id]
        armor_hp = ARMOR_DATA.get(armor, {}).get("hp", 0)

        return 100 + armor_hp

    async def update_msg(self, interaction=None, text=""):
        content = (
            f"👹 **보스전: {self.boss_name}**\n\n"
            f"🔁 턴: **{self.turn}**\n"
            f"❤️ 보스 체력: **{max(0, self.boss_hp)}/{self.boss['hp']}**\n"
            f"⚔️ 내 전투력: **{get_total_power(self.user_id)}**\n"
            f"❤️ 내 체력: **{max(0, self.player_hp)}/{self.max_hp}**\n\n"
            f"이번 턴 행동을 3개 골라라.\n\n"
            f"{text}"
        )

        if interaction:
            await interaction.response.edit_message(
                content=content,
                view=self
            )
        else:
            await self.message.edit(
                content=content,
                view=self
            )

    def judge_action(self, player_action, boss_action):
        if player_action == boss_action:
            return "draw"

        if boss_action in BOSS_ACTION_WIN[player_action]:
            return "win"

        return "lose"

    async def play_turn(self, interaction):
        await interaction.response.defer()

        boss_actions = random.choices(BOSS_ACTIONS, k=3)

        player_power = get_total_power(self.user_id)

        total_player_damage = 0
        total_boss_damage = 0

        logs = []

        for i in range(3):

            p_action = self.player_actions[i]
            b_action = boss_actions[i]

            content = (
                f"👹 **보스전: {self.boss_name}**\n\n"
                f"🔁 턴: **{self.turn}**\n"
                f"❤️ 보스 체력: **{max(0, self.boss_hp)}/{self.boss['hp']}**\n"
                f"❤️ 내 체력: **{max(0, self.player_hp)}/{self.max_hp}**\n\n"
                f"⚔️ {i+1}번째 행동 비교 중...\n\n"
                f"너: **{p_action}**\n"
                f"보스: **???**"
            )

            await interaction.message.edit(
                content=content,
                view=None
            )

            await asyncio.sleep(0.8)

            result = self.judge_action(
                p_action,
                b_action
            )

            base_player_damage = random.randint(
                int(player_power * 0.7),
                int(player_power * 1.25)
            )

            base_boss_damage = random.randint(
                int(self.boss["hp"] * 0.01),
                int(self.boss["hp"] * 0.025)
            )

            if result == "win":

                dmg = int(base_player_damage * 1.6)

                total_player_damage += dmg

                result_text = (
                    f"✅ 승리! "
                    f"보스에게 **{dmg}** 피해"
                )

            elif result == "lose":

                dmg = int(base_boss_damage * 1.2)

                total_boss_damage += dmg

                result_text = (
                    f"❌ 패배... "
                    f"내 체력 **-{dmg}**"
                )

            else:

                dmg = int(base_player_damage * 0.4)
                enemy_dmg = int(base_boss_damage * 0.4)

                total_player_damage += dmg
                total_boss_damage += enemy_dmg

                result_text = (
                    f"➖ 비김. "
                    f"보스 **-{dmg}**, "
                    f"나 **-{enemy_dmg}**"
                )

            logs.append(
                f"{i+1}. "
                f"**{p_action}** vs **{b_action}** → "
                f"{result_text}"
            )

            content = (
                f"👹 **보스전: {self.boss_name}**\n\n"
                f"🔁 턴: **{self.turn}**\n"
                f"❤️ 보스 체력: **{max(0, self.boss_hp)}/{self.boss['hp']}**\n"
                f"❤️ 내 체력: **{max(0, self.player_hp)}/{self.max_hp}**\n\n"
                f"⚔️ {i+1}번째 행동 공개!\n\n"
                f"너: **{p_action}**\n"
                f"보스: **{b_action}**\n\n"
                f"{result_text}\n\n"
                f"## 현재까지 결과\n"
                + "\n".join(logs)
            )

            await interaction.message.edit(
                content=content,
                view=None
            )

            await asyncio.sleep(1.1)

        self.boss_hp -= total_player_damage
        self.player_hp -= total_boss_damage

        self.player_actions = []

        if self.boss_hp <= 0:
            await self.win_after_defer(interaction)
            return

        if self.player_hp <= 0:
            await self.lose_after_defer(interaction)
            return

        self.turn += 1

        await interaction.message.edit(
            content=(
                f"👹 **보스전: {self.boss_name}**\n\n"
                f"🔁 턴: **{self.turn}**\n"
                f"❤️ 보스 체력: **{max(0, self.boss_hp)}/{self.boss['hp']}**\n"
                f"⚔️ 내 전투력: **{get_total_power(self.user_id)}**\n"
                f"❤️ 내 체력: **{max(0, self.player_hp)}/{self.max_hp}**\n\n"
                f"🗡️ 이번 턴 총 피해: **{total_player_damage}**\n"
                f"💥 이번 턴 받은 피해: **{total_boss_damage}**\n\n"
                f"다음 턴 행동을 3개 골라라."
            ),
            view=self
        )

    async def win_after_defer(self, interaction):

        get_wallet(self.user_id)
        get_boss_user(self.user_id)

        material = self.boss["material"]

        amount = random.randint(
            self.boss["drop_min"],
            self.boss["drop_max"]
        )

        reward = self.boss["reward"]

        boss_materials[self.user_id][material] = (
            boss_materials[self.user_id].get(material, 0)
            + amount
        )

        money_data[self.user_id] += reward

        save_data()

        await interaction.message.edit(
            content=(
                f"🏆 **보스 처치 성공!**\n\n"
                f"처치한 보스: **{self.boss_name}**\n"
                f"획득 재료: **{material} x{amount}**\n"
                f"획득 돈: **{money(reward)}원**"
            ),
            view=None
        )

        self.stop()

    async def lose_after_defer(self, interaction):

        await interaction.message.edit(
            content=(
                f"💀 **보스전 실패...**\n\n"
                f"보스 **{self.boss_name}**에게 밀려났다."
            ),
            view=None
        )

        self.stop()

    async def on_timeout(self):

        if self.message:
            await self.message.edit(
                content="⏰ 시간이 지나 보스가 사라졌다...",
                view=None
            )


@bot.tree.command(name="보스목록", description="도전 가능한 보스 목록", guild=GUILD)
async def boss_list(interaction: discord.Interaction):
    text = "\n\n".join(
        f"**{name}**\n"
        f"입장권 가격: **{money(data['price'])}원**\n"
        f"체력: **{data['hp']}**\n"
        f"드랍: **{data['material']}**"
        for name, data in BOSS_DATA.items()
    )

    await interaction.response.send_message(
        f"👹 **보스 목록**\n\n{text}"
    )


@bot.tree.command(name="보스입장권", description="보스 입장권을 구매한다", guild=GUILD)
@app_commands.describe(보스="입장권을 구매할 보스 이름", 갯수="구매할 갯수")
async def buy_boss_ticket(interaction: discord.Interaction, 보스: str, 갯수: int = 1):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_boss_user(user_id)

    if 보스 not in BOSS_DATA:
        await interaction.response.send_message("❌ 그런 보스는 없음.", ephemeral=True)
        return

    if 갯수 <= 0:
        await interaction.response.send_message("❌ 1개 이상 구매해야 함.", ephemeral=True)
        return

    price = BOSS_DATA[보스]["price"] * 갯수

    if money_data[user_id] < price:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n필요 금액: **{money(price)}원**\n현재 잔액: **{money(money_data[user_id])}원**",
            ephemeral=True
        )
        return

    money_data[user_id] -= price
    boss_tickets[user_id][보스] = boss_tickets[user_id].get(보스, 0) + 갯수
    save_data()

    await interaction.response.send_message(
        f"🎟️ 보스 입장권 구매 완료!\n\n"
        f"보스: **{보스}**\n"
        f"수량: **{갯수}장**\n"
        f"사용 금액: **{money(price)}원**\n\n"
        f"현재 잔액: **{money(money_data[user_id])}원**"
    )


@bot.tree.command(name="보스도전", description="보스에게 도전한다", guild=GUILD)
@app_commands.describe(보스="도전할 보스 이름")
async def boss_challenge(interaction: discord.Interaction, 보스: str):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_boss_user(user_id)

    if 보스 not in BOSS_DATA:
        await interaction.response.send_message("❌ 그런 보스는 없음.", ephemeral=True)
        return

    if boss_tickets[user_id].get(보스, 0) <= 0:
        await interaction.response.send_message("❌ 해당 보스 입장권이 없음.", ephemeral=True)
        return

    boss_tickets[user_id][보스] -= 1

    if boss_tickets[user_id][보스] <= 0:
        del boss_tickets[user_id][보스]

    save_data()

    view = BossRaidView(user_id, 보스)

    await interaction.response.send_message(
        f"🌑 **보스전 입장...**\n\n"
        f"👹 **{보스}**가 나타났다!",
        view=view
    )

    view.message = await interaction.original_response()
    await view.update_msg()


@bot.tree.command(name="보스가방", description="보스 재료와 입장권 확인", guild=GUILD)
async def boss_bag(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_boss_user(user_id)

    ticket_text = "\n".join(
        f"🎟️ {name}: {count}장"
        for name, count in boss_tickets[user_id].items()
    ) or "없음"

    material_text = "\n".join(
        f"🧩 {name}: {count}개"
        for name, count in boss_materials[user_id].items()
    ) or "없음"

    equips = boss_data[user_id].get("equips", [])
    equipped = boss_data[user_id].get("equipped")

    equip_text = "\n".join(
        f"{'✅ ' if item == equipped else ''}{item}"
        for item in equips
    ) or "없음"

    await interaction.response.send_message(
        f"🎒 **보스 가방**\n\n"
        f"## 입장권\n{ticket_text}\n\n"
        f"## 재료\n{material_text}\n\n"
        f"## 장비\n{equip_text}"
    )


@bot.tree.command(name="보스장비제작", description="보스 재료로 장비를 제작한다", guild=GUILD)
@app_commands.describe(장비="제작할 장비 이름")
async def craft_boss_equip(interaction: discord.Interaction, 장비: str):
    user_id = interaction.user.id

    get_wallet(user_id)
    get_boss_user(user_id)

    if 장비 not in BOSS_EQUIP_DATA:
        await interaction.response.send_message("❌ 그런 장비는 없음.", ephemeral=True)
        return

    if 장비 in boss_data[user_id]["equips"]:
        await interaction.response.send_message("❌ 이미 제작한 장비임.", ephemeral=True)
        return

    data = BOSS_EQUIP_DATA[장비]
    material = data["material"]
    need = data["need"]
    price = data["price"]

    have = boss_materials[user_id].get(material, 0)

    if have < need:
        await interaction.response.send_message(
            f"❌ 재료 부족.\n필요: **{material} x{need}**\n보유: **{have}개**",
            ephemeral=True
        )
        return

    if money_data[user_id] < price:
        await interaction.response.send_message(
            f"❌ 돈 부족.\n필요 금액: **{money(price)}원**\n현재 잔액: **{money(money_data[user_id])}원**",
            ephemeral=True
        )
        return

    boss_materials[user_id][material] -= need

    if boss_materials[user_id][material] <= 0:
        del boss_materials[user_id][material]

    money_data[user_id] -= price
    boss_data[user_id]["equips"].append(장비)
    boss_data[user_id]["equipped"] = 장비

    save_data()

    await interaction.response.send_message(
        f"⚒️ 보스 장비 제작 완료!\n\n"
        f"제작 장비: **{장비}**\n"
        f"전투력: **+{data['power']}**\n"
        f"사용 재료: **{material} x{need}**\n"
        f"사용 금액: **{money(price)}원**\n\n"
        f"자동 장착됨."
    )


@bot.tree.command(name="보스장비목록", description="제작 가능한 보스 장비 목록", guild=GUILD)
async def boss_equip_list(interaction: discord.Interaction):
    text = "\n\n".join(
        f"**{name}**\n"
        f"전투력: **+{data['power']}**\n"
        f"필요 재료: **{data['material']} x{data['need']}**\n"
        f"제작 비용: **{money(data['price'])}원**"
        for name, data in BOSS_EQUIP_DATA.items()
    )

    await interaction.response.send_message(
        f"⚒️ **보스 장비 목록**\n\n{text}"
    )


@bot.tree.command(name="보스장비", description="보스 장비를 장착한다", guild=GUILD)
@app_commands.describe(장비="장착할 보스 장비 이름")
async def equip_boss_item(interaction: discord.Interaction, 장비: str):
    user_id = interaction.user.id
    get_boss_user(user_id)

    if 장비 not in boss_data[user_id]["equips"]:
        await interaction.response.send_message("❌ 보유한 보스 장비가 아님.", ephemeral=True)
        return

    boss_data[user_id]["equipped"] = 장비
    save_data()

    await interaction.response.send_message(
        f"✅ 보스 장비 장착 완료!\n현재 장비: **{장비}**\n"
        f"현재 전투력: **{get_boss_power(user_id)}**"
    )

def get_rpg_equipment(user_id):
    changed = False

    if user_id not in owned_weapons:
        owned_weapons[user_id] = ["녹슨 단검"]
        changed = True

    if user_id not in equipped_weapon:
        equipped_weapon[user_id] = "녹슨 단검"
        changed = True

    if user_id not in owned_armors:
        owned_armors[user_id] = ["찢어진 천옷"]
        changed = True

    if user_id not in equipped_armor:
        equipped_armor[user_id] = "찢어진 천옷"
        changed = True

    return changed


def get_total_power(user_id):
    get_rpg_equipment(user_id)

    weapon = equipped_weapon[user_id]
    armor = equipped_armor[user_id]

    weapon_power = WEAPON_DATA.get(weapon, {}).get("power", 0)
    armor_hp = ARMOR_DATA.get(armor, {}).get("hp", 0)

    return (
        10 +
        weapon_power +
        int(armor_hp / 20) +
        get_boss_power(user_id)
    )

@bot.tree.command(name="무기상점", description="무기 상점", guild=GUILD)
async def weapon_shop(interaction: discord.Interaction):

    text = "\n\n".join(
        f"⚔️ {name}\n"
        f"전투력: +{data['power']}\n"
        f"가격: {money(data['price'])}원"
        for name, data in WEAPON_DATA.items()
    )

    await interaction.response.send_message(
        f"⚔️ 무기 상점\n\n{text}"
    )

@bot.tree.command(name="갑옷상점", description="갑옷 상점", guild=GUILD)
async def armor_shop(interaction: discord.Interaction):

    text = "\n\n".join(
        f"🛡️ {name}\n"
        f"체력: +{data['hp']}\n"
        f"가격: {money(data['price'])}원"
        for name, data in ARMOR_DATA.items()
    )

    await interaction.response.send_message(
        f"🛡️ 갑옷 상점\n\n{text}"
    )

@bot.tree.command(name="무기구매", description="무기 구매", guild=GUILD)
@app_commands.describe(무기="구매할 무기")
async def buy_weapon(interaction: discord.Interaction, 무기: str):

    user_id = interaction.user.id

    get_wallet(user_id)
    get_rpg_equipment(user_id)

    if 무기 not in WEAPON_DATA:
        await interaction.response.send_message(
            "❌ 그런 무기는 없음.",
            ephemeral=True
        )
        return

    if 무기 in owned_weapons[user_id]:
        await interaction.response.send_message(
            "❌ 이미 보유중인 무기임.",
            ephemeral=True
        )
        return

    price = WEAPON_DATA[무기]["price"]

    if money_data[user_id] < price:
        await interaction.response.send_message(
            "❌ 돈 부족.",
            ephemeral=True
        )
        return

    money_data[user_id] -= price

    owned_weapons[user_id].append(무기)
    equipped_weapon[user_id] = 무기

    save_data()

    await interaction.response.send_message(
        f"⚔️ 무기 구매 완료!\n\n"
        f"구매 무기: **{무기}**\n"
        f"자동 장착됨.\n\n"
        f"현재 전투력: **{get_total_power(user_id)}**"
    )

@bot.tree.command(name="갑옷구매", description="갑옷 구매", guild=GUILD)
@app_commands.describe(갑옷="구매할 갑옷")
async def buy_armor(interaction: discord.Interaction, 갑옷: str):

    user_id = interaction.user.id

    get_wallet(user_id)
    get_rpg_equipment(user_id)

    if 갑옷 not in ARMOR_DATA:
        await interaction.response.send_message(
            "❌ 그런 갑옷은 없음.",
            ephemeral=True
        )
        return

    if 갑옷 in owned_armors[user_id]:
        await interaction.response.send_message(
            "❌ 이미 보유중인 갑옷임.",
            ephemeral=True
        )
        return

    price = ARMOR_DATA[갑옷]["price"]

    if money_data[user_id] < price:
        await interaction.response.send_message(
            "❌ 돈 부족.",
            ephemeral=True
        )
        return

    money_data[user_id] -= price

    owned_armors[user_id].append(갑옷)
    equipped_armor[user_id] = 갑옷

    save_data()

    await interaction.response.send_message(
        f"🛡️ 갑옷 구매 완료!\n\n"
        f"구매 갑옷: **{갑옷}**\n"
        f"자동 장착됨.\n\n"
        f"현재 전투력: **{get_total_power(user_id)}**"
    )

@bot.tree.command(name="무기장착", description="무기 장착", guild=GUILD)
@app_commands.describe(무기="장착할 무기")
async def equip_weapon(interaction: discord.Interaction, 무기: str):

    user_id = interaction.user.id
    get_rpg_equipment(user_id)

    if 무기 not in owned_weapons[user_id]:
        await interaction.response.send_message(
            "❌ 보유하지 않은 무기임.",
            ephemeral=True
        )
        return

    equipped_weapon[user_id] = 무기
    save_data()

    await interaction.response.send_message(
        f"⚔️ 장착 완료!\n현재 무기: **{무기}**"
    )


@bot.tree.command(name="갑옷장착", description="갑옷 장착", guild=GUILD)
@app_commands.describe(갑옷="장착할 갑옷")
async def equip_armor(interaction: discord.Interaction, 갑옷: str):

    user_id = interaction.user.id
    get_rpg_equipment(user_id)

    if 갑옷 not in owned_armors[user_id]:
        await interaction.response.send_message(
            "❌ 보유하지 않은 갑옷임.",
            ephemeral=True
        )
        return

    equipped_armor[user_id] = 갑옷
    save_data()

    await interaction.response.send_message(
        f"🛡️ 장착 완료!\n현재 갑옷: **{갑옷}**"
    )

@bot.tree.command(name="내장비", description="현재 장비 확인", guild=GUILD)
async def my_equipment(interaction: discord.Interaction):

    user_id = interaction.user.id

    get_rpg_equipment(user_id)
    get_boss_user(user_id)

    weapon = equipped_weapon[user_id]
    armor = equipped_armor[user_id]

    boss_equip = boss_data[user_id].get("equipped")

    await interaction.response.send_message(
        f"⚔️ 현재 장비\n\n"
        f"무기: **{weapon}**\n"
        f"갑옷: **{armor}**\n"
        f"보스 장비: **{boss_equip or '없음'}**\n\n"
        f"총 전투력: **{get_total_power(user_id)}**"
    )


load_data()
bot.run(TOKEN)
