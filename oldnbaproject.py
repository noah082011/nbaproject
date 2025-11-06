#import pandas as pd
#pd.set_option('display.max_columns', None)
#from nba_api.stats.static import players
#from nba_api.stats.endpoints import playercareerstats
#player_dict = players.get_players()
#player_dict = players.get_active_players()
#print("NBA API seems to be working. Found players:", len(player_dict))
#print(player_dict)
#career_df = career.get_dict()[0]
#print(career_df.head())

'''
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd


mj_list = players.find_players_by_full_name('Michael Jordan')
if mj_list:
    player_id = mj_list[0]['id']
else:
    print("Could not find the player's ID. Check the spelling.")
    player_id = None 
if player_id:

    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career.get_data_frames()[0]


lbj_list = players.find_players_by_full_name('Lebron James')
if lbj_list:
    player_id = lbj_list[0]['id']
else:
    print("Could not find player ID. Spell the players name right")
    player_id = None
if player_id:
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df1 = career.get_data_frames()[0]


x = input("Choose Lebron James or Michael Jordan ")
x = x.upper()
if x == "LEBRON JAMES":
    print(career_df1)
if x == "MICHAEL JORDAN":
    print(career_df)

def main():
    input("Choose a nba player to see the stats for")
    '''

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import time

# --- 1. Utility Functions ---

def get_player_id(player_name):
    """Searches for a player's ID by name."""
    try:
        nba_players = players.get_players()
        # Case-insensitive partial match for robust searching
        matching_players = [
            player for player in nba_players 
            if player_name.lower() in player['full_name'].lower() and player['is_active']
        ]

        if not matching_players:
            print(f"Player '{player_name}' not found or is not currently active.")
            return None
        
        # Simple selection for multiple matches (e.g., "Gary Payton")
        if len(matching_players) > 1:
            print("\nMultiple players found. Please select one:")
            for i, p in enumerate(matching_players):
                print(f"  {i+1}. {p['full_name']} (ID: {p['id']})")
            
            selection = input("Enter the number of the player: ")
            try:
                selected_index = int(selection) - 1
                if 0 <= selected_index < len(matching_players):
                    return matching_players[selected_index]['id']
                else:
                    print("Invalid selection.")
                    return None
            except ValueError:
                print("Invalid input.")
                return None
        
        return matching_players[0]['id']

    except Exception as e:
        print(f"An error occurred during player lookup: {e}")
        return None

def fetch_and_display_stats(player_id, player_name):
    """Fetches and formats the current season stats."""
    
    # We use PlayerCareerStats to get season averages
    # The API call is being made here.
    try:
        # NOTE: Adding a short delay to respect the NBA API's rate limits
        time.sleep(0.5) 
        
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        
        # The first DataFrame contains the Career Regular Season Stats
        career_df = career.get_data_frames()[0]

    except Exception as e:
        print(f"Failed to fetch stats from the API. Error: {e}")
        return

    # --- Data Processing ---
    
    # Filter for the most recent (current) season, which is usually the last row
    current_season_stats = career_df.iloc[-1]
    
    # Ensure stats are in floating-point format for calculation
    stats = current_season_stats.to_dict()

    # Calculate custom "Stocks" stat: Steals (STL) + Blocks (BLK)
    stocks = stats.get('STL', 0) + stats.get('BLK', 0)
    
    # --- Output Formatting ---
    
    print(f"\n{stats.get('PLAYER_NAME', player_name).upper()}")
    print("-" * 30)

    # Dictionary to map API column names to user-friendly names
    STAT_MAPPING = {
        'PTS': 'Points',
        'AST': 'Assists',
        'REB': 'Rebounds',
        'STL': 'Steals',
        'BLK': 'Blocks',
        'TOV': 'Turnovers',
        'PF': 'Fouls',
        'MIN': 'Minutes Played',
        'FG_PCT': 'FG%',
        'FG3_PCT': '3P%',
        # Advanced stats from the same table (often included)
        'GP': 'Games Played',
    }

    # Basic Stats
    for api_key, friendly_name in STAT_MAPPING.items():
        value = stats.get(api_key, 'N/A')
        
        # Format percentages
        if 'PCT' in api_key and isinstance(value, (int, float)):
            formatted_value = f"{value * 100:.1f}%"
        # Format Minutes Played
        elif api_key == 'MIN':
            formatted_value = f"{float(value):.1f}"
        # Format other stats
        elif isinstance(value, (int, float)):
            formatted_value = f"{value:.1f}".rstrip('0').rstrip('.')
        else:
            formatted_value = value
            
        print(f"{friendly_name.ljust(15)}: {formatted_value}")
    
    # Custom Stats
    print(f"{'Stocks (Stl + Blk)'.ljust(15)}: {stocks:.1f}".rstrip('0').rstrip('.'))
    print("-" * 30)
    print("Advanced Stats (Available in a different API endpoint):")
    # You would use a different endpoint (like PlayerDashPtShotDefend) here 
    # to get true advanced stats (like PIE, Net Rating, etc.)
    print(" ...")


# --- 2. Main Application Loop ---

def main():
    """Runs the main CLI interface for the user."""
    print("🏀 NBA Player Stats Lookup Tool 🏀")
    
    while True:
        player_name = input("\nEnter a player's name (or type 'quit' to exit): ").strip()
        
        if player_name.lower() == 'quit':
            break
        if not player_name:
            continue
            
        print(f"Searching for stats for: {player_name}...")
        
        player_id = get_player_id(player_name)
        
        if player_id:
            fetch_and_display_stats(player_id, player_name)

    print("\nThank you for using the NBA Stats Tool!")

if __name__ == "__main__":
    # Ensure pandas display is configured for cleaner output (optional)
    pd.set_option('display.max_columns', None)
    main()
