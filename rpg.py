import os, json, random, math
import discord
from discord import app_commands
from discord.ui import View, Button


    active_battles = {}
    
RPG_FILE = "/data/rpg_data.json"
os.makedirs("/data", exist_ok=True)

active_battles = {}

BASE_STATS = {
    "힘": 0,
    "민첩": 0,
    "방어력": 0,
    "체력": 0,
    "지능": 0,
    "지혜": 0
}

FIRST_JOBS = ["전사", "궁수", "도적", "탱커"]

JOB_NAMES = [
    "검투사", "광전사", "기사", "성기사", "용병", "창기사", "검성", "무투가", "권왕", "파괴자",
    "저격수", "명궁", "사냥꾼", "석궁병", "바람궁수", "추적자", "매의눈", "포수", "탄궁사", "그림자궁수",
    "암살자", "닌자", "괴도", "그림자도적", "독술사", "추격자", "밤의칼날", "처형자", "환영도적", "단검왕",
    "수호자", "철벽기사", "방패병", "성벽", "중갑전사", "요새기사", "불굴자", "도발자", "방패성자", "거석병",
    "마검사", "룬기사", "전투마법사", "현자", "원소술사", "빙결술사", "화염술사", "폭풍술사", "치유사", "대마도사"
]

JOB_BONUS = {
    name: {
        "힘": random.randint(0, 5),
        "민첩": random.randint(0, 5),
        "방어력": random.randint(0, 5),
        "체력": random.randint(0, 5),
        "지능": random.randint(0, 5),
        "지혜": random.randint(0, 5),
    }
    for name in JOB_NAMES + FIRST_JOBS
}

JOB_SKILLS = {
    job: [
        f"{job} 기본기",
        f"{job} 연격",
        f"{job} 각성기 I",
        f"{job} 각성기 II",
        f"{job} 궁극기"
    ]
    for job in JOB_NAMES + FIRST_JOBS
}

MONSTER_PREFIX = [
    "굶주린", "붉은", "검은", "푸른", "오래된", "저주받은", "광기의", "철갑", "독안개", "불타는",
    "얼어붙은", "그림자", "폭풍의", "심연의", "고대의", "흉포한", "거대한", "작은", "피투성이", "광폭한"
]

MONSTER_BASE = [
    "슬라임", "고블린", "늑대", "멧돼지", "해골병", "좀비", "박쥐", "거미", "오크", "트롤",
    "리자드맨", "하피", "미믹", "골렘", "망령", "임프", "와이번", "가고일", "키메라", "미노타우로스",
    "코볼트", "구울", "사령견", "뱀술사", "도마뱀전사", "흡혈박쥐", "암석정령", "불꽃정령", "얼음정령", "늪괴물"
]

MONSTERS = []
for i in range(120):
    name = f"{MONSTER_PREFIX[i % len(MONSTER_PREFIX)]} {MONSTER_BASE[i % len(MONSTER_BASE)]}"
    level = i + 1
    MONSTERS.append({
        "name": name,
        "level": level,
        "hp": 80 + level * 25,
        "atk": 8 + level * 3,
        "def": level,
        "exp": 40 + level * 15,
        "gold": 50 + level * 20,
        "weapon": f"{name}의 무기",
        "armor": f"{name}의 갑옷"
    })

SHOP_WEAPONS = {
    f"훈련용 무기 {i}": {
        "price": 500 * i,
        "atk": 3 * i,
        "matk": i
    }
    for i in range(1, 21)
}

SHOP_ARMORS = {
    f"훈련용 갑옷 {i}": {
        "price": 500 * i,
        "def": 2 * i,
        "hp": 20 * i
    }
    for i in range(1, 21)
}

DROP_WEAPONS = {
    mob["weapon"]: {
        "atk": 5 + mob["level"] * 2,
        "matk": mob["level"],
        "source": mob["name"]
    }
    for mob in MONSTERS
}

