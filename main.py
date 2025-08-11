import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.utilities import SerpAPIWrapper
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain import hub
import subprocess
from urllib.parse import urlparse
from pydantic import HttpUrl
from langchain_core.tools import StructuredTool
from dotenv import load_dotenv
import os
import requests
import json
from typing import Optional

# Configuration de la page Streamlit
st.set_page_config(
    page_title="PronosAI",
    page_icon="😎",
    layout="wide"
)

# Chargement des variables d'environnement
load_dotenv()

def ping(url: HttpUrl, return_error: bool = False) -> str:
    """Effectue un ping vers une URL pour tester la connectivité réseau."""
    try:
        hostname = urlparse(str(url)).netloc
        if not hostname:
            return f"Erreur: URL invalide '{url}'. Veuillez inclure https:// ou http://"
        completed_process = subprocess.run(
            ["ping", "-c", "1", hostname],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = completed_process.stdout
        if return_error and completed_process.returncode != 0:
            return completed_process.stderr
        if completed_process.returncode == 0:
            return f"✅ Ping réussi pour {hostname}:\n{output}"
        else:
            return f"❌ Ping échoué pour {hostname}:\n{completed_process.stderr}"
    except Exception as e:
        return f"❌ Erreur lors du ping: {str(e)}"

def test_odds_api_connection(api_key: str) -> str:
    """Teste la connexion à l'API The Odds API avec la clé fournie."""
    if not api_key:
        return "❌ Pas de clé API fournie"
    try:
        url = "https://api.the-odds-api.com/v4/sports"
        params = {'apiKey': api_key}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"✅ API connectée ! {len(data)} sports disponibles. Quota restant: {response.headers.get('x-requests-remaining', 'N/A')}"
        elif response.status_code == 401:
            return "❌ Clé API invalide (401 Unauthorized)"
        elif response.status_code == 429:
            return "❌ Quota API dépassé (429 Too Many Requests)"
        else:
            return f"❌ Erreur API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Erreur de connexion: {str(e)}"

def get_sports_odds(
    sport_key: str,
    regions: str = "eu",
    markets: str = "h2h",
    api_key: Optional[str] = None
) -> str:
    """Récupère les cotes sportives pour un sport spécifique depuis The Odds API."""
    if not api_key:
        return "❌ Clé API Odds manquante. Ajoutez ODDS_API_KEY à votre fichier .env"
    try:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {
            'apiKey': api_key,
            'regions': regions,
            'markets': markets,
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return f"❌ Aucune cote trouvée pour le sport: {sport_key}"
            result = f"🏆 **Cotes pour {sport_key.upper()}**\n\n"
            for match in data[:5]:
                home_team = match['home_team']
                away_team = match['away_team']
                commence_time = match['commence_time']
                result += f"**{home_team} vs {away_team}**\n"
                result += f"📅 Date: {commence_time}\n"
                if match['bookmakers']:
                    bookmaker = match['bookmakers'][0]
                    if bookmaker['markets']:
                        outcomes = bookmaker['markets'][0]['outcomes']
                        result += f"💰 Cotes ({bookmaker['title']}):\n"
                        for outcome in outcomes:
                            result += f"  - {outcome['name']}: {outcome['price']}\n"
                result += "\n---\n\n"
            return result
        else:
            return f"❌ Erreur API Odds (Code {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ Erreur lors de la récupération des cotes: {str(e)}"

def get_available_sports(api_key: str = None) -> str:
    """Récupère la liste de tous les sports disponibles depuis The Odds API."""
    if not api_key:
        return "❌ Clé API Odds manquante"
    try:
        url = "https://api.the-odds-api.com/v4/sports"
        params = {'apiKey': api_key}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = "🏆 **Sports disponibles:**\n\n"
            soccer_sports = [s for s in data if 'soccer' in s['key']]
            other_sports = [s for s in data if 'soccer' not in s['key']]
            if soccer_sports:
                result += "⚽ **Football/Soccer:**\n"
                for sport in soccer_sports[:10]:
                    result += f"- {sport['title']} (`{sport['key']}`)\n"
                result += "\n"
            if other_sports:
                result += "🏈 **Autres sports:**\n"
                for sport in other_sports[:10]:
                    result += f"- {sport['title']} (`{sport['key']}`)\n"
            result += f"\n📊 Total: {len(data)} sports disponibles"
            return result
        else:
            return f"❌ Erreur API: {response.text}"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def initialize_llm_and_tools():
    """Initialise le modèle LLM et tous les outils disponibles pour l'agent."""
    openai_key = os.getenv("OPENAI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    spot_key = os.getenv("SPORTMONKS_API_KEY")
    
    if not openai_key:
        st.error("❌ OPENAI_API_KEY manquante dans le fichier .env")
        st.stop()
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        api_key=openai_key
    )
    
    ping_tool = StructuredTool.from_function(ping)
    search = SerpAPIWrapper(serpapi_api_key=serp_key) if serp_key else None

    def odds_wrapper(sport_key: str) -> str:
        """Récupère les cotes sportives pour un sport donné."""
        return get_sports_odds(sport_key, api_key=spot_key)

    def sports_list_wrapper(query: str = "") -> str:
        """Liste tous les sports disponibles avec leurs clés."""
        return get_available_sports(api_key=spot_key)

    def test_connection_wrapper(query: str = "") -> str:
        """Teste la connexion à l'API des cotes sportives."""
        return test_odds_api_connection(spot_key)

    tools = []
    if search:
        tools.append(Tool(
            name="search",
            func=search.run,
            description="Utile pour rechercher des informations actuelles sur internet"
        ))
    if spot_key:
        tools.append(Tool(
            name="test_odds_connection",
            func=test_connection_wrapper,
            description="Teste la connexion à l'API des cotes sportives"
        ))
        tools.append(Tool(
            name="get_sports_odds",
            func=odds_wrapper,
            description="Récupère les cotes sportives pour un sport donné. Utilisez les clés comme 'soccer_epl', etc."
        ))
        tools.append(Tool(
            name="list_available_sports",
            func=sports_list_wrapper,
            description="Liste tous les sports disponibles avec leurs clés"
        ))
    
    tools.append(ping_tool)
    return llm, tools, search is not None, spot_key is not None

# Interface Streamlit principale
def main():
    """Fonction principale qui lance l'interface Streamlit de PronosAI."""
    st.title("🤗TippS")
    st.markdown("---")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Vérification des clés API
        openai_key = os.getenv("OPENAI_API_KEY")
        serp_key = os.getenv("SERPAPI_KEY")
        odds_key = os.getenv("ODDS_API_KEY")
        
        st.subheader("🔑 Statut des APIs")
        
        # Statut OpenAI
        if openai_key:
            st.success("✅ OpenAI API configurée")
        else:
            st.error("❌ OpenAI API manquante")
            
        # Statut SerpAPI
        if serp_key:
            st.success("✅ SerpAPI configurée")
        else:
            st.warning("⚠️ SerpAPI non configurée (recherche web désactivée)")
            
        # Statut Odds API
        if odds_key:
            st.success("✅ Odds API configurée")
            if st.button("🔍 Tester la connexion Odds API"):
                with st.spinner("Test en cours..."):
                    result = test_odds_api_connection(odds_key)
                    if "✅" in result:
                        st.success(result)
                    else:
                        st.error(result)
        else:
            st.error("❌ Odds API manquante")
            
        st.markdown("---")
        
        # Options d'affichage
        st.subheader("📊 Options")
        show_available_sports = st.checkbox("Afficher les sports disponibles", value=False)
        
        if show_available_sports and odds_key:
            with st.expander("🏆 Sports disponibles"):
                sports_info = get_available_sports(odds_key)
                st.markdown(sports_info)

    # Interface principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat avec PronosAI")
        
        # Initialisation de l'historique de conversation
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        # Initialisation de l'agent
        if 'agent_executor' not in st.session_state:
            try:
                llm, tools, has_search, has_odds = initialize_llm_and_tools()
                
                # Création du prompt personnalisé
                prompt_text = """Tu es PronosAI, un assistant expert en pronostics sportifs.

Tu peux utiliser les outils suivants :
- search : pour rechercher des informations actuelles sur internet
- get_sports_odds : pour récupérer les cotes sportives
- list_available_sports : pour lister les sports disponibles
- test_odds_connection : pour tester la connexion API
- ping : pour tester la connectivité

Contexte : Tu aides les utilisateurs à analyser les matchs sportifs et à fournir des pronostics éclairés.

Consignes :
1. Utilise les cotes en temps réel quand disponibles
2. Recherche des informations récentes sur les équipes/joueurs
3. Analyse les statistiques et les tendances
4. Fournis des pronostics argumentés mais rappelle toujours les risques
5. Sois précis et informatif

Messages précédents:
{chat_history}

Question actuelle: {input}

Réflexion: {agent_scratchpad}"""

                # Utilisation du prompt par défaut de LangChain pour les agents OpenAI
                try:
                    # Essayer d'utiliser le prompt hub
                    prompt = hub.pull("hwchase17/openai-functions-agent")
                except:
                    # Si le hub ne fonctionne pas, utiliser un prompt simple
                    prompt = None

                # Création de l'agent
                agent = create_openai_functions_agent(llm, tools, prompt)
                st.session_state.agent_executor = AgentExecutor(
                    agent=agent, 
                    tools=tools, 
                    verbose=True,
                    max_iterations=3,
                    handle_parsing_errors=True
                )
                
                # Message de bienvenue
                welcome_msg = """🎯 **Bienvenue sur PronosAI !**

Je suis votre assistant IA spécialisé dans les pronostics sportifs. Je peux vous aider à :

• 📊 Analyser les cotes sportives en temps réel
• 🔍 Rechercher des informations sur les équipes et joueurs
• 📈 Fournir des analyses statistiques
• 🎯 Proposer des pronostics argumentés

**Exemples de questions :**
- "Quelles sont les cotes pour la Premier League ce week-end ?"
- "Analyse le match Barcelona vs Real Madrid"
- "Quels sont les sports disponibles ?"

⚠️ **Rappel important :** Les paris sportifs comportent des risques. Jouez de manière responsable !"""

                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'initialisation : {str(e)}")
                st.stop()
        
        # Affichage de l'historique des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input utilisateur
        if prompt := st.chat_input("Posez votre question sur les pronostics sportifs..."):
            # Affichage du message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Génération de la réponse
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyse en cours..."):
                    try:
                        # Construction de l'historique pour le contexte
                        chat_history = ""
                        for msg in st.session_state.messages[-10:]:  # Derniers 10 messages
                            role = "Humain" if msg["role"] == "user" else "Assistant"
                            chat_history += f"{role}: {msg['content']}\n"
                        
                        # Exécution de l'agent avec le contexte système
                        system_message = """Tu es PronosAI, un assistant expert en pronostics sportifs. 

Utilise les outils disponibles pour :
- Récupérer les cotes sportives en temps réel
- Rechercher des informations actuelles 
- Analyser les matchs et fournir des pronostics argumentés

Rappelle toujours les risques liés aux paris sportifs."""

                        # Préparation du contexte complet
                        full_prompt = f"{system_message}\n\nHistorique récent:\n{chat_history}\n\nQuestion: {prompt}"
                        
                        response = st.session_state.agent_executor.invoke({
                            "input": full_prompt
                        })
                        
                        assistant_response = response["output"]
                        st.markdown(assistant_response)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                        
                    except Exception as e:
                        error_msg = f"❌ Erreur lors du traitement : {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    with col2:
        st.header("📋 Raccourcis")
        
        # Boutons de raccourcis
        if st.button("🏆 Sports disponibles"):
            st.session_state.messages.append({"role": "user", "content": "Quels sont les sports disponibles ?"})
            st.rerun()
            
        if st.button("⚽ Cotes Premier League"):
            st.session_state.messages.append({"role": "user", "content": "Montre-moi les cotes de la Premier League"})
            st.rerun()
            
        if st.button("🏈 Cotes NFL"):
            st.session_state.messages.append({"role": "user", "content": "Quelles sont les cotes NFL actuelles ?"})
            st.rerun()
            
        if st.button("🔄 Nouvelle conversation"):
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        
        # Informations utiles
        st.subheader("ℹ️ Informations")
        st.info("""
        **Codes sports populaires :**
        • `soccer_epl` - Premier League
        • `americanfootball_nfl` - NFL
        • `basketball_nba` - NBA
        • `soccer_spain_la_liga` - La Liga
        • `soccer_italy_serie_a` - Serie A
        """)
        
        # Avertissement
        st.warning("⚠️ **Avertissement :** Les pronostics sont fournis à titre informatif. Pariez de manière responsable !")

if __name__ == "__main__":
    main()
