import pandas as pd
import numpy as np
from scipy.stats import ttest_rel
import base64
import os

# 1. 專案根目錄 & 檔案路徑設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES   = ['cpbl_2022_scores.csv', 'cpbl_2023_scores.csv']
LOGO_DIR = os.path.join(BASE_DIR, 'logos')

# 2. 讀入並合併賽事資料
df = pd.concat([pd.read_csv(os.path.join(BASE_DIR, f)) for f in FILES], ignore_index=True)

# 3. 中文→英文隊名映射
team_map = {
    "中信兄弟": "CTBC Brothers",
    "味全龍":   "WeiChuan Dragons",
    "樂天桃猿": "Rakuten Monkeys",
    "統一7-ELEVEn獅":   "Uni-Lions",
    "富邦悍將": "Fubon Guardians"
}
df['home_team'] = df['home_team'].map(team_map)
df['away_team'] = df['away_team'].map(team_map)

# 4. 計算勝利指標
df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
df['away_win'] = (df['away_score'] > df['home_score']).astype(int)

# 5. Logo Base64 編碼函式
def encode_logo_png(filename):
    path = os.path.join(LOGO_DIR, filename)
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/png;base64,{b64}'

# 6. 配對 t‑test 與 Cohen’s d 計算
results = []
logo_files = {
    "CTBC Brothers":    "ctbc_brothers.png",
    "WeiChuan Dragons": "weichuan_dragons.png",
    "Rakuten Monkeys":  "rakuten_monkeys.png",
    "Uni-Lions":        "uni_lions.png",
    "Fubon Guardians":  "fubon_guardians.png"
}

for team in team_map.values():
    # 6.1 勝率差配對 t-test
    hw = df[df.home_team == team]['home_win'].values
    aw = df[df.away_team == team]['away_win'].values
    n   = min(len(hw), len(aw))
    hw, aw = hw[:n], aw[:n]
    t_w, p_w = ttest_rel(hw, aw)
    d_w = np.mean(hw-aw) / np.std(hw-aw, ddof=1) if np.std(hw-aw, ddof=1) else np.nan

    # 6.2 得分差配對 t-test
    hs = df[df.home_team == team]['home_score'].values
    as_ = df[df.away_team == team]['away_score'].values
    m   = min(len(hs), len(as_))
    hs, as_ = hs[:m], as_[:m]
    t_s, p_s = ttest_rel(hs, as_)
    d_s = np.mean(hs-as_) / np.std(hs-as_, ddof=1) if np.std(hs-as_, ddof=1) else np.nan

    # 6.3 Logo Data URI
    uri = encode_logo_png(logo_files[team])

    # 6.4 星號標記（僅對勝率差檢定）
    sig_mark = " ★" if p_w < 0.05 else ""

    results.append({
        'Logo':            f'<img src="{uri}" width="32"/>',
        'Team':            team + sig_mark,
        'win_t-statistic': round(t_w, 3),
        'win_p-value':     round(p_w, 3),
    })

# 7. 轉成 DataFrame 並輸出 CSV
res_df = pd.DataFrame(results)
res_df.to_csv(os.path.join(BASE_DIR, 'paired_ttest_results.csv'),
              index=False, encoding='utf-8-sig')

# 8. 在 Jupyter/Notebook 渲染表格（若在 Streamlit 中使用：escape=False + unsafe_allow_html=True）
from IPython.display import HTML, display
display(HTML(res_df.to_html(index=False, escape=False)))
