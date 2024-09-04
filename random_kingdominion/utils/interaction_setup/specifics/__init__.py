from .cost_change import add_all_cost_change_interactions
from .end_buy import add_all_end_buy_interactions
from .events import add_all_event_interactions
from .individual_cards import add_all_individual_card_interactions
from .on_clean_up import add_all_on_clean_up_interactions
from .on_discard import add_all_on_discard_interactions
from .on_gain import add_all_on_gain_interactions
from .on_start_of_turn import add_all_on_start_of_turn_interactions
from .projects import add_all_project_interactions
from .prophecies import add_all_prophecy_interactions
from .traits import add_all_trait_interactions
from .victory_card_plays import add_all_victory_card_play_interactions
from .ways import add_all_way_interactions
from .allies import add_all_allies_interactions

__all__ = [
    "add_all_allies_interactions",
    "add_all_on_gain_interactions",
    "add_all_cost_change_interactions",
    "add_all_way_interactions",
    "add_all_prophecy_interactions",
    "add_all_trait_interactions",
    "add_all_end_buy_interactions",
    "add_all_victory_card_play_interactions",
    "add_all_individual_card_interactions",
    "add_all_on_discard_interactions",
    "add_all_project_interactions",
    "add_all_event_interactions",
    "add_all_on_start_of_turn_interactions",
    "add_all_on_clean_up_interactions",
]
