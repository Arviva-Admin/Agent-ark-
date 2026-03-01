from arviva_agent.desktop_control.agent_s_wrapper import AgentSWrapper
from arviva_agent.desktop_control.gui_interaction import GUICommand, GUIInteraction


class _FakeAgentSClient:
    def perform_action(self, action: str, payload: str = ""):
        class _Result:
            ok = True
            message = f"{action}:{payload}"
            screenshot_path = None
            simulated = True

        return _Result()

    def is_available(self) -> bool:
        return False


def test_gui_screenshot_action() -> None:
    wrapper = AgentSWrapper(client=_FakeAgentSClient())
    gui = GUIInteraction(agent_s=wrapper)
    ok, details = gui.execute(GUICommand(action="screenshot", payload=""))
    assert ok is True
    assert "simulated" in details
