from entity.favourite import Favourite


class ReadFavouriteController:
    def read_favourites(self, doner_account_id):
        return Favourite.get_favourites(doner_account_id)