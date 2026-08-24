from .base_section import NurseSection


class TemporaryOrdersSection(NurseSection):
    SECTION_TITLE = "临时医嘱"

    def open_add_order(self) -> "TemporaryOrdersSection":
        return self.click_action("添加医嘱", "新增医嘱")

    def execute_selected_order(self) -> "TemporaryOrdersSection":
        return self.click_action("执行医嘱", "执行")
