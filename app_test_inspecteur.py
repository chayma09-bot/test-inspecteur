import streamlit as st
import sqlite3

# connexion base
conn = sqlite3.connect("inspecteurs.db", check_same_thread=False)
c = conn.cursor()

# table utilisateurs
c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# table résultats
c.execute("""
CREATE TABLE IF NOT EXISTS resultats(
username TEXT,
score INTEGER
)
""")

conn.commit()

# corrigé
correct_answers = {
1:"B",2:"A",3:"B",4:"A",5:"C",6:"B",7:"C",8:"A",9:"B",10:"C",
11:"A",12:"B",13:"C",14:"B",15:"C",16:"B",17:"C",18:"B",19:"B",20:"C",
21:"B",22:"A",23:"B",24:"A",25:"C",26:"B",27:"C",28:"C",29:"C",30:"C"
}

st.title("Test Inspecteur VIPP")

menu = ["Connexion","Créer un compte"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- CREER COMPTE ----------------

if choice == "Créer un compte":

    st.subheader("Créer un compte inspecteur")

    new_user = st.text_input("Identifiant")
    new_password = st.text_input("Mot de passe", type="password")

    if st.button("Créer le compte"):

        c.execute("INSERT INTO users(username,password) VALUES (?,?)",(new_user,new_password))
        conn.commit()

        st.success("Compte créé avec succès")

# ---------------- LOGIN ----------------

if choice == "Connexion":

    st.subheader("Connexion")

    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):

        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        data = c.fetchone()

        if data:

            st.success("Connexion réussie")

            answers = {}

            for i in range(1,31):

                answers[i] = st.radio(
                    f"Question {i}",
                    ["A","B","C"],
                    key=i
                )

            if st.button("Valider le test"):

                score = 0

                for q in correct_answers:
                    if answers[q] == correct_answers[q]:
                        score += 1

                st.subheader(f"Score : {score}/30")

                if score >= 24:
                    st.success("Apte à sortir en terrain")
                else:
                    st.error("Non apte – formation requise")

                c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",(username,score))
                conn.commit()

        else:
            st.error("Identifiants incorrects")