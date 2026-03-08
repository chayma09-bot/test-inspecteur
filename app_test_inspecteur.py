import streamlit as st
import sqlite3
import pandas as pd
import openai

# --- Clé API OpenAI ---
openai.api_key = "VOTRE_CLE_API"

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

# --- Fonction évaluation IA ---
def evaluer_question(question_text, reponse_inspecteur):
    prompt = f"""
    Tu es un expert en inspection des ouvrages.
    Question: {question_text}
    Réponse de l'inspecteur: {reponse_inspecteur}

    Évalue si la gravité est correcte.
    Renvoie uniquement "Correct" si la réponse est cohérente ou "Incorrect" sinon.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        verdict = response['choices'][0]['message']['content'].strip()
        if verdict not in ["Correct","Incorrect"]:
            verdict = "Incorrect"
        return verdict
    except Exception as e:
        st.error(f"Erreur IA: {e}")
        return "Incorrect"

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
                c.execute("INSERT INTO users(username,password) VALUES (?,?)",(new_user,new_password))
                conn.commit()
                st.success("Compte créé avec succès")

    # ---- Connexion ----
    elif menu == "Connexion":
        st.subheader("Connexion inspecteur")
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
            user = c.fetchone()
            if user:
                st.session_state.user = username
                st.session_state.page = "accueil"
                st.experimental_rerun()
            else:
                st.error("Identifiants incorrects")

    # ---- Admin ----
    elif menu == "Admin":
        st.subheader("Admin - Tableau des résultats")
        password = st.text_input("Mot de passe admin", type="password")
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
        if st.button("Lancer le test"):
            st.session_state.page = "quiz"
            st.session_state.question = 1
            st.session_state.answers = {}
            st.experimental_rerun()

    if st.button("Déconnexion"):
        st.session_state.page = "home"
        st.experimental_rerun()

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
        ["Grave à suivre","Alerte"],
        index=0 if st.session_state.answers[q] is None else ["Grave à suivre","Alerte"].index(st.session_state.answers[q])
    )

    col1, col2 = st.columns(2)
    if col1.button("Précédent") and q > 1:
        st.session_state.question -= 1
        st.experimental_rerun()

    if col2.button("Suivant"):
        if q < 30:
            st.session_state.question += 1
        else:
            st.session_state.page = "result"
        st.experimental_rerun()

# --- PAGE RESULTAT ---
elif st.session_state.page == "result":

    st.title("Résultat du test")

    score = 0
    with st.spinner("Évaluation IA en cours..."):
        for q, ans in st.session_state.answers.items():
            question_text = questions[q]
            verdict = evaluer_question(question_text, ans)
            if verdict == "Correct":
                score += 1

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

    if st.button("Retour accueil"):
        st.session_state.page = "accueil"
        st.experimental_rerun()
