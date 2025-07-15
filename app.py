import streamlit as st
import matplotlib.pyplot as plt
import math
import pandas as pd

# ---------- FUNZIONI ----------
def calculate_divisor(d_score):
    return 1 if d_score >= 9 else (1.5 if d_score >= 7 else 2)

def calculate_multiplier(m_score):
    return 2 if m_score >= 9 else (1.5 if m_score >= 7 else 1)

# ---------- SESSION STATE ----------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.game = None
    st.session_state.setup_step = 0
    st.session_state.num_teams = 0
    st.session_state.volleys = 0
    st.session_state.team_names = []
    st.session_state.teams = {}
    st.session_state.current_volley = 1
    st.session_state.current_team_index = 0
    st.session_state.button_key = 0
ss = st.session_state

# ---------- NAVIGAZIONE ----------
if ss.page == 'home':
    st.title("Archery Games Hub")
    if st.button("Archery Duo Challenge"):
        ss.game = 'duo'
        ss.page = 'rules'
        st.rerun()
    if st.button("La Classica"):
        ss.game = 'classica'
        ss.page = 'rules_classica'
        st.rerun()

# -------------------------------------------------
# DUO CHALLENGE – REgole
# -------------------------------------------------
elif ss.page == 'rules':
    st.title("Archery Duo Challenge – Regole")
    st.markdown("""
- Squadra mista: principiante + veterano  
- Volée dispari: principiante 3 frecce, veterano 1 freccia = **divisore**  
- Volée pari: veterano 3 frecce, principiante 1 freccia = **moltiplicatore**  
- Numero di volée pari  
- Punteggio cumulativo  

### Scala Punteggi
| Freccia | Moltiplicatore | Divisore |
|---------|----------------|----------|
| 10-9    | ×2             | ÷1       |
| 8-7     | ×1.5           | ÷1.5     |
| 6-1 / M | ×1             | ÷2       |
""")
    if st.button("Inizia Gioco"):
        ss.page = 'setup'
        ss.setup_step = 0
        st.rerun()

# -------------------------------------------------
# LA CLASSICA – REgole
# -------------------------------------------------
elif ss.page == 'rules_classica':
    st.title("La Classica – Regole")
    st.markdown("""
- Ogni arciero tira 3 frecce (solo valori 1-10 o M).  
- Il punteggio della squadra è la **somma dei 6 valori** (3+3).  
- Volée pari o dispari → nessun moltiplicatore/divisore.  
- Numero di volée pari.  
""")
    if st.button("Inizia Gioco"):
        ss.page = 'setup'
        ss.setup_step = 0
        st.rerun()

# -------------------------------------------------
# SETUP COMUNE
# -------------------------------------------------
elif ss.page == 'setup':
    st.title(f"Setup Torneo – {ss.game.title()}")
    if ss.setup_step == 0:
        n = st.number_input("Numero Squadre", 1, 20, 2)
        v = st.number_input("Volée per Squadra (pari)", 2, 10, 4, step=2)
        if st.button("Conferma Configurazione"):
            ss.num_teams = n
            ss.volleys = v
            ss.setup_step = 1
            st.rerun()
    else:
        st.subheader("Inserisci nomi delle squadre")
        if not ss.team_names:
            ss.team_names = [f"Squadra {i+1}" for i in range(ss.num_teams)]
        for i in range(ss.num_teams):
            ss.team_names[i] = st.text_input(f"Squadra {i+1}", value=ss.team_names[i], key=f"name_{i}")
        if st.button("Conferma Nomi"):
            for name in ss.team_names:
                ss.teams[name] = {'scores': [], 'total': 0}
            ss.page = 'game'
            ss.current_volley = 1
            ss.current_team_index = 0
            st.rerun()

