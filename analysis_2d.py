import sys
import json
import pandas as pd
import plotly.express as px

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect

def run_analysis_2d(config_path="configs/config_2d.json"):
    with open(config_path, "r") as f:
        config = json.load(f)["analysis"]

    # Parametros de la configuración
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
    fixed_level = config["fixed_level"]

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
    print("Resultados totales (primeras 100 filas):")
    print(df.head(100))

    # Imprimir la combinación óptima para cada pokemon en cada nivel
    print("\nMejores combinaciones para cada Pokémon:")
    for pkmn in df["pokemon"].unique():
        df_pkmn = df[df["pokemon"] == pkmn]
        max_rate = df_pkmn["success_rate"].max()
        best_combinations = df_pkmn[df_pkmn["success_rate"] == max_rate]
        print(f"\n{pkmn.capitalize()} - Mejor tasa de captura: {max_rate:.4f}")
        print(best_combinations.to_string(index=False))

    # Generar gráficos por cada Pokémon
    for pkmn in df["pokemon"].unique():
        df_pkmn = df[df["pokemon"] == pkmn]

        # ----------------------------
        # Variar HP (current_hp) manteniendo nivel y status fijos 
        mask_hp = (df_pkmn["level"] == fixed_level) & (df_pkmn["status"] == fixed_status.name)
        df_hp = df_pkmn[mask_hp]
        fig_hp = px.bar(
            df_hp,
            x="hp_perc",
            y="success_rate",
            color="pokeball",
            barmode="group",
            title=f"{pkmn.capitalize()}: Capture Success vs. HP Percentage\n(Level fixed at {fixed_level}, Status fixed at {fixed_status.name})",
            labels={"hp_perc": "HP Percentage", "success_rate": "Success Rate"}
        )
        fig_hp.show()

        # ----------------------------
        # Variar Level manteniendo HP y status fijos
        mask_level = (df_pkmn["hp_perc"] == fixed_hp) & (df_pkmn["status"] == fixed_status.name)
        df_level = df_pkmn[mask_level]
        fig_level = px.line(
            df_level,
            x="level",
            y="success_rate",
            color="pokeball",
            markers=True,
            title=f"{pkmn.capitalize()}: Capture Success vs. Level\n(HP fixed at {fixed_hp*100:.0f}%, Status fixed at {fixed_status.name})",
            labels={"level": "Level", "success_rate": "Success Rate"}
        )
        fig_level.show()

        # ----------------------------
        # Variar Status manteniendo HP y nivel fijos
        mask_status = (df_pkmn["hp_perc"] == fixed_hp) & (df_pkmn["level"] == fixed_level)
        df_status = df_pkmn[mask_status]
        fig_status = px.bar(
            df_status,
            x="status",
            y="success_rate",
            color="pokeball",
            barmode="group",
            title=f"{pkmn.capitalize()}: Capture Success vs. Status\n(HP fixed at {fixed_hp*100:.0f}%, Level fixed at {fixed_level})",
            labels={"status": "Status", "success_rate": "Success Rate"}
        )
        fig_status.show()

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/config_2d.json"
    run_analysis_2d(config_path)
