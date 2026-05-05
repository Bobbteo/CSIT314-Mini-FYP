from entity.fra_category import FRACategory


class CreateCategoryController:
    def create_category(self, form_data):
        return FRACategory.create_category(
            category_name=form_data.get("category_name", ""),
            description=form_data.get("description", "")
        )