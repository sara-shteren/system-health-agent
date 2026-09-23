"""Funny waiting messages - no LLM needed, just random selection."""

import random

WAITING_MESSAGES = [
    # Cooking & Baking
    "🍳 Frying some bytes...",
    "🥧 Baking your response...",
    "🍝 Cooking up something good...",
    "🧁 Adding sprinkles to your answer...",
    "🍕 Tossing the data dough...",
    "🥗 Mixing the ingredients...",
    "☕ Brewing your results...",
    "🍪 Cookies are in the oven...",
    
    # Tech humor
    "🔧 Adjusting the flux capacitor...",
    "💾 Defragmenting the cloud...",
    "🧮 Counting ones and zeros...",
    "🔌 Plugging in the hamsters...",
    "⚡ Charging the quantum batteries...",
    "🛠️ Tightening the loose bits...",
    "📡 Pinging the mothership...",
    "🧲 Aligning the magnetic fields...",
    
    # Health theme (fitting for System Health Agent)
    "🩺 Taking the system's pulse...",
    "💊 Prescribing some diagnostics...",
    "🏥 The doctor is analyzing...",
    "🌡️ Checking the server's temperature...",
    "❤️ Listening to the heartbeat...",
    "🧬 Sequencing the data DNA...",
    
    # Office humor
    "📋 Filling out the TPS reports...",
    "📊 Making the charts look pretty...",
    "📝 Writing very important notes...",
    "🗂️ Organizing the filing cabinet...",
    "☕ Refilling the coffee machine...",
    
    # Space & Science
    "🚀 Launching the calculation rockets...",
    "🌙 Consulting the moon phase...",
    "⭐ Aligning the stars...",
    "🔭 Scanning the data horizon...",
    "🛸 Downloading from alien servers...",
    
    # Random fun
    "🎲 Rolling the dice of knowledge...",
    "🎯 Aiming for the right answer...",
    "🎨 Painting the pixels...",
    "🎭 Rehearsing the response...",
    "🎪 Juggling the variables...",
    "🧙 Casting a processing spell...",
    "🦄 Summoning the unicorns...",
    "🐙 Consulting the octopus oracle...",
]


def get_random_waiting_message() -> str:
    """Returns a random funny waiting message."""
    return random.choice(WAITING_MESSAGES)


def get_waiting_messages_sequence(count: int = 3) -> list[str]:
    """Returns a sequence of different waiting messages."""
    return random.sample(WAITING_MESSAGES, min(count, len(WAITING_MESSAGES)))
