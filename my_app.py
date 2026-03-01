from pathlib import Path
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, VerticalScroll
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


class WhiteLabelTemplate:
    FIELD_MAP = {
        "ORIGEN": "origen",
        "FECHA TUESTE": "fecha_tueste",
        "NIVEL TUESTE": "nivel_tueste",
        "PESO": "peso",
        "LOTE": "lote",
    }
    ROAST_LEVEL_MARKER_FO = {
        "Medium Light": "453,620",
        "Medium": "531,620",
        "Medium Dark": "609,620",
    }

    def __init__(self, template_path: Path | None = None) -> None:
        self.template_path = template_path or Path(__file__).with_name("white_label_template.zpl")

    def render(self, payload: dict[str, str | None]) -> str:
        zpl = self.template_path.read_text(encoding="utf-8")
        for placeholder, key in self.FIELD_MAP.items():
            value = payload.get(key) or ""
            zpl = zpl.replace(f"^FD{placeholder}\\&", f"^FD{value}\\&")
        marker_fo = self.ROAST_LEVEL_MARKER_FO.get(payload.get("nivel_tueste") or "", "531,620")
        zpl = zpl.replace("^FO531,620\n^GFA", f"^FO{marker_fo}\n^GFA", 1)
        return zpl


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
            yield VerticalScroll(id="label")
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

    def _selected_radio(self, selector: str) -> str | None:
        rs = self.query_one(selector, RadioSet)
        return str(rs.pressed_button.label) if rs.pressed_button else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.label) != "Print":
            return

        picker = self.query_one("#fecha_tueste", DatePicker)
        roast_date = getattr(picker, "date", getattr(picker, "value", None))
        formatted_roast_date = roast_date.py_date().strftime("%d • %m • %Y") if roast_date else None

        payload = {
            "label_type": self._selected_radio("#label_select"),
            "origen": self._selected_radio("#origen"),
            "nivel_tueste": self._selected_radio("#nivel_tueste"),
            "peso": self._selected_radio("#peso"),
            "lote": self.query_one("#lote", Input).value,
            "fecha_tueste": formatted_roast_date if formatted_roast_date else None,
        }

        zpl_output = WhiteLabelTemplate().render(payload)
        try:
            subprocess.run(
                ["lpr", "-P", "ZTC-ZD420-300dpi-ZPL", "-o", "raw"],
                input=zpl_output,
                text=True,
                check=True,
            )
            self.notify("Label sent to printer")
        except FileNotFoundError:
            self.notify("lpr command not found", severity="error")
        except subprocess.CalledProcessError as exc:
            self.notify(f"Printer command failed ({exc.returncode})", severity="error")


if __name__ == "__main__":
    app = CaciqueZPL()
    app.run()
