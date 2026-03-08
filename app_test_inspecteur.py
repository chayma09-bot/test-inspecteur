import streamlit as st
import sqlite3
import pandas as pd

# --- Connexion base de données ---
conn = sqlite3.connect("inspecteurs.db", check_same_thread=False)
c = conn.cursor()

# --- Création des tables ---
c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT,
tests INTEGER DEFAULT 0
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS resultats(
username TEXT,
score INTEGER
)
""")
conn.commit()

# --- Paramètres ---
MAX_TEST = 2

# --- Questions et corrigé ---
questions = {
1:"Fissuration : Une fissure longitudinale de 0,4 mm, continue sur 2 m, est observée en zone tendue.",
2:"Épaufrement : Épaufrement localisé (2–3 cm), sans armature visible.",
3:"Armatures apparentes : Armatures visibles, oxydées, perte de section estimée à 10–15 %.",
4:"Efflorescences : Coulures blanchâtres sans fissure ni corrosion.",
5:"Déformation : Flèche excessive visible comparée aux travées voisines.",
6:"Appareils d’appui : Appareil fortement encrassé avec blocage apparent.",
7:"Précontrainte : Fissures longitudinales + traces de rouille + suintements.",
8:"Parement : Altération superficielle sans perte de matière.",
9:"Joint : Joint laissant passer l’eau sur appuis.",
10:"Désordres combinés : Fissures > 0,5 mm + armatures visibles sur élément porteur.",
11:"Fissuration transversale : Fissures transversales espacées régulièrement (~1 m), largeur 0,2 mm, en sous-face de poutre.",
12:"Éclatement localisé : Éclatement du béton avec armature apparente localement, corrosion superficielle sans perte mesurable de section.",
13:"About de poutre : Fissures inclinées à 45° à proximité d’un appui, largeur 0,6 mm.",
14:"Infiltration tablier : Traces d’humidité persistantes sous le tablier, sans fissuration visible.",
15:"Corrosion avancée : Armatures longitudinales fortement oxydées, éclatement généralisé, perte de section estimée > 20 %.",
16:"Précontrainte (VIPP) : Fissure longitudinale fine (0,3 mm) parallèle aux gaines, sans trace de corrosion ni suintement.",
17:"Déformation évolutive : Flèche paraissant supérieure aux valeurs observées lors de la précédente inspection.",
18:"Appareil d’appui : Appareil déplacé latéralement de quelques millimètres, sans fissuration associée.",
19:"Béton altéré : Carbonatation mesurée atteignant les armatures, sans corrosion visible.",
20:"Désordre combiné : Infiltrations actives + épaufrures + corrosion visible sur about de poutre.",
21:"Fissure en âme : Fissure verticale isolée de 0,5 mm en âme de poutre, sans autre désordre associé.",
22:"Appui béton : Microfissuration diffuse en tête de pile sans éclatement ni corrosion.",
23:"Joint de chaussée : Joint dégradé avec perte partielle d’étanchéité, corrosion débutante sur corbeau d’appui.",
24:"Fissuration généralisée : Maillage de fissures fines (<0,2 mm) sur parement exposé au soleil.",
25:"Précontrainte critique : Fissure longitudinale > 0,8 mm + suintement brunâtre localisé.",
26:"Décollement en sous-face : Son creux étendu sur 1 m² en sous-face de dalle, sans chute de béton.",
27:"Effondrement partiel : Chute récente de fragments de béton sur zone circulée.",
28:"Torsion apparente : Rotation visible d’un appareil d’appui avec fissures radiales en about.",
29:"About fissuré : Fissures multiples > 0,5 mm + armatures visibles sur zone d’ancrage.",
30:"Cumul évolutif : Fissuration modérée connue + augmentation notable de la largeur lors du contrôle actuel."
}

correct_answers = {
1:"Grave à suivre",2:"Grave à suivre",3:"Grave à suivre",4:"Grave à suivre",
5:"Alerte",6:"Grave à suivre",7:"Alerte",8:"Grave à suivre",9:"Grave à suivre",10:"Alerte",
11:"Grave à suivre",12:"Grave à suivre",13:"Alerte",14:"Grave à suivre",15:"Alerte",
16:"Grave à suivre",17:"Alerte",18:"Grave à suivre",19:"Grave à suivre",20:"Alerte",
21:"Grave à suivre",22:"Grave à suivre",23:"Grave à suivre",24:"Grave à suivre",
25:"Alerte",26:"Grave à suivre",27:"Alerte",28:"Alerte",29:"Alerte",30:"Alerte"
}

# --- Session State ---
for key in ["page","question","answers","user"]:
    if key not in st.session_state:
        if key=="answers":
            st.session_state[key] = {}
        elif key=="question":
            st.session_state[key] = 1
        else:
            st.session_state[key] = None

# -------------------- PAGES --------------------

# --- PAGE HOME / MENU ---
if st.session_state.page == "home":
    st.title("Test Inspecteur VIPP")
    menu = st.sidebar.radio("Menu", ["Connexion","Créer un compte","Admin"])

    # --- CREER COMPTE ---
    if menu=="Créer un compte":
        st.subheader("Créer un compte")
        username = st.text_input("Identifiant", key="new_user")
        password = st.text_input("Mot de passe", type="password", key="new_pass")
        if st.button("Créer le compte"):
            if username and password:
                try:
                    c.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))
                    conn.commit()
                    st.success("Compte créé avec succès")
                except sqlite3.IntegrityError:
                    st.error("Identifiant déjà utilisé")
            else:
                st.error("Veuillez remplir tous les champs")

    # --- CONNEXION ---
    elif menu=="Connexion":
        st.subheader("Connexion")
        username = st.text_input("Identifiant", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
            user = c.fetchone()
            if user:
                st.session_state.user = username
                st.session_state.page = "accueil"
                st.experimental_rerun()
            else:
                st.error("Identifiants incorrects")

    # --- ADMIN ---
    elif menu=="Admin":
        st.subheader("Admin")
        admin_pass = st.text_input("Mot de passe admin", type="password")
        if admin_pass=="admin123":
            df = pd.read_sql_query("SELECT * FROM resultats", conn)
            st.dataframe(df)
        elif admin_pass:
            st.error("Mot de passe incorrect")

# --- PAGE ACCUEIL INSPECTEUR ---
elif st.session_state.page == "accueil":
    st.title(f"Bienvenue {st.session_state.user}")
    c.execute("SELECT tests FROM users WHERE username=?",(st.session_state.user,))
    tests = c.fetchone()[0]
    st.write(f"Nombre de tests effectués : {tests} / {MAX_TEST}")
    if tests >= MAX_TEST:
        st.warning("Vous avez atteint la limite de tests")
    else:
        if st.button("Lancer le test"):
            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.experimental_rerun()
    if st.button("Retour menu"):
        st.session_state.page = "home"
        st.experimental_rerun()

# --- PAGE QUIZ ---
elif st.session_state.page == "quiz":
    q = st.session_state.question
    st.title(f"Question {q} / 30")
    st.write(questions[q])
    answer = st.radio("Choisir la gravité", ["Grave à suivre","Alerte"], key=q)
    st.session_state.answers[q] = answer

    col1,col2 = st.columns(2)
    if q>1:
        if col1.button("Précédent"):
            st.session_state.question -=1
            st.experimental_rerun()
    if col2.button("Suivant"):
        if q<30:
            st.session_state.question +=1
        else:
            st.session_state.page = "result"
        st.experimental_rerun()

# --- PAGE RESULTAT ---
elif st.session_state.page == "result":
    st.title("Résultat du test")
    score = sum([1 for k,v in st.session_state.answers.items() if correct_answers[k]==v])
    st.subheader(f"Score : {score} / 30")
    if score>=24:
        st.success("Inspecteur apte à sortir en terrain")
    else:
        st.error("Inspecteur non apte – formation requise")

    c.execute("INSERT INTO resultats(username,score) VALUES (?,?)",(st.session_state.user,score))
    c.execute("UPDATE users SET tests=tests+1 WHERE username=?",(st.session_state.user,))
    conn.commit()

    if st.button("Retour accueil"):
        st.session_state.page="accueil"
        st.experimental_rerun()
