from entity.fra import FRA


class SearchFraController:
    def search_fra(self, fundraiser_account_id, keyword):
        return FRA.search_fra(fundraiser_account_id, keyword)