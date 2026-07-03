from src.browser.models import BrowserAction, BrowserSnapshot


def test_browser_action():
    action = BrowserAction(
        action="navigate", parameters={"url": "https://example.com"}, reasoning="start"
    )
    assert action.action == "navigate"
    assert action.parameters["url"] == "https://example.com"


def test_browser_snapshot():
    snap = BrowserSnapshot(url="https://example.com", title="Test", dom_summary="hello")
    assert snap.url == "https://example.com"
    assert snap.title == "Test"
    assert snap.dom_summary == "hello"
    assert snap.form_fields == []
    assert snap.links == []
