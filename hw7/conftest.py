import os
import pytest
from hw7.api.employee_api import EmployeeApi

@pytest.fixture
def api():
    base = os.getenv("EMP_BASE")  # optional override, default is inside EmployeeApi
    return EmployeeApi(base_url=base)
