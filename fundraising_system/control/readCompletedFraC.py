from entity.fra import FRA


class ReadCompletedFraController:
    def read_completed_closed_fras(self, fundraiser_account_id):
        return FRA.get_completed_closed_fras_by_fundraiser(fundraiser_account_id)