import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ---------------- CONFIG ----------------
ALPHA = 0.7          # peso da posição vs tempo dentro de cada sub-score
BETA  = 0.6          # peso forma-2025 vs histórico da pista
MIN_Q3_PISTA = 2
PROXIMOS_GPS = [
    'Hungarian Grand Prix',
    'Dutch Grand Prix',
    'Italian Grand Prix',
    'Azerbaijan Grand Prix',
    'Singapore Grand Prix'
]

# -------------- UTIL --------------------
def tempo_segundos(t):
    if pd.isna(t):
        return None
    m, s = t.split(':')
    return int(m) * 60 + float(s)

def carregar():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='Mazembe30*1234', database='f1_data'
    )
    df = pd.read_sql("""
        SELECT year, grand_prix, driver, team, position, q2_time, q3_time
        FROM qualifying_results
        WHERE year BETWEEN 2023 AND 2025
          AND position > 0
    """, conn)
    conn.close()
    return df

# -------------- PREPARO GLOBAL ----------
df = carregar()
df['best_q'] = df.apply(
    lambda r: tempo_segundos(r.q3_time)
              if pd.notna(r.q3_time) else tempo_segundos(r.q2_time), axis=1
)
df['q3_flag'] = df['position'] <= 10          # esteve no Q3?

df_23_24 = df[df.year < 2025].copy()
df_25    = df[df.year == 2025].copy()

# --- forma 2025 (score_25) ---
agg_25 = (df_25.groupby('driver')
          .agg(team=('team','last'),
               pos_avg=('position','mean'),
               time_avg=('best_q','mean'))
          .reset_index())
sc25 = MinMaxScaler()
agg_25[['pos_n','time_n']] = sc25.fit_transform(
    agg_25[['pos_avg','time_avg']])
agg_25['score_25'] = ALPHA*agg_25.pos_n + (1-ALPHA)*agg_25.time_n

# --- fallback global 23-24 ---
glob = (df_23_24.groupby('driver')
        .agg(pos_avg=('position','mean'),
             time_avg=('best_q','mean'))
        .reset_index())
scg = MinMaxScaler()
glob[['pos_n','time_n']] = scg.fit_transform(glob[['pos_avg','time_avg']])
glob['score_track'] = ALPHA*glob.pos_n + (1-ALPHA)*glob.time_n
fallback = glob[['driver','score_track']]

# -------------- LOOP POR GP FUTURO --------------
for gp in PROXIMOS_GPS:
    # -------- histórico na mesma pista (2023-24) --------
    hist = df_23_24[(df_23_24.grand_prix == gp) & (df_23_24.q3_flag)]
    cnt = hist.groupby('driver')['q3_flag'].count()
    eleg = cnt[cnt >= MIN_Q3_PISTA].index
    hist = hist[hist.driver.isin(eleg)]
    if not hist.empty:
        pista = (hist.groupby('driver')
                 .agg(pos_avg=('position','mean'),
                      time_avg=('best_q','mean'))
                 .reset_index())
        scp = MinMaxScaler()
        pista[['pos_n','time_n']] = scp.fit_transform(
            pista[['pos_avg','time_avg']])
        pista['score_track'] = ALPHA*pista.pos_n + (1-ALPHA)*pista.time_n
        pista = pista[['driver','score_track']]
    else:
        pista = pd.DataFrame(columns=['driver','score_track'])

    # -------- merge forma 2025 + pista/history/fallback --------
    merged = agg_25.merge(pista, on='driver', how='left')
    merged = merged.merge(fallback, on='driver', how='left', suffixes=('','_fb'))
    merged['score_track'] = merged['score_track'].fillna(merged['score_track_fb'])
    merged.drop(columns='score_track_fb', inplace=True)
    merged['score_final'] = BETA*merged.score_25 + (1-BETA)*merged.score_track
    merged = merged.sort_values('score_final')

    # -------- texto ----------
    print(f"\n🏁 {gp} – previsão de pole (Top 5):")
    for _, r in merged.head(5).iterrows():
        print(f"  ➡️ {r.driver} ({r.team})  |  score25={r.score_25:.3f} "
              f"| track={r.score_track:.3f} | final={r.score_final:.3f}")

    # -------- gráfico ----------
    top5 = merged.head(5)
    plt.figure(figsize=(6,4))
    plt.bar(top5.driver, top5.score_final)      # sem definir cor
    plt.gca().invert_yaxis()                    # menor score = barra “alta”
    plt.title(f"{gp} – Top 5 Score de pole")
    plt.xlabel("Piloto")
    plt.ylabel("Score final (menor → melhor)")
    plt.tight_layout()
    plt.show()
