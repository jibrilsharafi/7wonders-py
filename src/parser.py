class EffectType(Enum):
    RESOURCE_CHOICE = auto()  # e.g., "+resource{W/S/O/B}"
    TRADE_DISCOUNT = auto()   # e.g., "trade-${GLP} <>"
    VICTORY_POINTS = auto()   # e.g., "VP3"
    COINS = auto()           # e.g., "C3"
    MILITARY = auto()        # e.g., "M2"
    SCIENCE = auto()         # e.g., "S_GEAR"

class EffectParser:
    @staticmethod
    def parse_effect(effect_str: str) -> Dict[EffectType, any]:
        """Parse effect string into structured data"""
        pass

    @staticmethod
    def apply_effect(effect: Dict[EffectType, any], player: Player) -> None:
        """Apply parsed effect to player"""
        pass