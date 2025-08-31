from faker import Faker
import pytest
from hw7.api.employee_api import EmployeeApi

fake = Faker()

def norm_keys(d: dict) -> dict:
    return {str(k).lower(): v for k, v in d.items()}

@pytest.mark.parametrize("changes", [{"position": "QA Engineer", "age": 30}])
def test_employee_e2e_create_info_change(api: EmployeeApi, changes):
    seed = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "age": fake.random_int(min=22, max=55),
        "position": "QA",
        "city": fake.city(),

    }

    resp, emp_id = api.create_with_fallbacks(seed)
    assert 200 <= resp.status_code < 300

    r = api.info(emp_id)
    assert r.status_code == 200, f"info failed: {r.status_code} {r.text}"

    r = api.change(emp_id, changes)
    assert r.status_code in (200, 204), f"change failed: {r.status_code} {r.text}"

    r = api.info(emp_id)
    assert r.status_code == 200, f"info after change failed: {r.status_code} {r.text}"
    data = api._json(r).get("data", {}) or {}
    if isinstance(data, dict):
        got = norm_keys(data)
        for k, v in norm_keys(changes).items():
            if k in got:
                assert got[k] == v, f"change not applied for {k}"
