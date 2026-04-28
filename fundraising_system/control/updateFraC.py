from entity.fra import FRA


class UpdateFraController:
    def get_fra(self, fra_id):
        return FRA.find_by_id(fra_id)

    def update_fra(self, fra_id, fundraiser_account_id, form_data):
        return FRA.update_fra(
            fra_id=fra_id,
            fundraiser_account_id=fundraiser_account_id,
            title=form_data.get("title", ""),
            description=form_data.get("description", ""),
            category=form_data.get("category", ""),
            target_amount=form_data.get("target_amount", ""),
            start_date=form_data.get("start_date", ""),
            end_date=form_data.get("end_date", "")
        )