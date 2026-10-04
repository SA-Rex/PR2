from __future__ import annotations


class Denied(PermissionError):
    pass


class SandboxedCaps:
    def __init__(self, allowed: list[str], sink: list[tuple[str, str]]) -> None:
        self._allowed = set(allowed)
        self._sink = sink

    def _require(self, permission: str) -> None:
        if permission not in self._allowed:
            raise Denied(f"permission not declared: {permission}")

    def net(self, host: str, body: str) -> str:
        self._require(f"net:{host}")
        self._sink.append((f"net:{host}", body))
        return f"net-{len(self._sink)}"

    def fs_write(self, name: str, data: str) -> str:
        self._require(f"fs:{name}")
        self._sink.append((f"fs:{name}", data))
        return f"file-{len(self._sink)}"


DENY_ALL = SandboxedCaps([], [])
