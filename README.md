# 🐈‍⬛ PronosAI - Assistant IA pour Pronostics Sportifs

PronosAI est une application Streamlit qui combine l'intelligence artificielle de GPT-4 avec des données sportives en temps réel pour fournir des analyses et pronostics éclairés, elle etait disponible sur https://pronosai.streamlit.app/ .

## ✨ Fonctionnalités

### 🎯 Core Features

- **Chat IA interactif** avec gpt-4o spécialisé dans les pronostics sportifs
- **Cotes sportives en temps réel** via The Odds API
- **Recherche web** d'informations actuelles sur les équipes et joueurs
- **Analyses argumentées** basées sur les données disponibles
- **Interface intuitive** avec raccourcis et historique de conversation

### 🛠️ Outils disponibles

- **get_sports_odds** : Récupération des cotes pour un sport spécifique
- **list_available_sports** : Liste de tous les sports disponibles
- **search** : Recherche web d'informations actuelles
- **ping** : Test de connectivité réseau
- **test_odds_connection** : Vérification de la connexion API

## 🚀 Installation

### Prérequis

- Python 3.8+
- Compte OpenAI avec clé API
- Clé API The Odds API (optionnel mais recommandé)
- Clé SerpAPI (optionnel pour la recherche web)

### 1. Cloner le projet

```bash
git clone <repository-url>
cd pronosai
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Obligatoire
OPENAI_API_KEY=sk-your-openai-key-here

# Optionnel mais recommandé
ODDS_API_KEY=your-odds-api-key-here

# Optionnel (pour la recherche web)
SERPAPI_KEY=your-serpapi-key-here
```

### 4. Créer le fichier requirements.txt

```txt
streamlit
langchain
langchain-openai
langchain-community
python-dotenv
requests
pydantic
```

## 🎮 Utilisation

### Lancer l'application

```bash
streamlit run main.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Exemples d'utilisation

#### 📊 Consulter les cotes sportives

```
"Quelles sont les cotes pour la Premier League ce week-end ?"
"Montre-moi les cotes NBA actuelles"
"Cotes pour le match PSG vs Marseille"
```

#### 🔍 Analyses et pronostics

```
"Analyse le match Barcelona vs Real Madrid"
"Qui a le plus de chances de gagner entre Liverpool et Manchester City ?"
"Donne-moi ton pronostic pour le match de ce soir"
```

#### ⚙️ Outils techniques

```
"Quels sont les sports disponibles ?"
"Teste la connexion à l'API des cotes"
"Ping google.com"
```

## 📋 APIs et Services

### 🔑 The Odds API

- **URL** : https://the-odds-api.com/
- **Usage** : Récupération des cotes sportives en temps réel
- **Sports supportés** : Football, Basketball, Tennis, etc.
- **Quota** : Varie selon le plan choisi

### 🔍 SerpAPI (Optionnel)

- **URL** : https://serpapi.com/
- **Usage** : Recherche web d'informations actuelles
- **Quota** : 100 requêtes/mois (plan gratuit)

### 🧠 OpenAI API

- **Modèle** : GPT-4
- **Usage** : Intelligence artificielle pour l'analyse et les pronostics
- **Coût** : Facturation à l'usage

## 🏗️ Architecture

```
PronosAI/
├── main.py
├── requirements.txt                  # Application principale Streamlit
├── .env                # Variables d'environnement (à créer)     # Dépendances Python
└── README.md             # Documentation
```

### 🔧 Composants principaux

#### Fonctions API

- `get_sports_odds()` : Récupère les cotes pour un sport
- `get_available_sports()` : Liste les sports disponibles
- `test_odds_api_connection()` : Test de connexion API

#### Outils utilitaires

- `ping()` : Test de connectivité réseau
- `initialize_llm_and_tools()` : Initialisation de l'agent IA

#### Interface Streamlit

- **Sidebar** : Configuration et statut des APIs
- **Chat principal** : Interface de conversation
- **Raccourcis** : Boutons pour requêtes courantes

## ⚠️ Limitations et avertissements

### 🚫 Responsabilité

- **Les pronostics sont fournis à titre informatif uniquement**
- **Pariez de manière responsable**
- **Les paris sportifs comportent des risques financiers**

### 🔒 Quotas API

- The Odds API : Nombre de requêtes limité selon le plan
- OpenAI API : Facturation à l'usage
- SerpAPI : 100 requêtes/mois (plan gratuit)

### 🌐 Connectivité

- Nécessite une connexion internet stable
- Certains outils peuvent ne pas fonctionner sans les APIs correspondantes

## 🛠️ Développement

### Structure du code

```python
# Fonctions API
def get_sports_odds(sport_key, regions="eu", markets="h2h", api_key=None)
def get_available_sports(api_key=None)
def test_odds_api_connection(api_key)

# Outils LangChain
def initialize_llm_and_tools()

# Interface Streamlit
def main()
```

### Ajout de nouveaux sports

Pour ajouter de nouveaux sports, consultez la liste des sports disponibles via The Odds API et utilisez les clés correspondantes.

### Personnalisation du prompt

Le comportement de l'IA peut être modifié en ajustant le `system_message` dans la fonction `main()`.

## 📝 Codes sports populaires

| Sport             | Code                      | Description          |
| ----------------- | ------------------------- | -------------------- |
| ⚽ Premier League | `soccer_epl`              | Championnat anglais  |
| 🏈 NFL            | `americanfootball_nfl`    | Football américain   |
| 🏀 NBA            | `basketball_nba`          | Basketball américain |
| ⚽ La Liga        | `soccer_spain_la_liga`    | Championnat espagnol |
| ⚽ Serie A        | `soccer_italy_serie_a`    | Championnat italien  |
| ⚽ Ligue 1        | `soccer_france_ligue_one` | Championnat français |
| 🎾 ATP            | `tennis_atp_*`            | Tennis professionnel |

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Optimiser le code

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

En cas de problème :

1. Vérifiez que toutes les clés API sont correctement configurées
2. Consultez les logs d'erreur dans la console
3. Vérifiez votre connexion internet
4. Assurez-vous que les quotas API ne sont pas dépassés

---

**⚠️ Disclaimer** : PronosAI est un outil d'aide à la décision. Les pronostics ne garantissent aucun résultat. Pariez de manière responsable et selon vos moyens.
