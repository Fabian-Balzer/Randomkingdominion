from random_kingdominion import CustomConfigParser
from random_kingdominion.constants import EXPANSION_LIST, RENEWED_EXPANSIONS
from random_kingdominion.utils import get_expansion_icon_path, override

from .expansion_number_slider import ExpansionNumSlider
from .group_checkbox_button_container import GroupCheckboxButtonContainer


class ExpansionGroupWidget(GroupCheckboxButtonContainer):
    """Container for the expansion group."""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        names = [exp for exp in EXPANSION_LIST if exp not in RENEWED_EXPANSIONS]
        tooltips = [f"Randomize cards from the {exp} expansion." for exp in names]
        super().__init__(names, "Expansions", tooltips, initially_collapsed=False)
        self.max_expansion_slider = ExpansionNumSlider(config)
        self.content_layout.addWidget(self.max_expansion_slider)

        self._set_initial_values()
        self.connect_to_change_func(self.update_config_for_expansions)

    def update_config_for_expansions(self):
        """Reads out the currently selected expansions and saves them.
        Also changes the selection.
        """
        selected_exps = self.get_names_of_selected()
        self.config.set_expansions(selected_exps)

    def _set_initial_values(self):
        for exp in self.config.get_expansions(add_renewed_bases=False):
            self.widget_dict[exp].setChecked(True)
        self.set_toggle_button_text()

    @override
    def get_icon_path(self, name: str) -> str:
        """Returns the image path for the given expansion icon."""
        return get_expansion_icon_path(name)
