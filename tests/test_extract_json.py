import pytest

from youtube_automation.providers.llm.anthropic_provider import extract_json


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_with_markdown_fence():
    text = '```json\n{"a": 1, "b": [1, 2]}\n```'
    assert extract_json(text) == {"a": 1, "b": [1, 2]}


def test_extract_json_with_surrounding_prose():
    text = 'Sure, here is the JSON:\n{"a": 1}\nHope that helps!'
    assert extract_json(text) == {"a": 1}


def test_extract_json_raises_on_garbage():
    with pytest.raises(ValueError):
        extract_json("no json here at all")
