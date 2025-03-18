import sys
import json
import math
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def run_analysis_2d(config_path="configs/config_2c.json"):
    # Load configuration
    with open(config_path, "r") as f:
        config = json.load(f)["analysis"]

    # Parameters from config
    pokemon_list = config["pokemon"]
    pokeballs = config["pokeballs"]
    statuses = config["statuses"]
    hp_percentages = config["hp_percentages"]
    levels = config["levels"]
    num_experiments = config["num_experiments"]
    noise = config["noise"]

    # Fixed parameters for analyses that vary one factor at a time
    fixed_status = StatusEffect[config["fixed_status"]]
    fixed_hp = config["fixed_hp"]
    fixed_level = config["fixed_level"]

    factory = PokemonFactory("pokemon.json")
    results = []

    # Run simulation over all combinations
    for pkmn_name in pokemon_list:
        for status_str in statuses:
            status_effect = StatusEffect[status_str]
            for hp_perc in hp_percentages:
                for lvl in levels:
                    for ball in pokeballs:
                        success_count = 0
                        for _ in range(num_experiments):
                            poke = factory.create(pkmn_name, lvl, status_effect, hp_perc)
                            attempt_success, _ = attempt_catch(poke, ball, noise)
                            if attempt_success:
                                success_count += 1
                        success_rate = success_count / num_experiments
                        results.append({
                            "pokemon": pkmn_name,
                            "status": status_str,
                            "hp_perc": hp_perc,
                            "level": lvl,
                            "pokeball": ball,
                            "success_rate": success_rate
                        })

    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    
    # --- Graph 1: Combined Success vs. HP Percentage (Normal Pokéball, Fixed Level & Status) ---
    fig, ax = plt.subplots(figsize=(8, 5))
    hp_diff_percentages = []  # store per-Pokémon percentage differences over HP
    for pkmn in df["pokemon"].unique():
        subset = df[(df["pokemon"] == pkmn) &
                    (df["pokeball"] == "pokeball") &  # normal pokéball
                    (df["level"] == fixed_level) &
                    (df["status"] == fixed_status.name)]
        if not subset.empty:
            ax.plot(subset["hp_perc"], subset["success_rate"], marker='o', label=pkmn.capitalize())
            max_success = subset["success_rate"].max()
            min_success = subset["success_rate"].min()
            mean_success = subset["success_rate"].mean()
            diff_pct = ((max_success - min_success) / mean_success * 100) if mean_success != 0 else 0
            hp_diff_percentages.append(diff_pct)
    overall_hp_diff = np.mean(hp_diff_percentages) if hp_diff_percentages else 0
    print(f"\nGraph 1 (HP Variation) - Overall Average % Difference: {overall_hp_diff:.2f}%")
    ax.set_title(f"Combined: Success vs. HP Percentage\n(Fixed Level: {fixed_level}, Status: {fixed_status.name}, Normal Pokéball)\nAvg % Difference: {overall_hp_diff:.2f}%")
    ax.set_xlabel("HP Percentage")
    ax.set_ylabel("Success Rate")
    ax.legend()
    plt.tight_layout()
    plt.show()
    
    # --- Graph 2: Combined Success vs. Level (Normal Pokéball, Fixed HP & Status) ---
    fig, ax = plt.subplots(figsize=(8, 5))
    level_diff_percentages = []  # store per-Pokémon percentage differences over Level
    for pkmn in df["pokemon"].unique():
        subset = df[(df["pokemon"] == pkmn) &
                    (df["pokeball"] == "pokeball") &
                    (df["hp_perc"] == fixed_hp) &
                    (df["status"] == fixed_status.name)]
        if not subset.empty:
            ax.plot(subset["level"], subset["success_rate"], marker='o', label=pkmn.capitalize())
            max_success = subset["success_rate"].max()
            min_success = subset["success_rate"].min()
            mean_success = subset["success_rate"].mean()
            diff_pct = ((max_success - min_success) / mean_success * 100) if mean_success != 0 else 0
            level_diff_percentages.append(diff_pct)
    overall_level_diff = np.mean(level_diff_percentages) if level_diff_percentages else 0
    print(f"\nGraph 2 (Level Variation) - Overall Average % Difference: {overall_level_diff:.2f}%")
    ax.set_title(f"Combined: Success vs. Level\n(Fixed HP: {fixed_hp*100:.0f}%, Status: {fixed_status.name}, Normal Pokéball)\nAvg % Difference: {overall_level_diff:.2f}%")
    ax.set_xlabel("Level")
    ax.set_ylabel("Success Rate")
    ax.legend()
    plt.tight_layout()
    plt.show()
    
    # --- Graph 3: Combined Status Variation (Normal Pokéball, Fixed HP & Level, All Pokémon) ---
    mask_status = (df["hp_perc"] == fixed_hp) & (df["level"] == fixed_level) & (df["pokeball"] == "pokeball")
    df_status_fixed = df[mask_status]
    pivot_status = df_status_fixed.pivot_table(index="pokemon", columns="status", values="success_rate", aggfunc="mean")
    pivot_status = pivot_status.sort_index()
    status_diff_percentages = {}
    for pkmn, row in pivot_status.iterrows():
        max_val = row.max()
        min_val = row.min()
        mean_val = row.mean()
        diff_pct = ((max_val - min_val) / mean_val * 100) if mean_val != 0 else 0
        status_diff_percentages[pkmn] = diff_pct
    overall_status_diff = np.mean(list(status_diff_percentages.values()))
    print(f"\nGraph 3 (Status Variation) - Overall Average % Difference: {overall_status_diff:.2f}%")
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_status.plot(kind="bar", ax=ax)
    ax.set_title(f"Success vs. Status per Pokémon (Normal Pokéball, Fixed HP & Level)\nAvg % Difference across statuses: {overall_status_diff:.2f}%")
    ax.set_xlabel("Pokémon")
    ax.set_ylabel("Average Success Rate")
    plt.tight_layout()
    plt.show()
    
    # --- Graph 4: Combined Graph for Fixed HP, Level, and Status (Pokéball Variation) ---
    mask_fixed = (df["hp_perc"] == fixed_hp) & (df["level"] == fixed_level) & (df["status"] == fixed_status.name)
    df_fixed = df[mask_fixed]
    summary_fixed = df_fixed.groupby(["pokemon", "pokeball"])["success_rate"].mean().reset_index()
    pivot_fixed = summary_fixed.pivot(index="pokemon", columns="pokeball", values="success_rate")
    pivot_fixed = pivot_fixed.sort_index()
    pokeball_diff_percentages = {}
    for pkmn, row in pivot_fixed.iterrows():
        max_val = row.max()
        min_val = row.min()
        mean_val = row.mean()
        diff_pct = ((max_val - min_val) / mean_val * 100) if mean_val != 0 else 0
        pokeball_diff_percentages[pkmn] = diff_pct
    overall_pokeball_diff = np.mean(list(pokeball_diff_percentages.values()))
    print(f"\nGraph 4 (Pokéball Variation) - Overall Average % Difference between pokéballs: {overall_pokeball_diff:.2f}%")
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_fixed.plot(kind='bar', ax=ax)
    ax.set_title(
        f"Average Success Rate by Pokéball for each Pokémon\n"
        f"(Fixed HP: {fixed_hp*100:.0f}%, Level: {fixed_level}, Status: {fixed_status.name})\n"
        f"Avg % Difference between Pokéballs: {overall_pokeball_diff:.2f}%"
    )
    ax.set_xlabel("Pokémon")
    ax.set_ylabel("Average Success Rate")
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/config_2c.json"
    run_analysis_2d(config_path)
