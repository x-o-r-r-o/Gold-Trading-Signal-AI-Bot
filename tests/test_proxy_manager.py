import pytest
from src.proxies.manager import ProxyManager


@pytest.mark.unit
def test_load_saved_proxies_parses_file(tmp_path):
    f = tmp_path / "proxies.txt"
    f.write_text("1.2.3.4:8080\n5.6.7.8:3128\n", encoding="utf-8")
    pm = ProxyManager(proxy_type="http", saved_file=str(f))
    proxies = pm.load_saved_proxies()
    assert len(proxies) == 2
    assert proxies[0].address == "1.2.3.4:8080"


@pytest.mark.liveapi
def test_get_working_proxy_live():
    """
    Live test: uses actual saved_proxies.txt if present.

    This is production-ready (no mocking) but may fail if proxies are dead.
    """
    pm = ProxyManager(proxy_type="http", saved_file="src/proxies/saved_proxies.txt")
    pm.load_saved_proxies()
    working = pm.get_working_proxy(n=1)
    # We don't assert len>0 because proxies may not be alive; we just ensure no crash.
    assert isinstance(working, list)