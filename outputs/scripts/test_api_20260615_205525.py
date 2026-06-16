import pytest
import requests


class TestUserLogin:
    """用户登录 - 接口自动化测试"""

    BASE_URL = "http://121.40.104.18"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()

    def test_01_normal_login(self):
        """TC-001: 正常登录-使用正确的账号和密码登录成功"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13800138000",
                "password": "Pass@123"
            }
        )
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
        data = resp.json()
        assert "token" in data or "session" in data, "响应中缺少会话凭证"

    def test_02_account_not_exist(self):
        """TC-002: 账号不存在-输入未注册的账号"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13900000000",
                "password": "Pass@123"
            }
        )
        assert resp.status_code in [401, 404], f"期望 401 或 404，实际 {resp.status_code}"
        data = resp.json()
        # 根据预期，可能提示账号不存在或统一错误提示
        assert "message" in data or "error" in data, "响应中缺少错误信息"

    def test_03_wrong_password(self):
        """TC-003: 密码错误-使用正确的账号但输入错误的密码"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13800138000",
                "password": "Wrong@456"
            }
        )
        assert resp.status_code == 401, f"期望 401，实际 {resp.status_code}"
        data = resp.json()
        assert "token" not in data, "密码错误不应返回 Token"

    def test_04_empty_fields(self):
        """TC-004: 账号密码均为空-直接点击登录按钮"""
        # 接口层面通常无法模拟前端拦截，但可测试后端对空值的处理
        # 假设后端会拒绝空参数或返回参数校验错误
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "",
                "password": ""
            }
        )
        # 预期：前端拦截不发起请求，若发起则后端应返回 400 或类似校验错误
        assert resp.status_code in [400, 422], f"期望参数校验错误，实际 {resp.status_code}"

    def test_05_invalid_format(self):
        """TC-005: 账号格式错误-输入非手机号/邮箱格式的账号"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "abc",
                "password": "Pass@123"
            }
        )
        # 预期：前端拦截或后端格式校验失败
        assert resp.status_code in [400, 422], f"期望格式校验错误，实际 {resp.status_code}"

    def test_06_account_locked(self):
        """TC-006: 连续登录失败-多次输入错误密码触发账号锁定"""
        # 模拟多次失败登录以触发锁定
        for i in range(5):
            resp = self.session.post(
                f"{self.BASE_URL}/api/login",
                json={
                    "username": "13800138000",
                    "password": "Wrong@456"
                }
            )
            assert resp.status_code == 401, f"第 {i+1} 次失败登录应返回 401"
        
        # 第 6 次尝试，预期被锁定
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13800138000",
                "password": "Pass@123"
            }
        )
        # 预期：返回 403 或 401，并提示账号锁定
        assert resp.status_code in [401, 403], f"账号锁定后应返回 401 或 403，实际 {resp.status_code}"
        data = resp.json()
        assert "locked" in str(data.get("message", "")).lower() or "error" in str(data), "应提示账号锁定"

    def test_07_banned_account(self):
        """TC-007: 账号被禁用-使用已注销或被封禁的账号登录"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "banned_user",
                "password": "Pass@123"
            }
        )
        assert resp.status_code in [401, 403], f"期望 401 或 403，实际 {resp.status_code}"
        data = resp.json()
        assert "token" not in data, "禁用账号不应返回 Token"

    def test_08_sql_injection(self):
        """TC-008: 特殊字符注入-账号或密码输入SQL/XSS脚本"""
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "' OR '1'='1",
                "password": "<script>alert(1)</script>"
            }
        )
        # 预期：登录失败，不执行恶意代码，返回错误提示
        assert resp.status_code in [401, 403, 400], f"期望安全拦截，实际 {resp.status_code}"
        data = resp.json()
        assert "token" not in data, "注入攻击不应返回 Token"

    def test_09_remember_me(self):
        """TC-009: 记住我功能-勾选后关闭浏览器重新打开自动登录"""
        # 接口测试无法直接模拟浏览器 Cookie 持久化，但可测试登录接口是否支持持久化 Token
        # 此处主要验证登录成功，持久化逻辑通常由前端/客户端处理
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13800138000",
                "password": "Pass@123",
                "remember_me": True
            }
        )
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
        data = resp.json()
        assert "token" in data or "refresh_token" in data, "应返回持久化凭证"

    def test_10_password_visibility(self):
        """TC-10: 密码可见性切换-点击眼睛图标查看/隐藏密码"""
        # 接口测试无法模拟前端 UI 交互（如点击眼睛图标）
        # 此用例属于前端 UI 测试，接口层无法直接验证
        # 此处跳过或标记为无效，或仅验证密码字段能正常接收
        resp = self.session.post(
            f"{self.BASE_URL}/api/login",
            json={
                "username": "13800138000",
                "password": "123456"
            }
        )
        # 仅验证正常登录流程，密码可见性切换由前端负责
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"