from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_cpbl_score(game_id):
    # game_id 請用三位數字字串，如 "010"
    url = f"https://www.cpbl.com.tw/box?year=2022&KindCode=A&gameSno={game_id}"
    print("🔗 載入", url)
    driver = webdriver.Safari()
    driver.get(url)

    try:
        # 等到 ScoreBoard 裡的 away 隊出現，最多等 10 秒
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item.ScoreBoard .team.away"))
        )

        away_team  = driver.find_element(By.CSS_SELECTOR, ".item.ScoreBoard .team.away .team_name a").text
        away_score = driver.find_element(By.CSS_SELECTOR, ".item.ScoreBoard .team.away .score").text
        home_team  = driver.find_element(By.CSS_SELECTOR, ".item.ScoreBoard .team.home .team_name a").text
        home_score = driver.find_element(By.CSS_SELECTOR, ".item.ScoreBoard .team.home .score").text

        print(f"✅ {away_team} {away_score} : {home_score} {home_team}")
        return {
            "game_id":    game_id,
            "away_team":  away_team,
            "home_team":  home_team,
            "away_score": int(away_score),
            "home_score": int(home_score)
        }

    except Exception as e:
        print("⚠️ 擷取失敗:", e)
        return None

    finally:
        driver.quit()

# 範例測試

import pandas as pd
import time

results = []
for i in range(1, 301):
    gid = str(i).zfill(3)           # "001", "002", ..., "300"
    data = fetch_cpbl_score(gid)
    if data:
        results.append(data)
    time.sleep(0.3)

df = pd.DataFrame(results)
df.to_csv("cpbl_2022_scores.csv", index=False, encoding="utf-8-sig")
print("🎉 完成，共抓到", len(df), "場")
