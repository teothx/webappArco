import streamlit as st
import matplotlib.pyplot as plt
import math
import pandas as pd

# ---------- FUNZIONI ----------
def calculate_divisor(d_score):
    return 1 if d_score >= 9 else (1.5 if d_score >= 7 else 2)

def calculate_multiplier(m_score):
    return 2 if m_score >= 9 else (1.5 if m_score >= 7 else 1)

def game_data():
    return (st.session_state.participant_names, st.session_state.scores) \
        if st.session_state.game == 'solo' \
        else (st.session_state.team_names, st.session_state.teams)

# ---------- SESSION STATE ----------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.game = None
    st.session_state.setup_step = 0
    st.session_state.num_participants = 0
    st.session_state.volleys = 0
    st.session_state.team_names = []
    st.session_state.participant_names = []
    st.session_state.teams = {}
    st.session_state.scores = {}
    st.session_state.current_volley = 1
    st.session_state.current_index = 0
    st.session_state.button_key = 0
ss = st.session_state

# ---------- NAVIGAZIONE ----------
if ss.page == 'home':
    st.title("Archery Games Hub")
    st.write("Scegli la modalità:")
    if st.button("Archery Duo Challenge"):
        ss.game = 'duo'
        ss.page = 'rules'
        st.rerun()
    if st.button("La Classica"):
        ss.game = 'classica'
        ss.page = 'rules_classica'
        st.rerun()
    if st.button("Bull’s Revenge"):
        ss.game = 'bull'
        ss.page = 'rules_bull'
        st.rerun()
    if st.button("18 m Singolo"):
        ss.game = 'solo'
        ss.page = 'rules_solo'
        st.rerun()

# -------------------------------------------------
# REgole giochi
# -------------------------------------------------
elif ss.page == 'rules':
    st.title("Archery Duo Challenge – Regole")
    st.markdown("""
- Squadra mista: principiante + veterano  
- Volée dispari: principiante 3 frecce, veterano 1 freccia = **divisore**  
- Volée pari: veterano 3 frecce, principiante 1 freccia = **moltiplicatore**  
- Numero di volée pari – punteggio cumulativo  
""")
    if st.button("Inizia Gioco"):
        ss.page = 'setup'
        ss.setup_step = 0
        st.rerun()

elif ss.page == 'rules_classica':
    st.title("La Classica – Regole")
    st.markdown("""
- Ogni arciero tira 3 frecce → somma 6 valori per squadra  
- Nessun moltiplicatore  
- Numero di volée pari  
""")
    if st.button("Inizia Gioco"):
        ss.page = 'setup'
        ss.setup_step = 0
        st.rerun()

elif ss.page == 'rules_bull':
    st.title("Bull’s Revenge – Regole")
    st.markdown("""
- **Volée dispari**: Arciere A tira 3 frecce (1-10), Arciere B la Bull (1-10 o M)  
- **Volée pari**: ruoli invertiti  
- **Punteggio squadra** = (somma 3 frecce) × moltiplicatore Bull  
  - 10 → ×3, 9-8 → ×2, 7-6 → ×1.5, 5-1 → ×1, 0 (M) → 0  
""")
    if st.button("Inizia Gioco"):
        ss.page = 'setup'
        ss.setup_step = 0
        st.rerun()

