import streamlit as st
import sqlite3
import pandas as pd

# ---------------- Base de données ----------------
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

MAX_TEST = 2

# ---------------- Corrigé et questions ----------------
correct_answers = {
1:"Grave à suivre",2:"Grave à suivre",3:"Grave à suivre",4:"Alerte",
5:"Alerte",6:"Alerte",7:"Grave à suivre",8:"Alerte",9:"Alerte",10:"Grave à suivre",
11:"Grave à suivre",12:"Alerte",13:"Alerte",14:"Alerte",15:"Grave à suivre",
16:"Alerte",17:"Grave à suivre",18:"Alerte",19:"Grave à suivre",20:"Grave à suivre",
21:"Grave à suivre",22:"Grave à suivre",23:"Alerte",24:"Alerte",25:"Grave à suivre",
26:"Alerte",27:"Grave à suivre",28:"Grave à suivre",29:"Grave à suivre",30:"Alerte"
}

questions = {
1:"Fissure longitudinale de 0,4 mm, continue sur 2 m, observée en zone tendue",
2:"Épaufrement localisé (2–3 cm), sans armature visible",
3:"Armatures visibles, oxydées, perte de section estimée à 10–15 %",
4:"Coulures blanchâtres sans fissure ni corrosion",
5:"Flèche excessive visible comparée aux travées voisines",
6:"Appareil fortement encrassé avec blocage apparent",
7:"Fissures longitudinales + traces de rouille + suintements",
8:"Altération superficielle sans perte de matière",
9:"Joint laissant passer l’eau sur appuis",
10:"Fissures > 0,5 mm + armatures visibles sur élément porteur",
11:"Fissures transversales espacées (~1 m), largeur 0,2 mm, sous-face de poutre",
12:"Éclatement du béton avec armature apparente localement, corrosion superficielle",
13:"Fissures inclinées à 45° à proximité d’un appui, largeur 0,6 mm",
14:"Traces d’humidité persistantes sous le tablier, sans fissuration visible",
15:"Armatures longitudinales fortement oxydées, éclatement généralisé, perte > 20 %",
16:"Fissure longitudinale fine (0,3 mm) parallèle aux gaines, sans corrosion",
17:"Flèche supérieure aux valeurs observées lors de la précédente inspection",
18:"Appareil déplacé latéralement de quelques millimètres, sans fissuration associée",
19:"Carbonatation atteignant les armatures, sans corrosion visible",
20:"Infiltrations actives + épaufrures + corrosion visible sur about de poutre",
21:"Fissure verticale isolée de 0,5 mm en âme de poutre",
22:"Microfissuration diffuse en tête de pile sans éclatement ni corrosion",
23:"Joint dégradé avec perte partielle d’étanchéité, corrosion débutante",
24:"Maillage de fissures fines (<0,2 mm) sur parement exposé au soleil",
25:"Fissure longitudinale > 0,8 mm + suintement brunâtre localisé",
26:"Son creux étendu sur 1 m² en sous-face de dalle, sans chute de béton",
27:"Chute récente de fragments de béton sur zone circulée",
28:"Rotation visible d’un appareil d’appui avec fissures radiales en about",
29:"Fissures multiples > 0,5 mm + armatures visibles sur zone d’ancrage",
30:"Fissuration modérée connue + augmentation notable de largeur lors du contrôle"
}

# ---------------- Session state ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "question" not in st.session_state:
    st.session_state.question = 1

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- Sidebar Menu ----------------
menu = st.sidebar.selectbox("Menu", ["Accueil","Créer un compte","Connexion","Admin"])

# ---------------- Créer compte ----------------
if menu == "Créer un compte":
    st.subheader("Créer un compte inspecteur")
    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Créer le compte"):
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            st.error("Cet identifiant existe déjà !")
        else:
            c.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))
            conn.commit()
            st.success("Compte créé avec succès !")

# ---------------- Connexion ----------------
elif menu == "Connexion":
    st.subheader("Connexion Inspecteur")
    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        if user:
            st.session_state.user = username
            st.session_state.page = "accueil"
            st.rerun()
        else:
            st.error("Identifiants incorrects")

# ---------------- Admin ----------------
elif menu == "Admin":
    st.subheader("Admin Dashboard")
    password = st.text_input("Mot de passe admin", type="password")
    if password == "admin123":
        df = pd.read_sql_query("SELECT u.username, r.score, u.tests FROM users u LEFT JOIN resultats r ON u.username=r.username",conn)
        st.dataframe(df)
    else:
        st.info("Entrez le mot de passe admin pour voir le tableau")

# ---------------- Page accueil inspecteur ----------------
if st.session_state.page == "accueil":
    st.title(f"Bienvenue {st.session_state.user}")
    username = st.session_state.user
    c.execute("SELECT tests FROM users WHERE username=?",(username,))
    tests = c.fetchone()[0]
    st.write(f"Nombre de tests effectués : {tests}/{MAX_TEST}")
    
    if tests >= MAX_TEST:
        st.warning("Vous avez atteint la limite de tests")
    else:
        if st.button("Lancer le test"):
            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.rerun()
    
    if st.button("Déconnexion / Retour accueil"):
        st.session_state.page = "home"
        st.session_state.user = None
        st.rerun()

# ---------------- Quiz ----------------
elif st.session_state.page == "quiz":
    q = st.session_state.question
    st.title(f"Question {q} / 30")
    question_text = questions.get(q, f"Question {q}")
    st.write(question_text)

    st.session_state.answers[q] = st.radio("Choisir la gravité", ["Grave à suivre","Alerte"], key=q)

    col1, col2 = st.columns(2)
    if q > 1:
        if col1.button("Précédent"):
            st.session_state.question -= 1
            st.rerun()
    else:
        col1.empty()  # Question 1 : pas de précédent

    if col2.button("Suivant"):
        if q < 30:
            st.session_state.question += 1
        else:
            st.session_state.page = "result"
        st.rerun()

# ---------------- Résultat ----------------
elif st.session_state.page == "result":
    st.title("Résultat du test")
    score = 0
    for q in correct_answers:
        if st.session_state.answers.get(q) == correct_answers[q]:
            score += 1

    st.subheader(f"Score : {score}/30")
    if score >= 24:
        st.success("Inspecteur apte à sortir en terrain")
    else:
        st.error("Inspecteur non apte – formation requise")

    # Sauvegarde des résultats
    username = st.session_state.user
    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",(username,score))
    c.execute("UPDATE users SET tests = tests + 1 WHERE username=?",(username,))
    conn.commit()

    if st.button("Retour accueil"):
        st.session_state.page = "accueil"
        st.rerun()
