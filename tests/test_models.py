from youtube_automation.models import Script, ScriptScene


def test_script_estimates_duration_from_scenes():
    script = Script(
        title="t",
        hook_line="h",
        scenes=[
            ScriptScene(index=0, narration="a", visual_direction="v", duration_hint_seconds=5),
            ScriptScene(index=1, narration="b", visual_direction="v", duration_hint_seconds=7),
        ],
        call_to_action="subscribe",
    )
    assert script.estimated_duration_seconds == 12


def test_script_respects_explicit_duration():
    script = Script(
        title="t",
        hook_line="h",
        scenes=[ScriptScene(index=0, narration="a", visual_direction="v")],
        call_to_action="subscribe",
        estimated_duration_seconds=99,
    )
    assert script.estimated_duration_seconds == 99