# -------------------------------------------------
# GAME – routing
# -------------------------------------------------
elif ss.page == 'game':
    names = ss.team_names
    current = names[ss.current_team_index]
    team = ss.teams[current]
    volley = ss.current_volley
    for n in names:
        ss.pop(f"done_{n}_{volley}", None)

    if ss.game == 'duo':
        st.title(f"Volée {volley} – {current}  (Duo)")
        st.info("**Volée Divisoria**" if volley % 2 else "**Volée Moltiplicatrice**")
        st.write(f"Totale attuale: **{team['total']}**")
        cols = st.columns(4)
        inputs = [c.selectbox(f"Freccia {i+1}", options=list(range(1, 11)) + ['M'], key=f"inp_{current}_{volley}_{i}")
                  for i, c in enumerate(cols)]
        if st.button("Valida Volée"):
            nums = [0 if v == 'M' else int(v) for v in inputs]
            last = nums[3]
            sum_three = sum(nums[:3])
            score = math.ceil(sum_three / calculate_divisor(last)) if volley % 2 \
                    else math.ceil(sum_three * calculate_multiplier(last))
            team['scores'].append(score)
            team['total'] += score
            st.success(f"Punteggio: {score} → Totale: {team['total']}")
            ss.current_team_index += 1
            if ss.current_team_index >= len(names):
                ss.current_team_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

    elif ss.game == 'classica':
        st.title(f"Volée {volley} – {current}  (Classica)")
        st.write("Ogni arciero tira 3 frecce (1-10, M=0) → somma 6 valori")
        st.write(f"Totale attuale: **{team['total']}**")
        cols = st.columns(6)
        inputs = [c.selectbox(f"Freccia {i+1}", options=list(range(1, 11)) + ['M'], key=f"inp_{current}_{volley}_{i}")
                  for i, c in enumerate(cols)]
        if st.button("Valida Volée"):
            score = sum(0 if v == 'M' else int(v) for v in inputs)
            team['scores'].append(score)
            team['total'] += score
            st.success(f"Punteggio volée: {score} → Totale: {team['total']}")
            ss.current_team_index += 1
            if ss.current_team_index >= len(names):
                ss.current_team_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

# -------------------------------------------------
# MID RANKING – tabella senza errori di formattazione
# -------------------------------------------------
elif ss.page == 'mid_ranking':
    st.title(f"Classifica dopo la Volée {ss.current_volley - 1}")
    df_mid = (
        pd.DataFrame([(t, d['total']) for t, d in ss.teams.items()],
                     columns=['Squadra', 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_mid.index += 1
    st.dataframe(df_mid.astype(str), use_container_width=True)
    if st.button("Prossima volée"):
        ss.page = 'game'
        st.rerun()

# -------------------------------------------------
# RESULTS – tabella finale senza errori
# -------------------------------------------------
elif ss.page == 'results':
    st.title("Classifica Finale")
    df_final = (
        pd.DataFrame([(t, d['total']) for t, d in ss.teams.items()],
                     columns=['Squadra', 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_final.index += 1
    st.dataframe(df_final.astype(str), use_container_width=True)

    rows = [{'Squadra': team} for team in ss.team_names]
    for team in ss.teams:
        for v in range(1, ss.volleys + 1):
            rows[ss.team_names.index(team)][f'Volée {v}'] = (
                ss.teams[team]['scores'][v - 1] if v <= len(ss.teams[team]['scores']) else ''
            )
        rows[ss.team_names.index(team)]['Totale'] = ss.teams[team]['total']
    csv = pd.DataFrame(rows).to_csv(index=False)
    st.download_button("Scarica CSV", csv, f"risultati_{ss.game}.csv", "text/csv")

    st.subheader("Evoluzione Punteggi")
    fig, ax = plt.subplots()
    for t, d in ss.teams.items():
        ax.plot(range(1, len(d['scores']) + 1),
                pd.Series(d['scores']).cumsum(),
                marker='o', label=t)
    ax.set_xlabel("Volée")
    ax.set_ylabel("Punteggio")
    ax.legend()
    st.pyplot(fig)

    if st.button("Torna alla home"):
        for k in list(ss.keys()):
            del ss[k]
        st.rerun()