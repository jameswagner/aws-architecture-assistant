from common.llm import DEFAULT_MODEL, get_judge_llm, get_llm


def test_get_llm_defaults(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)

    llm = get_llm()

    assert llm.model == DEFAULT_MODEL


def test_get_llm_respects_env_override(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")

    llm = get_llm()

    assert llm.model == "gpt-4o"


def test_get_judge_llm_defaults_to_same_model_as_synthesis(monkeypatch):
    monkeypatch.delenv("JUDGE_LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert get_judge_llm().model == DEFAULT_MODEL


def test_get_judge_llm_follows_synthesis_model_override(monkeypatch):
    monkeypatch.delenv("JUDGE_LLM_MODEL", raising=False)
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")

    assert get_judge_llm().model == "gpt-4o"


def test_get_judge_llm_can_be_overridden_independently(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")
    monkeypatch.setenv("JUDGE_LLM_MODEL", "gpt-4o-mini")

    assert get_judge_llm().model == "gpt-4o-mini"
    assert get_llm().model == "gpt-4o"
