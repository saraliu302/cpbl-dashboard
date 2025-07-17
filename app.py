from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel
import plotly.express as px
import os, base64, re

# ---- Configuration ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="CPBL Home/Away Analytics", layout="wide")

# ---- Sidebar Logo ----
st.sidebar.image(os.path.join(BASE_DIR, 'logos', 'cpbl_logo.png'), use_container_width=True)

# ---- CSS Styling ----
st.markdown("""
<style>
[data-baseweb="multi-select"] div[class*="valueContainer"] > div {
    background-color: #0060B0 !important;
    color: white !important;
    border-radius: 0.5rem !important;
    padding: 0.3rem 0.6rem !important;
}
[data-baseweb="multi-select"] div[role="option"] {
    background-color: white !important;
    color: #0060B0 !important;
    border: 1px solid #0060B0 !important;
    border-radius: 0.3rem !important;
    margin: 2px 0 !important;
}
th, td {
    text-align: center !important;
    border: none !important;
    border-bottom: 1px solid #ddd !important;
    padding: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ---- Load raw data dynamically ----
@st.cache_data
def load_data():
    # auto-detect cpbl CSV files in BASE_DIR
    files = [f for f in os.listdir(BASE_DIR) if re.match(r"cpbl_\d{4}\.csv", f)]
    years = sorted([int(re.findall(r"cpbl_(\d{4})\.csv", f)[0]) for f in files])
    frames = []
    for y in years:
        path = os.path.join(BASE_DIR, f"cpbl_{y}.csv")
        df = pd.read_csv(path)
        df['year'] = y
        frames.append(df)
    df_all = pd.concat(frames, ignore_index=True)
    team_map = {
        "中信兄弟": "CTBC Brothers",
        "味全龍": "WeiChuan Dragons",
        "樂天桃猿": "Rakuten Monkeys",
        "統一7-ELEVEn獅": "Uni-Lions",
        "富邦悍將": "Fubon Guardians",
        "台鋼雄鷹": "TSG Hawks"
    }
    df_all['home_team'] = df_all['home_team'].map(team_map)
    df_all['away_team'] = df_all['away_team'].map(team_map)
    df_all.dropna(subset=['home_team','away_team'], inplace=True)
    df_all['home_win'] = (df_all['home_score'] > df_all['away_score']).astype(int)
    df_all['away_win'] = (df_all['away_score'] > df_all['home_score']).astype(int)
    return df_all, years

# load data and dynamic years
df_all, YEARS = load_data()

# ---- Helper for Cohen's d classification ----
def d_size(d):
    if abs(d) < 0.2: return 'negligible'
    if abs(d) < 0.5: return 'small'
    if abs(d) < 0.8: return 'medium'
    return 'large'

# ---- Compute metrics per year ----
@st.cache_data
def compute_metrics(df_year, year, alpha=0.1):
    recs = []
    logo_map = {
        "CTBC Brothers": "ctbc_brothers.png",
        "WeiChuan Dragons": "weichuan_dragons.png",
        "Rakuten Monkeys": "rakuten_monkeys.png",
        "Uni-Lions": "uni_lions.png",
        "Fubon Guardians": "fubon_guardians.png",
        "TSG Hawks": "tsg_hawks.png"
    }
    for team in sorted(df_year['home_team'].dropna().unique()):
        # only show Hawks if available year
        if team == 'TSG Hawks' and year != 2024:
            continue
        home = df_year[df_year['home_team'] == team]
        away = df_year[df_year['away_team'] == team]
        if len(home) < 2 or len(away) < 2:
            continue
        n = min(len(home), len(away))
        # Win metrics
        hr = home['home_win'].mean()
        ar = away['away_win'].mean()
        wr_diff = hr - ar
        hw = home['home_win'].values[:n]
        aw = away['away_win'].values[:n]
        t_w, p_w = ttest_rel(hw, aw)
        d_w = np.mean(hw - aw) / np.std(hw - aw, ddof=1)
        sig_w = '★' if p_w < alpha else ''
        # Score metrics
        hs = home['home_score'].mean()
        as_ = away['away_score'].mean()
        sc_diff = hs - as_
        hsc = home['home_score'].values[:n]
        asc = away['away_score'].values[:n]
        t_s, p_s = ttest_rel(hsc, asc)
        d_s = np.mean(hsc - asc) / np.std(hsc - asc, ddof=1)
        sig_s = '★' if p_s < alpha else ''
        # Logo URI
        logo_path = os.path.join(BASE_DIR, 'logos', logo_map.get(team, ''))
        data_uri = ''
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            data_uri = f'<img src="data:image/png;base64,{b64}" width="32"/>'
        recs.append({
            'Logo': data_uri,
            'Team': team,
            'Home Win Rate': round(hr, 3),
            'Away Win Rate': round(ar, 3),
            'Win Rate Diff': round(wr_diff, 3),
            't-stat (Win)': round(t_w, 3),
            'p-value (Win)': round(p_w, 3),
            'Cohen d (Win)': d_size(d_w),
            'Significant (Win)': sig_w,
            'Home Avg Score': round(hs, 3),
            'Away Avg Score': round(as_, 3),
            'Score Diff': round(sc_diff, 3),
            't-stat (Score)': round(t_s, 3),
            'p-value (Score)': round(p_s, 3),
            'Cohen d (Score)': d_size(d_s),
            'Significant (Score)': sig_s
        })
    return pd.DataFrame(recs)

# ---- Sidebar Controls ----
st.sidebar.header("Controls")
year = st.sidebar.selectbox("Select Year", YEARS)
metric = st.sidebar.selectbox(
    "Select Metric",
    ['Win Rate', 'Score Difference'],
    help="Choose which metric to analyze"
)
alpha = st.sidebar.slider("Significance Level (α)", 0.01, 0.3, 0.1, 0.01)
show_sig = st.sidebar.checkbox("Show only significant teams", False)
opts = sorted(df_all['home_team'].dropna().unique())
if year != 2024 and 'TSG Hawks' in opts:
    opts.remove('TSG Hawks')
teams = st.sidebar.multiselect(
    "Select Teams ❔",
    options=opts,
    default=opts,
    help="Choose which teams to include in the table and charts"
)
drill = st.sidebar.selectbox(
    "Drill-down Team ❔",
    options=[''] + opts,
    help="Pick a team to see detailed data and timelines"
)

# ---- Compute & Filter ----
df_y = df_all[df_all['year'] == year]
mt = compute_metrics(df_y, year, alpha)
# Determine lists
if metric == 'Win Rate':
    sig_list = mt[mt['Significant (Win)'] == '★']['Team'].tolist()
    metric_label = 'win rates'
else:
    sig_list = mt[mt['Significant (Score)'] == '★']['Team'].tolist()
    metric_label = 'score differences'
non_sig = [t for t in teams if t not in sig_list]
# Filter for display
df_disp = mt[mt['Team'].isin(teams)]
if show_sig:
    if metric == 'Win Rate': df_disp = df_disp[df_disp['Significant (Win)'] == '★']
    else: df_disp = df_disp[df_disp['Significant (Score)'] == '★']
df_idx = df_disp.set_index('Team')

# ---- Title & Insights at Top ----
st.title("CPBL Seasonal Home/Away Analysis")
st.write("A data‑driven analysis of CPBL home‑field performance across seasons. We compare home vs. away win rates and scoring, apply paired t‑tests for statistical significance, and quantify effect size with Cohen’s d.")
st.write(f"Year: {year} • α={alpha}")
st.subheader("Insights")
st.info(f"**{', '.join(sig_list) if sig_list else 'None'}** have significant differences in {metric_label}, which confirms a real home-field boost.")
st.info(f"**{', '.join(non_sig) if non_sig else 'None'}** have no meaningful difference in {metric_label}.")

# ---- Metrics Table ----
st.subheader("Metrics Table")
if metric == 'Win Rate':
    cols = ['Logo','Team','Home Win Rate','Away Win Rate','Win Rate Diff',
            't-stat (Win)','p-value (Win)','Cohen d (Win)','Significant (Win)']
else:
    cols = ['Logo','Team','Home Avg Score','Away Avg Score','Score Diff',
            't-stat (Score)','p-value (Score)','Cohen d (Score)','Significant (Score)']
html = df_disp[cols].to_html(escape=False, index=False)
html = html.replace('<table ', '<table style="width:100%;border-collapse:collapse;" ')
st.markdown(f'<div style="width:100%;overflow-x:auto;">{html}</div>', unsafe_allow_html=True)

# ---- Charts ----
if metric == 'Win Rate':
    st.subheader("Home vs Away Win Rates")
    st.write("Comparing home and away win rates for each team.")
    st.plotly_chart(
        px.bar(
            df_idx[['Home Win Rate','Away Win Rate']],
            barmode='group',
            color_discrete_map={'Home Win Rate':'#0060B0','Away Win Rate':'#05AF7A'}
        ), use_container_width=True
    )
    st.subheader("Win Rate Difference")
    st.write("Visualizing the difference in win rates between home and away games.")
    fig = px.bar(
        x=df_idx['Win Rate Diff'].sort_values(),
        y=df_idx.index,
        orientation='h',
        color_discrete_sequence=['#0060B0']
    )
    fig.update_layout(
    xaxis_title="Win Rate Difference",
    yaxis_title="Team"
    )
    fig.add_vline(x=0, line_dash='dash', line_color='gray')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.subheader("Home vs Away Average Score")
    st.write("Comparing average scores for home and away games.")
    st.plotly_chart(
        px.bar(
            df_idx[['Home Avg Score','Away Avg Score']],
            barmode='group',
            color_discrete_map={'Home Avg Score':'#0060B0','Away Avg Score':'#05AF7A'}
        ), use_container_width=True
    )
    st.subheader("Score Difference")
    st.write("Visualizing the difference in average scores between home and away games.")
    fig = px.bar(
        x=df_idx['Score Diff'].sort_values(),
        y=df_idx.index,
        orientation='h',
        color_discrete_sequence=['#05AF7A']
    )
    fig.update_layout(
    xaxis_title="Score Difference",
    yaxis_title="Team"
    )
    fig.add_vline(x=0, line_dash='dash', line_color='gray')
    st.plotly_chart(fig, use_container_width=True)

# ---- Drill-down ----
if drill:
    st.subheader(f"Details for {drill} ({year})")
    df_raw = df_y[(df_y['home_team']==drill)|(df_y['away_team']==drill)].reset_index(drop=True)
    st.markdown(
    "**<p style='font-size:25px;'>Raw game data</p>**",
    unsafe_allow_html=True,
)
    # compute per-game scored by team
    df_raw['For'] = np.where(
        df_raw['home_team']==drill,
        df_raw['home_score'],
        df_raw['away_score']
    )
    # compute summary metrics
    avg_score = round(df_raw['For'].mean(),3)
    df_raw['Win'] = np.where(
        (df_raw['home_team']==drill)&(df_raw['home_score']>df_raw['away_score']) |
        (df_raw['away_team']==drill)&(df_raw['away_score']>df_raw['home_score']),
        1, 0
    )
    win_rate = round(df_raw['Win'].mean(),3)
    st.markdown(f"**Average Runs:** {avg_score}  •  **Win Rate:** {win_rate}")
    st.dataframe(
        df_raw[['game_id','home_team','away_team','home_score','away_score']],
        use_container_width=True
    )
    # Score Timeline
    st.subheader("Score Timeline")
    st.write("Visualizing the score progression for each game involving the selected team.")
    melt = df_raw.melt(
        id_vars=['game_id'],
        value_vars=['home_score','away_score'],
        var_name='Type',
        value_name='Score'
    )
    st.plotly_chart(
        px.line(melt, x='game_id', y='Score', color='Type', title=f"{drill} Score Timeline ({year})"),
        use_container_width=True
    )
    # Win Rate Timeline
    st.subheader("Win Rate Timeline")
    st.write("Visualizing the cumulative win rate over the season for the selected team.")
    df_raw['Cume Win Rate'] = df_raw['Win'].expanding().mean()
    st.plotly_chart(
        px.line(df_raw, x='game_id', y='Cume Win Rate', title=f"{drill} Cumulative Win Rate ({year})"),
        use_container_width=True
    )
# ---- Legend & Cohen's d info ----
st.markdown("---")
st.markdown("★ indicates p < selected α  |  Cohen's d effect sizes: negligible (<0.2), small (0.2–0.5), medium (0.5–0.8), large (>0.8)")
last_edit = datetime.now().astimezone().strftime("%Y‑%m‑%d %H:%M:%S %Z")

# ---- Project Info & Contact ----
st.markdown(
    """
    **Data Sources**  
    - Official CPBL CSV logs: https://www.cpbl.com.tw
    - Internal name mapping   
    """,
    unsafe_allow_html=True
)
st.markdown(f"**Last edited:** {last_edit}")
with st.sidebar:
    st.markdown("### About This App")
    st.markdown(
        """
        **Author:** Sara Liu  
        **Contact:** saraliu302@gmail.com  
        """
    )