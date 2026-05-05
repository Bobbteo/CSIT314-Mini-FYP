from entity.fra_category import FRACategory


class ReadCategoryController:
    def read_categories(self):
        return FRACategory.get_all_categories()