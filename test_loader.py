from bot import data_loader

# Load all your JSON test matches
df = data_loader.load_data("data/test_matches")

print("✅ Total deliveries loaded:", len(df))
print("✅ Unique batters:", df["batter"].nunique())
print("✅ Unique bowlers:", df["bowler"].nunique())
print("✅ Unique venues:", df["venue"].nunique())

print("\n🔹 Sample rows:")
print(df.head(10))
