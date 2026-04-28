from entity.fra import FRA


class ReadFraStatisticsController:
    def read_statistics(self, fundraiser_account_id):
        return FRA.get_fra_statistics_by_fundraiser(fundraiser_account_id)