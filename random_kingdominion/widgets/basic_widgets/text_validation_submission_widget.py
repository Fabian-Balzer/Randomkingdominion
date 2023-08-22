from typing import Sequence

import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.utils import override


class AutocompleteTooltip(QW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QC.Qt.Tool | QC.Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: lightyellow; border: 1px solid gray;")
        self.layout = QW.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QW.QLabel()
        self.label.setAlignment(QC.Qt.AlignLeading)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.hide()

    def showAt(self, pos, suggestions):
        self.move(pos)
        self.label.setText(", ".join(suggestions))
        self.adjustSize()
        self.setMaximumWidth(self.parentWidget().width())
        self.show()


class TextValidationSubmissionWidget(QW.QWidget):
    """A widget with a QTextEdit with a validator for a given set of terms
    which can be set via the `set_allowed_terms` method.
    """

    submitPressed = QC.pyqtSignal(list)
    # TODO: Properly handle strings with spaces in between them!

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a horizontal layout
        layout = QW.QHBoxLayout()

        # Create a LineEdit widget
        self.text_edit = QW.QTextEdit(self)
        self.text_edit.setPlaceholderText("Enter new cards to ban...")
        self._adjust_text_edit_height()

        # Set up the autocomplete:
        self._allowed_autocompletes = {}

        # Create a custom tooltip-like widget for autocompletion
        self.autocomplete_tooltip = AutocompleteTooltip(self.text_edit)

        # Install an event filter to capture autocomplete input
        self.text_edit.installEventFilter(self)
        self.text_edit.textChanged.connect(self.validateInput)

        # Create a submit button with an icon
        self.submit_button = QW.QPushButton(QG.QIcon(".png"), "", self)
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.onSubmit)

        # Add widgets to the horizontal layout
        layout.addWidget(self.text_edit)
        layout.addWidget(self.submit_button)

        # Create a vertical layout for the entire widget
        main_layout = QW.QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)
        self.setToolTip(
            "Enter a comma-separated list of cards. Press tab for auto-completion."
        )

    def set_allowed_terms(self, term_list: Sequence[str]):
        """Externally set the allowed terms for the autocomplete (e.g. a list of
        CSO names)
        """
        self._allowed_autocompletes = set(term_list)

    @override
    def eventFilter(self, obj, event):
        """Redirekt the Tab and Return Key presses to the autocompletion"""
        if obj == self.text_edit and event.type() == event.KeyPress:
            key = event.key()
            if key == QC.Qt.Key_Tab or key == QC.Qt.Key_Return:
                # Handle Tab key press for autocompletion
                successful_autocomplete = self._autocomplete()
                if (
                    not successful_autocomplete
                    and key == QC.Qt.Key_Return
                    and self._is_text_valid()
                ):
                    self.onSubmit()
                return True
        return super().eventFilter(obj, event)

    def validateInput(self):
        """Validates the text input and enables or disables the submitButton"""
        self.submit_button.setEnabled(self._is_text_valid())
        self._set_autocomplete_tooltip()
        self._adjust_text_edit_height()

    def onSubmit(self):
        """Called whenever the submit-button is clicked or the Return Key is pressed in the
        TextEdit.
        """
        inputs = self._get_csv_values()
        self.text_edit.clear()
        self.submitPressed.emit(inputs)

    def _get_currently_selected_word(self) -> str:
        """Return the word currently under the cursor in the TextEdit-"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QG.QTextCursor.StartOfWord, QG.QTextCursor.KeepAnchor)
        # Get the current word the cursor is in
        return cursor.selectedText().strip()

    def _get_autocomplete_words(self, wordstart: str) -> list[str]:
        """Retrieve the remaining words valid for the autocompleter.
        This includes all initial words, but excludes all the ones that are currently
        already written out.
        Sort them and return them as a list.
        """
        remaining = sorted(
            self._allowed_autocompletes.difference(self._get_csv_values())
        )
        return [word for word in remaining if word.startswith(wordstart.title())]

    def _autocomplete(self) -> bool:
        """Perform all actions to complete the current word with the top word from the list.
        Returns whether any autocomplete was actually performed.
        """
        if not (current_word := self._get_currently_selected_word()):
            return False
        if not (filtered_words := self._get_autocomplete_words(current_word)):
            return False

        # Select the first suggestion
        self.text_edit.insertPlainText(
            filtered_words[0].title()[len(current_word) :] + ", "
        )
        self.text_edit.moveCursor(QG.QTextCursor.Right)
        self.autocomplete_tooltip.hide()
        return True

    def _set_autocomplete_tooltip(self):
        """Set the autocomplete tooltip to the list of available words."""
        self.autocomplete_tooltip.hide()
        if not (current_word := self._get_currently_selected_word()):
            return
        if not (filtered_words := self._get_autocomplete_words(current_word)):
            return

        # Show the autocomplete tooltip
        cursor_pos = self.text_edit.mapToGlobal(
            self.text_edit.cursorRect().bottomLeft()
        )
        cursor_pos.setY(cursor_pos.y())
        self.autocomplete_tooltip.showAt(cursor_pos, filtered_words)

    def _adjust_text_edit_height(self):
        """Sets the Height of the TextEdit so it appropriately wraps its content."""
        doc_height = self.text_edit.document().size().height()
        self.text_edit.setFixedHeight(int(doc_height) + 2)

    def _get_csv_values(self) -> list[str]:
        text = self.text_edit.toPlainText().strip(", ")
        inputs = [card.strip().title().replace("_", " ") for card in text.split(",")]
        return inputs

    def _is_text_valid(self) -> bool:
        inputs = self._get_csv_values()
        return set(self._allowed_autocompletes).issuperset(set(inputs))
