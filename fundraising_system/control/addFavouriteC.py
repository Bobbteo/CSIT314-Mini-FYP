from entity.favourite import Favourite


class AddFavouriteController:
    def add_favourite(self, doner_account_id, fra_id):
        return Favourite.add_favourite(doner_account_id, fra_id)