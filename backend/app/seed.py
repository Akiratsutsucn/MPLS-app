from app.models.checklist import ChecklistItem

DEFAULT_CHECKLIST: dict[str, list[str]] = {
    "preparation": [
        "商务",
        "Kick off",
        "人员预约",
        "人员培训",
        "基础信息收集",
    ],
    "self_assessment": [
        "人员预约",
        "Onsite自测评",
        "Online自测评",
    ],
    "rectification": [
        "差距分析提出",
        "整改方法提出",
        "整改联络",
        "整改决策调整",
        "整改实施",
        "结果验证",
        "整改结论对齐",
        "P1 Closing",
    ],
    "formal_evaluation": [
        "商务",
        "Kick off",
        "人员预约",
        "Onsite正式测评",
        "Online正式测评",
        "差距分析提出",
        "整改方法提出",
        "整改联络",
        "整改决策调整",
        "整改实施",
        "结果验证",
        "整改结论对齐",
    ],
    "filing": [
        "备案资料填写",
        "用户确认资料",
        "专家评审",
        "备案资料盖章",
        "备案资料上传",
        "备案审核",
        "获得备案号",
        "获得备案证",
    ],
    "reporting": [
        "汇总评测结果",
        "生成报告",
        "核对修改报告",
        "报告盖章",
        "报告提交用户",
        "报告提交网安",
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
