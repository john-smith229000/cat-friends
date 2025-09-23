# game/entities/components/cat_chat.py
import random

# game/entities/components/cat_chat.py
import random

class CatChat:
    def __init__(self, cat_name="kitty"):
        self.cat_name = cat_name
        
        # --- NEW: Movie and phrase lists ---
        self.movies = ["Call Me Chihiro", "Love Untangled", "Materialists", "Monster", "Y Tu Mamá También", "One Million Yen Girl", "True Beauty", "Whisper of the Heart", "Perfect Days", "Us and Them", "Lost in Translation", "Castle in the Sky", "One Day, You Will Reach the Sea", "Haru", "Barbie", "Yi Yi", "The Handmaiden", "All About Lily Chou-Chou", "I'm a Cyborg, But That's OK", "Last Life in the Universe", "Howl's Moving Castle", "Paprika", "Burning", "Drive My Car", "Wheel of Fortune and Fantasy", "Taipei Story", "A Brighter Summer Day", "Chungking Express", "Love & Pop", "Ritual", "Tokyo Godfathers", "Norwegian Wood", "Asako I & II", "Perfect Blue", "Love Letter"]

        self.movie_phrases = [
            "I love watching it on a warm lap!",
            "It's the best... next to naps, of course.",
            "Mrow! It's purr-fect.",
            "I could watch it all day!",
            "It always makes my tail twitch."
        ]
        
        # Define the rules for conversation
        self.chat_rules = {
            ("hello", "hi", "hey"): [
                "Mrow.",
                "Purrrr...",
                f"{self.cat_name} looks at you.",
            ],
            ("food", "hungry", "eat", "fish"): [
                "Mrrrow? *looks at the food bowl*",
                "Meow!",
            ],
            ("pet", "cuddle", "pat", "love"): [
                "*purrs happily*",
                f"{self.cat_name} leans into your hand.",
                "Prrrrrt.",
            ],
            ("play", "toy", "fun"): [
                f"{self.cat_name}'s eyes widen.",
                "*pounces at a dust bunny*",
            ],
            ("who are you", "name"): [
                f"Meow, I'm {self.cat_name}!",
                "Mrow?"
            ]
        }
        # A default response if no keywords are found
        self.default_responses = [
            f"{self.cat_name} blinks slowly.",
            f"{self.cat_name} looks at you curiously.",
            "*tilts head*",
            "..."
        ]

    def get_response(self, player_input):
        """Finds a response based on keywords in the player's input."""
        player_input = player_input.lower().strip()
        
        if not player_input:
            return random.choice(self.default_responses)

        # --- NEW: Special check for favorite movie ---
        has_movie_word = "movie" in player_input or "movies" in player_input or "film" in player_input or 'films' in player_input
        has_favorite_word = "favorite" in player_input or "favorites" in player_input or "like" in player_input or 'fav' in player_input

        if has_movie_word and has_favorite_word:
            movie = random.choice(self.movies)
            phrase = random.choice(self.movie_phrases)
            return f"{movie}! {phrase}"

        # Original keyword check
        for keywords, responses in self.chat_rules.items():
            for keyword in keywords:
                if keyword in player_input:
                    return random.choice(responses)
        
        return random.choice(self.default_responses)