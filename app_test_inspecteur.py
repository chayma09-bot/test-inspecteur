import streamlit as st
import sqlite3
import pandas as pd

# --- Base de données ---
conn = sqlite3.connect("inspecteurs.db", check_same_thread=False)
c = conn.cursor()

# Table utilisateurs
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    tests INTEGER DEFAULT 0
)
""")

# Table résultats
c.execute("""
CREATE TABLE IF NOT EXISTS resultats(
    username TEXT,
    score INTEGER
)
""")

conn.commit()

# --- Paramètres ---
MAX_TEST = 2

# Corrigé pour calcul automatique
correct_answers = {
    1:"Grave à suivre",2:"Grave à suivre",3:"Grave à suivre",4:"Grave à suivre",
    5:"Alerte",6:"Grave à suivre",7:"Alerte",8:"Grave à suivre",9:"Grave à suivre",10:"Alerte",
    11:"Grave à suivre",12:"Grave à suivre",13:"Alerte",14:"Grave à suivre",15:"Alerte",
    16:"Grave à suivre",17:"Alerte",18:"Grave à suivre",19:"Grave à suivre",20:"Alerte",
    21:"Grave à suivre",22:"Grave à suivre",23:"Grave à suivre",24:"Grave à suivre",
    25:"Alerte",26:"Grave à suivre",27:"Alerte",28:"Alerte",29:"Alerte",30:"Alerte"
}

# Questions
questions = {
    1:"Fissuration - Une fissure longitudinale de 0,4 mm sur 2 m",
    2:"Épaufrement localisé (2–3 cm), sans armature visible",
    3:"Armatures visibles, oxydées, perte de section 10–15%",
    4:"Efflorescences sans fissure ni corrosion",
    5:"Flèche excessive visible",
    6:"Appareil d’appui fortement encrassé",
    7:"Précontrainte - fissures + traces de rouille",
    8:"Altération superficielle sans perte de matière",
    9:"Joint laissant passer l’eau sur appuis",
    10:"Fissures >0,5 mm + armatures visibles",
    11:"Fissures transversales 0,2 mm en sous-face de poutre",
    12:"Éclatement localisé du béton avec armature apparente",
    13:"Fissures inclinées 45° près d’un appui, 0,6 mm",
    14:"Traces d’humidité persistantes sous tablier",
    15:"Armatures longitudinales fortement oxydées",
    16:"Fissure longitudinale fine (0,3 mm) sans corrosion",
    17:"Flèche évolutive par rapport à précédente inspection",
    18:"Appareil d’appui déplacé latéralement de quelques mm",
    19:"Carbonatation atteignant les armatures",
    20:"Infiltrations actives + épaufrures + corrosion",
    21:"Fissure verticale 0,5 mm en âme de poutre",
    22:"Microfissuration diffuse en tête de pile",
    23:"Joint de chaussée dégradé + corrosion débutante",
    24:"Maillage de fissures fines <0,2 mm sur parement",
    25:"Fissure longitudinale >0,8 mm + suintement brunâtre",
    26:"Décollement en sous-face 1 m² sans chute de béton",
    27:"Effondrement partiel récent sur zone circulée",
    28:"Rotation d’appareil d’appui avec fissures radiales",
    29:"Fissures multiples >0,5 mm + armatures visibles",
    30:"Fissuration modérée + augmentation notable de largeur"
}

# --- Session state ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "question" not in st.session_state:
    st.session_state.question = 1

if "answers" not in st.session_state:
    st.session_state.answers = {}

# --- PAGE ACCUEIL / MENU ---
if st.session_state.page == "home":

    st.title("Test Inspecteur VIPP")
    menu = st.sidebar.radio("Menu", ["Connexion", "Créer un compte", "Admin"])

    # ---- Créer compte ----
    if menu == "Créer un compte":
        st.subheader("Créer un compte inspecteur")
        new_user = st.text_input("Identifiant")
        new_password = st.text_input("Mot de passe", type="password")
        if st.button("Créer le compte"):
            c.execute("SELECT * FROM users WHERE username=?", (new_user,))
            if c.fetchone():
                st.error("Nom d'utilisateur déjà utilisé")
            else:
                c.execute("INSERT INTO users(username,password) VALUES (?,?)", (new_user,new_password))
                conn.commit()
                st.success("Compte créé avec succès")

    # ---- Connexion ----
    elif menu == "Connexion":
        st.subheader("Connexion inspecteur")
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
            user = c.fetchone()
            if user:
                st.session_state.user = username
                st.session_state.page = "accueil"
                st.stop()
            else:
                st.error("Identifiants incorrects")

    # ---- Admin ----
    elif menu == "Admin":
        st.subheader("Admin - Tableau des résultats")
        password = st.text_input("Mot de passe admin", type="password")
        if password == "admin123":
            df = pd.read_sql_query("SELECT * FROM resultats", conn)
            st.dataframe(df)

# --- PAGE ACCUEIL INSPECTEUR APRÈS LOGIN ---
elif st.session_state.page == "accueil":

    st.title(f"Bienvenue {st.session_state.user}")

    username = st.session_state.user
    c.execute("SELECT tests FROM users WHERE username=?", (username,))
    tests = c.fetchone()[0]

    st.write(f"Nombre de tests effectués : {tests}/{MAX_TEST}")

    if tests >= MAX_TEST:
        st.warning("Vous avez atteint la limite de tests")
    else:
        if st.button("Lancer le test"):
            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.stop()

    if st.button("Déconnexion"):
        st.session_state.page = "home"
        st.stop()

# --- PAGE QUIZ ---
# --- PAGE QUIZ ---
elif st.session_state.page == "quiz":

    q = st.session_state.question
    st.title(f"Question {q} / 30")
    st.write(questions[q])

    if q not in st.session_state.answers:
        st.session_state.answers[q] = None

    st.session_state.answers[q] = st.radio(
        "Choisir la gravité",
        ["Grave à suivre", "Alerte"],
        index=0 if st.session_state.answers[q] is None else ["Grave à suivre", "Alerte"].index(st.session_state.answers[q]),
        key=f"q{q}"
    )

    col1, col2 = st.columns(2)

    # --- Précédent ---
    if col1.button("Précédent", key=f"prev_{q}"):
        if st.session_state.question > 1:
            st.session_state.question -= 1
        st.stop()  # stoppe l'exécution pour forcer la mise à jour

    # --- Suivant ---
    if col2.button("Suivant", key=f"next_{q}"):
        if st.session_state.question < 30:
            st.session_state.question += 1
        else:
            st.session_state.page = "result"
        st.stop()
# --- PAGE RESULTAT ---
elif st.session_state.page == "result":

    st.title("Résultat du test")
    score = sum([1 for q,ans in st.session_state.answers.items() if ans == correct_answers[q]])
    st.subheader(f"Score : {score} / 30")

    if score >= 24:
        st.success("Inspecteur apte à sortir en terrain")
    else:
        st.error("Inspecteur non apte – formation requise")

    # Sauvegarde résultats
    username = st.session_state.user
    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)", (username,score))
    c.execute("UPDATE users SET tests = tests + 1 WHERE username=?", (username,))
    conn.commit()

    if st.button("Retour accueil"):
        st.session_state.page = "accueil"
        st.stop()

