"""Tests for RedLabelTemplate class."""
from pathlib import Path

import pytest

from red_label import RedLabelTemplate


@pytest.fixture
def template() -> RedLabelTemplate:
    """Create a RedLabelTemplate instance."""
    return RedLabelTemplate()


@pytest.fixture
def sample_payload() -> dict[str, str | None]:
    """Sample payload for rendering."""
    return {
        "label_type": "Red label",
        "origen": "Puerto Rico Yauco",
        "fecha_tueste": "01 • 07 • 2026",
        "nivel_tueste": "Medium",
        "cata": "chocolate, honey, peanut butter, lemon-lime",
        "altitud": "2000'",
        "peso": "12 oz | 340 g",
        "lote": "123",
    }


class TestRedLabelTemplate:
    """Tests for RedLabelTemplate class."""

    def test_template_loads_default_file(self, template: RedLabelTemplate) -> None:
        """Test that template loads the default ZPL file."""
        assert template.template_path.exists()
        assert template.template_path.name == "red_label_template.zpl"

    def test_template_can_use_custom_path(self, tmp_path: Path) -> None:
        """Test that template can use a custom path."""
        custom_zpl = tmp_path / "custom.zpl"
        custom_zpl.write_text("^XA^FDTEST\\&^XZ")
        template = RedLabelTemplate(template_path=custom_zpl)
        assert template.template_path == custom_zpl

    def test_render_replaces_origen(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that ORIGEN placeholder is replaced."""
        result = template.render(sample_payload)
        assert "Puerto Rico Yauco" in result
        assert "^FDORIGEN\\\\&" not in result

    def test_render_replaces_fecha_tueste(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that FECHA TUESTE placeholder is replaced."""
        result = template.render(sample_payload)
        assert "01 • 07 • 2026" in result
        assert "^FDFECHA TUESTE\\&" not in result

    def test_render_replaces_nivel_tueste(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that NIVEL TUESTE placeholder is replaced."""
        result = template.render(sample_payload)
        assert "Medium" in result
        assert "^FDNIVEL TUESTE\\&" not in result

    def test_render_replaces_cata(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that CATA placeholder is replaced."""
        result = template.render(sample_payload)
        assert "chocolate, honey, peanut butter, lemon-lime" in result
        assert "^FDCATA\\&" not in result

    def test_render_replaces_altitud(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that ALTITUD placeholder is replaced."""
        result = template.render(sample_payload)
        assert "2000'" in result
        assert "^FDALTITUD\\&" not in result

    def test_render_replaces_peso(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that PESO placeholder is replaced."""
        result = template.render(sample_payload)
        assert "12 oz | 340 g" in result
        assert "^FDPESO\\&" not in result

    def test_render_replaces_lote(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that LOTE placeholder is replaced."""
        result = template.render(sample_payload)
        assert "123" in result
        assert "^FDLOTE\\&" not in result

    def test_render_updates_roast_level_position(self, template: RedLabelTemplate) -> None:
        """Test that roast level marker FO position changes based on roast level."""
        # Medium Light
        payload_ml = {"nivel_tueste": "Medium Light"}
        result_ml = template.render(payload_ml)
        assert "^FO684,650" in result_ml

        # Medium
        payload_m = {"nivel_tueste": "Medium"}
        result_m = template.render(payload_m)
        assert "^FO774,650" in result_m

        # Medium Dark
        payload_md = {"nivel_tueste": "Medium Dark"}
        result_md = template.render(payload_md)
        assert "^FO864,650" in result_md

    def test_cata_by_origen_mapping(self, template: RedLabelTemplate) -> None:
        """Test CATA_BY_ORIGEN mapping."""
        assert template.CATA_BY_ORIGEN["Puerto Rico Yauco"] == "chocolate, honey, peanut butter, lemon-lime"
        assert template.CATA_BY_ORIGEN["Puerto Rico Maricao"] == "chocolate, butter, citrus, honey"
        assert template.CATA_BY_ORIGEN["Puerto Rico Segundas"] == "cold brew"

    def test_altitud_by_origen_mapping(self, template: RedLabelTemplate) -> None:
        """Test ALTITUD_BY_ORIGEN mapping."""
        assert template.ALTITUD_BY_ORIGEN["Puerto Rico Yauco"] == "2000'"
        assert template.ALTITUD_BY_ORIGEN["Puerto Rico Maricao"] == "2200'"
        assert template.ALTITUD_BY_ORIGEN["Puerto Rico Segundas"] == "2000' +"

    def test_roast_level_marker_mapping(self, template: RedLabelTemplate) -> None:
        """Test ROAST_LEVEL_MARKER_FO mapping."""
        assert template.ROAST_LEVEL_MARKER_FO["Medium Light"] == "684,650"
        assert template.ROAST_LEVEL_MARKER_FO["Medium"] == "774,650"
        assert template.ROAST_LEVEL_MARKER_FO["Medium Dark"] == "864,650"

    def test_render_with_none_values(self, template: RedLabelTemplate) -> None:
        """Test rendering with None values doesn't crash."""
        payload = {
            "label_type": "Red label",
            "origen": None,
            "fecha_tueste": None,
            "nivel_tueste": None,
            "cata": None,
            "altitud": None,
            "peso": None,
            "lote": None,
        }
        result = template.render(payload)
        assert isinstance(result, str)
        # Empty strings should replace placeholders
        assert "^FDORIGEN\\&" not in result

    def test_render_returns_zpl_format(self, template: RedLabelTemplate, sample_payload: dict) -> None:
        """Test that render output starts with ZPL header and ends with trailer."""
        result = template.render(sample_payload)
        assert result.startswith("^XA")
        assert result.rstrip().endswith("^XZ")
