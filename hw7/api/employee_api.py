import os
import random
import requests
from typing import Any, Dict, Optional, Tuple


class EmployeeApi:
    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None):
        self.base = (base_url or os.getenv("EMP_BASE") or "http://5.101.50.27:8000").rstrip("/")
        self.s = session or requests.Session()

    # utils
    @staticmethod
    def _json(resp: requests.Response) -> Dict[str, Any]:
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text}

    @staticmethod
    def pick_id(payload: Dict[str, Any]) -> Any:
        for k in ("id", "employee_id", "emp_id", "uid", "_id"):
            if k in payload:
                return payload[k]
        for k in ("data", "employee"):
            v = payload.get(k)
            if isinstance(v, dict):
                got = EmployeeApi.pick_id(v)
                if got is not None:
                    return got
        return None

    def create(self, data: Dict[str, Any]) -> requests.Response:
        return self.s.post(f"{self.base}/employee/create", json=data)

    def info(self, emp_id: Any) -> requests.Response:
        url = f"{self.base}/employee/info"
        r = self.s.get(url, params={"id": emp_id, "employee_id": emp_id})
        if r.status_code >= 400:
            r = self.s.get(url, json={"id": emp_id})
            if r.status_code >= 400:
                r = self.s.get(url, json={"employee_id": emp_id})
        return r

    def change(self, emp_id: Any, changes: Dict[str, Any]) -> requests.Response:
        url = f"{self.base}/employee/change"
        payload = {"id": emp_id, "employee_id": emp_id}
        payload.update(changes)
        return self.s.patch(url, json=payload)

    def create_with_fallbacks(self, seed: Dict[str, Any]) -> Tuple[requests.Response, Any]:
        first = seed.get("first_name") or seed.get("firstName") or "John"
        last = seed.get("last_name") or seed.get("lastName") or "Doe"
        base_id = seed.get("id") or random.randint(10000, 999999)
        extra = {k: v for k, v in seed.items() if k not in {"first_name", "last_name", "firstName", "lastName", "company_id", "id"}}

        company_ids = []
        if "company_id" in seed:
            company_ids.append(seed["company_id"])
        company_ids += [1, 2, 3, 4, 5, 10, 100]

        tried = []
        for cid in company_ids:
            for with_id in (False, True):
                for shape in ("snake", "camel", "name_only"):
                    if shape == "snake":
                        payload = {"company_id": cid, "first_name": first, "last_name": last}
                    elif shape == "camel":
                        payload = {"companyId": cid, "firstName": first, "lastName": last}
                    else:
                        payload = {"company_id": cid, "name": f"{first} {last}"}
                    payload.update(extra)
                    if with_id:
                        payload["id"] = base_id

                    r = self.create(payload)
                    tried.append((r.status_code, payload))
                    if 200 <= r.status_code < 300:
                        j = self._json(r)
                        emp_id = self.pick_id(j) or payload.get("id")
                        return r, emp_id

        last_r, last_payload = tried[-1]
        raise AssertionError(f"create did not succeed (last status {last_r}). last payload: {last_payload}")
