from textual.widgets import Footer


class NeonFooter(Footer, inherit_css=True):
    """A skin for textual's native Footer widget."""
    DEFAULT_CSS = """
    NeonFooter {
        background: transparent;
        border: none !important;
        margin: 0 0 1 0;
        padding: 0 1 0 1;
        FooterKey.-command-palette {
            border: none !important;
            background: $background !important;
        }
        .footer-key--key {
            color: $primary !important;
            padding: 0 0 0 1 !important;
        }
        FooterKey:hover {
            background: $background-lighten-1 !important;
            .footer-key--key {
                color: $accent !important;
            }
        }
    }
    """