from entity.fra import FRA


class CreateFraController:
    def create_fra(self, fundraiser_account_id, form_data):
        return FRA.create_fra(
            fundraiser_account_id=fundraiser_account_id,
            title=form_data.get("title", ""),
            description=form_data.get("description", ""),
            category=form_data.get("category", ""),
            target_amount=form_data.get("target_amount", ""),
            start_date=form_data.get("start_date", ""),
            end_date=form_data.get("end_date", "")
        )