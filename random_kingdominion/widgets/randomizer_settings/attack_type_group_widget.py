

from random_kingdominion import CustomConfigParser
from random_kingdominion.constants import ATTACK_TYPE_LIST, PATH_ASSETS
from random_kingdominion.utils import override

from .group_checkbox_button_container import GroupCheckboxButtonContainer


class AttackTypeGroupWidget(GroupCheckboxButtonContainer):
    """Container for selecting the AttackTypes"""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        tooltips = [
            f"Toggle exclusion of the {type_} attack type."
            for type_ in ATTACK_TYPE_LIST
        ]
        super().__init__(ATTACK_TYPE_LIST, "Allowed attack types", tooltips)

        self._set_initial_values()
        self.connect_to_change_func(self.update_config_for_attack_types)

    def update_config_for_attack_types(self):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        selected_types = self.get_names_of_selected()
        self.config.setlist("Specialization", "attack_types", selected_types)

    def _set_initial_values(self):
        for exp in self.config.getlist("Specialization", "attack_types"):
            self.widget_dict[exp].setChecked(True)
        self.set_toggle_button_text()

    @override
    def get_icon_path(self, name: str) -> str:
        """Returns the image path for the given attack icon."""
        fpath = PATH_ASSETS.joinpath(f"icons/attack_types/{name}.png")
        return str(fpath)
