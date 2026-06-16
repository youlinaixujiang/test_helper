import pytest
import requests


class TestAuthAPI:
    """认证模块 - 接口自动化测试"""

    BASE_URL = "http://localhost:8080"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()

    def test_TC_001_login_success(self):
        """TC-001: 登录接口测试"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            json={
                "username": "test_user",
                "password": "Test@123"
            }
        )
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
        data = resp.json()
        assert data.get("code") == 200, "业务状态码不为 200"
        assert "token" in data, "响应中缺少 token 字段"
        assert "user" in data, "响应中缺少 user 字段"
        assert "id" in data["user"], "用户信息中缺少 id"
        assert "name" in data["user"], "用户信息中缺少 name"