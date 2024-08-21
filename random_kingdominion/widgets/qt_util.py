import PyQt5.QtWidgets as QW


def clear_layout(layout: QW.QLayout):
    """Clear the given layout (remove all its children in a safe way)

    Parameters
    ----------
    layout : QW.QLayout
        The layout to be cleared
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
