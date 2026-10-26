#!/usr/bin/env python3
"""空間幾何契約校驗：量測 vs 模型、單位/軸向、物體與房間邊界、相機內參投影誤差。

規範見 docs/scan-to-threejs-spatial-agent-spec.md。只用標準庫。
這是「幾何計算」工具，不是關鍵字檢查：所有判定都來自座標與矩陣運算。

輸入 JSON（scene）：
{
  "units": "meters", "up_axis": "+Y", "handedness": "right",
  "room": {"floor_y": 0, "ceiling_y": 2.6, "footprint": [[x,z], ...]},
  "objects": [{"id", "center": [x,y,z], "size": [w,h,d], "rotation_y_deg": 0,
               "support": "floor" | "<另一物體 id>" | "none"}],
  "measurements": [{"id", "measured_m", "model_m", "tolerance_m"}],
  "camera": {"intrinsics": {"fx","fy","cx","cy","width","height"},
             "camera_to_world": [16 個數字, column-major],
             "convention": "arkit",
             "landmarks": [{"id", "world": [x,y,z], "pixel": [u,v]}],
             "max_reproj_px": 8.0}
}
退出碼：0 通過、1 有 error 級發現、2 輸入無法解析。
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

POS_TOL = 0.02  # 公尺：貼地、貼牆的位置容許誤差
ROT_TOL = 1e-3  # 旋轉矩陣正交性容許誤差

# ---------------------------------------------------------------- 基礎幾何


def mat_from_column_major(values):
    """16 個數字（column-major，Three.js Matrix4.elements / ARKit simd_float4x4 同序）→ 4x4 列表。"""
    if len(values) != 16:
        raise ValueError("camera_to_world 需要 16 個數字")
    return [[float(values[c * 4 + r]) for c in range(4)] for r in range(4)]


def rigid_inverse(m):
    """剛體變換 [R|t] 的反矩陣；R 非正交（含縮放或鏡像）時丟 ValueError。"""
    r = [[m[i][j] for j in range(3)] for i in range(3)]
    for i in range(3):
        for j in range(3):
            dot = sum(r[k][i] * r[k][j] for k in range(3))
            if abs(dot - (1.0 if i == j else 0.0)) > ROT_TOL:
                raise ValueError("camera_to_world 的旋轉部分不是正交矩陣（含縮放或錯位）")
    det = (
        r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1])
        - r[0][1] * (r[1][0] * r[2][2] - r[1][2] * r[2][0])
        + r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0])
    )
    if det < 0:
        raise ValueError("camera_to_world 行列式為負：含鏡像（左右手系被翻轉）")
    t = [m[i][3] for i in range(3)]
    rt = [[r[j][i] for j in range(3)] for i in range(3)]
    tp = [-sum(rt[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [rt[0] + [tp[0]], rt[1] + [tp[1]], rt[2] + [tp[2]], [0.0, 0.0, 0.0, 1.0]]


def apply(m, p):
    return [sum(m[i][k] * p[k] for k in range(3)) + m[i][3] for i in range(3)]


def project_point(world, camera_to_world, k, convention="arkit"):
    """世界座標 → 像素 (u, v, depth)。depth <= 0 代表在相機後方，回傳 None。

    arkit 約定（= Three.js 相機）：相機看向 -Z、+Y 向上、+X 向右；像素原點在左上、v 向下。
        d = -Zc;  u = cx + fx*Xc/d;  v = cy - fy*Yc/d
    opencv 約定：相機看向 +Z、+Y 向下。
        d = Zc;   u = cx + fx*Xc/d;  v = cy + fy*Yc/d
    """
    w2c = rigid_inverse(camera_to_world)
    xc, yc, zc = apply(w2c, world)
    if convention == "arkit":
        d = -zc
        if d <= 1e-9:
            return None
        return k["cx"] + k["fx"] * xc / d, k["cy"] - k["fy"] * yc / d, d
    if convention == "opencv":
        d = zc
        if d <= 1e-9:
            return None
        return k["cx"] + k["fx"] * xc / d, k["cy"] + k["fy"] * yc / d, d
    raise ValueError(f"未知相機約定：{convention}")


def vertical_fov_deg(fy, height):
    """Three.js PerspectiveCamera.fov（垂直、度）= 2*atan(H / (2*fy))；主點置中時成立。"""
    return math.degrees(2.0 * math.atan(height / (2.0 * fy)))


def z_up_to_y_up(p):
    """Z-up、右手系（多數 CAD/部分 USD）→ Y-up、右手系：(x, y, z) -> (x, z, -y)。"""
    return [p[0], p[2], -p[1]]


def box_corners_xz(center, size, rot_y_deg):
    """物體在 XZ 平面的 4 個角。Three.js 繞 +Y 旋轉 θ：x' = x cosθ + z sinθ, z' = -x sinθ + z cosθ。"""
    th = math.radians(rot_y_deg)
    c, s = math.cos(th), math.sin(th)
    hx, hz = size[0] / 2.0, size[2] / 2.0
    out = []
    for lx, lz in ((-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)):
        out.append((center[0] + lx * c + lz * s, center[2] - lx * s + lz * c))
    return out


def _dist_point_segment(p, a, b):
    ax, az = a
    bx, bz = b
    dx, dz = bx - ax, bz - az
    L2 = dx * dx + dz * dz
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - az) * dz) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (az + t * dz))


def point_in_polygon(p, poly, tol=POS_TOL):
    """射線法；距離邊界在 tol 內視為在內（物體貼牆不算穿牆）。"""
    n = len(poly)
    for i in range(n):
        if _dist_point_segment(p, poly[i], poly[(i + 1) % n]) <= tol:
            return True
    inside = False
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > p[1]) != (z2 > p[1]):
            if p[0] < (x2 - x1) * (p[1] - z1) / (z2 - z1) + x1:
                inside = not inside
    return inside


# ---------------------------------------------------------------- 檢查


def _f(severity, code, message):
    return {"severity": severity, "code": code, "message": message}


def check_frame(scene):
    out = []
    if scene.get("units") != "meters":
        out.append(_f("error", "UNITS_NOT_METERS", f"units 宣告為 {scene.get('units')!r}，契約要求 'meters'"))
    if scene.get("up_axis") != "+Y":
        out.append(_f("error", "UP_AXIS_NOT_PLUS_Y", f"up_axis 為 {scene.get('up_axis')!r}，契約要求 '+Y'（Z-up 資料請先用 z_up_to_y_up 轉換）"))
    if scene.get("handedness") != "right":
        out.append(_f("error", "NOT_RIGHT_HANDED", f"handedness 為 {scene.get('handedness')!r}，契約要求 'right'"))
    return out


def check_room(scene):
    out = []
    room = scene.get("room")
    if not room:
        return [_f("error", "NO_ROOM", "缺少 room")]
    floor_y, ceil_y = float(room["floor_y"]), float(room["ceiling_y"])
    height = ceil_y - floor_y
    if height <= 0:
        out.append(_f("error", "Y_INVERTED", f"ceiling_y({ceil_y}) <= floor_y({floor_y})：Y 軸被倒置或天花板/地板互換"))
        return out
    if abs(floor_y) > POS_TOL:
        out.append(_f("error", "FLOOR_NOT_ZERO", f"floor_y={floor_y}，契約要求地面在 Y=0（容許 ±{POS_TOL} m）"))
    # 單位尺度推測：住宅天花板高度合理範圍 2.0~4.5 m
    if not 2.0 <= height <= 4.5:
        hint = ""
        for factor, name in ((100.0, "公分"), (1000.0, "公釐"), (39.3701, "英寸"), (3.28084, "英尺")):
            if 2.0 <= height / factor <= 4.5:
                hint = f"；若實際單位是{name}，換算後高度為 {height / factor:.2f} m"
                break
        out.append(_f("error", "UNITS_SCALE_SUSPECT", f"房間高度 {height:.3f} m 不在住宅合理範圍 2.0~4.5 m{hint}"))
    fp = room.get("footprint") or []
    if len(fp) < 3:
        out.append(_f("error", "BAD_FOOTPRINT", "footprint 至少需要 3 個點"))
    return out


def check_objects(scene):
    out = []
    room = scene.get("room") or {}
    if "footprint" not in room or "floor_y" not in room:
        return out
    poly = [tuple(p) for p in room["footprint"]]
    floor_y, ceil_y = float(room["floor_y"]), float(room["ceiling_y"])
    objs = {o["id"]: o for o in scene.get("objects", [])}
    below = 0
    for o in objs.values():
        cx, cy, cz = o["center"]
        h = o["size"][1]
        lo, hi = cy - h / 2.0, cy + h / 2.0
        oid = o["id"]
        if lo < floor_y - POS_TOL:
            below += 1
            out.append(_f("error", "OBJECT_BELOW_FLOOR", f"{oid}: 最低點 y={lo:.3f} 低於地板 {floor_y}"))
        if hi > ceil_y + POS_TOL:
            out.append(_f("error", "OBJECT_ABOVE_CEILING", f"{oid}: 最高點 y={hi:.3f} 高於天花板 {ceil_y}"))
        bad = [c for c in box_corners_xz(o["center"], o["size"], o.get("rotation_y_deg", 0.0)) if not point_in_polygon(c, poly)]
        if bad:
            out.append(_f("error", "OBJECT_OUTSIDE_ROOM", f"{oid}: {len(bad)}/4 個角落在房間圍牆外（例 x={bad[0][0]:.3f}, z={bad[0][1]:.3f}）"))
        support = o.get("support", "floor")
        if support == "floor":
            gap = lo - floor_y
            if gap > POS_TOL:
                out.append(_f("error", "OBJECT_FLOATING", f"{oid}: support=floor 但底面離地 {gap:.3f} m（懸空）"))
        elif support in objs and support != oid:
            s = objs[support]
            top = s["center"][1] + s["size"][1] / 2.0
            if abs(lo - top) > POS_TOL:
                out.append(_f("error", "OBJECT_NOT_ON_SUPPORT", f"{oid}: 底面 y={lo:.3f} 與 {support} 頂面 y={top:.3f} 差 {abs(lo - top):.3f} m"))
        elif support not in ("none",):
            out.append(_f("error", "BAD_SUPPORT", f"{oid}: support={support!r} 不是 floor/none/既有物體 id"))
    if objs and below == len(objs):
        out.append(_f("error", "Y_INVERTED", "所有物體都在地板下方：Y 軸疑似倒置（或 floor_y 設錯）"))
    return out


def check_measurements(scene):
    out = []
    for m in scene.get("measurements", []):
        measured, model = float(m["measured_m"]), float(m["model_m"])
        tol = float(m.get("tolerance_m", 0.05))
        err = abs(measured - model)
        if err > tol:
            hint = ""
            if measured > 0 and model > 0:
                ratio = model / measured
                for factor, name in ((100.0, "100 倍（公分↔公尺）"), (1000.0, "1000 倍（公釐↔公尺）"), (25.4, "25.4 倍（英寸↔公釐）"), (39.3701, "39.37 倍（英寸↔公尺）")):
                    if abs(ratio - factor) / factor < 0.02 or abs(ratio - 1 / factor) * factor < 0.02:
                        hint = f"；模型/量測比 {ratio:.4g} ≈ {name}，疑似單位錯"
                        break
            out.append(_f("error", "MEASUREMENT_MISMATCH", f"{m['id']}: 量測 {measured:.3f} m vs 模型 {model:.3f} m，差 {err:.3f} m > 容許 {tol} m{hint}"))
    return out


def reprojection_errors(camera, convention):
    k = camera["intrinsics"]
    c2w = mat_from_column_major(camera["camera_to_world"])
    errs = []
    for lm in camera.get("landmarks", []):
        p = project_point(lm["world"], c2w, k, convention)
        if p is None:
            errs.append((lm["id"], None, None))
            continue
        errs.append((lm["id"], math.hypot(p[0] - lm["pixel"][0], p[1] - lm["pixel"][1]), p))
    return errs


def _rms(errs):
    vals = [e for _, e, _ in errs if e is not None]
    if len(vals) != len(errs) or not vals:
        return None  # 有點在相機後方：此約定不成立
    return math.sqrt(sum(v * v for v in vals) / len(vals))


def check_camera(scene):
    cam = scene.get("camera")
    if not cam:
        return []
    out = []
    k = cam["intrinsics"]
    w, h = k["width"], k["height"]
    if not (0 <= k["cx"] <= w and 0 <= k["cy"] <= h):
        out.append(_f("error", "PRINCIPAL_POINT_OUTSIDE_IMAGE", f"主點 ({k['cx']}, {k['cy']}) 在影像 {w}x{h} 之外：內參與影像解析度不對應（需依 intrinsicMatrixReferenceDimensions 縮放，或影像被旋轉過）"))
    if k["fx"] <= 0 or k["fy"] <= 0:
        out.append(_f("error", "BAD_FOCAL", "fx/fy 必須為正"))
        return out
    declared = cam.get("convention", "arkit")
    limit = float(cam.get("max_reproj_px", 8.0))
    try:
        main = _rms(reprojection_errors(cam, declared))
    except ValueError as e:
        return out + [_f("error", "BAD_CAMERA_POSE", str(e))]
    if main is not None and main <= limit:
        return out
    detail = "有地標落在相機後方" if main is None else f"RMS 重投影誤差 {main:.2f}px > 容許 {limit}px"
    # 診斷：其他約定能不能解釋？
    hints = []
    for conv in ("arkit", "opencv"):
        if conv == declared:
            continue
        try:
            r = _rms(reprojection_errors(cam, conv))
        except ValueError:
            r = None
        if r is not None and r <= limit:
            hints.append(f"改用 {conv} 約定可擬合（RMS {r:.2f}px）：相機軸向約定宣告錯誤")
    # 診斷：位姿被反（world_to_camera 當成 camera_to_world）
    try:
        inv = [row[:] for row in rigid_inverse(mat_from_column_major(cam["camera_to_world"]))]
        cam2 = dict(cam, camera_to_world=[inv[r][c] for c in range(4) for r in range(4)])
        r = _rms(reprojection_errors(cam2, declared))
        if r is not None and r <= limit:
            hints.append(f"把位姿取反後可擬合（RMS {r:.2f}px）：矩陣方向（camera_to_world vs world_to_camera）搞反")
    except ValueError:
        pass
    out.append(_f("error", "REPROJECTION_ERROR", detail + ("；" + "；".join(hints) if hints else "")))
    return out


def verify(scene):
    findings = []
    for fn in (check_frame, check_room, check_objects, check_measurements, check_camera):
        findings.extend(fn(scene))
    return findings


# ---------------------------------------------------------------- CLI


def _utf8():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def main(argv=None):
    _utf8()
    ap = argparse.ArgumentParser(description="空間幾何契約校驗（單位、軸向、邊界、量測誤差、相機重投影）。")
    ap.add_argument("scene", help="scene JSON 路徑")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出發現")
    args = ap.parse_args(argv)
    try:
        scene = json.loads(Path(args.scene).read_text(encoding="utf-8"))
        findings = verify(scene)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"[ERROR] 輸入無法解析：{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['code']}: {f['message']}")
        print("[PASS] 空間契約通過" if not errors else f"[FAIL] {len(errors)} 項違反")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
