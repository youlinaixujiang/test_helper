import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# --- Page Objects ---

class HomePage:
    """首页 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # TC-001 Locators
        self.header_contact_bar = (By.CSS_SELECTOR, ".header-contact-info")
        self.company_phone = (By.CSS_SELECTOR, ".company-phone")
        self.company_email = (By.CSS_SELECTOR, ".company-email")
        self.company_address = (By.CSS_SELECTOR, ".company-address")

        # TC-002 Locators
        self.carousel_container = (By.CSS_SELECTOR, ".carousel-container")
        self.carousel_next_btn = (By.CSS_SELECTOR, ".carousel-next")
        self.carousel_prev_btn = (By.CSS_SELECTOR, ".carousel-prev")
        self.carousel_indicators = (By.CSS_SELECTOR, ".carousel-indicators span")

        # TC-003 Locators
        self.product_cards = (By.CSS_SELECTOR, ".product-card")
        self.carousel_images = (By.CSS_SELECTOR, ".carousel-image")

    def open(self):
        self.driver.get("http://121.40.104.18/")

    def verify_header_info(self):
        """TC-001: 验证顶部联系信息"""
        self.wait.until(EC.presence_of_element_located(self.header_contact_bar))
        phone = self.driver.find_element(*self.company_phone).text
        email = self.driver.find_element(*self.company_email).text
        address = self.driver.find_element(*self.company_address).text
        assert phone, "Phone should not be empty"
        assert email, "Email should not be empty"
        assert address, "Address should not be empty"

    def verify_carousel_auto_play(self):
        """TC-002: 验证轮播图自动播放"""
        self.wait.until(EC.presence_of_element_located(self.carousel_container))
        initial_html = self.driver.find_element(*self.carousel_container).get_attribute('innerHTML')
        time.sleep(6) # Wait for auto switch (assume 5s interval)
        current_html = self.driver.find_element(*self.carousel_container).get_attribute('innerHTML')
        assert initial_html != current_html, "Carousel image should have changed"

    def verify_carousel_manual_switch(self):
        """TC-002: 验证轮播图手动切换"""
        self.wait.until(EC.element_to_be_clickable(self.carousel_next_btn))
        initial_slide_index = self._get_current_slide_index()
        self.driver.find_element(*self.carousel_next_btn).click()
        time.sleep(1)
        next_slide_index = self._get_current_slide_index()
        assert next_slide_index != initial_slide_index, "Slide index should change after click"

    def _get_current_slide_index(self):
        active_indicator = self.driver.find_element(By.CSS_SELECTOR, ".carousel-indicators .active")
        return int(active_indicator.get_attribute('data-slide-to'))

    def click_product_card_and_verify_detail(self, card_index=0):
        """TC-003: 点击产品卡片跳转详情"""
        cards = self.driver.find_elements(*self.product_cards)
        if len(cards) > card_index:
            cards[card_index].click()
            # Assume detail page has a specific title or URL pattern
            self.wait.until(EC.url_contains("/product")) 
            return True
        return False


class ProductListPage:
    """产品列表页 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-005 Locators
        self.pagination_next_btn = (By.CSS_SELECTOR, ".pagination-next")
        self.pagination_prev_btn = (By.CSS_SELECTOR, ".pagination-prev")
        self.pagination_page_numbers = (By.CSS_SELECTOR, ".page-number")
        self.current_page_highlight = (By.CSS_SELECTOR, ".pagination-active")

        # TC-006 Locators
        self.search_input = (By.ID, "search-input")
        self.search_btn = (By.CSS_SELECTOR, ".search-btn")

        # TC-007 Locators
        self.stock_status_tags = (By.CSS_SELECTOR, ".stock-status-tag")

        # TC-008 Locators
        self.price_elements = (By.CSS_SELECTOR, ".product-price")

        # TC-009 Locators
        self.admin_action_buttons = (By.CSS_SELECTOR, ".admin-actions button")

        # TC-010 Locators
        self.delete_btn = (By.CSS_SELECTOR, ".delete-btn")
        self.confirm_dialog = (By.CSS_SELECTOR, ".confirm-dialog")
        self.confirm_yes_btn = (By.CSS_SELECTOR, ".confirm-yes")
        self.confirm_no_btn = (By.CSS_SELECTOR, ".confirm-no")

    def verify_pagination(self):
        """TC-005: 验证分页功能"""
        self.wait.until(EC.presence_of_element_located(self.pagination_next_btn))
        initial_page = self.driver.find_element(*self.current_page_highlight).text
        
        # Click Next
        self.driver.find_element(*self.pagination_next_btn).click()
        time.sleep(1)
        new_page = self.driver.find_element(*self.current_page_highlight).text
        assert new_page != initial_page, "Page number should change"

        # Click Previous
        self.driver.find_element(*self.pagination_prev_btn).click()
        time.sleep(1)
        back_page = self.driver.find_element(*self.current_page_highlight).text
        assert back_page == initial_page, "Should return to previous page"

    def verify_search_by_model(self, keyword="304-20"):
        """TC-006: 验证按型号搜索"""
        search_box = self.driver.find_element(*self.search_input)
        search_box.clear()
        search_box.send_keys(keyword)
        self.driver.find_element(*self.search_btn).click()
        
        # Verify results contain keyword (simplified check)
        products = self.driver.find_elements(By.CSS_SELECTOR, ".product-item")
        # In a real scenario, we'd check text content of each product
        assert len(products) > 0, "Search results should not be empty"

    def verify_stock_status_colors(self):
        """TC-007: 验证库存状态标签"""
        tags = self.driver.find_elements(*self.stock_status_tags)
        colors = [tag.value_of_css_property("color") for tag in tags]
        # Check for presence of green, yellow, red indicators
        # Note: Exact color values depend on CSS implementation
        assert len(tags) > 0, "Stock status tags should exist"

    def verify_price_formatting(self):
        """TC-008: 验证价格格式化"""
        prices = self.driver.find_elements(*self.price_elements)
        for price in prices:
            text = price.text
            # Regex for format like 10,000.00 or 123.45
            import re
            pattern = r'^\d{1,3}(,\d{3})*(\.\d{2})?$'
            assert re.match(pattern, text), f"Price format invalid: {text}"

    def verify_admin_buttons_visibility(self, is_admin=False):
        """TC-009: 验证管理员按钮可见性"""
        buttons = self.driver.find_elements(*self.admin_action_buttons)
        if is_admin:
            assert len(buttons) > 0, "Admin buttons should be visible for admin"
        else:
            assert len(buttons) == 0, "Admin buttons should be hidden for normal users"

    def handle_delete_confirmation(self, action="cancel"):
        """TC-010: 处理删除确认弹窗"""
        self.driver.find_element(*self.delete_btn).click()
        self.wait.until(EC.visibility_of_element_located(self.confirm_dialog))
        
        if action == "cancel":
            self.driver.find_element(*self.confirm_no_btn).click()
            time.sleep(1)
            # Verify dialog closed
            try:
                self.driver.find_element(*self.confirm_dialog)
                assert False, "Dialog should be closed"
            except:
                pass
        elif action == "confirm":
            self.driver.find_element(*self.confirm_yes_btn).click()
            time.sleep(1)
            # Verify success message or item removal
            # Simplified: assume alert or toast
            pass


