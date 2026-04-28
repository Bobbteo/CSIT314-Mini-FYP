from entity.donation import Donation


class ReadDonationHistoryController:
    def read_history(self, doner_account_id):
        return Donation.get_donation_history(doner_account_id)