import os
import json
from datetime import datetime
from app.config import settings


class ReportGenerator:
    """报告生成器 —— 负责将结果保存为文件"""

    @staticmethod
    def save_json(data, subdir: str, prefix: str) -> str:
        """保存 JSON 数据到 outputs 目录"""
        dir_path = os.path.join(settings.OUTPUT_DIR, subdir)
        os.makedirs(dir_path, exist_ok=True)
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    @staticmethod
    def save_markdown(content: str, subdir: str, prefix: str) -> str:
        """保存 Markdown 内容到 outputs 目录"""
        dir_path = os.path.join(settings.OUTPUT_DIR, subdir)
        os.makedirs(dir_path, exist_ok=True)
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    @staticmethod
    def defect_to_markdown(result: dict) -> str:
        """将缺陷分析结果转换为 Markdown 格式"""
        md = f"# 缺陷分析报告\n\n"
        md += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += f"## 摘要\n\n{result.get('summary', '')}\n\n"
        md += f"**失败用例总数**: {result.get('total_failures', 0)}\n\n"
        md += "## 缺陷详情\n\n"

        defects = result.get("defects", [])
        for i, d in enumerate(defects, 1):
            md += f"### {i}. {d.get('test_case', '未知用例')}\n\n"
            md += f"- **分类**: `{d.get('category', '未分类')}`\n"
            md += f"- **错误信息**: {d.get('error_message', '')}\n"
            md += f"- **根因分析**: {d.get('root_cause', '')}\n"
            md += f"- **修复建议**: {d.get('suggestion', '')}\n\n"

        md += "## 整体建议\n\n"
        md += result.get("overall_suggestion", "")
        return md


report_generator = ReportGenerator()
