from pathlib import Path

from textual.containers import Center, Horizontal, VerticalScroll
from textual.widgets import Button, Input, Label, RadioButton, RadioSet

from textual_timepiece.pickers import DatePicker


class Origen(VerticalScroll):
    def compose(self):
        origen = RadioSet(id="origen")
        origen.border_title = "Origen"
        origen.border_subtitle = "Origin"
        with origen:
            yield RadioButton("Puerto Rico Yauco")
            yield RadioButton("Puerto Rico Maricao")
            yield RadioButton("Puerto Rico Segundas")


class FechaTueste(VerticalScroll):
    def compose(self):
        fecha_tueste = DatePicker(id="fecha_tueste")
        fecha_tueste.border_title = "Fecha de Tueste"
        fecha_tueste.border_subtitle = "Roast Date"
        yield fecha_tueste


class NivelTueste(VerticalScroll):
    def compose(self):
        nivel_tueste = RadioSet(id="nivel_tueste")
        nivel_tueste.border_title = "Nivel de Tueste"
        nivel_tueste.border_subtitle = "Roast Level"
        with nivel_tueste:
            yield RadioButton("Medium Light")
            yield RadioButton("Medium")
            yield RadioButton("Medium Dark")


class Proceso(VerticalScroll):
    def compose(self):
        yield Label("Proceso")
        with RadioSet(id="proceso"):
            yield RadioButton("Washed", True)


class Altitud(VerticalScroll):
    def compose(self):
        yield Label("Altitud")
        with RadioSet(id="altitud"):
            yield RadioButton("2000'")
            yield RadioButton("2200'")
            yield RadioButton("2000'+")


class Cata(VerticalScroll):
    def compose(self):
        yield Label("Notas de Cata")
        with RadioSet(id="cata"):
            yield RadioButton("chocolate, honey, peanut butter, lemon-lime")
            yield RadioButton("chocolate, butter, citrus, honey")
            yield RadioButton("cold brew")


class Peso(VerticalScroll):
    def compose(self):
        peso = RadioSet(id="peso")
        peso.border_title = "Peso"
        peso.border_subtitle = "Weight"
        with peso:
            yield RadioButton("2.5 oz | 71 g")
            yield RadioButton("4 oz | 113 g")
            yield RadioButton("12 oz | 340 g")
            yield RadioButton("5 lb | 2.2 kg")


class Lote(VerticalScroll):
    def compose(self):
        lote = Input(id="lote", type="integer")
        lote.border_title = "No. de Lote"
        lote.border_subtitle = "Batch No."
        yield lote


class WhiteLabel(VerticalScroll):
    def compose(self):
        yield Origen()

        with Horizontal():
            yield FechaTueste()
            yield NivelTueste()

        with Horizontal():
            yield Peso()
            yield Lote()

        with Center():
            yield Button("Print", variant="primary", id="print", disabled=True)


class WhiteLabelTemplate:
    FIELD_MAP = {
        "ORIGEN": "origen",
        "FECHA TUESTE": "fecha_tueste",
        "NIVEL TUESTE": "nivel_tueste",
        "CATA": "cata",
        "ALTITUD": "altitud",
        "PESO": "peso",
        "LOTE": "lote",
    }
    CATA_BY_ORIGEN = {
        "Puerto Rico Yauco": "chocolate, honey, peanut butter, lemon-lime",
        "Puerto Rico Maricao": "chocolate, butter, citrus, honey",
        "Puerto Rico Segundas": "cold brew",
    }
    ROAST_LEVEL_MARKER_FO = {
        "Medium Light": "453,620",
        "Medium": "531,620",
        "Medium Dark": "609,620",
    }
    ALTITUD_BY_ORIGEN = {
        "Puerto Rico Yauco": "2000'",
        "Puerto Rico Maricao": "2200'",
        "Puerto Rico Segundas": "2000' +",
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
