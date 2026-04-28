from entity.donation import Donation


class CreateDonationController:
    def create_donation(self, doner_account_id, fra_id, amount):
        return Donation.create_donation(doner_account_id, fra_id, amount)