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

    if menu == "Créer un compte":
        st.subheader("Créer un compte inspecteur")
        new_user = st.text_input("Identifiant", key="new_user")
        new_password = st.text_input("Mot de passe", type="password", key="new_pass")
        if st.button("Créer le compte", key="btn_create"):
            c.execute("SELECT * FROM users WHERE username=?", (new_user,))
            if c.fetchone():
                st.error("Nom d'utilisateur déjà utilisé")
            else:
                c.execute("INSERT INTO users(username,password) VALUES (?,?)",(new_user,new_password))
                conn.commit()
                st.success("Compte créé avec succès")

    elif menu == "Connexion":
        st.subheader("Connexion inspecteur")
        username = st.text_input("Identifiant", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter", key="btn_login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
            user = c.fetchone()
            if user:
                st.session_state.user = username
                st.session_state.page = "accueil"
                st.stop()  # rafraîchit la page
            else:
                st.error("Identifiants incorrects")

    elif menu == "Admin":
        st.subheader("Admin - Tableau des résultats")
        password = st.text_input("Mot de passe admin", type="password", key="admin_pass")
        if password == "admin123":
            df = pd.read_sql_query("SELECT * FROM resultats",conn)
            st.dataframe(df)

# --- PAGE ACCUEIL INSPECTEUR APRÈS LOGIN ---
elif st.session_state.page == "accueil":
    st.title(f"Bienvenue {st.session_state.user}")
    username = st.session_state.user
    c.execute("SELECT tests FROM users WHERE username=?",(username,))
    tests = c.fetchone()[0]

    st.write(f"Nombre de tests effectués : {tests}/{MAX_TEST}")

    if tests >= MAX_TEST:
        st.warning("Vous avez atteint la limite de tests")
    else:
        if st.button("Lancer le test", key="btn_start_test"):
            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.stop()  # rafraîchit la page

    if st.button("Déconnexion", key="btn_logout"):
        st.session_state.page = "home"
        st.stop()

# --- PAGE QUIZ ---
elif st.session_state.page == "quiz":
    q = st.session_state.question
    st.title(f"Question {q} / 30")
    question_text = questions[q]
    st.write(question_text)

    if q not in st.session_state.answers:
        st.session_state.answers[q] = None

    st.session_state.answers[q] = st.radio(
        "Choisir la gravité",
        ["Grave à suivre", "Alerte"],
        index=0 if st.session_state.answers[q] is None else ["Grave à suivre", "Alerte"].index(st.session_state.answers[q]),
        key=f"q{q}"
    )

    col1, col2 = st.columns(2)
    prev_clicked = col1.button("Précédent", key=f"prev{q}") if q>1 else False
    next_clicked = col2.button("Suivant", key=f"next{q}")

    if prev_clicked:
        st.session_state.question -= 1
        st.stop()
    if next_clicked:
        if q < 30:
            st.session_state.question += 1
        else:
            st.session_state.page = "result"
        st.stop()

# --- PAGE RESULTAT ---
elif st.session_state.page == "result":
    st.title("Résultat du test")

    # Simulation IA : score basé sur réponses “raisonnées”
    correct_answers = ["Grave à suivre"]*30  # ici on peut améliorer avec IA simulée
    score = sum(1 for i, ans in st.session_state.answers.items() if ans == correct_answers[i-1])

    st.subheader(f"Score : {score} / 30")
    if score >= 24:
        st.success("Inspecteur apte à sortir en terrain")
    else:
        st.error("Inspecteur non apte – formation requise")

    # Sauvegarde résultats
    username = st.session_state.user
    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",(username,score))
    c.execute("UPDATE users SET tests = tests + 1 WHERE username=?",(username,))
    conn.commit()

    if st.button("Retour accueil", key="btn_back_home"):
        st.session_state.page = "accueil"
        st.stop()
