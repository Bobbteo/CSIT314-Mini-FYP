from entity.fra import FRA


class ReadFraController:
    def read_fra(self, fundraiser_account_id):
        return FRA.get_by_fundraiser(fundraiser_account_id)