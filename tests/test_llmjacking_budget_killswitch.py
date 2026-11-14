"""Execute the template's Python block offline; never import cloud SDKs."""

import base64
import json
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "templates/llmjacking-defense-checklist-prompt.md"
)


def load_handler():
    blocks = re.findall(
        r"^```python\n(.*?)^```", TEMPLATE.read_text(encoding="utf-8"), re.M | re.S
    )
    if len(blocks) != 1:
        raise ValueError("Expected exactly one executable Python block")
    namespace = {}
    exec(compile(blocks[0], str(TEMPLATE), "exec"), namespace)
    return namespace["stop_billing"]


class BudgetKillswitchTests(unittest.TestCase):
    def setUp(self):
        self.service = MagicMock()
        self.projects = self.service.projects.return_value
        self.info = {"billingEnabled": True}
        self.projects.getBillingInfo.return_value.execute.side_effect = (
            lambda: self.info.copy()
        )

        def detach():
            self.info["billingEnabled"] = False
            return self.info.copy()

        self.projects.updateBillingInfo.return_value.execute.side_effect = detach
        self.discovery = SimpleNamespace(build=MagicMock(return_value=self.service))
        self.modules = patch.dict(sys.modules, {
            "googleapiclient": SimpleNamespace(discovery=self.discovery),
            "functions_framework": SimpleNamespace(cloud_event=lambda f: f),
        })
        self.env = patch.dict(os.environ, {
            "TARGET_PROJECT_ID": "example-project",
            "EXPECTED_BUDGET_ID": "budget-1",
            "BILLING_ACCOUNT_ID": "billing-1",
            "ENABLE_BILLING_DISABLE": "true",
        })
        self.modules.start()
        self.env.start()
        self.addCleanup(self.modules.stop)
        self.addCleanup(self.env.stop)
        self.handler = load_handler()

    def event(self, cost=50, budget=50, **changes):
        payload = {"costAmount": cost, "budgetAmount": budget, "currencyCode": "USD"}
        payload.update(changes)
        return self.raw_event(json.dumps(payload).encode())

    def raw_event(self, raw):
        return SimpleNamespace(data={"message": {
            "data": base64.b64encode(raw).decode(),
            "attributes": {"budgetId": "budget-1", "billingAccountId": "billing-1"},
        }})

    def test_cost_0_1_49_do_not_detach(self):
        for cost in (0, 1, 49):
            with self.subTest(cost=cost):
                self.assertEqual(self.handler(self.event(cost)), "below-budget")
        self.discovery.build.assert_not_called()
        self.projects.updateBillingInfo.assert_not_called()

    def test_cost_50_detaches_at_equality_and_uses_fixed_target(self):
        self.assertEqual(self.handler(self.event()), "disabled")
        self.projects.getBillingInfo.assert_called_once_with(
            name="projects/example-project"
        )
        self.projects.updateBillingInfo.assert_called_once_with(
            name="projects/example-project", body={"billingAccountName": ""}
        )
        self.projects.updateBillingInfo.return_value.execute.assert_called_once()

    def test_over_budget_and_fractional_cost_detach(self):
        for cost, budget in ((51, 50), (0.3, 0.3)):
            with self.subTest(cost=cost):
                self.info["billingEnabled"] = True
                self.assertEqual(self.handler(self.event(cost, budget)), "disabled")

    def test_redelivery_and_new_handler_are_idempotent(self):
        event = self.event()
        self.assertEqual(self.handler(event), "disabled")
        self.assertEqual(load_handler()(event), "already-disabled")
        self.projects.updateBillingInfo.assert_called_once()

    def test_already_disabled_does_not_update(self):
        self.info["billingEnabled"] = False
        self.assertEqual(self.handler(self.event()), "already-disabled")
        self.projects.updateBillingInfo.assert_not_called()

    def test_simulation_is_default_and_requires_explicit_enable(self):
        for flag in (None, "false", "TRUE", ""):
            with self.subTest(flag=flag):
                if flag is None:
                    os.environ.pop("ENABLE_BILLING_DISABLE", None)
                else:
                    os.environ["ENABLE_BILLING_DISABLE"] = flag
                self.assertEqual(self.handler(self.event()), "simulated")
        self.projects.updateBillingInfo.assert_not_called()

    def test_invalid_schema_and_empty_input_raise_without_cloud_calls(self):
        invalid = [b"", b"not json", b"[]", b"null", b"{}", b'"text"',
                   b'{"costAmount":50,"costAmount":0,"budgetAmount":50,"currencyCode":"USD"}']
        for field in ("costAmount", "budgetAmount"):
            for value in (None, True, "50", [], {}, float("nan"), float("inf"), -1):
                payload = {"costAmount": 50, "budgetAmount": 50, "currencyCode": "USD"}
                payload[field] = value
                invalid.append(json.dumps(payload).encode())
        invalid.append(b'{"costAmount":0,"budgetAmount":0,"currencyCode":"USD"}')
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.handler(self.raw_event(raw))
        self.discovery.build.assert_not_called()

    def test_bad_envelope_base64_identity_and_currency_raise(self):
        events = [SimpleNamespace(data=data) for data in
                  (None, {}, [], {"message": None}, {"message": {"data": "!"}})]
        for value in ("", "not-base64!", None, 50):
            event = self.event()
            event.data["message"]["data"] = value
            events.append(event)
        for field in ("budgetId", "billingAccountId"):
            event = self.event()
            event.data["message"]["attributes"][field] = "wrong"
            events.append(event)
        for attrs in (None, {}, []):
            event = self.event()
            event.data["message"]["attributes"] = attrs
            events.append(event)
        events.extend([self.event(currencyCode="EUR"), self.event(currencyCode=None)])
        for event in events:
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.handler(event)
        self.discovery.build.assert_not_called()

    def test_missing_or_invalid_configuration_raises(self):
        for name in ("TARGET_PROJECT_ID", "EXPECTED_BUDGET_ID", "BILLING_ACCOUNT_ID"):
            with self.subTest(name=name), patch.dict(os.environ):
                os.environ.pop(name)
                with self.assertRaises(ValueError):
                    self.handler(self.event())
        with patch.dict(os.environ, {"TARGET_PROJECT_ID": "projects/other-project"}):
            with self.assertRaises(ValueError):
                self.handler(self.event())
        self.discovery.build.assert_not_called()

    def test_unknown_billing_state_and_api_failure_are_not_success(self):
        for info in ({}, {"billingEnabled": None}, {"billingEnabled": "false"}):
            self.info = info
            with self.subTest(info=info), self.assertRaises(ValueError):
                self.handler(self.event())
        self.projects.updateBillingInfo.assert_not_called()
        self.projects.getBillingInfo.return_value.execute.side_effect = RuntimeError(
            "permission denied"
        )
        with self.assertRaisesRegex(RuntimeError, "permission denied"):
            self.handler(self.event())

    def test_update_failure_is_retriable_and_not_cached(self):
        request = self.projects.updateBillingInfo.return_value
        request.execute.side_effect = RuntimeError("temporary failure")
        with self.assertRaisesRegex(RuntimeError, "temporary failure"):
            self.handler(self.event())
        request.execute.side_effect = lambda: {"billingEnabled": False}
        self.assertEqual(self.handler(self.event()), "disabled")
        self.assertEqual(request.execute.call_count, 2)


