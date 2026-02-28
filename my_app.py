from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet
from textual_timepiece.pickers import DatePicker


class Origen(VerticalScroll):
    def compose(self) -> ComposeResult:
        origen = RadioSet(id="origen")
        origen.border_title = "Origen"
        origen.border_subtitle = "Origin"
        with origen:
            yield RadioButton("Puerto Rico Yauco")
            yield RadioButton("Puerto Rico Maricao")
            yield RadioButton("Puerto Rico Segundas")


class FechaTueste(VerticalScroll):
    def compose(self) -> ComposeResult:
        fecha_tueste = DatePicker(id="fecha_tueste")
        fecha_tueste.border_title = "Fecha de Tueste"
        fecha_tueste.border_subtitle = "Roast Date"
        yield fecha_tueste


class NivelTueste(VerticalScroll):
    def compose(self) -> ComposeResult:
        nivel_tueste = RadioSet(id="nivel_tueste")
        nivel_tueste.border_title = "Nivel de Tueste"
        nivel_tueste.border_subtitle = "Roast Level"
        with nivel_tueste:
            yield RadioButton("Medium Light")
            yield RadioButton("Medium")
            yield RadioButton("Medium Dark")


class Proceso(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Proceso")
        with RadioSet(id="proceso"):
            yield RadioButton("Washed", True)


class Altitud(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Altitud")
        with RadioSet(id="altitud"):
            yield RadioButton("2000'")
            yield RadioButton("2200'")
            yield RadioButton("2000'+")


class Cata(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Notas de Cata")
        with RadioSet(id="cata"):
            yield RadioButton("chocolate, honey, peanut butter, lemon-lime")
            yield RadioButton("chocolate, butter, citrus, honey")
            yield RadioButton("cold brew")


class Peso(VerticalScroll):
    def compose(self) -> ComposeResult:
        peso = RadioSet(id="peso")
        peso.border_title = "Peso"
        peso.border_subtitle = "Weight"
        with peso:
            yield RadioButton("2.5 oz | 71 g")
            yield RadioButton("4 oz | 113 g")
            yield RadioButton("12 oz | 340 g")
            yield RadioButton("5 lb | 2.2 kg")


class Lote(VerticalScroll):
    def compose(self) -> ComposeResult:
        lote = Input(id="lote", type="integer")
        lote.border_title = "No. de Lote"
        lote.border_subtitle = "Batch No."
        yield lote


class WhiteLabel(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Origen()

        with Horizontal():
            yield FechaTueste()
            yield NivelTueste()

        with Horizontal():
            yield Peso()
            yield Lote()

        with Center():
            yield Button("Print", variant="primary")


class CaciqueZPL(App):
    CSS_PATH = "caciquezpl.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            label_select = RadioSet(id="label_select")
            label_select.border_title = "Label Select"
            with label_select:
                yield RadioButton("White label")
                yield RadioButton("Red label")
            yield Container(id="label")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(RadioSet).focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        if event.pressed.label == "White label":
            new_white_label = WhiteLabel()
            self.query_one("#label").remove_children()
            self.query_one("#label").mount(new_white_label)
            new_white_label.scroll_visible()
        elif event.pressed.label == "Red label":
            new_unsupported_label = Label("Red label is currently unsupported")
            self.query_one("#label").remove_children()
            self.query_one("#label").mount(new_unsupported_label)
            new_unsupported_label.scroll_visible()


if __name__ == "__main__":
    app = CaciqueZPL()
    app.run()
