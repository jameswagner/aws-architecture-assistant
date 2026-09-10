from common.llm import DEFAULT_MODEL, get_llm


def test_get_llm_defaults(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)

    llm = get_llm()

    assert llm.model == DEFAULT_MODEL


def test_get_llm_respects_env_override(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")

    llm = get_llm()

    assert llm.model == "gpt-4o"
