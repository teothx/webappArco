import streamlit as st
import matplotlib.pyplot as plt
import math
import pandas as pd

# ---------- FUNZIONI ----------
def calculate_divisor(d_score):
    if d_score >= 9:
        return 1
    elif d_score >= 7:
        return 1.5
    else:
        return 2

def calculate_multiplier(m_score):
    if m_score >= 9:
        return 2
    elif m_score >= 7:
        return 1.5
    else:
        return 1

# ---------- SESSION STATE ----------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.setup_step = 0
    st.session_state.num_teams = 0
    st.session_state.volleys = 0
    st.session_state.team_names = []
    st.session_state.teams = {}
    st.session_state.current_volley = 1
    st.session_state.current_team_index = 0
    st.session_state.button_key = 0
ss = st.session_state

# ---------- PAGINE ----------
if ss.page == 'home':
    st.title("Archery Games Hub")
    if st.button("Play Archery Duo Challenge", key=f"btn_play_{ss.button_key}"):
        ss.page = 'rules'
        ss.button_key += 1
        st.rerun()

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
    if st.button("Inizia Gioco", key=f"btn_start_{ss.button_key}"):
        ss.page = 'setup'
        ss.setup_step = 0
        ss.button_key += 1
        st.rerun()

elif ss.page == 'setup':
    st.title("Setup Torneo")
    if ss.setup_step == 0:
        n = st.number_input("Numero Squadre", 1, 20, 2)
        v = st.number_input("Volée per Squadra (pari)", 2, 10, 4, step=2)
        if st.button("Conferma Configurazione", key=f"btn_conf_{ss.button_key}"):
            ss.num_teams = n
            ss.volleys = v
            ss.setup_step = 1
            ss.button_key += 1
            st.rerun()
    else:
        st.subheader("Inserisci nomi delle squadre")
        if not ss.team_names:
            ss.team_names = [f"Squadra {i+1}" for i in range(ss.num_teams)]
        for i in range(ss.num_teams):
            ss.team_names[i] = st.text_input(f"Squadra {i+1}", value=ss.team_names[i], key=f"name_{i}")
        if st.button("Conferma Nomi", key=f"btn_names_{ss.button_key}"):
            for name in ss.team_names:
                ss.teams[name] = {'scores': [], 'total': 0}
            ss.page = 'game'
            ss.button_key += 1
            st.rerun()

elif ss.page == 'game':
    names = ss.team_names
    current = names[ss.current_team_index]
    team = ss.teams[current]
    volley = ss.current_volley

    # Rimuove eventuali chiavi di validazione residue della nuova volée
    for n in names:
        ss.pop(f"done_{n}_{volley}", None)

    st.title(f"Volée {volley} – {current}")
    st.info("**Volée Divisoria**" if volley % 2 else "**Volée Moltiplicatrice**")
    st.write(f"Totale attuale: **{team['total']}**")

    cols = st.columns(4)
    inputs = [c.text_input(f"Freccia {i+1}", key=f"inp_{current}_{volley}_{i}")
              for i, c in enumerate(cols)]
    allowed = [str(x) for x in range(10, 0, -1)] + ['M']

    if st.button("Valida Volée", key=f"btn_val_{ss.button_key}"):
        nums = [0 if v == 'M' else int(v) for v in inputs if v in allowed]
        if len(nums) != 4:
            st.error("Valori non validi! Usa 10-1 o M")
            st.stop()

        sum_three, last = sum(nums[:3]), nums[3]
        score = math.ceil(sum_three / calculate_divisor(last)) if volley % 2 \
                else math.ceil(sum_three * calculate_multiplier(last))

        team['scores'].append(score)
        team['total'] += score
        st.success(f"Punteggio volée: {score}  → Totale: {team['total']}")

        ss.current_team_index += 1
        if ss.current_team_index >= len(names):
            ss.current_team_index = 0
            ss.current_volley += 1  # incremento effettivo
            if ss.current_volley <= ss.volleys:
                ss.page = 'mid_ranking'
            else:
                ss.page = 'results'
        ss.button_key += 1
        st.rerun()

elif ss.page == 'mid_ranking':
    st.title(f"Classifica dopo la Volée {ss.current_volley - 1}")
    df_mid = (
        pd.DataFrame([(t, d['total']) for t, d in ss.teams.items()],
                     columns=['Squadra', 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_mid.index += 1  # parte da 1
    st.table(df_mid)

    if st.button("Prossima volée", key=f"btn_next_{ss.button_key}"):
        ss.page = 'game'
        ss.button_key += 1
        st.rerun()

elif ss.page == 'results':
    st.title("Classifica Finale")
    df_final = (
        pd.DataFrame([(t, d['total']) for t, d in ss.teams.items()],
                     columns=['Squadra', 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_final.index += 1  # 1°, 2°, 3°…
    st.table(df_final)

    rows = []
    for team, data in ss.teams.items():
        r = {'Squadra': team}
        for v in range(1, ss.volleys + 1):
            r[f'Volée {v}'] = data['scores'][v - 1] if v <= len(data['scores']) else ''
        r['Totale'] = data['total']
        rows.append(r)
    csv = pd.DataFrame(rows).to_csv(index=False)
    st.download_button("Scarica CSV", csv, "risultati_archery_duo.csv", "text/csv")

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