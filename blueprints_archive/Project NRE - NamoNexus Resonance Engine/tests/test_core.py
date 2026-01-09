from nre_core import (
    AdaptiveEvolutionCore,
    ContextDetector,
    EmotionalMatrix,
    DynamicAtmosphereGenerator,
    _normalize_directives,
)


def test_evolution_trigger() -> None:
    core = AdaptiveEvolutionCore()
    result = core.absorb_emotion("a" * 2001)
    assert result == "EVOLUTION_TRIGGERED"
    assert core.current_state == "TRANSCENDENCE"


def test_context_detector() -> None:
    detector = ContextDetector()
    assert detector.detect("I need help now") == "crisis"
    assert detector.detect("I love this") == "affection"
    assert detector.detect("Let's plan ahead") == "strategy"
    assert detector.detect("Hello there") == "neutral"


def test_emotional_matrix_update() -> None:
    matrix = EmotionalMatrix()
    matrix.update("crisis")
    assert matrix.tension > 0.3
    assert matrix.dominance > 0.5


def test_atmosphere_generator() -> None:
    generator = DynamicAtmosphereGenerator()
    assert "Atmosphere" in generator.generate("AWAKENING")
    assert "Atmosphere" in generator.generate("UNKNOWN")


def test_normalize_directives() -> None:
    assert _normalize_directives(None) == ""
    assert _normalize_directives([" one ", "", "two "]) == "one\ntwo"
