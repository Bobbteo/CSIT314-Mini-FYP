from entity.fra import FRA


class ReactivateFraController:
    def reactivate_fra(self, fra_id, fundraiser_account_id):
        return FRA.reactivate_fra(fra_id, fundraiser_account_id)