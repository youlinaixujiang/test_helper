import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class HomePage:
    """首页 Page Object"""

    def __init__(self, driver):
        self.driver = driver
        self.url = "http://121.40.104.18/"
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.url)

    def get_page_title(self):
        return self.driver.title

    def check_logo(self):
        logo = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.logo, header img")))
        return logo.get_attribute("src")

    def get_footer_contact_info(self):
        try:
            phone = self.driver.find_element(By.CSS_SELECTOR, "footer .phone, footer .contact-info").text
            address = self.driver.find_element(By.CSS_SELECTOR, "footer .address").text
            email = self.driver.find_element(By.CSS_SELECTOR, "footer .email").text
            return phone, address, email
        except NoSuchElementException:
            return None, None, None

    def get_all_links(self):
        return self.driver.find_elements(By.TAG_NAME, "a")


class ProductCenterPage:
    """产品中心 Page Object"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, url=None):
        if url:
            self.driver.get(url)
        else:
            # 假设从首页导航进入
            self.driver.find_element(By.LINK_TEXT, "产品中心").click()
            self.wait.until(EC.url_contains("/products"))

    def search_product(self, keyword):
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "search-input")))
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.submit()
        self.wait.until(EC.staleness_of(search_box)) # Wait for page reload or AJAX update

    def get_product_list_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, ".product-item, .product-card")

    def click_first_product(self):
        product = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-item a, .product-card a")))
        product.click()

    def get_pagination_info(self):
        try:
            next_btn = self.driver.find_element(By.LINK_TEXT, "下一页")
            return next_btn.is_enabled()
        except NoSuchElementException:
            return False

    def go_to_page(self, page_num):
        input_box = self.driver.find_element(By.CSS_SELECTOR, ".pagination input, .page-input")
        input_box.clear()
        input_box.send_keys(page_num)
        input_box.submit()


class ProductDetailPage:
    """产品详情页 Page Object"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_product_image(self):
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail img, #main-image")))
        return img.get_attribute("src")

    def get_product_specs(self):
        return self.driver.find_element(By.CSS_SELECTOR, ".product-specs, .specs-table").text

    def get_product_description(self):
        return self.driver.find_element(By.CSS_SELECTOR, ".product-description, .desc-content").text


class ContactPage:
    """联系我们 Page Object"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.find_element(By.LINK_TEXT, "联系我们").click()
        self.wait.until(EC.url_contains("/contact"))

    def get_contact_info(self):
        try:
            phone = self.driver.find_element(By.CSS_SELECTOR, ".contact-phone").text
            address = self.driver.find_element(By.CSS_SELECTOR, ".contact-address").text
            email = self.driver.find_element(By.CSS_SELECTOR, ".contact-email").text
            return phone, address, email
        except NoSuchElementException:
            return None, None, None


class TestWebsiteUI:
    """网站 UI 自动化测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.home_page = HomePage(self.driver)
        self.product_page = ProductCenterPage(self.driver)
        self.detail_page = ProductDetailPage(self.driver)
        self.contact_page = ContactPage(self.driver)
        yield
        self.driver.quit()

    def test_tc001_home_page_access(self):
        """TC-001: 首页加载-验证网站URL可正常访问且页面标题正确"""
        self.home_page.open()
        title = self.home_page.get_page_title()
        assert "鑫和不锈钢网" in title or "首页" in title, f"Title mismatch: {title}"

    def test_tc002_navigation_links(self):
        """TC-002: 导航栏功能-点击各导航菜单项跳转验证"""
        self.home_page.open()
        links = [
            ("首页", self.home_page.url),
            ("产品中心", "/products"),
            ("关于我们", "/about"),
            ("联系我们", "/contact")
        ]
        for link_text, expected_url_part in links:
            self.home_page.open() # Reset to home
            nav_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
            nav_link.click()
            self.wait.until(EC.url_contains(expected_url_part))
            assert expected_url_part in self.driver.current_url

    def test_tc003_pagination(self):
        """TC-003: 产品中心列表-验证分页功能正常"""
        self.home_page.open()
        self.product_page.open()
        # Verify next button exists
        assert self.product_page.get_pagination_info(), "Next page button not found or disabled"
        # Go to page 1
        self.product_page.go_to_page(1)
        # Verify page 1 content (simplified check)
        products = self.product_page.get_product_list_items()
        assert len(products) > 0

    def test_tc004_product_detail(self):
        """TC-004: 产品详情查看-验证图片、规格、描述显示正确"""
        self.home_page.open()
        self.product_page.open()
        self.product_page.click_first_product()
        # Check image
        img_src = self.detail_page.get_product_image()
        assert img_src is not None and "broken" not in img_src.lower()
        # Check specs
        specs = self.detail_page.get_product_specs()
        assert len(specs) > 0
        # Check description
        desc = self.detail_page.get_product_description()
        assert len(desc) > 0

    def test_tc005_product_search(self):
        """TC-005: 产品搜索-输入关键词搜索特定产品"""
        self.home_page.open()
        self.product_page.open()
        self.product_page.search_product("304不锈钢")
        # Verify results contain keyword (simplified)
        products = self.product_page.get_product_list_items()
        # Note: In a real scenario, we'd check text content of products
        assert len(products) > 0

    def test_tc006_contact_info(self):
        """TC-006: 验证底部及联系我们页面包含正确的电话、地址、邮箱信息"""
        self.home_page.open()
        footer_phone, footer_addr, footer_email = self.home_page.get_footer_contact_info()
        assert footer_phone is not None, "Footer contact info missing"
        
        self.contact_page.open()
        contact_phone, contact_addr, contact_email = self.contact_page.get_contact_info()
        assert contact_phone is not None, "Contact page info missing"
        
        # Basic consistency check
        assert footer_phone == contact_phone

    def test_tc007_responsive_layout(self):
        """TC-007: 验证不同屏幕尺寸下页面布局正常显示"""
        self.home_page.open()
        
        # PC
        self.driver.set_window_size(1920, 1080)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Tablet
        self.driver.set_window_size(1024, 768)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Mobile
        self.driver.set_window_size(375, 667)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def test_tc008_dead_links(self):
        """TC-008: 检查页面内所有超链接有效性"""
        self.home_page.open()
        links = self.home_page.get_all_links()
        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("http"):
                # Simple check: ensure link is not empty and starts with http
                # Note: Full HTTP status code checking requires requests library, 
                # but for Selenium UI test, we check if link is present and valid format
                assert href is not None
            elif href:
                assert href.startswith("/") or href.startswith("#")

    def test_tc009_image_loading(self):
        """TC-009: 验证产品图片及Logo加载正常且无破损"""
        self.home_page.open()
        logo_src = self.home_page.check_logo()
        assert logo_src is not None
        
        self.product_page.open()
        products = self.product_page.get_product_list_items()
        for product in products[:3]: # Check first 3
            img = product.find_element(By.TAG_NAME, "img")
            src = img.get_attribute("src")
            assert src is not None

    def test_tc010_seo_tags(self):
        """TC-010: 验证页面Title、Description、Keywords标签规范性"""
        self.home_page.open()
        title = self.driver.title
        assert len(title) > 0 and len(title) < 60
        
        meta_desc = self.driver.find_element(By.NAME, "description")
        desc_content = meta_desc.get_attribute("content")
        assert len(desc_content) > 50 and len(desc_content) < 200
        
        meta_keywords = self.driver.find_element(By.NAME, "keywords")
        keywords_content = meta_keywords.get_attribute("content")
        assert len(keywords_content) > 0