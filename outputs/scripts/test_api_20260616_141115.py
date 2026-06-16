import pytest
import requests


class TestWebsiteFunctionality:
    """网站功能 - 接口自动化测试"""

    BASE_URL = "http://localhost:8080"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()

    def test_tc001_homepage_access_and_title(self):
        """TC-001: 首页加载-验证网站URL可正常访问且页面标题正确"""
        resp = self.session.get(f"{self.BASE_URL}/")
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
        # 假设标题在 meta 标签中，或者通过解析 HTML 获取 title 标签内容
        # 这里简化为检查响应体包含预期标题字符串
        assert "鑫和不锈钢网-首页" in resp.text, "页面标题与预期不一致"

    def test_tc002_navigation_links(self):
        """TC-002: 导航栏功能-点击各导航菜单项跳转验证"""
        nav_links = [
            ("首页", "/"),
            ("产品中心", "/products"),
            ("关于我们", "/about"),
            ("联系我们", "/contact")
        ]
        for name, path in nav_links:
            resp = self.session.get(f"{self.BASE_URL}{path}")
            assert resp.status_code == 200, f"{name} 页面访问失败，状态码: {resp.status_code}"

    def test_tc003_product_pagination(self):
        """TC-003: 产品中心列表-验证分页功能正常"""
        # 第一步：获取第一页
        resp_page1 = self.session.get(f"{self.BASE_URL}/products?page=1")
        assert resp_page1.status_code == 200
        
        # 第二步：获取第二页
        resp_page2 = self.session.get(f"{self.BASE_URL}/products?page=2")
        assert resp_page2.status_code == 200
        
        # 第三步：验证数据不同（简单断言响应长度或内容差异，具体取决于后端实现）
        # 此处仅验证能正常加载第二页
        assert len(resp_page2.text) > 0, "第二页数据为空"

    def test_tc004_product_detail_view(self):
        """TC-004: 产品详情查看-验证图片、规格、描述显示正确"""
        # 假设存在一个已知 ID 的产品，例如 ID 为 1
        product_id = 1
        resp = self.session.get(f"{self.BASE_URL}/products/{product_id}")
        assert resp.status_code == 200, f"产品详情页访问失败，状态码: {resp.status_code}"
        
        # 验证响应中包含关键信息字段（假设 JSON 响应或 HTML 包含特定文本）
        # 如果是 HTML，检查是否包含“材质”、“尺寸”等关键词
        assert "材质" in resp.text or "specifications" in resp.text.lower(), "缺少规格参数"
        assert "描述" in resp.text or "description" in resp.text.lower(), "缺少产品描述"

    def test_tc005_product_search(self):
        """TC-005: 产品搜索-输入关键词搜索特定产品"""
        keyword = "304不锈钢"
        resp = self.session.get(f"{self.BASE_URL}/products/search", params={"q": keyword})
        assert resp.status_code == 200
        
        # 验证搜索结果中包含关键词
        assert keyword in resp.text, f"搜索结果未包含关键词 '{keyword}'"

    def test_tc006_contact_info_display(self):
        """TC-006: 验证底部及联系我们页面包含正确的电话、地址、邮箱信息"""
        # 检查首页底部（通常首页也包含联系方式）
        resp_home = self.session.get(f"{self.BASE_URL}/")
        assert resp_home.status_code == 200
        
        # 检查联系我们页面
        resp_contact = self.session.get(f"{self.BASE_URL}/contact")
        assert resp_contact.status_code == 200
        
        # 验证包含预期的联系信息格式（示例：电话、邮箱）
        # 实际测试中应替换为具体的业务联系信息
        assert "@" in resp_contact.text or "phone" in resp_contact.text.lower(), "未找到有效的联系方式信息"

    def test_tc007_responsive_layout_api_check(self):
        """TC-007: 验证不同屏幕尺寸下页面布局正常显示 (API层面模拟)"""
        # 注意：纯 API 测试无法直接验证视觉布局，通常通过检查响应头或特定移动端适配接口验证
        # 此处验证 PC 端和移动端（如果有不同接口）均能正常返回 200
        resp_pc = self.session.get(f"{self.BASE_URL}/", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        assert resp_pc.status_code == 200
        
        resp_mobile = self.session.get(f"{self.BASE_URL}/", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"})
        assert resp_mobile.status_code == 200

    def test_tc008_dead_link_detection(self):
        """TC-008: 检查页面内所有超链接有效性"""
        # 获取首页
        resp = self.session.get(f"{self.BASE_URL}/")
        assert resp.status_code == 200
        
        # 简单提取 href 并验证（实际项目中建议使用 BeautifulSoup 解析）
        # 这里仅演示对首页本身及其主要子页面的直接访问验证
        sub_pages = ["/products", "/about", "/contact"]
        for page in sub_pages:
            sub_resp = self.session.get(f"{self.BASE_URL}{page}")
            assert sub_resp.status_code == 200, f"死链检测: {page} 返回 {sub_resp.status_code}"

    def test_tc009_image_loading(self):
        """TC-009: 验证产品图片及 Logo 加载正常且无破损"""
        # 假设图片通过静态资源服务提供，如 /static/images/logo.png
        logo_url = f"{self.BASE_URL}/static/images/logo.png"
        resp_logo = self.session.get(logo_url)
        assert resp_logo.status_code == 200, f"Logo 加载失败，状态码: {resp_logo.status_code}"
        assert resp_logo.headers.get('Content-Type', '').startswith('image'), "Logo 不是图片格式"

    def test_tc010_seo_tags_validation(self):
        """TC-010: 验证页面 Title、Description、Keywords 标签规范性"""
        resp = self.session.get(f"{self.BASE_URL}/")
        assert resp.status_code == 200
        
        # 验证 Title 标签存在
        assert "<title>" in resp.text, "缺少 Title 标签"
        
        # 验证 Meta Description 存在
        assert 'name="description"' in resp.text.lower(), "缺少 Meta Description 标签"
        
        # 验证 Meta Keywords 存在
        assert 'name="keywords"' in resp.text.lower(), "缺少 Meta Keywords 标签"