elif ss.page == 'rules_solo':
    st.title("18 m Singolo – Regole")
    st.markdown("""
- Gara individuale – 3 frecce per volée  
- Valori 1-10 o M (0) – punteggio cumulativo  
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
        n = st.number_input("Numero squadre / partecipanti", 1, 20, 2)
        v = st.number_input("Numero di volée", 2, 10, 4, step=2)
        if st.button("Conferma"):
            ss.num_participants = n
            ss.volleys = v
            ss.setup_step = 1
            st.rerun()
    else:
        st.subheader("Inserisci i nomi")
        names_list = ss.participant_names if ss.game == 'solo' else ss.team_names
        data_dict  = ss.scores       if ss.game == 'solo' else ss.teams

        if not names_list:
            names_list.extend([f"{'Arciere' if ss.game == 'solo' else 'Squadra'} {i+1}"
                               for i in range(ss.num_participants)])
        for i in range(ss.num_participants):
            names_list[i] = st.text_input(f"{'Arciere' if ss.game == 'solo' else 'Squadra'} {i+1}",
                                          value=names_list[i], key=f"name_{i}")
        if st.button("Conferma Nomi"):
            for name in names_list:
                data_dict[name] = {'scores': [], 'total': 0}
            ss.page = 'game'
            ss.current_volley = 1
            ss.current_index = 0
            st.rerun()

# -------------------------------------------------
# GAME – routing
# -------------------------------------------------
elif ss.page == 'game':
    names, data = game_data()
    current = names[ss.current_index]
    volley = ss.current_volley
    for n in names:
        data[n].pop(f"done_{n}_{volley}", None)

    # ----------- DUO -----------
    if ss.game == 'duo':
        st.title(f"Volée {volley} – {current}  (Duo)")
        st.info("**Volée Divisoria**" if volley % 2 else "**Volée Moltiplicatrice**")
        st.write(f"Totale attuale: **{data[current]['total']}**")
        inputs = [st.selectbox(f"Freccia {i+1}", list(range(1, 11)) + ['M'],
                              key=f"inp_{current}_{volley}_{i}") for i in range(4)]
        if st.button("Valida Volée"):
            nums = [0 if v == 'M' else int(v) for v in inputs]
            last = nums[3]
            sum_three = sum(nums[:3])
            score = math.ceil(sum_three / calculate_divisor(last)) if volley % 2 \
                    else math.ceil(sum_three * calculate_multiplier(last))
            data[current]['scores'].append(score)
            data[current]['total'] += score
            st.success(f"Punteggio: {score} → Totale: {data[current]['total']}")
            ss.current_index += 1
            if ss.current_index >= len(names):
                ss.current_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

    # ----------- CLASSICA -----------
    elif ss.game == 'classica':
        st.title(f"Volée {volley} – {current}  (Classica)")
        st.write("Ogni arciero tira 3 frecce → somma 6 valori")
        st.write(f"Totale attuale: **{data[current]['total']}**")
        inputs = [st.selectbox(f"Freccia {i+1}", list(range(1, 11)) + ['M'],
                              key=f"inp_{current}_{volley}_{i}") for i in range(6)]
        if st.button("Valida Volée"):
            score = sum(0 if v == 'M' else int(v) for v in inputs)
            data[current]['scores'].append(score)
            data[current]['total'] += score
            st.success(f"Punteggio volée: {score} → Totale: {data[current]['total']}")
            ss.current_index += 1
            if ss.current_index >= len(names):
                ss.current_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

    # ----------- BULL’S REVENGE -----------
    elif ss.game == 'bull':
        st.title(f"Volée {volley} – {current}  (Bull’s Revenge)")
        role = "Arciere A 3 frecce – Arciere B la Bull" if volley % 2 else "Arciere B 3 frecce – Arciere A la Bull"
        st.write(role)
        st.write(f"Totale attuale: **{data[current]['total']}**")
        normal = [st.selectbox(f"3 frecce {i+1}", list(range(1, 11)), key=f"norm_{current}_{volley}_{i}")
                  for i in range(3)]
        bull = st.selectbox("Bull", list(range(1, 11)) + ['M'], key=f"bull_{current}_{volley}")
        if st.button("Valida Volée"):
            sum_norm = sum(normal)
            bull_val = 0 if bull == 'M' else int(bull)
            if bull_val == 0:
                score = 0
            elif bull_val == 10:
                score = sum_norm * 3
            elif bull_val >= 8:
                score = sum_norm * 2
            elif bull_val >= 6:
                score = int(sum_norm * 1.5)
            else:
                score = sum_norm
            data[current]['scores'].append(score)
            data[current]['total'] += score
            st.success(f"Punteggio volée: {score} → Totale: {data[current]['total']}")
            ss.current_index += 1
            if ss.current_index >= len(names):
                ss.current_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

    # ----------- 18 m SINGOLO -----------
    elif ss.game == 'solo':
        st.title(f"Volée {volley} – {current}  (18 m Singolo)")
        st.write("3 frecce (1-10 o M) – somma punteggio")
        st.write(f"Totale attuale: **{data[current]['total']}**")
        inputs = [st.selectbox(f"Freccia {i+1}", list(range(1, 11)) + ['M'],
                               key=f"inp_{current}_{volley}_{i}") for i in range(3)]
        if st.button("Valida Volée"):
            score = sum(0 if v == 'M' else int(v) for v in inputs)
            data[current]['scores'].append(score)
            data[current]['total'] += score
            st.success(f"Punteggio volée: {score} → Totale: {data[current]['total']}")
            ss.current_index += 1
            if ss.current_index >= len(names):
                ss.current_index = 0
                ss.current_volley += 1
                ss.page = 'mid_ranking' if ss.current_volley <= ss.volleys else 'results'
            st.rerun()

# -------------------------------------------------
# MID RANKING
# -------------------------------------------------
elif ss.page == 'mid_ranking':
    st.title(f"Classifica dopo la Volée {ss.current_volley - 1}")
    names, data = game_data()
    labels = 'Nome' if ss.game == 'solo' else 'Squadra'
    df_mid = (
        pd.DataFrame([(n, data[n]['total']) for n in names],
                     columns=[labels, 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_mid.index += 1
    st.dataframe(df_mid.astype(str), use_container_width=True)
    if st.button("Prossima volée"):
        ss.page = 'game'
        st.rerun()

# -------------------------------------------------
# RESULTS
# -------------------------------------------------
elif ss.page == 'results':
    st.title("Classifica Finale")
    names, data = game_data()
    labels = 'Nome' if ss.game == 'solo' else 'Squadra'
    df_final = (
        pd.DataFrame([(n, data[n]['total']) for n in names],
                     columns=[labels, 'Totale'])
        .sort_values('Totale', ascending=False)
        .reset_index(drop=True)
    )
    df_final.index += 1
    st.dataframe(df_final.astype(str), use_container_width=True)

    rows = [{labels: n} for n in names]
    for n in names:
        for v in range(1, ss.volleys + 1):
            rows[names.index(n)][f'Volée {v}'] = (
                data[n]['scores'][v - 1] if v <= len(data[n]['scores']) else ''
            )
        rows[names.index(n)]['Totale'] = data[n]['total']
    csv = pd.DataFrame(rows).to_csv(index=False)
    st.download_button("Scarica CSV", csv, f"risultati_{ss.game}.csv", "text/csv")

    st.subheader("Evoluzione Punteggi")
    fig, ax = plt.subplots()
    for n in names:
        ax.plot(range(1, len(data[n]['scores']) + 1),
                pd.Series(data[n]['scores']).cumsum(),
                marker='o', label=n)
    ax.set_xlabel("Volée")
    ax.set_ylabel("Punteggio")
    ax.legend()
    st.pyplot(fig)

    if st.button("Torna alla home"):
        for k in list(ss.keys()):
            del ss[k]
        st.rerun()