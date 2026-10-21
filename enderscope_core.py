"""Core parsing and formatting helpers for EnderScope."""

import math
import pandas as pd

SAMPLE = {
    "stats": {
        "minecraft:mined": {
            "minecraft:stone": 1250,
            "minecraft:deepslate": 820,
            "minecraft:dirt": 410,
            "minecraft:coal_ore": 95,
            "minecraft:iron_ore": 72,
            "minecraft:diamond_ore": 8,
        },
        "minecraft:custom": {
            "minecraft:play_time": 144000,
            "minecraft:walk_one_cm": 850000,
            "minecraft:sprint_one_cm": 320000,
            "minecraft:jump": 1200,
            "minecraft:deaths": 3,
            "minecraft:damage_dealt": 2480,
            "minecraft:mob_kills": 69,
            "minecraft:time_since_death": 72000,
        },
        "minecraft:killed": {
            "minecraft:zombie": 42,
            "minecraft:skeleton": 18,
            "minecraft:creeper": 9,
        },
    },
    "DataVersion": 0,
}

CUSTOM_LABELS = {
    "play_time": "Play Time",
    "walk_one_cm": "Distance Walked",
    "sprint_one_cm": "Distance Sprinting",
    "swim_one_cm": "Distance Swum",
    "fly_one_cm": "Distance Flown",
    "aviate_one_cm": "Distance Elytra",
    "jump": "Jumps",
    "deaths": "Deaths",
    "mob_kills": "Mob Kills",
    "damage_dealt": "Damage Dealt",
    "damage_taken": "Damage Taken",
    "animals_bred": "Animals Bred",
    "fish_caught": "Fish Caught",
    "villager_trades": "Villager Trades",
    "chests_opened": "Chests Opened",
    "player_kills": "Player Kills",
    "walk_under_water_one_cm": "Distance Walked Underwater",
    "walk_on_water_one_cm": "Distance Walked on Water",
    "fall_one_cm": "Distance Fallen",
    "climb_one_cm": "Distance Climbed",
}

def label_id(identifier):
    name = str(identifier).split(":", 1)[-1]
    return name.replace("_", " ").title()

def safe_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )

def parse_stats(data):
    if not isinstance(data, dict):
        raise ValueError("The JSON root must be an object.")
    stats = data.get("stats", {})
    if not isinstance(stats, dict):
        raise ValueError("The 'stats' field must be an object.")

    def section(name):
        value = stats.get(f"minecraft:{name}", {})
        if not isinstance(value, dict):
            raise ValueError(f"The minecraft:{name} section is invalid.")
        for key, number in value.items():
            if not isinstance(key, str) or not safe_number(number):
                raise ValueError(f"Invalid statistic value in minecraft:{name}.")
        return value

    mined = section("mined")
    killed = section("killed")
    custom = section("custom")
    broken = section("broken")
    crafted = section("crafted")
    used = section("used")
    picked_up = section("picked_up")
    dropped = section("dropped")

    def custom_value(key):
        return float(custom.get(f"minecraft:{key}", 0))

    mined_df = pd.DataFrame(
        [{"Block": label_id(k), "ID": k, "Count": int(v)} for k, v in mined.items()],
        columns=["Block", "ID", "Count"],
    ).sort_values("Count", ascending=False, ignore_index=True)
    killed_df = pd.DataFrame(
        [{"Mob": label_id(k), "ID": k, "Count": int(v)} for k, v in killed.items()],
        columns=["Mob", "ID", "Count"],
    ).sort_values("Count", ascending=False, ignore_index=True)

    def item_df(items, title):
        return pd.DataFrame(
            [{title: label_id(k), "ID": k, "Count": int(v)} for k, v in items.items()],
            columns=[title, "ID", "Count"],
        ).sort_values("Count", ascending=False, ignore_index=True)

    # Minecraft play_time is measured in ticks; 20 ticks = 1 second.
    play_ticks = custom_value("play_time")
    return {
        "mined": mined_df,
        "killed": killed_df,
        "broken": item_df(broken, "Item"),
        "crafted": item_df(crafted, "Item"),
        "used": item_df(used, "Item"),
        "picked_up": item_df(picked_up, "Item"),
        "dropped": item_df(dropped, "Item"),
        "play_hours": play_ticks / 72000,
        "play_ticks": play_ticks,
        "walk_km": custom_value("walk_one_cm") / 100000,
        "sprint_km": custom_value("sprint_one_cm") / 100000,
        "jumps": int(custom_value("jump")),
        "deaths": int(custom_value("deaths")),
        "mob_kills": int(custom_value("mob_kills")),
        "damage_dealt": custom_value("damage_dealt") / 10,
        "damage_taken": custom_value("damage_taken") / 10,
        "animals_bred": int(custom_value("animals_bred")),
        "fish_caught": int(custom_value("fish_caught")),
        "villager_trades": int(custom_value("villager_trades")),
        "chests_opened": int(custom_value("open_chest")),
        "data_version": data.get("DataVersion", "Unknown"),
    }

def format_duration(hours):
    total_minutes = int(hours * 60)
    days, remainder = divmod(total_minutes, 24 * 60)
    hrs, minutes = divmod(remainder, 60)
    if days:
        return f"{days}d {hrs}h"
    if hrs:
        return f"{hrs}h {minutes}m"
    return f"{minutes}m"

