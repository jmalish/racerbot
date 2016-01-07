import json
import random
import time

fish_facts = []

with open('fish_facts.json') as fish_json:  # get contents of secrets file (contains api keys)
    facts_json = json.load(fish_json)

for fact in facts_json:
    fish_facts.append(fact)


def get_random_fact():
    random.seed(time.time())
    random_int = random.randint(0, len(fish_facts)-1)  # get a random quote
    return fish_facts[random_int]
