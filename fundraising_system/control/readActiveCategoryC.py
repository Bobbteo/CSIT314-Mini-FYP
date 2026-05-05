from entity.fra_category import FRACategory


class ReadActiveCategoryController:
    def read_active_categories(self):
        return FRACategory.get_active_categories()