import json
import sys

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect
from analysis_2a import analyze_status_effects
from analysis_2b import analyze_hp_effects

if __name__ == "__main__":
    factory = PokemonFactory("pokemon.json")
    with open(f"{sys.argv[1]}", "r") as f:
        config = json.load(f)
        ball_2a = config["pokeball"]
        pokemon_names_2a = config["pokemon"]
    
    with open(f"{sys.argv[2]}", "r") as f:
        config = json.load(f)
        ball_2b = config["pokeball"]
        pokemon_names_2b = config["pokemon"]

        #Exercise 2a
        analyze_status_effects(pokemon_names_2a, ball_2a)

        #Exercise 2b
        analyze_hp_effects(pokemon_names_2b, ball_2b)
