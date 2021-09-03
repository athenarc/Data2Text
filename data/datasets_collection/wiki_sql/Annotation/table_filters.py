def is_sport(table) -> bool:
    SPORTS_WORDS = ["game", "manufacturer", "position", "winner", "driver", "captain",
                    "player", "pick", "round", "tournament", "club", "result", "crowd",
                    "goals", "points", "lane", "score", "opponent", "team", "mascot"]
    col_names_concatenated = " ".join(table['header']).lower()
    return any(x in col_names_concatenated for x in SPORTS_WORDS)


def is_movie(table) -> bool:
    MOVIE_WORDS = ["written by", "directed by"]
    col_names_concatenated = " ".join(table['header']).lower()
    return any(x in col_names_concatenated for x in MOVIE_WORDS)
