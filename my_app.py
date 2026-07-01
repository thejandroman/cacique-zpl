import subprocess

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet
from textual_timepiece.pickers import DatePicker


from white_label import WhiteLabel, WhiteLabelTemplate


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

    def _all_required_fields_present(self) -> bool:
        try:
            required_radios = (
                self.query_one("#label_select", RadioSet),
                self.query_one("#origen", RadioSet),
                self.query_one("#nivel_tueste", RadioSet),
                self.query_one("#peso", RadioSet),
            )
            picker = self.query_one("#fecha_tueste", DatePicker)
            lote = self.query_one("#lote", Input).value.strip()
        except NoMatches:
            return False
        roast_date = getattr(picker, "date", getattr(picker, "value", None))
        return all(radio.pressed_button is not None for radio in required_radios) and bool(roast_date) and bool(lote)

    def _sync_print_button_disabled(self) -> None:
        try:
            self.query_one("#print", Button).disabled = not self._all_required_fields_present()
        except NoMatches:
            return

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
        self._sync_print_button_disabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "lote":
            self._sync_print_button_disabled()

    def on_date_picker_changed(self, _: DatePicker.Changed) -> None:
        self._sync_print_button_disabled()

    def _selected_radio(self, selector: str) -> str | None:
        rs = self.query_one(selector, RadioSet)
        return str(rs.pressed_button.label) if rs.pressed_button else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.label) != "Print":
            return

        picker = self.query_one("#fecha_tueste", DatePicker)
        roast_date = getattr(picker, "date", getattr(picker, "value", None))
        formatted_roast_date = roast_date.py_date().strftime("%d • %m • %Y") if roast_date else None

        origen = self._selected_radio("#origen")
        cata = WhiteLabelTemplate.CATA_BY_ORIGEN.get(origen or "", None)
        altitud = WhiteLabelTemplate.ALTITUD_BY_ORIGEN.get(origen or "", None)

        payload = {
            "label_type": self._selected_radio("#label_select"),
            "origen": origen,
            "nivel_tueste": self._selected_radio("#nivel_tueste"),
            "cata": cata,
            "altitud": altitud,
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
