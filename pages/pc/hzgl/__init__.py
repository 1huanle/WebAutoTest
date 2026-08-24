"""PC 端患者管理页面对象。"""

from .hzgl_page import HzglPage
from .patient_detail_dialog import PatientDetailDialog
from .patient_filter_section import PatientFilterSection
from .patient_list_section import PatientCard, PatientListSection
from .patient_create_page import PatientCreatePage

__all__ = [
    "HzglPage",
    "PatientCard",
    "PatientDetailDialog",
    "PatientCreatePage",
    "PatientFilterSection",
    "PatientListSection",
]
