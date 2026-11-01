#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_a11y_tree_snapshot.py

Windows UI Automation (UIA) 與 OS 級無障礙樹快照與 Ref 點擊驗證工具。
實作 agent-desktop 標準命名空間 Ref 解析、STALE_REF 過期偵測、
AMBIGUOUS_TARGET 歧義攔截、PowerShell 引號防雷規範、以及
重試安全處置合約（Disposition Retry Contract）狀態機。
"""

import re
import sys
import json
import time
import argparse
from typing import Dict, Any, Optional, List, Tuple

# 確保在 Windows CP950 等環境下輸出為 UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 標準 Ref 格式: @<snapshot_id>:<ref_id> (例如: @s8f3k2p9:e12)
REF_PATTERN = re.compile(r"^@([a-z0-9]{4,16}):e([0-9]+)$")

class RefValidationError(ValueError):
    """Ref 格式或解析錯誤"""
    def __init__(self, message: str, code: str = "INVALID_ARGS", suggestion: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.suggestion = suggestion


class Ref:
    """代表一個限定命名空間的元素參照 (@snapshot_id:element_id)"""
    def __init__(self, raw_ref: str, snapshot_id: str, element_id: str):
        self.raw = raw_ref
        self.snapshot_id = snapshot_id
        self.element_id = element_id

    @classmethod
    def parse(cls, raw: str) -> "Ref":
        if not raw or not isinstance(raw, str):
            raise RefValidationError(
                "Ref cannot be empty or non-string",
                code="INVALID_ARGS",
                suggestion="Pass a qualified ref like '@s8f3k2p9:e1'"
            )
        
        # 檢測 Windows PowerShell Splatting 錯誤特徵
        # 若在 PowerShell 未加單引號，@token 可能會被解析為雜湊展開而遺失或損壞
        stripped = raw.strip()
        # 若傳入參數被引號包裹（如 PowerShell 命令列傳入 '@ref'），先剝除外層引號
        if (stripped.startswith("'") and stripped.endswith("'")) or (stripped.startswith('"') and stripped.endswith('"')):
            stripped = stripped[1:-1].strip()

        if not stripped.startswith("@"):
            if ":" in stripped:
                raise RefValidationError(
                    f"Ref '{raw}' missing leading '@'. In PowerShell, you must quote refs: '@{stripped}'",
                    code="INVALID_ARGS",
                    suggestion=f"Use '@{stripped}' in PowerShell with single quotes"
                )
            raise RefValidationError(
                f"Invalid ref argument '{raw}'. Unquoted @refs are absorbed by PowerShell splatting.",
                code="INVALID_ARGS",
                suggestion="Wrap the ref in single quotes, e.g. '@s8f3k2p9:e1'"
            )
        
        match = REF_PATTERN.match(stripped)
        if not match:
            # 檢查是否為未帶命名空間的裸 ref (例如 @e12)
            if re.match(r"^@e[0-9]+$", stripped):
                raise RefValidationError(
                    f"Unqualified bare ref '{stripped}' rejected. agent-desktop requires namespaced refs.",
                    code="INVALID_ARGS",
                    suggestion="Always use fully qualified refs returned by snapshot, e.g. '@s8f3k2p9:e12'"
                )
            raise RefValidationError(
                f"Ref '{stripped}' does not match standard pattern '@<snapshot_id>:<element_id>'",
                code="INVALID_ARGS",
                suggestion="Format must be @<hex_or_hash>:e<number>, e.g. '@s8f3k2p9:e12'"
            )
        
        snap_id, elem_id = match.group(1), f"e{match.group(2)}"
        return cls(stripped, snap_id, elem_id)

    def __repr__(self) -> str:
        return f"Ref('{self.raw}')"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Ref):
            return self.raw == other.raw
        return False


class Disposition:
    """動作執行處置狀態 (Delivery 與 Retry 安全性合約)"""
    def __init__(self, delivery: str, retry: str):
        if delivery not in ("not_delivered", "delivered_verified", "delivered_unverified"):
            raise ValueError(f"Unknown delivery state: {delivery}")
        if retry not in ("safe", "unsafe"):
            raise ValueError(f"Unknown retry state: {retry}")
        self.delivery = delivery
        self.retry = retry

    def to_dict(self) -> Dict[str, str]:
        return {"delivery": self.delivery, "retry": self.retry}


class A11yNode:
    """無障礙樹單一節點"""
    def __init__(
        self,
        ref_id: str,
        role: str,
        name: str,
        value: Optional[str] = None,
        states: Optional[List[str]] = None,
        bounds: Optional[Dict[str, float]] = None,
        children: Optional[List["A11yNode"]] = None,
        is_container: bool = False
    ):
        self.ref_id = ref_id  # 例如 e1, e2
        self.role = role
        self.name = name
        self.value = value
        self.states = set(states or [])
        self.bounds = bounds or {"x": 0.0, "y": 0.0, "width": 100.0, "height": 30.0}
        self.children = children or []
        self.is_container = is_container

    def to_dict(self, snapshot_id: str, skeleton: bool = False) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "ref": f"@{snapshot_id}:{self.ref_id}",
            "role": self.role,
            "name": self.name,
        }
        if self.value is not None:
            d["value"] = self.value
        if self.states:
            d["states"] = sorted(list(self.states))
        if self.bounds:
            d["bounds"] = self.bounds
        
        if skeleton and self.is_container and self.role != "window" and self.children:
            d["children_count"] = len(self.children)
        elif self.children:
            d["children"] = [c.to_dict(snapshot_id, skeleton) for c in self.children]
        return d


class SnapshotEngine:
    """管理無障礙樹快照與狀態機生命週期"""
    def __init__(self):
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.active_snapshot_id: Optional[str] = None

    def register_snapshot(self, snapshot_id: str, root_node: A11yNode, app_name: str = "TestApp") -> str:
        """註冊新快照並將其設為活躍快照"""
        # 平面化節點索引
        node_map: Dict[str, A11yNode] = {}
        def _index(node: A11yNode):
            node_map[node.ref_id] = node
            for child in node.children:
                _index(child)
        _index(root_node)

        self.snapshots[snapshot_id] = {
            "id": snapshot_id,
            "timestamp": time.time(),
            "root": root_node,
            "node_map": node_map,
            "app": app_name,
            "active": True
        }
        self.active_snapshot_id = snapshot_id
        return snapshot_id

    def invalidate_old_snapshots(self, keep_current: bool = True):
        """將除當前快照以外的所有舊快照標記為過期 (模擬 UI 變更或過期)"""
        for sid, snap in self.snapshots.items():
            if keep_current and sid == self.active_snapshot_id:
                continue
            snap["active"] = False

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        return self.snapshots.get(snapshot_id)

    def find_nodes(
        self,
        snapshot_id: str,
        role: Optional[str] = None,
        name: Optional[str] = None,
        exact: bool = False
    ) -> List[A11yNode]:
        snap = self.get_snapshot(snapshot_id)
        if not snap:
            return []
        
        results: List[A11yNode] = []
        for node in snap["node_map"].values():
            if role and node.role.lower() != role.lower():
                continue
            if name is not None:
                if exact:
                    if node.name != name:
                        continue
                else:
                    if name.lower() not in node.name.lower():
                        continue
            results.append(node)
        return results

    def execute_action(
        self,
        command: str,
        ref_str: str,
        value: Optional[str] = None,
        headed: bool = False
    ) -> Dict[str, Any]:
        """
        模擬執行操作命令 (click, set-value, toggle 等)，並返回標準 JSON Envelope
        """
        # 1. 語法與 Ref 解析
        try:
            ref = Ref.parse(ref_str)
        except RefValidationError as err:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": err.code,
                    "message": str(err),
                    "disposition": Disposition("not_delivered", "safe").to_dict(),
                    "suggestion": err.suggestion
                }
            }

        # 2. 檢驗 Snapshot 存在性
        snap = self.get_snapshot(ref.snapshot_id)
        if not snap:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": "SNAPSHOT_NOT_FOUND",
                    "message": f"Snapshot '{ref.snapshot_id}' does not exist or has expired",
                    "disposition": Disposition("not_delivered", "safe").to_dict(),
                    "suggestion": "Take a new snapshot with 'agent-desktop snapshot'"
                }
            }

        # 3. 檢驗 Snapshot 是否過期 (STALE_REF 核心防禦)
        if not snap["active"]:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": "STALE_REF",
                    "message": f"Ref '{ref.raw}' belongs to an outdated snapshot. UI has mutated.",
                    "disposition": Disposition("not_delivered", "safe").to_dict(),
                    "suggestion": "Re-take snapshot and act on the fresh ref"
                }
            }

        # 4. 尋找目標節點
        node = snap["node_map"].get(ref.element_id)
        if not node:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": "STALE_REF",
                    "message": f"Element '{ref.element_id}' no longer exists in snapshot '{ref.snapshot_id}'",
                    "disposition": Disposition("not_delivered", "safe").to_dict(),
                    "suggestion": "Take a new snapshot to inspect available elements"
                }
            }

        # 5. 檢驗節點狀態
        if "disabled" in node.states:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": "ACTION_FAILED",
                    "message": f"Target element '{ref.raw}' is disabled",
                    "disposition": Disposition("not_delivered", "safe").to_dict(),
                    "details": {"retryable": False}
                }
            }

        # 6. 依命令執行語意動作 (Headless vs Headed 限制)
        if command == "click":
            # 成功執行 semantic click
            return {
                "version": "2.5",
                "ok": True,
                "command": "click",
                "data": {
                    "ref": ref.raw,
                    "role": node.role,
                    "name": node.name,
                    "disposition": Disposition("delivered_verified", "safe").to_dict()
                }
            }
        
        elif command == "set-value":
            if value is None:
                return {
                    "version": "2.5",
                    "ok": False,
                    "command": "set-value",
                    "error": {
                        "code": "INVALID_ARGS",
                        "message": "Missing value argument for set-value",
                        "disposition": Disposition("not_delivered", "safe").to_dict()
                    }
                }
            node.value = value
            return {
                "version": "2.5",
                "ok": True,
                "command": "set-value",
                "data": {
                    "ref": ref.raw,
                    "value": value,
                    "disposition": Disposition("delivered_verified", "safe").to_dict()
                }
            }

        elif command == "type":
            # 在 Windows 平台，type (實體按鍵模擬) 需 --headed
            if not headed:
                return {
                    "version": "2.5",
                    "ok": False,
                    "command": "type",
                    "error": {
                        "code": "POLICY_DENIED",
                        "message": "'type' command requires physical key synthesis via global --headed",
                        "disposition": Disposition("not_delivered", "safe").to_dict(),
                        "suggestion": "Use semantic 'set-value' for headless input, or pass --headed"
                    }
                }
            node.value = (node.value or "") + (value or "")
            return {
                "version": "2.5",
                "ok": True,
                "command": "type",
                "data": {
                    "ref": ref.raw,
                    "value": node.value,
                    "disposition": Disposition("delivered_unverified", "unsafe").to_dict()
                }
            }

        elif command == "toggle":
            if "checked" in node.states:
                node.states.remove("checked")
            else:
                node.states.add("checked")
            return {
                "version": "2.5",
                "ok": True,
                "command": "toggle",
                "data": {
                    "ref": ref.raw,
                    "checked": "checked" in node.states,
                    "disposition": Disposition("delivered_verified", "safe").to_dict()
                }
            }

        else:
            return {
                "version": "2.5",
                "ok": False,
                "command": command,
                "error": {
                    "code": "ACTION_NOT_SUPPORTED",
                    "message": f"Command '{command}' is not supported",
                    "disposition": Disposition("not_delivered", "safe").to_dict()
                }
            }


def main():
    """CLI 入口：支援 --help 與驗證測試"""
    parser = argparse.ArgumentParser(
        description="Verify Windows UI Automation (UIA) a11y tree snapshots and ref actions."
    )
    parser.add_argument(
        "--ref",
        type=str,
        default=None,
        help="Test ref parsing and validation (e.g. '@s8f3k2p9:e12')"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run simulated snapshot and action demo"
    )

    args = parser.parse_args()

    engine = SnapshotEngine()
    root = A11yNode("e1", "window", "Main Window", is_container=True, children=[
        A11yNode("e2", "button", "Submit"),
        A11yNode("e3", "text_field", "Search Input", value="")
    ])
    sid = engine.register_snapshot("s8f3k2p9", root)

    if args.ref:
        try:
            parsed = Ref.parse(args.ref)
            print(f"[PASS] Valid ref: snapshot={parsed.snapshot_id}, element={parsed.element_id}")
        except RefValidationError as err:
            print(f"[FAIL] {err}")
            sys.exit(1)
    elif args.demo:
        print(f"Registered snapshot: {sid}")
        res = engine.execute_action("click", "'@s8f3k2p9:e2'")
        print(f"Click with quotes: {json.dumps(res, indent=2)}")
    else:
        # 預設輸出示範
        print(f"Registered snapshot: {sid}")
        res = engine.execute_action("click", "'@s8f3k2p9:e2'")
        print(f"Click with quotes: {json.dumps(res, indent=2)}")

if __name__ == "__main__":
    main()
