from .base_section import NurseSection


class MonitoringRecordsSection(NurseSection):
    SECTION_TITLE = "监测记录"

    def open_add_record(self) -> "MonitoringRecordsSection":
        return self.click_action("添加监测", "新增监测")
