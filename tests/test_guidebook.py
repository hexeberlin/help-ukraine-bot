from typing import Dict

import pytest
import toml
from src.guidebook import Guidebook


class TestGuidebook:
    @pytest.fixture(scope="session")
    def settings(self) -> Dict[str, str]:
        return toml.load("settings.toml")

    def test_constructor(self, settings: Dict[str, str]):
        gb = Guidebook(
            guidebook_path=settings["GUIDEBOOK_PATH"],
            vocabulary_path=settings["VOCABULARY_PATH"],
        )
        assert isinstance(gb, Guidebook)
