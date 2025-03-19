import numpy as np
import plotly.graph_objects as go
import csv
import json
import sys

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def analyze_status_effects(config_path="configs/config_2a.json"):
    factory = PokemonFactory("pokemon.json")
    
    with open(f"{sys.argv[1]}", "r") as f:
        config = json.load(f)
        ball = config["pokeball"]
        pokemon_list = config["pokemon"]
        num_trials = config["num_trials"]
        noise = config["noise"]

    #statuses we will test
    status_effects = [
        StatusEffect.NONE,
        StatusEffect.SLEEP,
        StatusEffect.PARALYSIS,
        StatusEffect.BURN,
        StatusEffect.FREEZE,
        StatusEffect.POISON,
    ]

    #store results grouped by pokemons
    results = {pokemon_name: {} for pokemon_name in pokemon_list}

    for pokemon_name in pokemon_list:
        for status in status_effects:
            successful_catches = []
            capture_rates = [] #only for printing, wont be in graph

            for _ in range(num_trials):
                #create pokemon with 100hp and level 1
                pokemon = factory.create(pokemon_name, 100, status, 1)
                success, capture_rate = attempt_catch(pokemon, ball, noise)
                successful_catches.append(success)
                capture_rates.append(capture_rate)

            #statistics for printing + graphing
            avg_success_rate = sum(successful_catches) / num_trials
            std_dev = np.std(capture_rates)

            #storing stats for each pokemon & status
            results[pokemon_name][status.name] = {
                "success_rate": avg_success_rate,
                "std_dev": std_dev
            }

            print(f"[{pokemon_name}] Status: {status.name}, Success Rate: {avg_success_rate:.2%}, Std Dev: {std_dev:.4f}")

    colors = ["yellow", "orange", "purple", "red", "blue", "green"]
    fig = go.Figure()

    x_positions = np.arange(len(pokemon_list))  #position for each pokemon on x-axis
    bar_width = 0.15 

    #iterate through each pokemon and create their status bars
    for i, pokemon_name in enumerate(pokemon_list):
        status_names = list(results[pokemon_name].keys())
        success_rates = [results[pokemon_name][status]["success_rate"] for status in status_names]
        std_devs = [results[pokemon_name][status]["std_dev"] for status in status_names]

        #a bar for each status in the group
        fig.add_trace(go.Bar(
            x=[x_positions[i] + j * bar_width for j in range(len(status_names))],  #status positions
            y=success_rates,
            error_y=dict(type="data", array=std_devs),
            name=pokemon_name,
            marker=dict(color=colors),
            text=status_names,  #status effect labels
            width=bar_width  
        ))

    fig.update_layout(
        title="Effect of Status Conditions on Capture Rate",
        xaxis_title="Pokemon",
        yaxis_title="Capture Success Rate",
        yaxis=dict(tickformat=".0%"),
        barmode="group", 
        xaxis=dict(
            tickvals=x_positions,  #pokemon group position
            ticktext=pokemon_list  #placing pokemon names on x-axis
        ),
        template="plotly_dark"
    )

    #show graph
    fig.show()

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/config_2a.json"
    analyze_status_effects(config_path)