from entity.donation import Donation


class SearchDonationHistoryController:
    def search_history(self, doner_account_id, keyword):
        return Donation.search_donation_history(doner_account_id, keyword)