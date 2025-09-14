from bot import data_loader

def answer_query(parsed: dict) -> str:
    player = parsed.get("player")
    bowler = parsed.get("bowler")
    venue = parsed.get("venue")
    metric = parsed.get("metric")

    if not player:
        return "Sorry, I couldn’t recognize the player."

    # Fetch only relevant data
    player_df = data_loader.fetch_player_data(player, bowler, venue)

    if player_df.empty:
        details = []
        if bowler: details.append(f"against {bowler}")
        if venue: details.append(f"at {venue}")
        return f"No data available for {player} {' '.join(details)}."

    runs = player_df["runs_batter"].sum()
    dismissals = player_df["dismissal"].sum()
    balls = len(player_df)

    if metric == "average":
        if dismissals == 0:
            return f"{player} hasn’t been dismissed yet; average cannot be calculated."
        avg = runs / dismissals
        return f"{player} scored {runs} runs and was dismissed {dismissals} times, giving an average of {avg:.2f}."
    elif metric == "strike_rate":
        sr = (runs / balls) * 100 if balls > 0 else 0
        return f"{player} scored {runs} runs in {balls} balls, strike rate {sr:.2f}."
    elif metric == "dismissals":
        return f"{player} was dismissed {dismissals} times."
    elif metric == "runs":
        text = f"{player} scored {runs} runs"
        if venue: text += f" at {venue}"
        if bowler: text += f" against {bowler}"
        return text + "."
    elif metric == "wickets" and bowler:
        wkts = player_df["dismissal"].sum()
        return f"{bowler} dismissed {player} {wkts} times."
    else:
        return f"I found {len(player_df)} deliveries for {player}."
