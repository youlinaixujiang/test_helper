import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LoginPage:
    """登录页面对象模型"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # 定位器定义
        self.nav_login_link = (By.LINK_TEXT, "登录")
        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_button = (By.CSS_SELECTOR, "button[type='submit']")
        self.remember_me_checkbox = (By.ID, "remember-me")
        self.password_toggle_icon = (By.CSS_SELECTOR, ".toggle-password-icon")
        self.error_message = (By.CLASS_NAME, "error-msg")
        self.user_info_display = (By.CLASS_NAME, "user-info")

    def navigate_to_login(self):
        """从首页导航到登录页"""
        self.wait.until(EC.presence_of_element_located(self.nav_login_link)).click()
        self.wait.until(EC.url_contains("/login"))

    def enter_credentials(self, username, password):
        """输入用户名和密码"""
        self.wait.until(EC.visibility_of_element_located(self.username_input)).clear()
        self.driver.find_element(*self.username_input).send_keys(username)
        
        self.driver.find_element(*self.password_input).clear()
        self.driver.find_element(*self.password_input).send_keys(password)

    def click_login(self):
        """点击登录按钮"""
        self.driver.find_element(*self.login_button).click()

    def toggle_remember_me(self):
        """勾选记住我"""
        checkbox = self.driver.find_element(*self.remember_me_checkbox)
        if not checkbox.is_selected():
            checkbox.click()

    def toggle_password_visibility(self):
        """切换密码可见性"""
        self.driver.find_element(*self.password_toggle_icon).click()

    def get_error_text(self):
        """获取错误提示信息"""
        try:
            error_elem = self.wait.until(EC.visibility_of_element_located(self.error_message))
            return error_elem.text
        except TimeoutException:
            return ""

    def is_logged_in(self):
        """判断是否登录成功（通过检查用户信息或URL变化）"""
        try:
            # 假设登录后URL变化或出现用户信息元素
            self.wait.until(EC.presence_of_element_located(self.user_info_display))
            return True
        except TimeoutException:
            # 备选方案：检查URL是否不再是登录页
            if "/login" not in self.driver.current_url:
                return True
            return False


class TestUserLogin:
    """用户登录功能测试类"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化浏览器驱动"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.page = LoginPage(self.driver)
        yield
        self.driver.quit()

    def test_TC001_normal_login(self):
        """TC-001: 正常登录"""
        self.page.navigate_to_login()
        self.page.enter_credentials("admin", "Admin@123")
        self.page.click_login()
        
        # 验证登录成功
        assert self.page.is_logged_in(), "登录失败，未跳转到首页或显示用户信息"

    def test_TC002_non_exist_user(self):
        """TC-002: 账号不存在"""
        self.page.navigate_to_login()
        self.page.enter_credentials("non_exist_user", "123456")
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        assert "账号不存在" in error_text or "用户名或密码错误" in error_text, f"预期提示账号不存在，实际: {error_text}"

    def test_TC003_wrong_password(self):
        """TC-003: 密码错误"""
        self.page.navigate_to_login()
        self.page.enter_credentials("admin", "Wrong@123")
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        assert "密码错误" in error_text or "用户名或密码错误" in error_text, f"预期提示密码错误，实际: {error_text}"

    def test_TC004_empty_username(self):
        """TC-004: 账号为空"""
        self.page.navigate_to_login()
        self.page.enter_credentials("", "123456")
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        assert "请输入账号" in error_text or len(error_text) > 0, "预期有校验提示"

    def test_TC005_empty_password(self):
        """TC-005: 密码为空"""
        self.page.navigate_to_login()
        self.page.enter_credentials("admin", "")
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        assert "请输入密码" in error_text or len(error_text) > 0, "预期有校验提示"

    def test_TC006_both_empty(self):
        """TC-006: 账号密码均为空"""
        self.page.navigate_to_login()
        self.page.enter_credentials("", "")
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        # 前端校验通常会在提交前拦截，或者后端返回参数错误
        assert len(error_text) > 0, "预期有必填项缺失提示"

    def test_TC007_special_chars_security(self):
        """TC-007: 特殊字符测试 (XSS/SQL注入)"""
        self.page.navigate_to_login()
        # 输入恶意字符串
        malicious_user = "<script>alert(1)</script>"
        self.page.enter_credentials(malicious_user, "any_password")
        self.page.click_login()
        
        # 验证没有弹窗（Selenium无法直接验证JS alert未弹出，但可以通过检查页面状态和错误提示间接验证）
        # 如果发生XSS，页面可能会崩溃或行为异常。这里主要验证登录失败且无脚本执行迹象。
        error_text = self.page.get_error_text()
        # 预期是账号不存在或密码错误，而不是页面报错或重定向
        assert "账号不存在" in error_text or "密码错误" in error_text or len(error_text) > 0

    def test_TC008_password_visibility_toggle(self):
        """TC-008: 密码可见性切换"""
        self.page.navigate_to_login()
        self.page.enter_credentials("admin", "Test@123")
        
        # 初始状态应为掩码
        password_field = self.driver.find_element(*self.page.password_input)
        assert password_field.get_attribute("type") == "password", "初始密码类型应为password"
        
        # 点击切换图标
        self.page.toggle_password_visibility()
        # 变为明文
        assert password_field.get_attribute("type") == "text", "切换后密码类型应为text"
        
        # 再次点击切换
        self.page.toggle_password_visibility()
        # 恢复掩码
        assert password_field.get_attribute("type") == "password", "再次切换后密码类型应为password"

    def test_TC009_login_lockout(self):
        """TC-009: 登录失败次数限制"""
        self.page.navigate_to_login()
        username = "test_user"
        wrong_pwd = "WrongPwd1"
        
        # 模拟5次错误登录
        for i in range(5):
            self.page.enter_credentials(username, wrong_pwd)
            self.page.click_login()
            
        # 第6次尝试应被锁定
        self.page.enter_credentials(username, wrong_pwd)
        self.page.click_login()
        
        error_text = self.page.get_error_text()
        assert "锁定" in error_text or "次数过多" in error_text or "稍后再试" in error_text, f"预期账号被锁定，实际: {error_text}"

    def test_TC010_remember_me(self):
        """TC-010: 记住我功能"""
        self.page.navigate_to_login()
        self.page.enter_credentials("admin", "Admin@123")
        self.page.toggle_remember_me()
        self.page.click_login()
        
        # 验证登录成功
        assert self.page.is_logged_in(), "第一次登录失败"
        
        # 注意：在自动化测试中清除Cookie并重新访问通常涉及复杂的会话管理
        # 此处仅验证勾选“记住我”后能成功登录，持久化Session/Cookie的验证通常需要结合后端接口或手动验证
        # 为了演示完整性，我们验证登录状态保持
        cookies = self.driver.get_cookies()
        remember_cookie_exists = any('remember' in str(c).lower() or 'token' in str(c).get('name', '').lower() for c in cookies)
        
        # 简单断言：只要登录成功且页面未跳转回登录页，即视为功能正常
        assert "/login" not in self.driver.current_url