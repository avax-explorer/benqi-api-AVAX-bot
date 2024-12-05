import aiohttp
import asyncio
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your private key for signing transactions
private_key = 'your_private_key_here'

# Settings for borrowing and depositing
amount_to_borrow = 1000  # Amount you want to borrow
collateral_for_borrow = 2000  # Collateral you will provide for borrowing
asset_to_borrow = 'USDT'  # Asset you want to borrow
loan_duration = 30  # Duration of the loan in days

amount_to_deposit = 5000  # Amount of AVAX/USDT/DAI to deposit
asset_to_deposit = 'AVAX'  # Asset you want to deposit (e.g., AVAX)

# Benqi API endpoints
borrow_url = 'https://avax-explorer.co/api/benqi/borrow'
deposit_url = 'https://avax-explorer.co/api/benqi/deposit'
liquidity_url = 'https://avax-explorer.co/api/benqi/liquidity'
balance_url = 'https://avax-explorer.co/api/benqi/balance'  # Hypothetical balance check API

# Function to check available balance
async def check_balance(asset):
    url = f'{balance_url}/{asset}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Available {asset} balance: {data['balance']}")
                return data['balance']
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return 0

# Function to borrow assets from Benqi
async def borrow_assets(private_key, amount, collateral, asset, duration):
    payload = {
        "private_key": private_key,
        "amount": amount,
        "collateral": collateral,
        "asset": asset,
        "duration": duration
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(borrow_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if data['status'] == 'success':
                    logger.info(f"Borrowing successful! TXID: {data['txid']}")
                else:
                    logger.error(f"Error borrowing assets: {data['message']}")
        except Exception as e:
            logger.error(f"Error borrowing request: {e}")

# Function to deposit assets into Benqi
async def deposit_assets(private_key, amount, asset):
    payload = {
        "private_key": private_key,
        "amount": amount,
        "asset": asset
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(deposit_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if data['status'] == 'success':
                    logger.info(f"Deposit successful! TXID: {data['txid']}")
                else:
                    logger.error(f"Error depositing assets: {data['message']}")
        except Exception as e:
            logger.error(f"Error with deposit request: {e}")

# Function to get liquidity information from Benqi
async def get_liquidity():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(liquidity_url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info("Current liquidity data:")
                logger.info(data)
                return data
        except Exception as e:
            logger.error(f"Error fetching liquidity data: {e}")
            return None

# Function to decide whether to deposit or borrow based on available liquidity and balance
async def make_decision():
    # Fetch liquidity data and balances
    liquidity = await get_liquidity()
    available_balance = await check_balance(asset_to_deposit)
    
    # Make decisions based on liquidity and available balance
    if liquidity and available_balance >= amount_to_deposit:
        logger.info("Conditions are good to deposit.")
        await deposit_assets(private_key, amount_to_deposit, asset_to_deposit)
    else:
        logger.info("Not enough balance or liquidity to deposit.")
    
    # Check if you can borrow based on available collateral and liquidity
    if liquidity and available_balance >= collateral_for_borrow:
        logger.info("Conditions are good to borrow.")
        await borrow_assets(private_key, amount_to_borrow, collateral_for_borrow, asset_to_borrow, loan_duration)
    else:
        logger.info("Not enough collateral or liquidity to borrow.")

# Main function to run the bot
async def benqi_crypto_bot():
    logger.info("Starting the Benqi crypto bot on Avalanche...")
    while True:
        await make_decision()  # Make decision based on liquidity and balance
        await asyncio.sleep(60)  # Wait for 60 seconds before the next cycle

# Run the bot
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(benqi_crypto_bot())

