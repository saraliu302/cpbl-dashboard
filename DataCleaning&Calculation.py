import pandas as pd

# 1. 讀入 2022 & 2023 資料
files = ['cpbl_2022_scores.csv', 'cpbl_2023_scores.csv']  # <-- 換成你自己的檔名
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# 2. 中文隊名對應到英文
team_map = {
    "中信兄弟": "CTBC Brothers",
    "味全龍":   "WeiChuan Dragons",
    "樂天桃猿": "Rakuten Monkeys",
    "統一7-ELEVEn獅":   "Uni-Lions",
    "富邦悍將": "Fubon Guardians"
}
df['home_team'] = df['home_team'].map(team_map)
df['away_team'] = df['away_team'].map(team_map)

# 3. 計算主場/客場勝利指標
df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
df['away_win'] = (df['away_score'] > df['home_score']).astype(int)

# 4. 彙總主場指標
home_stats = df.groupby('home_team').agg(
    home_win_rate  = ('home_win',  'mean'),
    home_avg_score= ('home_score','mean'),
    home_games    = ('home_win',  'count')
)

# 5. 彙總客場指標
away_stats = df.groupby('away_team').agg(
    away_win_rate  = ('away_win',  'mean'),
    away_avg_score = ('away_score','mean'),
    away_games     = ('away_win',  'count')
)

# 6. 合併，並計算差值
metrics = home_stats.join(away_stats, how='inner')
metrics['win_rate_diff'] = metrics['home_win_rate'] - metrics['away_win_rate']
metrics['score_diff']    = metrics['home_avg_score'] - metrics['away_avg_score']

# 7. 顯示最終結果
print(metrics.reset_index().round(3))

# 1. 儲存為 CSV
metrics.reset_index().to_csv('team_metrics.csv', index=False, encoding='utf-8-sig')

print("✅ 已將統計資料儲存到 team_metrics.csv")
