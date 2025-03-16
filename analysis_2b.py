import numpy as np
import plotly.graph_objects as go
import csv

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def analyze_hp_effects(pokemon_list, ball, num_trials=50, noise=0.15):
    factory = PokemonFactory("pokemon.json")

    hp_values = list(range(1, 101)) 
    results = {pokemon: {} for pokemon in pokemon_list}
    binned_results = {pokemon: {} for pokemon in pokemon_list}  #for binning by 5 hps

    for pokemon_name in pokemon_list:
        for hp in hp_values:
            successful_catches = []
            capture_rates = []

            for _ in range(num_trials):
                #create pokemon with specific hp from iteration and level 1
                pokemon = factory.create(pokemon_name, hp, StatusEffect.NONE, 1)
                success, capture_rate = attempt_catch(pokemon, ball, noise)
                successful_catches.append(success)
                capture_rates.append(capture_rate)

            #statistics for printing + graphing
            avg_success_rate = sum(successful_catches) / num_trials
            avg_capture_rate = np.mean(capture_rates)
            std_dev = np.std(capture_rates)

            #store stats for graphing
            results[pokemon_name][hp] = {
                "success_rate": avg_success_rate,
                "avg_capture_rate": avg_capture_rate,
                "std_dev": std_dev
            }

            #grouping hp's into 5% intervals
            hp_bin = (hp // 5) * 5  #grouping 0-4% as 0, 5-9% as 5, etc
            if hp_bin not in binned_results[pokemon_name]:
                binned_results[pokemon_name][hp_bin] = {"success_rates": [], "capture_rates": []}

            binned_results[pokemon_name][hp_bin]["success_rates"].append(avg_success_rate)
            binned_results[pokemon_name][hp_bin]["capture_rates"].append(avg_capture_rate)

            print(f"[{pokemon_name}] HP: {hp}%, Success Rate: {avg_success_rate:.2%}, Capture Rate: {avg_capture_rate:.4f}, Std Dev: {std_dev:.4f}")

    #calculating average for each bin
    for pokemon_name in pokemon_list:
        for hp_bin in binned_results[pokemon_name]:
            binned_results[pokemon_name][hp_bin]["avg_success_rate"] = np.mean(
                binned_results[pokemon_name][hp_bin]["success_rates"]
            )
            binned_results[pokemon_name][hp_bin]["avg_capture_rate"] = np.mean(
                binned_results[pokemon_name][hp_bin]["capture_rates"]
            )
            
    #graphing
    colors = ["deepskyblue", "orangered"]
    fig = go.Figure()
    fig_binned = go.Figure()

    for i, pokemon_name in enumerate(pokemon_list):
        hp_values = list(results[pokemon_name].keys())
        success_rates = [results[pokemon_name][hp]["success_rate"] for hp in hp_values]
        std_devs = [results[pokemon_name][hp]["std_dev"] for hp in hp_values]

        #create line graph
        fig.add_trace(go.Scatter(
            x=hp_values,
            y=success_rates,
            mode="lines+markers",
            name=f"{pokemon_name} Capture Success Rate",
            line=dict(color=colors[i]),
            marker=dict(size=5)
        ))

        #error bars (dotted, different color)
        #upper bound
        fig.add_trace(go.Scatter(
            x=hp_values,
            y=[success_rates[j] + std_devs[j] for j in range(len(hp_values))],
            mode="lines",
            line=dict(color=colors[i], dash="dot", width=1),
            showlegend=False
        ))
        #lower bound
        fig.add_trace(go.Scatter(
            x=hp_values,
            y=[success_rates[j] - std_devs[j] for j in range(len(hp_values))],
            mode="lines",
            line=dict(color=colors[i], dash="dot", width=1),
            showlegend=False
        ))

        #binned graph
        binned_hp_values = list(binned_results[pokemon_name].keys())
        binned_success_rates = [binned_results[pokemon_name][hp_bin]["avg_success_rate"] for hp_bin in binned_hp_values]

        fig_binned.add_trace(go.Scatter(
            x=binned_hp_values,
            y=binned_success_rates,
            mode="lines+markers",
            name=f"{pokemon_name} (Binned 5%)",
            line=dict(color=colors[i]),
            marker=dict(size=8, symbol="square")
        ))

    fig.update_layout(
        title="Effect of HP on Capture Rate",
        xaxis_title="HP (%)",
        yaxis_title="Capture Success Rate",
        yaxis=dict(tickformat=".0%"),
        template="plotly_dark"
    )
    fig_binned.update_layout(
    title="Effect of HP on Capture Rate (Binned Every 5%)",
    xaxis_title="HP Bin (%)",
    yaxis_title="Average Capture Success Rate",
    yaxis=dict(tickformat=".0%"),
    template="plotly_dark"
    )

    fig.show()
    fig_binned.show()