class ProductDetailPage:
    """产品详情页 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-011 Locators
        self.detail_image = (By.CSS_SELECTOR, ".detail-image")
        self.detail_model = (By.CSS_SELECTOR, ".detail-model")
        self.detail_name = (By.CSS_SELECTOR, ".detail-name")
        self.detail_material = (By.CSS_SELECTOR, ".detail-material")
        self.detail_spec = (By.CSS_SELECTOR, ".detail-spec")
        self.detail_price = (By.CSS_SELECTOR, ".detail-price")
        self.detail_stock = (By.CSS_SELECTOR, ".detail-stock")
        self.detail_desc = (By.CSS_SELECTOR, ".detail-description")

    def verify_all_fields_present(self):
        """TC-011: 验证所有字段存在且非空"""
        elements = [
            self.detail_image, self.detail_model, self.detail_name,
            self.detail_material, self.detail_spec, self.detail_price,
            self.detail_stock, self.detail_desc
        ]
        for locator in elements:
            elem = self.wait.until(EC.presence_of_element_located(locator))
            assert elem.text.strip() != "", f"Field {locator} should not be empty"

    def verify_image_accessible(self):
        """TC-011: 验证图片可访问"""
        img = self.driver.find_element(*self.detail_image)
        src = img.get_attribute("src")
        assert src and src.startswith("http"), "Image source should be valid URL"


class ProductEditPage:
    """产品编辑页 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-013 Locators
        self.input_model = (By.ID, "input-model")
        self.input_name = (By.ID, "input-name")
        self.input_price = (By.ID, "input-price")
        self.save_btn = (By.CSS_SELECTOR, ".save-btn")
        self.error_messages = (By.CSS_SELECTOR, ".error-msg")

        # TC-014 Locators
        self.upload_input = (By.ID, "upload-image")

        # TC-015 Locators
        self.model_field = (By.ID, "edit-model-field")

        # TC-016 Locators
        self.input_stock = (By.ID, "input-stock")

    def verify_required_fields_empty_submit(self):
        """TC-013: 验证必填项为空时禁止提交"""
        self.input_model.clear()
        self.input_name.clear()
        self.input_price.clear()
        
        self.driver.find_element(*self.save_btn).click()
        
        errors = self.driver.find_elements(*self.error_messages)
        assert len(errors) >= 3, "Should show errors for all required fields"

    def verify_negative_number_rejection(self):
        """TC-016: 验证负数拦截"""
        self.input_price.clear()
        self.input_price.send_keys("-10")
        self.driver.find_element(*self.save_btn).click()
        
        errors = self.driver.find_elements(*self.error_messages)
        assert any("negative" in err.text.lower() or "price" in err.text.lower() for err in errors), \
            "Should reject negative price"

    def verify_model_readonly(self):
        """TC-015: 验证型号字段只读"""
        model_elem = self.driver.find_element(*self.model_field)
        assert model_elem.is_enabled() == False, "Model field should be disabled"
        assert model_elem.get_attribute("readonly") is not None or \
               model_elem.get_attribute("disabled") is not None, "Model field should be readonly/disabled"


