from typing import Dict

import pytest
import toml
from src.infrastructure.yaml_guidebook import YamlGuidebook


class TestGuidebook:
    @pytest.fixture(scope="session")
    def settings(self) -> Dict[str, str]:
        return toml.load("settings.toml")

    def test_constructor(self, settings: Dict[str, str]):
        gb = YamlGuidebook(
            guidebook_path=settings["GUIDEBOOK_PATH"],
            vocabulary_path=settings["VOCABULARY_PATH"],
        )
        assert isinstance(gb, YamlGuidebook)
