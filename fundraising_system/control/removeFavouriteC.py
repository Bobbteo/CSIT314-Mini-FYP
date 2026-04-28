from entity.favourite import Favourite


class RemoveFavouriteController:
    def remove_favourite(self, doner_account_id, fra_id):
        return Favourite.remove_favourite(doner_account_id, fra_id)