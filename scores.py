# src/utils.py
import os
import json
import pandas as pd

def load_scores(file, specific_username):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        new_df = df[df["username"] == specific_username]
        return new_df
    else:
        return pd.DataFrame(columns=["username", "Time", "Score", "Content", "Total guess"])
# src/utils.py
def score_to_numeric(score):
    score = score.lower()
    if score == "poor":
        return 1
    elif score == "average":
        return 2
    elif score == "normal":
        return 3
    elif score == "good":
        return 4
