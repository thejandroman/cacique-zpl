"""Tests for the main CaciqueZPL app."""
import pytest
from textual.app import App
from textual.widgets import Button, RadioButton, RadioSet

from my_app import CaciqueZPL
from red_label import RedLabel
from white_label import WhiteLabel


class TestAppComposition:
    """Tests for app composition and initial state."""

    async def test_app_starts(self) -> None:
        """Test that app can start."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            # App should have a header
            assert app.query_one("Header") is not None
            # App should have a footer
            assert app.query_one("Footer") is not None

    async def test_has_label_select_radio(self) -> None:
        """Test that label select radio set exists."""
        app = CaciqueZPL()
        async with app.run_test():
            radio_set = app.query_one("#label_select", RadioSet)
            assert radio_set is not None

    async def test_has_label_container(self) -> None:
        """Test that label container exists."""
        app = CaciqueZPL()
        async with app.run_test():
            label_container = app.query_one("#label")
            assert label_container is not None

    async def test_default_label_selection(self) -> None:
        """Test that no label is selected by default."""
        app = CaciqueZPL()
        async with app.run_test():
            radio_set = app.query_one("#label_select", RadioSet)
            assert radio_set.pressed_button is None


class TestWhiteLabelSelection:
    """Tests for white label selection behavior."""

    async def test_selecting_white_label_shows_white_label_widget(self) -> None:
        """Test that selecting white label shows the WhiteLabel widget."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            radio_set = app.query_one("#label_select", RadioSet)
            # Focus the radio set and press enter to select first option
            radio_set.focus()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            # Should have a WhiteLabel widget
            label_container = app.query_one("#label")
            white_label = label_container.query_one(WhiteLabel)
            assert white_label is not None

    async def test_white_label_has_required_widgets(self) -> None:
        """Test that WhiteLabel contains all required widgets."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            # Select white label
            radio_set = app.query_one("#label_select", RadioSet)
            radio_set.focus()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            label_container = app.query_one("#label")
            white_label = label_container.query_one(WhiteLabel)

            # Check for origen radio set
            assert white_label.query_one("#origen", RadioSet) is not None

            # Check for nivel tueste radio set
            assert white_label.query_one("#nivel_tueste", RadioSet) is not None

            # Check for peso radio set
            assert white_label.query_one("#peso", RadioSet) is not None

            # Check for lote input
            assert white_label.query_one("#lote") is not None

            # Check for print button
            print_button = white_label.query_one("#print", Button)
            assert print_button is not None
            # Print button should be disabled by default
            assert print_button.disabled is True


class TestRedLabelSelection:
    """Tests for red label selection behavior."""

    async def test_selecting_red_label_shows_red_label_widget(self) -> None:
        """Test that selecting red label shows the RedLabel widget."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            radio_set = app.query_one("#label_select", RadioSet)
            # Focus the radio set and select second option using value property
            radio_set.focus()
            await pilot.pause()
            # Get the radio buttons
            radio_buttons = radio_set.query(RadioButton)
            # Select the second radio button (Red label)
            radio_buttons[1].value = True
            # Trigger the changed event manually
            radio_set._selected = 1
            await pilot.pause()

            label_container = app.query_one("#label")
            # Should have a RedLabel widget when red label is selected
            red_label = label_container.query_one(RedLabel)
            assert red_label is not None
            # Should NOT have a WhiteLabel when red label is selected
            white_labels = label_container.query(WhiteLabel)
            assert len(white_labels) == 0

    async def test_red_label_has_required_widgets(self) -> None:
        """Test that RedLabel contains all required widgets."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            # Select red label
            radio_set = app.query_one("#label_select", RadioSet)
            radio_set.focus()
            await pilot.pause()
            radio_buttons = radio_set.query(RadioButton)
            radio_buttons[1].value = True
            radio_set._selected = 1
            await pilot.pause()

            label_container = app.query_one("#label")
            red_label = label_container.query_one(RedLabel)

            # Check for origen radio set
            assert red_label.query_one("#origen", RadioSet) is not None

            # Check for nivel tueste radio set
            assert red_label.query_one("#nivel_tueste", RadioSet) is not None

            # Check for peso radio set
            assert red_label.query_one("#peso", RadioSet) is not None

            # Check for lote input
            assert red_label.query_one("#lote") is not None

            # Check for print button
            print_button = red_label.query_one("#print", Button)
            assert print_button is not None
            # Print button should be disabled by default
            assert print_button.disabled is True


class TestPrintButtonState:
    """Tests for print button disabled state."""

    async def test_print_button_disabled_initially(self) -> None:
        """Test that print button is disabled when no fields are filled."""
        app = CaciqueZPL()
        async with app.run_test() as pilot:
            # Select white label
            radio_set = app.query_one("#label_select", RadioSet)
            radio_set.focus()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            label_container = app.query_one("#label")
            white_label = label_container.query_one(WhiteLabel)
            print_button = white_label.query_one("#print", Button)

            assert print_button.disabled is True


class TestFieldValidation:
    """Tests for field validation logic."""

    async def test_all_required_fields_present_requires_all_fields(self) -> None:
        """Test that _all_required_fields_present returns False when no fields exist."""
        app = CaciqueZPL()
        async with app.run_test():
            # Without mounting any label widget, it should return False
            result = app._all_required_fields_present()
            assert result is False
