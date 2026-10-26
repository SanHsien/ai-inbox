"""tools/verify_spatial_alignment.py 單元測試：正常房間 + 穿牆、懸空、倒置、單位、相機軸向等反例。"""

import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import verify_spatial_alignment as v  # noqa: E402


def look_at_column_major(eye, target, up=(0.0, 1.0, 0.0)):
    """Three.js Matrix4.lookAt 同義：相機 -Z 指向 target。回傳 camera_to_world（column-major 16 值）。"""
    z = [eye[i] - target[i] for i in range(3)]
    n = math.sqrt(sum(a * a for a in z))
    z = [a / n for a in z]
    x = [up[1] * z[2] - up[2] * z[1], up[2] * z[0] - up[0] * z[2], up[0] * z[1] - up[1] * z[0]]
    n = math.sqrt(sum(a * a for a in x))
    x = [a / n for a in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    return x + [0.0] + y + [0.0] + z + [0.0] + list(eye) + [1.0]


K = {"fx": 1500.0, "fy": 1500.0, "cx": 960.0, "cy": 720.0, "width": 1920, "height": 1440}
CORNERS = [(0, 0, 0), (5, 0, 0), (5, 0, 4), (0, 0, 4), (0, 2.6, 0), (5, 2.6, 0), (5, 2.6, 4), (0, 2.6, 4)]


def good_scene():
    c2w = look_at_column_major((2.5, 1.5, 6.0), (2.5, 1.2, 2.0))
    m = v.mat_from_column_major(c2w)
    lms = []
    for i, p in enumerate(CORNERS):
        u, vv, _ = v.project_point(p, m, K, "arkit")
        lms.append({"id": f"c{i}", "world": list(p), "pixel": [u + (1.5 if i % 2 else -1.5), vv + 1.0]})
    return {
        "units": "meters", "up_axis": "+Y", "handedness": "right",
        "room": {"floor_y": 0.0, "ceiling_y": 2.6, "footprint": [[0, 0], [5, 0], [5, 4], [0, 4]]},
        "objects": [
            {"id": "sofa", "center": [1.2, 0.4, 1.0], "size": [2.0, 0.8, 0.9], "rotation_y_deg": 0},
            {"id": "cushion", "center": [1.2, 0.9, 1.0], "size": [0.4, 0.2, 0.4], "support": "sofa"},
            {"id": "tilted", "center": [3.5, 0.5, 2.0], "size": [1.0, 1.0, 1.0], "rotation_y_deg": 45},
        ],
        "measurements": [
            {"id": "width", "measured_m": 5.02, "model_m": 5.0, "tolerance_m": 0.05},
            {"id": "height", "measured_m": 2.58, "model_m": 2.6, "tolerance_m": 0.05},
        ],
        "camera": {"intrinsics": K, "camera_to_world": c2w, "convention": "arkit", "landmarks": lms, "max_reproj_px": 8.0},
    }


def codes(scene):
    return {f["code"] for f in v.verify(scene) if f["severity"] == "error"}


class GoodSceneTest(unittest.TestCase):
    def test_good_scene_passes(self):
        self.assertEqual(v.verify(good_scene()), [])


class FrameAndRoomTest(unittest.TestCase):
    def test_centimeters_declared(self):
        s = good_scene(); s["units"] = "centimeters"
        self.assertIn("UNITS_NOT_METERS", codes(s))

    def test_z_up_declared(self):
        s = good_scene(); s["up_axis"] = "+Z"
        self.assertIn("UP_AXIS_NOT_PLUS_Y", codes(s))

    def test_left_handed(self):
        s = good_scene(); s["handedness"] = "left"
        self.assertIn("NOT_RIGHT_HANDED", codes(s))

    def test_unit_scale_hint_cm_as_m(self):
        s = good_scene(); s["room"]["ceiling_y"] = 260.0  # 公分數值卻宣告公尺
        issues = [f for f in v.verify(s) if f["code"] == "UNITS_SCALE_SUSPECT"]
        self.assertTrue(issues)
        self.assertIn("公分", issues[0]["message"])

    def test_floor_not_zero(self):
        s = good_scene(); s["room"]["floor_y"] = 0.3; s["room"]["ceiling_y"] = 2.9
        self.assertIn("FLOOR_NOT_ZERO", codes(s))

    def test_y_inverted_room(self):
        s = good_scene(); s["room"]["floor_y"], s["room"]["ceiling_y"] = 0.0, -2.6
        self.assertIn("Y_INVERTED", codes(s))

    def test_y_inverted_objects_all_below_floor(self):
        s = good_scene()
        for o in s["objects"]:
            o["center"][1] *= -1
        self.assertIn("Y_INVERTED", codes(s))


class ObjectTest(unittest.TestCase):
    def test_through_wall(self):
        s = good_scene(); s["objects"][0]["center"][0] = 4.6  # 沙發寬 2m，右緣到 5.6 > 5
        self.assertIn("OBJECT_OUTSIDE_ROOM", codes(s))

    def test_touching_wall_is_ok(self):
        s = good_scene(); s["objects"][0]["center"][0] = 4.0  # 右緣剛好 5.0
        self.assertNotIn("OBJECT_OUTSIDE_ROOM", codes(s))

    def test_rotated_box_corner_pokes_out(self):
        s = good_scene()
        s["objects"][2]["center"] = [4.5, 0.5, 2.0]  # 45° 對角線半長 0.707，右角 5.207 > 5
        self.assertIn("OBJECT_OUTSIDE_ROOM", codes(s))
        s["objects"][2]["rotation_y_deg"] = 0  # 不旋轉右緣 5.0，OK
        self.assertNotIn("OBJECT_OUTSIDE_ROOM", codes(s))

    def test_floating(self):
        s = good_scene(); s["objects"][0]["center"][1] = 1.0
        self.assertIn("OBJECT_FLOATING", codes(s))

    def test_floating_allowed_when_support_none(self):
        s = good_scene(); s["objects"][0]["center"][1] = 1.0; s["objects"][0]["support"] = "none"
        self.assertNotIn("OBJECT_FLOATING", codes(s))

    def test_below_floor(self):
        s = good_scene(); s["objects"][0]["center"][1] = 0.1
        self.assertIn("OBJECT_BELOW_FLOOR", codes(s))

    def test_above_ceiling(self):
        s = good_scene(); s["objects"][0]["center"][1] = 2.5
        self.assertIn("OBJECT_ABOVE_CEILING", codes(s))

    def test_not_on_support(self):
        s = good_scene(); s["objects"][1]["center"][1] = 1.5
        self.assertIn("OBJECT_NOT_ON_SUPPORT", codes(s))

    def test_concave_footprint(self):
        s = good_scene()  # L 形房間：缺角 (3..5, 2..4)
        s["room"]["footprint"] = [[0, 0], [5, 0], [5, 2], [3, 2], [3, 4], [0, 4]]
        s["objects"] = [{"id": "in_notch", "center": [4.0, 0.5, 3.0], "size": [0.5, 1.0, 0.5]}]
        s["camera"]["landmarks"] = []
        self.assertIn("OBJECT_OUTSIDE_ROOM", codes(s))


class MeasurementTest(unittest.TestCase):
    def test_mismatch(self):
        s = good_scene(); s["measurements"][0]["model_m"] = 4.5
        self.assertIn("MEASUREMENT_MISMATCH", codes(s))

    def test_unit_ratio_hint(self):
        s = good_scene(); s["measurements"] = [{"id": "w", "measured_m": 5.0, "model_m": 500.0}]
        msg = [f["message"] for f in v.verify(s) if f["code"] == "MEASUREMENT_MISMATCH"][0]
        self.assertIn("100", msg)

    def test_within_tolerance(self):
        s = good_scene(); s["measurements"][0]["model_m"] = 5.04
        self.assertNotIn("MEASUREMENT_MISMATCH", codes(s))


class CameraTest(unittest.TestCase):
    def test_projection_center(self):
        c2w = look_at_column_major((0, 1, 5), (0, 1, 0))
        u, vv, d = v.project_point((0, 1, 0), v.mat_from_column_major(c2w), K, "arkit")
        self.assertAlmostEqual(u, K["cx"], places=6)
        self.assertAlmostEqual(vv, K["cy"], places=6)
        self.assertAlmostEqual(d, 5.0, places=6)

    def test_up_is_smaller_v(self):
        c2w = look_at_column_major((0, 1, 5), (0, 1, 0))
        _, v_up, _ = v.project_point((0, 2, 0), v.mat_from_column_major(c2w), K, "arkit")
        self.assertLess(v_up, K["cy"])  # 世界 +Y 往上，像素 v 往下增加，所以上方 v 更小

    def test_point_behind_camera(self):
        c2w = look_at_column_major((0, 1, 5), (0, 1, 0))
        self.assertIsNone(v.project_point((0, 1, 10), v.mat_from_column_major(c2w), K, "arkit"))

    def test_vertical_fov(self):
        self.assertAlmostEqual(v.vertical_fov_deg(720.0, 1440), 90.0, places=6)

    def test_pixel_offset_too_big(self):
        s = good_scene(); s["camera"]["landmarks"][0]["pixel"][0] += 80
        s["camera"]["max_reproj_px"] = 8.0
        self.assertIn("REPROJECTION_ERROR", codes(s))

    def test_wrong_convention_detected_with_hint(self):
        s = good_scene(); s["camera"]["convention"] = "opencv"
        issues = [f for f in v.verify(s) if f["code"] == "REPROJECTION_ERROR"]
        self.assertTrue(issues)
        self.assertIn("arkit", issues[0]["message"])

    def test_inverted_pose_detected_with_hint(self):
        s = good_scene()
        inv = v.rigid_inverse(v.mat_from_column_major(s["camera"]["camera_to_world"]))
        s["camera"]["camera_to_world"] = [inv[r][c] for c in range(4) for r in range(4)]
        issues = [f for f in v.verify(s) if f["code"] == "REPROJECTION_ERROR"]
        self.assertTrue(issues)
        self.assertIn("取反", issues[0]["message"])

    def test_mirrored_pose_rejected(self):
        s = good_scene(); m = s["camera"]["camera_to_world"]
        m[0], m[1], m[2] = -m[0], -m[1], -m[2]  # X 軸取反 → 鏡像
        self.assertIn("BAD_CAMERA_POSE", codes(s))

    def test_scaled_pose_rejected(self):
        s = good_scene(); s["camera"]["camera_to_world"][0] *= 2
        self.assertIn("BAD_CAMERA_POSE", codes(s))

    def test_principal_point_outside_image(self):
        s = good_scene(); s["camera"]["intrinsics"] = dict(K, cx=2400.0)
        self.assertIn("PRINCIPAL_POINT_OUTSIDE_IMAGE", codes(s))


class HelpersTest(unittest.TestCase):
    def test_z_up_to_y_up_keeps_right_handed(self):
        # Z-up 的 x×y = z；轉後 x'×y' 應 = z'
        def cross(a, b):
            return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        x, y, z = (v.z_up_to_y_up(p) for p in ([1, 0, 0], [0, 1, 0], [0, 0, 1]))
        self.assertEqual(cross(x, y), z)
        self.assertEqual(z, [0, 1, 0])  # 原 Z（上）→ Y（上）

    def test_box_corners_rotation_sign(self):
        # 繞 +Y 轉 90°：本地 +X 角 (hx, ., hz) 的 x' = z、z' = -x
        c = v.box_corners_xz([0, 0, 0], [2, 1, 4], 90)
        xs = sorted(round(p[0], 6) for p in c)
        self.assertEqual(xs, [-2.0, -2.0, 2.0, 2.0])


class CliTest(unittest.TestCase):
    def run_cli(self, scene):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "scene.json"
            p.write_text(json.dumps(scene), encoding="utf-8")
            return subprocess.run([sys.executable, str(TOOLS / "verify_spatial_alignment.py"), str(p)], capture_output=True, timeout=60)

    def test_exit_codes(self):
        self.assertEqual(self.run_cli(good_scene()).returncode, 0)
        bad = copy.deepcopy(good_scene()); bad["objects"][0]["center"][1] = 1.0
        proc = self.run_cli(bad)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("OBJECT_FLOATING", proc.stdout.decode("utf-8"))

    def test_unparsable_input(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"; p.write_text("{not json", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(TOOLS / "verify_spatial_alignment.py"), str(p)], capture_output=True, timeout=60)
            self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
