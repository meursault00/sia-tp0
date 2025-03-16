import sys
import json
import pandas as pd
import plotly.express as px

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def run_analysis(config_path="config.json"):
    # 1. Load the config
    with open(config_path, "r") as f:
        config = json.load(f)["analysis"]

    pokemon_list = config["pokemon"]
    pokeballs = config["pokeballs"]
    num_experiments = config["num_experiments"]
    noise = config["noise"]

    # 2. Prepare factory and data collector
    factory = PokemonFactory("pokemon.json")
    results = []

    # 3. Run simulations for ideal conditions
    for pkmn_name in pokemon_list:
        base_success_rate = None  # To store the success rate of the basic Pokéball
        for ball in pokeballs:
            success_count = 0
            # Attempt capture multiple times to estimate success rate
            for _ in range(num_experiments):
                # Create Pokémon with ideal conditions: HP=100%, LVL=100, no status
                poke = factory.create(
                    pkmn_name,
                    100,  # Level 100
                    StatusEffect.NONE,  # No status effect
                    1.0  # HP 100%
                )
                attempt_success, _ = attempt_catch(poke, ball, noise)
                if attempt_success:
                    success_count += 1

            success_rate = success_count / num_experiments

            # Store the success rate of the basic Pokéball
            if ball == "pokeball":
                base_success_rate = success_rate

            # Store the results
            results.append({
                "pokemon": pkmn_name,
                "pokeball": ball,
                "success_rate": success_rate,
                "relative_effectiveness": None  # Placeholder for now
            })

        # Calculate relative effectiveness for all Pokéballs for this Pokémon
        for result in results:
            if result["pokemon"] == pkmn_name:
                result["relative_effectiveness"] = (
                    result["success_rate"] / base_success_rate
                    if base_success_rate > 0 else None
                )

    # Convert results to a DataFrame for easier manipulation
    df = pd.DataFrame(results)
    print(df.head(10))  # Quick sanity check

    # ------------------------------------------------------------------
    # Visualization: Success Rate by Pokéball
    # ------------------------------------------------------------------
    fig = px.bar(
        df,
        x="pokeball",
        y="success_rate",
        color="pokemon",
        barmode="group",
        title="1.A) Capture Probability by Pokéball (Ideal Conditions: HP=100%, LVL=100)"
    )
    fig.show()

    # ------------------------------------------------------------------
    # Visualization: Relative Effectiveness by Pokéball
    # ------------------------------------------------------------------
    fig_relative = px.bar(
        df,
        x="pokeball",
        y="relative_effectiveness",
        color="pokemon",
        barmode="group",
        title="1.B) Relative Effectiveness of Pokéballs (Compared to Basic Pokéball)"
    )
    fig_relative.show()


if __name__ == "__main__":
    # Use a default config if not provided, otherwise accept a path from sys.argv.
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.json"

    run_analysis(config_path)