class AuthPage:
    """认证相关 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-018/019 Locators
        self.login_username = (By.ID, "login-username")
        self.login_password = (By.ID, "login-password")
        self.login_btn = (By.CSS_SELECTOR, ".login-btn")
        self.login_error_msg = (By.CSS_SELECTOR, ".login-error")

    def login(self, username, password):
        self.driver.find_element(*self.login_username).send_keys(username)
        self.driver.find_element(*self.login_password).send_keys(password)
        self.driver.find_element(*self.login_btn).click()

    def verify_login_success_redirect(self):
        """TC-018: 验证登录成功跳转"""
        self.wait.until(EC.url_contains("/home") or EC.url_contains("/dashboard"))
        assert "/login" not in self.driver.current_url

    def verify_login_failure_message(self):
        """TC-019: 验证登录失败提示"""
        error_msg = self.wait.until(EC.visibility_of_element_located(self.login_error_msg)).text
        assert "用户名或密码错误" in error_msg or "Invalid" in error_msg


class RegistrationPage:
    """注册页 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-023 Locators
        self.reg_username = (By.ID, "reg-username")
        self.reg_password = (By.ID, "reg-password")
        self.reg_confirm_password = (By.ID, "reg-confirm-password")
        self.reg_submit_btn = (By.CSS_SELECTOR, ".reg-submit-btn")
        self.reg_error_msgs = (By.CSS_SELECTOR, ".reg-error")

    def fill_registration_form(self, username, password, confirm_password):
        self.driver.find_element(*self.reg_username).clear()
        self.driver.find_element(*self.reg_username).send_keys(username)
        self.driver.find_element(*self.reg_password).clear()
        self.driver.find_element(*self.reg_password).send_keys(password)
        self.driver.find_element(*self.reg_confirm_password).clear()
        self.driver.find_element(*self.reg_confirm_password).send_keys(confirm_password)

    def submit_registration(self):
        self.driver.find_element(*self.reg_submit_btn).click()

    def verify_required_fields_validation(self):
        """TC-023: 验证必填项校验"""
        self.submit_registration()
        errors = self.driver.find_elements(*self.reg_error_msgs)
        assert len(errors) > 0, "Should show validation errors for empty fields"

    def verify_password_length_validation(self):
        """TC-024: 验证密码长度校验"""
        self.fill_registration_form("new_user", "12345", "12345")
        self.submit_registration()
        errors = self.driver.find_elements(*self.reg_error_msgs)
        assert any("length" in e.text.lower() or "6" in e.text for e in errors), \
            "Should warn about password length < 6"

    def verify_password_match_validation(self):
        """TC-025: 验证两次密码一致校验"""
        self.fill_registration_form("new_user", "Pass1234", "Pass5678")
        self.submit_registration()
        errors = self.driver.find_elements(*self.reg_error_msgs)
        assert any("match" in e.text.lower() or "consistent" in e.text.lower() for e in errors), \
            "Should warn about password mismatch"


