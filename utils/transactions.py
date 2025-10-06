import base64
import requests


class TransactionManager:
    """Manages fetching and filtering Skinport transactions via API."""

    def __init__(self, client_id, client_secret):
        """Initialize with API client credentials."""
        self.transactions = []  # List to store all transactions
        self.client_id = client_id
        self.client_secret = client_secret

    def load_transactions(self):
        """Fetch transactions from Skinport API and store in self.transactions."""
        # Encode client credentials for Basic Auth
        clientData = f"{self.client_id}:{self.client_secret}"
        encodedData = str(base64.b64encode(
            clientData.encode("utf-8")), "utf-8")
        authorizationHeaderString = f"Basic {encodedData}"

        page = 1
        max_pages = 2  # Initialize to enter the loop
        data = []

        # Paginate through all transaction pages
        while max_pages >= page:
            response = requests.get(
                "https://api.skinport.com/v1/account/transactions",
                headers={"authorization": authorizationHeaderString},
                params={
                    "page": page,
                    "limit": 100,
                    "order": "desc"
                }
            )

            json_data = response.json()

            # Update total pages from API response
            max_pages = json_data['pagination']['pages']

            try:
                data += json_data['data']  # Add transactions from this page
            except:
                print(json_data)  # Print unexpected response

            page += 1  # Move to next page

        self.transactions = data
        return True  # Indicate success

    def get_bought(self):
        """Return a list of transactions where type is 'purchase'."""
        return [transaction for transaction in self.transactions if transaction.get('type') == 'purchase']

    def get_sold(self):
        """Return a list of transactions where type is 'credit' (sold items)."""
        return [transaction for transaction in self.transactions if transaction.get('type') == 'credit']
