import streamlit as st
import pandas as pd
import plotly.express as px
import extract_msg
import re

st.set_page_config(page_title="Analyse des incidents API", layout="wide")

# -----------------------
# MOT DE PASSE
# -----------------------

PASSWORD = "SNCFAPI"

def check_password():

    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:

        password = st.text_input("Mot de passe", type="password")

        if password == PASSWORD:
            st.session_state.auth = True
            st.rerun()

        elif password:
            st.error("Mot de passe incorrect")

        st.stop()

check_password()

# -----------------------
# TITRE
# -----------------------

st.title("API Analysis")

st.write(
"Upload .msg files pour générer des statistiques API."
)

# -----------------------
# PARAMETRES METIER
# -----------------------

HEURES_PAR_JOUR = 12
DUREE_INCIDENT = 4

# -----------------------
# INPUT NOMBRE API
# -----------------------

col_api, col_info = st.columns([1,2])

with col_api:

    NB_API_TOTAL = st.number_input(
        "Nombre total d'APIs sur la période analysée",
        min_value=1,
        value=39,
        step=1
    )

with col_info:
    st.info(
        "Indiquer le nombre total d'APIs actives pendant la période couverte par les fichiers incidents."
    )

# -----------------------
# SESSION DATA
# -----------------------

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["date","signalement","url"]
    )

if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

if "uploaded_count" not in st.session_state:
    st.session_state.uploaded_count = 0

# -----------------------
# UPLOAD MSG
# -----------------------

st.subheader("Ajouter fichiers incidents Outlook")

uploaded_files = st.file_uploader(
    "Glisser les fichiers .msg ici",
    type=["msg"],
    accept_multiple_files=True,
    key=f"upload_{st.session_state.upload_key}"
)

# -----------------------
# PARSE EMAIL
# -----------------------

def parse_msg(file):

    msg = extract_msg.Message(file)

    body = msg.body
    sent_on = msg.date

    date_mail = pd.to_datetime(sent_on)

    pattern = r"Signalement.*?de ([A-Z0-9\-_]+).*?URL concernée\s+(https?://\S+|\$\{[^}]+\})"

    matches = re.findall(pattern, body)

    rows = []

    for signalement, url in matches:

        rows.append({
            "date": date_mail,
            "signalement": signalement,
            "url": url
        })

    return rows

# -----------------------
# AJOUT INCIDENTS
# -----------------------

if uploaded_files:

    new_rows = []

    for file in uploaded_files:

        try:

            rows = parse_msg(file)

            new_rows.extend(rows)

        except:
            st.warning(f"Impossible de lire {file.name}")

    if new_rows:

        df_new = pd.DataFrame(new_rows)

        nb_before = len(st.session_state.data)

        df_total = pd.concat(
            [st.session_state.data, df_new],
            ignore_index=True
        )

        df_total = df_total.drop_duplicates(
            subset=["date","signalement","url"]
        )

        st.session_state.data = df_total

        nb_after = len(df_total)

        added = nb_after - nb_before

        if added > 0:
            st.success(f"{added} nouveaux incidents ajoutés")
        else:
            st.warning("Aucun nouvel incident (doublons détectés)")

        st.session_state.uploaded_count += len(uploaded_files)

# -----------------------
# SUPPRIMER FICHIERS
# -----------------------

col1, col2 = st.columns(2)

with col1:
    st.info(f"Fichiers analysés : {st.session_state.uploaded_count}")

with col2:
    if st.button("🗑 Réinitialiser l'analyse"):

        st.session_state.data = pd.DataFrame(
            columns=["date","signalement","url"]
        )

        st.session_state.uploaded_count = 0
        st.session_state.upload_key += 1

        st.rerun()

# dataset actif
df = st.session_state.data.copy()

if len(df) == 0:

    st.warning("Ajouter des fichiers incidents pour commencer l'analyse.")
    st.stop()

# -----------------------
# PREPARATION DATA
# -----------------------

df["date"] = pd.to_datetime(df["date"])

df = df[df["date"].dt.weekday < 5]

df["mois_num"] = df["date"].dt.month

mois_fr = {
1:"Janvier",2:"Février",3:"Mars",4:"Avril",
5:"Mai",6:"Juin",7:"Juillet",8:"Août",
9:"Septembre",10:"Octobre",11:"Novembre",12:"Décembre"
}

df["mois"] = df["mois_num"].map(mois_fr)

# -----------------------
# KPI
# -----------------------

nb_incidents = len(df)

api_impactees = df["signalement"].nunique()

apis_stables = NB_API_TOTAL - api_impactees

jours_ouvres = df["date"].nunique()

temps_total = jours_ouvres * NB_API_TOTAL * HEURES_PAR_JOUR

temps_panne = nb_incidents * DUREE_INCIDENT

if temps_total > 0:
    disponibilite = 1 - (temps_panne / temps_total)
else:
    disponibilite = 1

st.subheader("Indicateurs")

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Incidents",nb_incidents)
col2.metric("APIs impactées",api_impactees)
col3.metric("APIs stables",apis_stables)
col4.metric("APIs totales",NB_API_TOTAL)
col5.metric("Disponibilité",f"{disponibilite:.2%}")

# -----------------------
# INCIDENTS PAR MOIS
# -----------------------

incidents = df.groupby("mois").size().reset_index(name="incidents")

fig_incidents = px.bar(
    incidents,
    x="mois",
    y="incidents",
    title="Incidents par mois"
)

st.plotly_chart(fig_incidents, use_container_width=True)

# -----------------------
# TOP API INCIDENTS
# -----------------------

top_n = st.slider(
    "Top APIs générant des incidents",
    3,20,10
)

incidents_api = (
    df.groupby("signalement")
    .size()
    .reset_index(name="incidents")
    .sort_values("incidents",ascending=False)
    .head(top_n)
)

fig_api = px.bar(
    incidents_api,
    x="incidents",
    y="signalement",
    orientation="h",
    title=f"Top {top_n} APIs incidents"
)

st.plotly_chart(fig_api, use_container_width=True)

# -----------------------
# CAMEMBERT
# -----------------------

fig_pie = px.pie(
    incidents_api,
    values="incidents",
    names="signalement",
    title="Répartition des incidents"
)

st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------
# TABLE DONNEES
# -----------------------

st.subheader("Données incidents")

st.dataframe(df)