from arviva_agent.integrations.superagi_client import SuperAGIClient


def test_superagi_client_handles_connection_error() -> None:
    client = SuperAGIClient(base_url="http://127.0.0.1:9")
    result = client.dispatch_workflow(goal="x")
    assert result.ok is False
    assert result.simulated is True


def test_superagi_health_handles_connection_error() -> None:
    client = SuperAGIClient(base_url="http://127.0.0.1:9")
    result = client.health()
    assert result.ok is False
    assert result.simulated is True
