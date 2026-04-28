from entity.fra import FRA


class CancelFraController:
    def cancel_fra(self, fra_id, fundraiser_account_id):
        return FRA.cancel_fra(fra_id, fundraiser_account_id)