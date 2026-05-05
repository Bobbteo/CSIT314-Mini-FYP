from entity.fra_category import FRACategory


class DisableCategoryController:
    def deactivate_category(self, category_id):
        return FRACategory.deactivate_category(category_id)

    def reactivate_category(self, category_id):
        return FRACategory.reactivate_category(category_id)