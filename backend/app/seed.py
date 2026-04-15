from app.models.checklist import ChecklistItem

DEFAULT_CHECKLIST: dict[str, list[str]] = {
    "grading": [
        "确定系统边界",
        "初步定级",
        "专家评审",
        "主管部门审核",
        "定级报告编写",
    ],
    "filing": [
        "准备备案材料",
        "提交公安机关",
        "备案审核",
        "获取备案证明",
    ],
    "rectification": [
        "安全方案设计",
        "安全产品部署",
        "安全策略配置",
        "整改验证测试",
    ],
    "evaluation": [
        "测评方案编制",
        "现场测评实施",
        "测评报告编写",
        "问题整改跟踪",
    ],
    "supervision": [
        "自查报告编写",
        "配合监督检查",
        "整改落实",
        "归档总结",
    ],
}


def create_default_checklist(project_id: int) -> list[ChecklistItem]:
    items = []
    for phase, contents in DEFAULT_CHECKLIST.items():
        for order, content in enumerate(contents):
            items.append(
                ChecklistItem(
                    project_id=project_id,
                    phase=phase,
                    content=content,
                    sort_order=order,
                    is_custom=False,
                )
            )
    return items
