from entity.fra_category import FRACategory


class UpdateCategoryController:
    def get_category(self, category_id):
        return FRACategory.find_by_id(category_id)

    def update_category(self, category_id, form_data):
        return FRACategory.update_category(
            category_id=category_id,
            category_name=form_data.get("category_name", ""),
            description=form_data.get("description", "")
        )