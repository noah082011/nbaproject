from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import time

# --- 1. Utility Functions ---

def get_player_id(player_name):
    """Searches for a player's ID by name."""
    try:
        nba_players = players.get_players()
        matching_players = [
            player for player in nba_players 
            if player_name.lower() in player['full_name'].lower()
        ]

        if not matching_players:
            print(f"Player '{player_name}' not found or is not currently active.")
            return None
        
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