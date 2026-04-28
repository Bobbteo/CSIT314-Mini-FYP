from entity.fra import FRA


class ReadPublicFraController:
    def get_fra(self, fra_id):
        return FRA.find_by_id(fra_id)