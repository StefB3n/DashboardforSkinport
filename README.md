# Skinport Transactions Dashboard

A dashboard to visualize and analyze your Skinport transactions, with the option of searching specific items and tracking payout history.

Note: This project is not affiliated with Skinport. It is an independent tool created to make it easier to view and analyze your transaction history via the Skinport API.

## Features

* Search transactions by **item name** (MarketHashName)
* View **purchase, sold, and payout history**
* Show **line charts** for sold vs purchased transactions
* View **total sales per buyer country**

## Examples
<img width="1687" height="780" alt="image" src="https://github.com/user-attachments/assets/2b614c46-4a33-41f4-923f-2e60e594d02a" />

<img width="958" height="618" alt="image" src="https://github.com/user-attachments/assets/9b29382d-36be-41bf-8ee2-4b13a0455ef7" />
<img width="938" height="433" alt="image" src="https://github.com/user-attachments/assets/3d8b73bb-b5e6-4d6a-b43f-9016f3deff31" />



## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/skinport-dashboard.git
cd skinport-dashboard
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create a `.env` file** (optional, or input keys directly in the dashboard)

```
API_CLIENT_ID=your_client_id
API_CLIENT_SECRET=your_client_secret
```

4. **Run the Streamlit app**

```bash
streamlit run app.py
```

5. **Use the dashboard**

* Enter your API keys if not already in `.env`
* Click **Load all transactions**, after they are all received the dashboard will load
