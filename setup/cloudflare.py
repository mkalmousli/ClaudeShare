"""Cloudflare API: create a tunnel, route a hostname to it, point DNS at it."""
import httpx

API = "https://api.cloudflare.com/client/v4"


class CloudflareError(Exception):
    pass


class Cloudflare:
    def __init__(self, token: str, transport: httpx.BaseTransport | None = None):
        self.http = httpx.Client(base_url=API, headers={"Authorization": f"Bearer {token}"}, timeout=30, transport=transport)

    def call(self, method: str, path: str, **kwargs):
        reply = self.http.request(method, path, **kwargs)
        try:
            body = reply.json()
        except ValueError:
            raise CloudflareError(f"Unexpected response ({reply.status_code}) from Cloudflare")
        if not body.get("success"):
            errors = "; ".join(e.get("message", "?") for e in body.get("errors", [])) or reply.reason_phrase
            raise CloudflareError(errors)
        return body["result"]

    def verify(self) -> None:
        self.call("GET", "/user/tokens/verify")

    def find_zone(self, hostname: str) -> dict:
        """Walk up the hostname (a.b.example.com -> b.example.com -> example.com) to find the zone."""
        labels = hostname.split(".")
        for start in range(len(labels) - 1):
            found = self.call("GET", "/zones", params={"name": ".".join(labels[start:])})
            if found:
                return {"id": found[0]["id"], "name": found[0]["name"], "account": found[0]["account"]["id"]}
        raise CloudflareError(f"No zone for {hostname} in this Cloudflare account (is the domain added and active?)")

    def tunnel(self, account: str, name: str) -> str:
        existing = self.call("GET", f"/accounts/{account}/cfd_tunnel", params={"name": name, "is_deleted": "false"})
        if existing:
            return existing[0]["id"]
        return self.call("POST", f"/accounts/{account}/cfd_tunnel", json={"name": name, "config_src": "cloudflare"})["id"]

    def tunnel_token(self, account: str, tunnel: str) -> str:
        return self.call("GET", f"/accounts/{account}/cfd_tunnel/{tunnel}/token")

    def route(self, account: str, tunnel: str, hostname: str, service: str) -> None:
        ingress = [{"hostname": hostname, "service": service}, {"service": "http_status:404"}]
        self.call("PUT", f"/accounts/{account}/cfd_tunnel/{tunnel}/configurations", json={"config": {"ingress": ingress}})

    def dns(self, zone: str, hostname: str, tunnel: str) -> str:
        target = f"{tunnel}.cfargotunnel.com"
        record = {"type": "CNAME", "name": hostname, "content": target, "proxied": True}
        existing = self.call("GET", f"/zones/{zone}/dns_records", params={"name": hostname})
        if not existing:
            self.call("POST", f"/zones/{zone}/dns_records", json=record)
            return "created"
        if existing[0]["type"] != "CNAME":
            raise CloudflareError(f"{hostname} already has a {existing[0]['type']} record; remove it in Cloudflare first.")
        self.call("PUT", f"/zones/{zone}/dns_records/{existing[0]['id']}", json=record)
        return "updated"