class DocumentationRegressionTests(unittest.TestCase):
    """Guard reviewed corrections; these checks do not verify external facts."""

    def test_budget_limit_and_case_evidence_are_qualified(self):
        text = (TEMPLATE.parents[1] / "docs/llmjacking-cloud-defense-spec.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("延遲式自動停用", text)
        self.assertIn("仍可能超支", text)
        self.assertIn("來源自述（未查證原文）", text)
        self.assertIn("個案鑑別推測", text)
        self.assertIn("已確認的一般威脅指標", text)
        self.assertNotIn("能徹底阻斷", text)
        for source in (
            "disable-billing-with-notifications#limitations",
            "docs.aws.amazon.com/cost-management/",
            "learn.microsoft.com/en-us/azure/cost-management-billing/",
        ):
            self.assertIn(source, text)

    def test_terraform_uses_project_number_and_catalog_service_ids(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        hcl = re.findall(r"^```hcl\n(.*?)^```", text, re.M | re.S)
        self.assertEqual(len(hcl), 1)
        self.assertIn('projects/${data.google_project.target.number}', hcl[0])
        self.assertIn('"services/${id}"', hcl[0])
        self.assertNotIn('aiplatform.googleapis.com', hcl[0])
        self.assertIn('google_pubsub_topic_iam_member.budget_publisher', hcl[0])
        self.assertIn('schema_version = "1.0"', hcl[0])
        self.assertIn("## 5. AWS", text)
        self.assertIn("bedrock:InvokeModelWithResponseStream", text)

    def test_harness_units_and_official_risk_are_attributed(self):
        text = (
            TEMPLATE.parents[1] / "docs/harness2-recursive-agent-harnessing-spec.md"
        ).read_text(encoding="utf-8")
        self.assertIn("+11.8 個百分點", text)
        self.assertNotIn("+11.8%", text)
        self.assertIn("作者報告", text)
        self.assertIn("partial pass rate", text)
        self.assertIn("#web-access", text)
        self.assertIn("不是已發生答案洩漏或作弊的證據", text)
        self.assertNotIn("導致 Benchmark 答案洩漏", text)


if __name__ == "__main__":
    unittest.main()
