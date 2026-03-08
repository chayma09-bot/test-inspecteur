import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("inspecteurs.db", check_same_thread=False)
c = conn.cursor()

# tables
c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT,
tests INTEGER DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS resultats(
username TEXT,
score INTEGER
)""")

conn.commit()

MAX_TEST = 2

correct_answers = {
1:"Grave à suivre",2:"Grave à suivre",3:"Grave à suivre",4:"Grave à suivre",
5:"Alerte",6:"Grave à suivre",7:"Alerte",8:"Grave à suivre",9:"Grave à suivre",10:"Alerte",
11:"Grave à suivre",12:"Grave à suivre",13:"Alerte",14:"Grave à suivre",15:"Alerte",
16:"Grave à suivre",17:"Alerte",18:"Grave à suivre",19:"Grave à suivre",20:"Alerte",
21:"Grave à suivre",22:"Grave à suivre",23:"Grave à suivre",24:"Grave à suivre",
25:"Alerte",26:"Grave à suivre",27:"Alerte",28:"Alerte",29:"Alerte",30:"Alerte"
}

# session state
if "page" not in st.session_state:
    st.session_state.page = "home"

if "question" not in st.session_state:
    st.session_state.question = 1

if "answers" not in st.session_state:
    st.session_state.answers = {}

# HOME
if st.session_state.page == "home":

    st.title("Test Inspecteur VIPP")

    menu = st.radio(
        "Menu",
        ["Connexion","Créer un compte","Admin"]
    )

    # CREATE ACCOUNT
    if menu == "Créer un compte":

        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe",type="password")

        if st.button("Créer le compte"):

            c.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))
            conn.commit()

            st.success("Compte créé")

    # LOGIN
    if menu == "Connexion":

        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe",type="password")

        if st.button("Se connecter"):

            c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
            user = c.fetchone()

            if user:

                st.session_state.user = username
                st.session_state.page = "accueil"
                st.rerun()

            else:

                st.error("Identifiants incorrects")

    # ADMIN
    if menu == "Admin":

        password = st.text_input("Mot de passe admin",type="password")

        if password == "admin123":

            df = pd.read_sql_query("SELECT * FROM resultats",conn)

            st.dataframe(df)

# PAGE ACCUEIL INSPECTEUR
elif st.session_state.page == "accueil":

    st.title("Bienvenue Inspecteur")

    username = st.session_state.user

    c.execute("SELECT tests FROM users WHERE username=?",(username,))
    tests = c.fetchone()[0]

    st.write(f"Nombre de tests effectués : {tests}/2")

    if tests >= MAX_TEST:

        st.warning("Vous avez atteint la limite de tests")

    else:

        if st.button("Lancer le test"):

            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.rerun()

    if st.button("Retour accueil"):

        st.session_state.page = "home"
        st.rerun()

# QUIZ
elif st.session_state.page == "quiz":

    q = st.session_state.question

    st.title(f"Question {q} / 30")

    answer = st.radio(
        "Choisir la gravité",
        ["Grave à suivre","Alerte"],
        key=q
    )

    st.session_state.answers[q] = answer

    col1,col2 = st.columns(2)

    if q > 1:
        if col1.button("Précédent"):
            st.session_state.question -= 1
            st.rerun()

    if col2.button("Suivant"):

        if q < 30:

            st.session_state.question += 1

        else:

            st.session_state.page = "result"

        st.rerun()

# RESULT
elif st.session_state.page == "result":

    st.title("Résultat du test")

    score = 0

    for q in correct_answers:

        if st.session_state.answers.get(q) == correct_answers[q]:

            score += 1

    st.subheader(f"Score : {score}/30")

    if score >= 24:

        st.success("Inspecteur apte terrain")

    else:

        st.error("Inspecteur non apte")

    username = st.session_state.user

    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",(username,score))

    c.execute("UPDATE users SET tests = tests + 1 WHERE username=?",(username,))

    conn.commit()

    if st.button("Retour accueil"):

        st.session_state.page = "accueil"
        st.rerun()
