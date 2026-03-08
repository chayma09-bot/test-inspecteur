import streamlit as st
import sqlite3

# Base de données
conn = sqlite3.connect("inspecteurs.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS resultats(
username TEXT,
score INTEGER)""")

conn.commit()

# Corrigé (utilisé seulement pour le calcul)
correct_answers = {
1:"Grave à suivre",2:"Grave à suivre",3:"Grave à suivre",4:"Grave à suivre",
5:"Alerte",6:"Grave à suivre",7:"Alerte",8:"Grave à suivre",9:"Grave à suivre",10:"Alerte",
11:"Grave à suivre",12:"Grave à suivre",13:"Alerte",14:"Grave à suivre",15:"Alerte",
16:"Grave à suivre",17:"Alerte",18:"Grave à suivre",19:"Grave à suivre",20:"Alerte",
21:"Grave à suivre",22:"Grave à suivre",23:"Grave à suivre",24:"Grave à suivre",
25:"Alerte",26:"Grave à suivre",27:"Alerte",28:"Alerte",29:"Alerte",30:"Alerte"
}

questions = {
1:"Fissure longitudinale de 0,4 mm sur 2 m",
2:"Épaufrement localisé sans armature visible",
3:"Armatures visibles oxydées",
4:"Efflorescences sans corrosion",
5:"Flèche excessive visible",
}

# Etat session
if "page" not in st.session_state:
    st.session_state.page = "login"

if "question" not in st.session_state:
    st.session_state.question = 1

if "answers" not in st.session_state:
    st.session_state.answers = {}

# PAGE LOGIN
if st.session_state.page == "login":

    st.title("Connexion Inspecteur")

    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):

        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        data = c.fetchone()

        if data:
            st.session_state.user = username
            st.session_state.page = "quiz"
            st.rerun()
        else:
            st.error("Identifiants incorrects")

# PAGE TEST
elif st.session_state.page == "quiz":

    q = st.session_state.question

    st.title(f"Question {q} / 30")

    question_text = questions.get(q, f"Question {q}")

    st.write(question_text)

    answer = st.radio(
        "Choisir la gravité",
        ["Grave à suivre","Alerte"],
        key=q
    )

    st.session_state.answers[q] = answer

    col1,col2 = st.columns(2)

    if col1.button("Précédent") and q > 1:
        st.session_state.question -= 1
        st.rerun()

    if col2.button("Suivant"):

        if q < 30:
            st.session_state.question += 1
            st.rerun()
        else:
            st.session_state.page = "result"
            st.rerun()

# PAGE RESULTAT
elif st.session_state.page == "result":

    st.title("Résultat du test")

    score = 0

    for q in correct_answers:
        if st.session_state.answers.get(q) == correct_answers[q]:
            score += 1

    st.subheader(f"Score : {score} / 30")

    if score >= 24:
        st.success("Inspecteur apte à sortir en terrain")
    else:
        st.error("Inspecteur non apte – formation requise")

    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",
              (st.session_state.user,score))
    conn.commit()
