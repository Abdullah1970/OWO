# Emoji mappings for CMD compatibility
EMOJIS = {
    # Status emojis
    '🚀': '[ROCKET]',
    '✅': '[CHECK]',
    '❌': '[X]',
    '⚠️': '[WARNING]',
    '🔍': '[SEARCH]',
    '📝': '[MEMO]',
    '📋': '[CLIPBOARD]',
    '🛑': '[STOP]',
    '⏰': '[CLOCK]',
    '🎯': '[TARGET]',
    
    # Bot feature emojis
    '🛡️': '[SHIELD]',
    '🔒': '[LOCK]',
    '💎': '[GEM]',
    '🦄': '[UNICORN]',
    '💰': '[MONEY]',
    '🔄': '[REFRESH]',
    '⚔️': '[SWORD]',
    '🙏': '[PRAY]',
    '😈': '[DEVIL]',
    '🪙': '[COIN]',
    '📅': '[CALENDAR]',
    '🗳️': '[VOTE]',
    '🏹': '[BOW]',
    '⭐': '[STAR]',
    '🔧': '[WRENCH]',
    
    # Statistics emojis
    '📊': '[CHART]',
    '📈': '[GRAPH]',
    '⏱️': '[TIMER]',
    '💡': '[BULB]',
    '✨': '[SPARKLES]',
    '🍀': '[CLOVER]',
    '🦁': '[LION]',
    'ℹ️': '[INFO]',
    '🔹': '[DIAMOND]',
    '⏳': '[HOURGLASS]',
    
    # Activity emojis
    '🎰': '[SLOT]',
    '🎲': '[DICE]',
    '🎮': '[GAME]',
    '🏆': '[TROPHY]',
    '🎊': '[CONFETTI]',
    '🎉': '[PARTY]',
    
    # Animal emojis
    '🐉': '[DRAGON]',
    '🦅': '[EAGLE]',
    '🐺': '[WOLF]',
    '🦊': '[FOX]',
    '🐼': '[PANDA]',
    '🐨': '[KOALA]',
    '🐧': '[PENGUIN]',
    '🦥': '[SLOTH]',
}

def replace_emojis(text):
    """Replace emojis in text with CMD-compatible alternatives"""
    for emoji, replacement in EMOJIS.items():
        text = text.replace(emoji, replacement)
    return text
