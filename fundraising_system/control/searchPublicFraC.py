from entity.fra import FRA


class SearchPublicFraController:
    def search_fra(self, keyword):
        return FRA.search_public_fras(keyword)