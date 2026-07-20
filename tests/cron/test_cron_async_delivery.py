from unittest.mock import MagicMock, patch


def test_cron_agent_disables_detached_async_delivery(tmp_path):
    """Cron must keep delegated batches in-process until their result returns."""
    from cron.scheduler import run_job
    from gateway.session_context import async_delivery_supported

    observed = []
    fake_db = MagicMock()

    def run_conversation(*_args, **_kwargs):
        observed.append(async_delivery_supported())
        return {"final_response": "ok"}

    job = {
        "id": "cron-sync-delegation-test",
        "name": "cron sync delegation test",
        "prompt": "hello",
        "model": None,
        "provider": None,
        "provider_snapshot": None,
        "base_url": None,
    }

    with (
        patch("cron.scheduler._hermes_home", tmp_path),
        patch("cron.scheduler._resolve_origin", return_value=None),
        patch("hermes_cli.env_loader.load_hermes_dotenv"),
        patch("hermes_cli.env_loader.reset_secret_source_cache"),
        patch("hermes_state.SessionDB", return_value=fake_db),
        patch(
            "hermes_cli.runtime_provider.resolve_runtime_provider",
            return_value={
                "api_key": "test-key",
                "base_url": "https://example.invalid/v1",
                "provider": "openrouter",
                "api_mode": "chat_completions",
            },
        ),
        patch("run_agent.AIAgent") as mock_agent_cls,
    ):
        mock_agent = MagicMock()
        mock_agent.run_conversation.side_effect = run_conversation
        mock_agent_cls.return_value = mock_agent

        success, _output, _response, error = run_job(job)

    assert success is True, error
    assert observed == [False]