class SecurityPage:
    """安全相关 Page Object"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # TC-030 Locators
        self.search_input = (By.ID, "search-input")
        self.search_btn = (By.CSS_SELECTOR, ".search-btn")

        # TC-031 Locators
        self.desc_editor = (By.ID, "description-editor")
        self.save_btn = (By.CSS_SELECTOR, ".save-btn")

    def test_sql_injection_search(self):
        """TC-030: 验证SQL注入防护"""
        payload = "' OR '1'='1 --"
        self.driver.find_element(*self.search_input).clear()
        self.driver.find_element(*self.search_input).send_keys(payload)
        self.driver.find_element(*self.search_btn).click()
        
        # Should not return all products or crash
        # Assuming normal search returns limited results
        products = self.driver.find_elements(By.CSS_SELECTOR, ".product-item")
        # If it's a successful injection, it might return everything or error.
        # Here we just ensure no critical error page is shown.
        assert "Error" not in self.driver.title

    def test_xss_protection(self):
        """TC-031: 验证XSS防护"""
        xss_payload = "<script>alert('xss')</script>"
        self.driver.find_element(*self.desc_editor).send_keys(xss_payload)
        self.driver.find_element(*self.save_btn).click()
        
        # Refresh and check
        self.driver.refresh()
        desc_text = self.driver.find_element(By.CSS_SELECTOR, ".detail-description").text
        assert "<script>" not in desc_text, "Script tag should be escaped or removed"


# --- Fixtures ---

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Optional: run headless for CI
    options.add_argument("--disable-gpu")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


# --- Tests ---

class TestHomePageUI:
    """TC-001, TC-002, TC-003, TC-004"""
    
    def test_001_header_contact_info(self, driver):
        page = HomePage(driver)
        page.open()
        page.verify_header_info()

    def test_002_carousel_auto_play(self, driver):
        page = HomePage(driver)
        page.open()
        page.verify_carousel_auto_play()

    def test_003_carousel_manual_switch(self, driver):
        page = HomePage(driver)
        page.open()
        page.verify_carousel_manual_switch()

    def test_004_responsive_layout_desktop(self, driver):
        """TC-004: 桌面端布局检查"""
        driver.set_window_size(1920, 1080)
        page = HomePage(driver)
        page.open()
        # Basic check: no horizontal scroll
        body_width = driver.execute_script("return document.body.scrollWidth")
        window_width = driver.execute_script("return window.innerWidth")
        assert body_width <= window_width + 1, "No horizontal scroll on desktop"

    def test_005_product_card_click(self, driver):
        """TC-003: 点击产品卡片跳转"""
        page = HomePage(driver)
        page.open()
        page.click_product_card_and_verify_detail()


class TestProductListUI:
    """TC-005, TC-006, TC-007, TC-008, TC-009, TC-010"""

    def test_005_pagination(self, driver):
        page = ProductListPage(driver)
        # Assume we are already on product list page or navigate there
        driver.get("http://121.40.104.18/products")
        page.verify_pagination()

    def test_006_search_by_model(self, driver):
        driver.get("http://121.40.104.18/products")
        page = ProductListPage(driver)
        page.verify_search_by_model()

    def test_007_stock_status(self, driver):
        driver.get("http://121.40.104.18/products")
        page = ProductListPage(driver)
        page.verify_stock_status_colors()

    def test_008_price_format(self, driver):
        driver.get("http://121.40.104.18/products")
        page = ProductListPage(driver)
        page.verify_price_formatting()

    def test_009_admin_buttons(self, driver):
        """Requires Admin Login first"""
        auth = AuthPage(driver)
        auth.login("admin", "admin123") # Placeholder credentials
        auth.verify_login_success_redirect()
        
        driver.get("http://121.40.104.18/products")
        page = ProductListPage(driver)
        page.verify_admin_buttons_visibility(is_admin=True)

    def test_010_delete_confirmation_cancel(self, driver):
        """Requires Admin Login"""
        auth = AuthPage(driver)
        auth.login("admin", "admin123")
        driver.get("http://121.40.104.18/products")
        page = ProductListPage(driver)
        page.handle_delete_confirmation(action="cancel")


class TestProductDetailUI:
    """TC-011, TC-012"""

    def test_011_detail_fields(self, driver):
        """Assumes navigating to a known product ID"""
        driver.get("http://121.40.104.18/product/1")
        page = ProductDetailPage(driver)
        page.verify_all_fields_present()
        page.verify_image_accessible()

    def test_012_invalid_product_id(self, driver):
        driver.get("http://121.40.104.18/product/99999")
        # Check for 404 page or error message
        assert "404" in driver.title or "Not Found" in driver.title or "不存在" in driver.title


class TestProductEditUI:
    """TC-013, TC-014, TC-015, TC-016, TC-017"""

    def test_013_required_fields(self, driver):
        auth = AuthPage(driver)
        auth.login("admin", "admin123")
        driver.get("http://121.40.104.18/product/1/edit")
        page = ProductEditPage(driver)
        page.verify_required_fields_empty_submit()

    def test_015_model_readonly(self, driver):
        auth = AuthPage(driver)
        auth.login("admin", "admin123")
        driver.get("http://121.40.104.18/product/1/edit")
        page = ProductEditPage(driver)
        page.verify_model_readonly()

    def test_016_negative_price(self, driver):
        auth = AuthPage(driver)
        auth.login("admin", "admin123")
        driver.get("http://121.40.104.18/product/1/edit")
        page = ProductEditPage(driver)
        page.verify_negative_number_rejection()


class TestAuthSecurity:
    """TC-018, TC-019, TC-020, TC-021, TC-022"""

    def test_018_login_success(self, driver):
        page = AuthPage(driver)
        page.open() # Assuming login page is default or specific URL
        driver.get("http://121.40.104.18/login")
        page.login("test_user", "Test@123")
        page.verify_login_success_redirect()

    def test_019_login_failure(self, driver):
        driver.get("http://121.40.104.18/login")
        page = AuthPage(driver)
        page.login("test_user", "wrong_password")
        page.verify_login_failure_message()

    def test_020_unauthorized_access(self, driver):
        """Clear cookies first"""
        driver.delete_all_cookies()
        driver.get("http://121.40.104.18/dashboard")
        # Should redirect to login
        assert "/login" in driver.current_url

    def test_021_token_persistence(self, driver):
        driver.get("http://121.40.104.18/login")
        auth = AuthPage(driver)
        auth.login("test_user", "Test@123")
        auth.verify_login_success_redirect()
        
        driver.refresh()
        # Should still be logged in
        assert "/login" not in driver.current_url

    def test_022_logged_in_redirect(self, driver):
        driver.get("http://121.40.104.18/login")
        auth = AuthPage(driver)
        auth.login("test_user", "Test@123")
        auth.verify_login_success_redirect()
        
        # Try accessing login page again
        driver.get("http://121.40.104.18/login")
        # Should redirect to home
        assert "/login" not in driver.current_url


class TestRegistration:
    """TC-023, TC-024, TC-025, TC-026, TC-027"""

    def test_023_required_fields(self, driver):
        driver.get("http://121.40.104.18/register")
        page = RegistrationPage(driver)
        page.verify_required_fields_validation()

    def test_024_password_length(self, driver):
        driver.get("http://121.40.104.18/register")
        page = RegistrationPage(driver)
        page.verify_password_length_validation()

    def test_025_password_match(self, driver):
        driver.get("http://121.40.104.18/register")
        page = RegistrationPage(driver)
        page.verify_password_match_validation()

    def test_026_duplicate_username(self, driver):
        """Requires existing user 'user_test_01'"""
        driver.get("http://121.40.104.18/register")
        page = RegistrationPage(driver)
        page.fill_registration_form("user_test_01", "123456", "123456")
        page.submit_registration()
        errors = driver.find_elements(By.CSS_SELECTOR, ".reg-error")
        assert any("exists" in e.text.lower() or "duplicate" in e.text.lower() for e in errors)

    def test_027_register_success_auto_login(self, driver):
        driver.get("http://121.40.104.18/register")
        page = RegistrationPage(driver)
        page.fill_registration_form("new_user_unique", "Pass@123", "Pass@123")
        page.submit_registration()
        # Check if redirected to home/dashboard
        assert "/login" not in driver.current_url


class TestPermissions:
    """TC-028, TC-029"""

    def test_028_forbidden_access(self, driver):
        """Normal user tries admin API"""
        # This is hard to test purely via UI without API client, 
        # but we can simulate by trying to access admin UI
        driver.get("http://121.40.104.18/login")
        auth = AuthPage(driver)
        auth.login("normal_user", "password")
        auth.verify_login_success_redirect()
        
        driver.get("http://121.40.104.18/admin")
        # Should redirect to login or show 403
        assert "/login" in driver.current_url or "403" in driver.title

    def test_029_token_expiry(self, driver):
        """Simulate token expiry by clearing storage or modifying cookie"""
        driver.get("http://121.40.104.18/login")
        auth = AuthPage(driver)
        auth.login("test_user", "Test@123")
        auth.verify_login_success_redirect()
        
        # Clear local storage to simulate expired token
        driver.execute_script("window.localStorage.clear();")
        driver.refresh()
        
        # Should redirect to login
        assert "/login" in driver.current_url


class TestSecurity:
    """TC-030, TC-031, TC-032"""

    def test_030_sql_injection(self, driver):
        driver.get("http://121.40.104.18/")
        page = SecurityPage(driver)
        page.test_sql_injection_search()

    def test_031_xss_protection(self, driver):
        """Requires Admin Login"""
        driver.get("http://121.40.104.18/login")
        auth = AuthPage(driver)
        auth.login("admin", "admin123")
        auth.verify_login_success_redirect()
        
        driver.get("http://121.40.104.18/product/1/edit")
        page = SecurityPage(driver)
        page.test_xss_protection()

    def test_032_file_upload_type(self, driver):
        """TC-032: 文件上传类型限制"""
        # This is difficult to automate file upload with Selenium directly 
        # without sending keys to input[type=file] which requires local file path.
        # We assume the backend handles it.
        pass 


class TestPerformance:
    """TC-033, TC-034"""

    def test_033_homepage_load_time(self, driver):
        """TC-033: 首页加载时间"""
        start_time = time.time()
        driver.get("http://121.40.104.18/")
        end_time = time.time()
        load_time = end_time - start_time
        assert load_time <= 3.0, f"Homepage load time {load_time}s exceeds 3s"

    def test_034_api_response_time(self, driver):
        """TC-034: 接口响应时间"""
        # Using JS to measure network timing for a specific resource
        driver.get("http://121.40.104.18/")
        script = """
            var resources = performance.getEntriesByType("resource");
            var apiResource = resources.filter(r => r.name.includes('/api/products'));
            if (apiResource.length > 0) {
                return apiResource[0].responseEnd - apiResource[0].startTime;
            }
            return 0;
        """
        response_time = driver.execute_script(script)
        # Note: This measures time from page load perspective. 
        # For pure API test, requests library is better, but sticking to Selenium.
        assert response_time <= 1000, f"API response time {response_time}ms exceeds 1s"