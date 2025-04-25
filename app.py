from flask import Flask, request, jsonify
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

LOTTO_RULES = {
    "ssq": {"front": 33, "back": 16, "frontPick": 6, "backPick": 1},
    "dlt": {"front": 35, "back": 12, "frontPick": 5, "backPick": 2},
    "k8": {"front": 80, "frontPick": 20},
}

WEIGHTS = {}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def compute_weights(df, front_cols, back_cols=None, type_="ssq"):
    front_numbers = df[front_cols].values.flatten().astype(int)
    front_counts = pd.Series(front_numbers).value_counts().sort_index()
    total_front = sum(front_counts)
    front_weights = [front_counts.get(i, 1) / total_front for i in range(1, LOTTO_RULES[type_]['front'] + 1)]
    if back_cols:
        back_numbers = df[back_cols].values.flatten().astype(int)
        back_counts = pd.Series(back_numbers).value_counts().sort_index()
        total_back = sum(back_counts)
        back_weights = [back_counts.get(i, 1) / total_back for i in range(1, LOTTO_RULES[type_]['back'] + 1)]
    else:
        back_weights = []
    return front_weights, back_weights

def fetch_ssq():
    url = "https://www.zhcw.com/kjxx/ssq/"
    res = requests.get(url, headers=HEADERS)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".kj_tablelist02 tr")
    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            balls = cols[1].find_all("em")
            if len(balls) == 7:
                reds = [int(b.text) for b in balls[:6]]
                blue = int(balls[6].text)
                data.append(reds + [blue])
    df = pd.DataFrame(data, columns=["red1", "red2", "red3", "red4", "red5", "red6", "blue"])
    df.to_csv("ssq_history.csv", index=False)
    return df

def load_data():
    try:
        ssq_df = fetch_ssq()
        f_w, b_w = compute_weights(ssq_df, ["red1", "red2", "red3", "red4", "red5", "red6"], ["blue"], type_="ssq")
        WEIGHTS["ssq"] = {"front": f_w, "back": b_w}
    except Exception as e:
        print("加载失败", e)
        WEIGHTS["ssq"] = {"front": [1 / 33] * 33, "back": [1 / 16] * 16}

load_data()

def weighted_sample(total, pick, weights):
    pool = list(range(1, total + 1))
    sample_pool = random.choices(pool, weights=weights, k=pick * 3)
    return sorted(random.sample(list(set(sample_pool)), pick))

@app.route("/api/predict")
def predict():
    type_ = request.args.get("type", "ssq")
    rule = LOTTO_RULES.get(type_)
    if not rule:
        return jsonify({"error": "Unsupported lottery type."}), 400
    predictions = []
    for _ in range(3):
        front = weighted_sample(rule["front"], rule["frontPick"], WEIGHTS[type_]["front"])
        back = weighted_sample(rule["back"], rule["backPick"], WEIGHTS[type_]["back"]) if "back" in rule else []
        predictions.append({"front": front, "back": back})
    return jsonify({"numbers": predictions})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)