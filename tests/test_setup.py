import httpx
import pytest

from setup.cloudflare import Cloudflare, CloudflareError


def handler(request: httpx.Request) -> httpx.Response:
    path, method = request.url.path, request.method
    ok = lambda result: httpx.Response(200, json={"success": True, "result": result})
    if path == "/client/v4/zones":
        name = request.url.params["name"]
        return ok([{"id": "z1", "name": name, "account": {"id": "acc"}}] if name == "example.com" else [])
    if path.endswith("/cfd_tunnel") and method == "GET":
        return ok([])
    if path.endswith("/cfd_tunnel") and method == "POST":
        return ok({"id": "tun1"})
    if path.endswith("/dns_records") and method == "GET":
        return ok([{"id": "r1", "type": "A"}] if request.url.params["name"] == "taken.example.com" else [])
    if path.endswith("/dns_records") and method == "POST":
        return ok({})
    return httpx.Response(403, json={"success": False, "errors": [{"message": "nope"}]})


@pytest.fixture
def cf():
    return Cloudflare("tok", transport=httpx.MockTransport(handler))


def test_zone_found_by_walking_up_hostname(cf):
    assert cf.find_zone("claude.sub.example.com")["id"] == "z1"
    with pytest.raises(CloudflareError):
        cf.find_zone("claude.other.org")


def test_tunnel_created_and_dns_conflict_detected(cf):
    assert cf.tunnel("acc", "name") == "tun1"
    assert cf.dns("z1", "claude.example.com", "tun1") == "created"
    with pytest.raises(CloudflareError, match="already has"):
        cf.dns("z1", "taken.example.com", "tun1")


def test_api_errors_surface_message(cf):
    with pytest.raises(CloudflareError, match="nope"):
        cf.verify()


def test_tunnel_id_parsing_and_config(tmp_path, monkeypatch):
    from setup import cloudflared_login as cl
    monkeypatch.setattr(cl, "DIR", tmp_path)
    monkeypatch.setattr(cl, "run", lambda *a, echo=False: (0, "Created tunnel claudeshare-x with id 6ff42ae2-765d-4adf-8112-31c55c1551ef"))
    assert cl.tunnel_id("claudeshare-x") == "6ff42ae2-765d-4adf-8112-31c55c1551ef"
    assert cl.URL_RE.search("Visit https://dash.cloudflare.com/argotunnel?aud=1&callback=x now").group(0).startswith("https://dash.cloudflare.com/argotunnel")
    assert "http://app:3000" in cl.CONFIG.format(tunnel="t", hostname="h.example.com")