DROP_ARMORS = {
    mob["armor"]: {
        "def": 3 + mob["level"],
        "hp": 30 + mob["level"] * 5,
        "source": mob["name"]
    }
    for mob in MONSTERS
}

CONSUMABLES = {
    f"회복 물약 {i}": {
        "type": "heal",
        "value": 30 + i * 5
    }
    for i in range(1, 151)
}

SKILLBOOKS = {
    f"{job} 스킬북 {i}": {
        "job": job,
        "skill": JOB_SKILLS[job][min(i + 1, 4)]
    }
    for job in JOB_NAMES + FIRST_JOBS
    for i in range(1, 4)
}

ITEM_PRICES = {
    name: 100 + i * 25
    for i, name in enumerate(CONSUMABLES.keys(), start=1)
}

def load_rpg():
    if not os.path.exists(RPG_FILE):
        return {}
    with open(RPG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rpg(data):
    with open(RPG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

rpg_data = load_rpg()

def get_player(user_id):
    user_id = str(user_id)

    if user_id not in rpg_data:
        rpg_data[user_id] = {
            "level": 1,
            "exp": 0,
            "gold": 0,
            "job": "초보자",
            "job_level": 0,
            "stat_points": 3,
            "stats": BASE_STATS.copy(),
            "weapon": None,
            "armor": None,
            "inventory": {},
            "weapons": [],
            "armors": [],
            "learned_skills": []
        }
        save_rpg(rpg_data)

    p = rpg_data[user_id]

    # 예전 저장 데이터 호환용
    p.setdefault("level", 1)
    p.setdefault("exp", 0)
    p.setdefault("gold", 0)
    p.setdefault("job", "초보자")
    p.setdefault("job_level", 0)
    p.setdefault("stat_points", 3)
    p.setdefault("stats", BASE_STATS.copy())
    p.setdefault("weapon", None)
    p.setdefault("armor", None)
    p.setdefault("inventory", {})
    p.setdefault("weapons", [])
    p.setdefault("armors", [])
    p.setdefault("learned_skills", [])

    for stat_name in BASE_STATS:
        p["stats"].setdefault(stat_name, 0)

    return p

def need_exp(level):
    return 100 + level * 50

def calc_stat(p):
    s = p["stats"]
    weapon = SHOP_WEAPONS.get(p["weapon"]) or DROP_WEAPONS.get(p["weapon"]) or {"atk": 0, "matk": 0}
    armor = SHOP_ARMORS.get(p["armor"]) or DROP_ARMORS.get(p["armor"]) or {"def": 0, "hp": 0}

    bonus = JOB_BONUS.get(p["job"], BASE_STATS)

    hp = 100 + p["level"] * 20 + s["체력"] * 10 + bonus["체력"] * 10 + armor.get("hp", 0)
    mp = 30 + s["지혜"] * 5 + bonus["지혜"] * 5

    atk = 10 + p["level"] * 2 + weapon.get("atk", 0)
    atk = int(atk * (1 + (s["힘"] + bonus["힘"]) * 0.02))

    matk = 8 + p["level"] * 2 + weapon.get("matk", 0)
    matk = int(matk * (1 + (s["지능"] + bonus["지능"]) * 0.02))

    evasion = min(40, (s["민첩"] + bonus["민첩"]) * 0.1)
    reduction = min(60, (s["방어력"] + bonus["방어력"]) * 0.1 + armor.get("def", 0) * 0.2)

    return {
        "hp": hp,
        "mp": mp,
        "atk": atk,
        "matk": matk,
        "evasion": evasion,
        "reduction": reduction
    }

def add_exp(p, amount):
    p["exp"] += amount
    leveled = 0

    while p["exp"] >= need_exp(p["level"]):
        p["exp"] -= need_exp(p["level"])
        p["level"] += 1
        p["stat_points"] += 3
        leveled += 1

    return leveled

def lose_penalty(p):
    p["level"] = max(1, p["level"] - 1)

    lost = None
    if random.random() < 0.10:
        candidates = []

        if p["weapon"]:
            candidates.append(("weapon", p["weapon"]))
        if p["armor"]:
            candidates.append(("armor", p["armor"]))
        for item, count in p["inventory"].items():
            if count > 0:
                candidates.append(("item", item))

        if candidates:
            kind, name = random.choice(candidates)
            lost = name

            if kind == "weapon":
                p["weapon"] = None
                if name in p["weapons"]:
                    p["weapons"].remove(name)
            elif kind == "armor":
                p["armor"] = None
                if name in p["armors"]:
                    p["armors"].remove(name)
            else:
                p["inventory"][name] -= 1
                if p["inventory"][name] <= 0:
                    del p["inventory"][name]

    return lost

class BattleView(View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    async def check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 니 전투 아님.", ephemeral=True)
            return False
        return True

    async def do_turn(self, interaction, action):
        if not await self.check(interaction):
            return

        uid = str(self.user_id)
        battle = active_battles.get(uid)

        if not battle:
            await interaction.response.send_message("❌ 전투 없음.", ephemeral=True)
            return

        p = get_player(self.user_id)
        stat = calc_stat(p)
        mob = battle["monster"]

        log = []

        if action == "attack":
            dmg = max(1, stat["atk"] - mob["def"])
            battle["mob_hp"] -= dmg
            log.append(f"🗡️ 공격! {mob['name']}에게 **{dmg}** 피해!")

        elif action == "defend":
            battle["defending"] = True
            log.append("🛡️ 방어 태세!")

        elif action == "skill":
            skills = JOB_SKILLS.get(p["job"], ["몸통박치기"])
            unlocked = 2
            if p["job_level"] >= 10:
                unlocked += 1
            if p["job_level"] >= 30:
                unlocked += 1
            if p["job_level"] >= 50:
                unlocked += 1

            skill = random.choice(skills[:unlocked])
            dmg = max(1, int(stat["matk"] * 1.8) - mob["def"])
            battle["mob_hp"] -= dmg
            log.append(f"✨ **{skill}** 사용! **{dmg}** 피해!")

        elif action == "item":
            inv = p["inventory"]
            potion = next((x for x in inv if x.startswith("회복 물약")), None)

            if not potion:
                log.append("🎒 쓸 아이템 없음!")
            else:
                heal = CONSUMABLES[potion]["value"]
                battle["player_hp"] = min(stat["hp"], battle["player_hp"] + heal)
                inv[potion] -= 1
                if inv[potion] <= 0:
                    del inv[potion]
                log.append(f"🧪 {potion} 사용! 체력 **{heal}** 회복!")

        if battle["mob_hp"] <= 0:
            exp = mob["exp"]
            gold = mob["gold"]

            get_wallet(self.user_id)
            money_data[self.user_id] += gold

            drop_text = ""

            if random.random() < 0.05:
                p["weapons"].append(mob["weapon"])
                drop_text += f"\n🎁 무기 드랍: **{mob['weapon']}**"

            if random.random() < 0.05:
                p["armors"].append(mob["armor"])
                drop_text += f"\n🎁 갑옷 드랍: **{mob['armor']}**"

            if random.random() < 0.25:
                item = random.choice(list(CONSUMABLES.keys()))
                p["inventory"][item] = p["inventory"].get(item, 0) + 1
                drop_text += f"\n🧪 아이템 드랍: **{item}**"

            if random.random() < 0.03:
                book = random.choice(list(SKILLBOOKS.keys()))
                p["inventory"][book] = p["inventory"].get(book, 0) + 1
                drop_text += f"\n📘 스킬북 드랍: **{book}**"

            active_battles.pop(uid, None)
            save_rpg(rpg_data)

            msg = (
                "\n".join(log)
                + f"\n\n🏆 승리!\nEXP +{exp}, 골드 +{gold}"
                + (f"\n⬆️ 레벨업 {leveled}번!" if leveled else "")
                + drop_text
            )

            await interaction.response.edit_message(content=msg, view=None)
            return

        if random.random() * 100 < stat["evasion"]:
            log.append(f"💨 {mob['name']}의 공격 회피!")
        else:
            mob_dmg = mob["atk"]
            reduction = stat["reduction"]

            if battle.get("defending"):
                reduction += 30
                battle["defending"] = False

            mob_dmg = max(1, int(mob_dmg * (1 - min(80, reduction) / 100)))
            battle["player_hp"] -= mob_dmg
            log.append(f"💥 {mob['name']}의 공격! **{mob_dmg}** 피해!")

        battle["turn"] += 1

        if battle["player_hp"] <= 0 or battle["turn"] > 150:
            lost = lose_penalty(p)
            active_battles.pop(uid, None)
            save_rpg(rpg_data)

            msg = "☠️ 패배...\n레벨 1 감소."
            if lost:
                msg += f"\n💀 10% 패널티 발동: **{lost}** 잃음."

            await interaction.response.edit_message(content=msg, view=None)
            return

        save_rpg(rpg_data)

        await interaction.response.edit_message(
            content=(
                "\n".join(log)
                + f"\n\n턴: **{battle['turn']} / 150**"
                + f"\n❤️ 내 체력: **{battle['player_hp']} / {stat['hp']}**"
                + f"\n👹 {mob['name']} 체력: **{battle['mob_hp']} / {mob['hp']}**"
            ),
            view=self
        )

    @discord.ui.button(label="공격", style=discord.ButtonStyle.danger)
    async def attack(self, interaction, button):
        await self.do_turn(interaction, "attack")

    @discord.ui.button(label="방어", style=discord.ButtonStyle.primary)
    async def defend(self, interaction, button):
        await self.do_turn(interaction, "defend")

    @discord.ui.button(label="스킬", style=discord.ButtonStyle.success)
    async def skill(self, interaction, button):
        await self.do_turn(interaction, "skill")

    @discord.ui.button(label="아이템", style=discord.ButtonStyle.secondary)
    async def item(self, interaction, button):
        await self.do_turn(interaction, "item")

def setup_rpg(bot, GUILD, money_data, get_wallet, save_data):

    @bot.tree.command(name="배틀", description="랜덤 몬스터와 턴제 전투", guild=GUILD)
    async def battle(interaction: discord.Interaction):
        p = get_player(interaction.user.id)
        uid = str(interaction.user.id)

        if uid in active_battles:
            await interaction.response.send_message("❌ 이미 전투 중임.", ephemeral=True)
            return

        level = p["level"]
        candidates = [
            m for m in MONSTERS
            if max(1, level - 10) <= m["level"] <= level + 10
        ]

        mob = random.choice(candidates)
        stat = calc_stat(p)

        active_battles[uid] = {
            "monster": mob,
            "mob_hp": mob["hp"],
            "player_hp": stat["hp"],
            "turn": 1,
            "defending": False
        }

        await interaction.response.send_message(
            f"⚔️ 전투 시작!\n\n"
            f"👹 몬스터: **Lv.{mob['level']} {mob['name']}**\n"
            f"❤️ 내 체력: **{stat['hp']}**\n"
            f"👹 몬스터 체력: **{mob['hp']}**\n\n"
            f"행동을 골라라.",
            view=BattleView(interaction.user.id)
        )

    @bot.tree.command(name="직업", description="레벨 5에 1차 직업 선택", guild=GUILD)
    @app_commands.describe(직업="전사, 궁수, 도적, 탱커")
    async def choose_job(interaction: discord.Interaction, 직업: str):
        p = get_player(interaction.user.id)

        if p["level"] < 5:
            await interaction.response.send_message("❌ 레벨 5부터 가능.")
            return

        if p["job"] != "초보자":
            await interaction.response.send_message("❌ 이미 직업 있음.")
            return

        if 직업 not in FIRST_JOBS:
            await interaction.response.send_message("❌ 전사/궁수/도적/탱커 중 하나.")
            return

        p["job"] = 직업
        p["job_level"] = 0
        save_rpg(rpg_data)

        await interaction.response.send_message(f"✅ 직업 선택 완료: **{직업}**")

    @bot.tree.command(name="전직", description="10레벨 이후 10레벨마다 랜덤 전직", guild=GUILD)
    async def job_change(interaction: discord.Interaction):
        p = get_player(interaction.user.id)

        if p["level"] < 10 or p["level"] % 10 != 0:
            await interaction.response.send_message("❌ 10레벨부터, 이후 10레벨 단위에서만 전직 가능.")
            return

        new_job = random.choices(
            JOB_NAMES,
            weights=[max(1, 60 - i) for i in range(len(JOB_NAMES))],
            k=1
        )[0]

        p["job"] = new_job
        p["job_level"] = 0
        save_rpg(rpg_data)

        await interaction.response.send_message(
            f"✨ 전직 완료!\n새 직업: **{new_job}**\n직업 레벨은 0으로 초기화됨."
        )

    @bot.tree.command(name="스탯창", description="내 RPG 스탯 확인", guild=GUILD)
    async def stat_window(interaction: discord.Interaction):
        p = get_player(interaction.user.id)
        stat = calc_stat(p)
        s = p["stats"]

        await interaction.response.send_message(
            f"📊 **스탯창**\n\n"
            f"Lv.{p['level']} / EXP {p['exp']} / {need_exp(p['level'])}\n"
            f"직업: **{p['job']}** Lv.{p['job_level']}\n"
            f"남은 스탯포인트: **{p['stat_points']}**\n\n"
            f"힘: {s['힘']}\n민첩: {s['민첩']}\n방어력: {s['방어력']}\n체력: {s['체력']}\n지능: {s['지능']}\n지혜: {s['지혜']}\n\n"
            f"❤️ HP: {stat['hp']}\n💙 MP: {stat['mp']}\n"
            f"🗡️ 물리공격: {stat['atk']}\n✨ 마법공격: {stat['matk']}\n"
            f"💨 회피: {stat['evasion']:.1f}%\n🛡️ 뎀감: {stat['reduction']:.1f}%"
        )

    @bot.tree.command(name="스탯투자", description="스탯포인트 투자", guild=GUILD)
    @app_commands.describe(스탯="힘/민첩/방어력/체력/지능/지혜", 수치="투자할 수치")
    async def add_stat(interaction: discord.Interaction, 스탯: str, 수치: int):
        p = get_player(interaction.user.id)

        if 스탯 not in BASE_STATS:
            await interaction.response.send_message("❌ 없는 스탯임.")
            return

        if 수치 <= 0 or p["stat_points"] < 수치:
            await interaction.response.send_message("❌ 스탯포인트 부족.")
            return

        p["stats"][스탯] += 수치
        p["stat_points"] -= 수치
        save_rpg(rpg_data)

        await interaction.response.send_message(f"✅ {스탯}에 {수치} 투자 완료.")

    @bot.tree.command(name="프로필", description="내 RPG 프로필 확인", guild=GUILD)
    async def profile(interaction: discord.Interaction):
    p = get_player(interaction.user.id)

    get_wallet(interaction.user.id)

    await interaction.response.send_message(
        f"🧾 **프로필**\n\n"
        f"레벨: **{p['level']}**\n"
        f"직업: **{p['job']}** Lv.{p['job_level']}\n"
        f"골드: **{money_data[interaction.user.id]:,}원**\n"
        f"무기: **{p['weapon'] or '없음'}**\n"
        f"갑옷: **{p['armor'] or '없음'}**\n"
        f"보유 무기: {len(p['weapons'])}개\n"
        f"보유 갑옷: {len(p['armors'])}개\n"
        f"아이템 종류: {len(p['inventory'])}개"
    )

    @bot.tree.command(name="무기상점", description="무기상점 보기 또는 구매", guild=GUILD)
    @app_commands.describe(무기이름="구매할 무기 이름")
    async def weapon_shop(interaction: discord.Interaction, 무기이름: str = None):
        p = get_player(interaction.user.id)

        if 무기이름 is None:
            text = "\n".join(
                f"{name} - {w['price']}G / 공격 +{w['atk']}"
                for name, w in SHOP_WEAPONS.items()
            )
            await interaction.response.send_message(f"⚔️ **무기상점**\n\n{text}")
            return

        if 무기이름 not in SHOP_WEAPONS:
            await interaction.response.send_message("❌ 그런 무기 없음.")
            return

        item = SHOP_WEAPONS[무기이름]

        if p["gold"] < item["price"]:
            await interaction.response.send_message("❌ 골드 부족.")
            return

        p["gold"] -= item["price"]
        p["weapons"].append(무기이름)
        p["weapon"] = 무기이름
        save_rpg(rpg_data)

        await interaction.response.send_message(f"✅ 구매 후 장착 완료: **{무기이름}**")

    @bot.tree.command(name="갑옷상점", description="갑옷상점 보기 또는 구매", guild=GUILD)
    @app_commands.describe(갑옷이름="구매할 갑옷 이름")
    async def armor_shop(interaction: discord.Interaction, 갑옷이름: str = None):
        p = get_player(interaction.user.id)

        if 갑옷이름 is None:
            text = "\n".join(
                f"{name} - {a['price']}G / 방어 +{a['def']} / 체력 +{a['hp']}"
                for name, a in SHOP_ARMORS.items()
            )
            await interaction.response.send_message(f"🛡️ **갑옷상점**\n\n{text}")
            return

        if 갑옷이름 not in SHOP_ARMORS:
            await interaction.response.send_message("❌ 그런 갑옷 없음.")
            return

        item = SHOP_ARMORS[갑옷이름]

        if p["gold"] < item["price"]:
            await interaction.response.send_message("❌ 골드 부족.")
            return

        p["gold"] -= item["price"]
        p["armors"].append(갑옷이름)
        p["armor"] = 갑옷이름
        save_rpg(rpg_data)

        await interaction.response.send_message(f"✅ 구매 후 장착 완료: **{갑옷이름}**")

    @bot.tree.command(name="장착", description="보유한 무기/갑옷을 장착", guild=GUILD)
    @app_commands.describe(
        장비이름="장착할 무기 또는 갑옷 이름"
    )
    async def equip_item(interaction: discord.Interaction, 장비이름: str):
        p = get_player(interaction.user.id)

        if 장비이름 in p["weapons"]:
            p["weapon"] = 장비이름
            save_rpg(rpg_data)
            await interaction.response.send_message(f"⚔️ 무기 장착 완료: **{장비이름}**")
            return

        if 장비이름 in p["armors"]:
            p["armor"] = 장비이름
            save_rpg(rpg_data)
            await interaction.response.send_message(f"🛡️ 갑옷 장착 완료: **{장비이름}**")
            return

        await interaction.response.send_message("❌ 그런 장비를 보유하고 있지 않음.")


    @bot.tree.command(name="인벤", description="내 RPG 인벤토리 확인", guild=GUILD)
    async def inventory(interaction: discord.Interaction):
        p = get_player(interaction.user.id)

        weapons = "\n".join(
            f"{'✅ ' if w == p['weapon'] else ''}{w}"
            for w in p["weapons"][:30]
        ) or "없음"

        armors = "\n".join(
            f"{'✅ ' if a == p['armor'] else ''}{a}"
            for a in p["armors"][:30]
        ) or "없음"

        items = "\n".join(
            f"{name} x{count}"
            for name, count in list(p["inventory"].items())[:50]
        ) or "없음"

        await interaction.response.send_message(
            f"🎒 **인벤토리**\n\n"
            f"⚔️ **무기**\n{weapons}\n\n"
            f"🛡️ **갑옷**\n{armors}\n\n"
            f"🧪 **아이템**\n{items}"
        )


    @bot.tree.command(name="아이템상점", description="아이템상점 보기 또는 구매", guild=GUILD)
    @app_commands.describe(
        아이템이름="구매할 아이템 이름",
        갯수="구매할 갯수"
    )
    async def item_shop(
        interaction: discord.Interaction,
        아이템이름: str = None,
        갯수: int = 1
    ):
        p = get_player(interaction.user.id)

        if 아이템이름 is None:
            sample_items = list(ITEM_PRICES.items())[:30]

            text = "\n".join(
                f"{name} - {price}G / 회복 {CONSUMABLES[name]['value']}"
                for name, price in sample_items
            )

            await interaction.response.send_message(
                f"🧪 **아이템상점**\n\n"
                f"{text}\n\n"
                f"※ 아이템은 총 150개 있음.\n"
                f"`/아이템상점 아이템이름 갯수` 로 구매"
            )
            return

        if 아이템이름 not in CONSUMABLES:
            await interaction.response.send_message("❌ 그런 아이템 없음.")
            return

        if 갯수 <= 0:
            await interaction.response.send_message("❌ 1개 이상 구매해야 함.")
            return

        price = ITEM_PRICES[아이템이름] * 갯수

        if p["gold"] < price:
            await interaction.response.send_message(
                f"❌ 골드 부족.\n필요 골드: **{price}G**\n보유 골드: **{p['gold']}G**"
            )
            return

        p["gold"] -= price
        p["inventory"][아이템이름] = p["inventory"].get(아이템이름, 0) + 갯수
        save_rpg(rpg_data)

        await interaction.response.send_message(
            f"✅ 구매 완료!\n"
            f"아이템: **{아이템이름} x{갯수}**\n"
            f"사용 골드: **{price}G**\n"
            f"남은 골드: **{p['gold']}G**"
        )


    @bot.tree.command(name="스킬북사용", description="스킬북을 사용해서 직업 스킬 습득", guild=GUILD)
    @app_commands.describe(
        스킬북이름="사용할 스킬북 이름"
    )
    async def use_skillbook(interaction: discord.Interaction, 스킬북이름: str):
        p = get_player(interaction.user.id)

        if 스킬북이름 not in p["inventory"] or p["inventory"][스킬북이름] <= 0:
            await interaction.response.send_message("❌ 해당 스킬북을 가지고 있지 않음.")
            return

        if 스킬북이름 not in SKILLBOOKS:
            await interaction.response.send_message("❌ 이건 스킬북이 아님.")
            return

        book = SKILLBOOKS[스킬북이름]

        if book["job"] != p["job"]:
            await interaction.response.send_message(
                f"❌ 현재 직업과 맞지 않는 스킬북임.\n"
                f"필요 직업: **{book['job']}**\n"
                f"현재 직업: **{p['job']}**"
            )
            return

        if "learned_skills" not in p:
            p["learned_skills"] = []

        skill = book["skill"]

        if skill in p["learned_skills"]:
            await interaction.response.send_message("❌ 이미 배운 스킬임.")
            return

        p["learned_skills"].append(skill)

        p["inventory"][스킬북이름] -= 1
        if p["inventory"][스킬북이름] <= 0:
            del p["inventory"][스킬북이름]

        save_rpg(rpg_data)

        await interaction.response.send_message(
            f"📘 스킬북 사용 완료!\n"
            f"새 스킬 습득: **{skill}**"
        )


    @bot.tree.command(name="아이템사용", description="인벤토리 아이템 직접 사용", guild=GUILD)
    @app_commands.describe(아이템이름="사용할 아이템 이름")
    async def use_item(interaction: discord.Interaction, 아이템이름: str):
        p = get_player(interaction.user.id)

        if 아이템이름 not in p["inventory"] or p["inventory"][아이템이름] <= 0:
            await interaction.response.send_message("❌ 해당 아이템을 가지고 있지 않음.")
            return

        if 아이템이름 in SKILLBOOKS:
            await interaction.response.send_message("📘 스킬북은 `/스킬북사용`으로 써야 함.")
            return

        if 아이템이름 not in CONSUMABLES:
            await interaction.response.send_message("❌ 사용할 수 없는 아이템임.")
            return

        item = CONSUMABLES[아이템이름]

        p["inventory"][아이템이름] -= 1
        if p["inventory"][아이템이름] <= 0:
            del p["inventory"][아이템이름]

        save_rpg(rpg_data)

        await interaction.response.send_message(
            f"🧪 **{아이템이름}** 사용 완료!\n"
            f"효과: 회복량 **{item['value']}**\n"
            f"※ 전투 중 회복은 `/배틀` 버튼의 `아이템`을 누르면 적용됨."
        )


    @bot.tree.command(name="스킬목록", description="현재 직업 스킬과 배운 스킬 확인", guild=GUILD)
    async def skill_list(interaction: discord.Interaction):
        p = get_player(interaction.user.id)

        skills = JOB_SKILLS.get(p["job"], ["몸통박치기"])
        unlocked = 2
        if p["job_level"] >= 10:
            unlocked += 1
        if p["job_level"] >= 30:
            unlocked += 1
        if p["job_level"] >= 50:
            unlocked += 1

        unlocked_skills = "\n".join(f"✅ {s}" for s in skills[:unlocked]) or "없음"
        locked_skills = "\n".join(f"🔒 {s}" for s in skills[unlocked:]) or "없음"
        learned = "\n".join(f"📘 {s}" for s in p.get("learned_skills", [])) or "없음"

        await interaction.response.send_message(
            f"✨ **스킬목록**\n\n"
            f"직업: **{p['job']}** Lv.{p['job_level']}\n\n"
            f"**해금된 직업 스킬**\n{unlocked_skills}\n\n"
            f"**잠긴 직업 스킬**\n{locked_skills}\n\n"
            f"**스킬북으로 배운 스킬**\n{learned}"
        )


    @bot.tree.command(name="장비목록", description="전체 장비 도감 일부 확인", guild=GUILD)
    async def equipment_list(interaction: discord.Interaction):
        shop_w = "\n".join(f"⚔️ {name} / 공격 +{v['atk']} / 마공 +{v['matk']}" for name, v in list(SHOP_WEAPONS.items())[:20])
        shop_a = "\n".join(f"🛡️ {name} / 방어 +{v['def']} / 체력 +{v['hp']}" for name, v in list(SHOP_ARMORS.items())[:20])

        await interaction.response.send_message(
            f"📚 **상점 장비 목록**\n\n"
            f"**무기 20종**\n{shop_w}\n\n"
            f"**갑옷 20종**\n{shop_a}\n\n"
            f"드랍 전용 무기 120종 / 갑옷 120종은 몬스터에게서 각각 5% 확률로 드랍됨."
        )


    @bot.tree.command(name="몹목록", description="등장 몬스터 일부 확인", guild=GUILD)
    async def monster_list(interaction: discord.Interaction):
        text = "\n".join(
            f"Lv.{m['level']} {m['name']} / HP {m['hp']} / ATK {m['atk']}"
            for m in MONSTERS[:40]
        )

        await interaction.response.send_message(
            f"👹 **몬스터 목록 일부**\n\n{text}\n\n"
            f"총 몬스터: **{len(MONSTERS)}종**"
        )

