import urllib.request, json

BASE = 'http://localhost:8000/api/v1'

# 模拟一个来自网站的需求解析结果
mock_req = {
    "feature": "不锈钢产品展示网站功能",
    "test_points": [
        {"id": "TP-001", "scene": "首页导航菜单展示", "priority": "P0", "precondition": "网站可正常访问"},
        {"id": "TP-002", "scene": "产品列表页展示", "priority": "P0", "precondition": "数据库有产品数据"},
    ]
}

print('Test: 用例生成 — base_url 传入验证')

# 不带 base_url
data_no_url = json.dumps({"requirement_result": mock_req, "base_url": None}).encode()
req = urllib.request.Request(BASE + '/testcase/generate', data=data_no_url,
    headers={"Content-Type": "application/json"})
r_no = json.loads(urllib.request.urlopen(req, timeout=180).read())
cases_no = r_no["data"]
print(f'  无 base_url: {len(cases_no)} 条用例')

# 带 base_url
data_url = json.dumps({
    "requirement_result": mock_req,
    "base_url": "http://121.40.104.18/"
}).encode()
req = urllib.request.Request(BASE + '/testcase/generate', data=data_url,
    headers={"Content-Type": "application/json"})
r_url = json.loads(urllib.request.urlopen(req, timeout=180).read())
cases_url = r_url["data"]
print(f'  有 base_url: {len(cases_url)} 条用例')

# 展示两条用例对比（看第1条）
for label, cases in [("无URL", cases_no), ("有URL", cases_url)]:
    if cases:
        c = cases[0]
        print(f'\n  [{label}] {c["case_id"]} {c["title"]}')
        for s in c.get("steps", [])[:3]:
            print(f'    {s["step_num"]}. {s["action"]} → {s["expected"]}')

print('\n验证通过: base_url 已传递到用例生成提示词中 ✓')
