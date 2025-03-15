import sys
import json
import pandas as pd
import plotly.express as px

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def run_analysis_2e(config_path="configs/config_2e.json"):
    with open(config_path, "r") as f:
        config = json.load(f)["analysis"]

    # Parámetros de la configuración
    pokemon_list = config["pokemon"]
    pokeballs = config["pokeballs"]
    statuses = config["statuses"]
    hp_percentages = config["hp_percentages"]
    levels = config["levels"]  
    num_experiments = config["num_experiments"]
    noise = config["noise"]

    # Valores fijos para los parámetros cuando otros varian 
    fixed_status = StatusEffect[config["fixed_status"]]
    fixed_hp = config["fixed_hp"]

    factory = PokemonFactory("pokemon.json")
    results = []

    # Correr simulación para todas las combinaciones
    for pkmn_name in pokemon_list:
        for status_str in statuses:
            status_effect = StatusEffect[status_str]
            for hp_perc in hp_percentages:
                for lvl in levels:
                    for ball in pokeballs:
                        success_count = 0
                        for _ in range(num_experiments):
                            poke = factory.create(
                                pkmn_name,
                                lvl,
                                status_effect,
                                hp_perc
                            )
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

    # Pasar resultados a DataFrame
    df = pd.DataFrame(results)
    print("Total results (first 100 rows):")
    print(df.head(100))

    # Imprimir la combinación óptima para cada pokemon en cada nivel
    print("\nOptimal combinations for each Pokémon at each level:")
    for pkmn in df["pokemon"].unique():
        for lvl in levels:
            df_subset = df[(df["pokemon"] == pkmn) & (df["level"] == lvl)]
            if not df_subset.empty:
                max_rate = df_subset["success_rate"].max()
                best = df_subset[df_subset["success_rate"] == max_rate]
                print(f"\n{pkmn.capitalize()} at Level {lvl} - Best success rate: {max_rate:.4f}")
                print(best.to_string(index=False))

    # Producir gráficos para cada pokemon en cada nivel que aparece en la configuración
    for pkmn in df["pokemon"].unique():
        df_pkmn = df[df["pokemon"] == pkmn]
        for lvl in levels:
            # -------------------------------------
            # Plot 1: Variar HP percentage manteniendo status fijo y level = current level
            mask_hp = (df_pkmn["level"] == lvl) & (df_pkmn["status"] == fixed_status.name)
            df_hp = df_pkmn[mask_hp]
            if not df_hp.empty:
                fig_hp = px.bar(
                    df_hp,
                    x="hp_perc",
                    y="success_rate",
                    color="pokeball",
                    barmode="group",
                    title=f"{pkmn.capitalize()} (Level = {lvl}): Capture Success vs. HP Percentage\n(Status fixed at {fixed_status.name})",
                    labels={"hp_perc": "HP Percentage", "success_rate": "Success Rate"}
                )
                fig_hp.show()

            # -------------------------------------
            # Gráfico 2: Variar Status manteniendo HP fijo y level = current level
            mask_status = (df_pkmn["level"] == lvl) & (df_pkmn["hp_perc"] == fixed_hp)
            df_status = df_pkmn[mask_status]
            if not df_status.empty:
                fig_status = px.bar(
                    df_status,
                    x="status",
                    y="success_rate",
                    color="pokeball",
                    barmode="group",
                    title=f"{pkmn.capitalize()} (Level = {lvl}): Capture Success vs. Status\n(HP fixed at {fixed_hp*100:.0f}%)",
                    labels={"status": "Status", "success_rate": "Success Rate"}
                )
                fig_status.show()

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/config_2e.json"
    run_analysis_2e(config_path)
