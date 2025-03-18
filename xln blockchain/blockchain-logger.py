import os
from web3 import Web3

# Read environment variables
GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL", "http://localhost:8545")
PRIVATE_KEY = os.getenv("GANACHE_PRIVATE_KEY")

if not PRIVATE_KEY:
    print("❌ Error: GANACHE_PRIVATE_KEY is not set! Use 'export GANACHE_PRIVATE_KEY=<your_private_key>'")
    exit(1)

print(f"ℹ️ Using RPC URL: {GANACHE_RPC_URL}")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))

if not w3.is_connected():
    print("❌ Failed to connect to blockchain at", GANACHE_RPC_URL)
    exit(1)

print("✅ Connected to blockchain:", GANACHE_RPC_URL)

# Get accounts
accounts = w3.eth.accounts
if not accounts:
    print("❌ No accounts found in Ganache.")
    exit(1)

print("✅ Found accounts:", accounts)

def log_to_blockchain(message):
    try:
        txn = {
            'to': accounts[1],  
            'from': accounts[0],  
            'value': 0,  
            'gas': 100000,  
            'gasPrice': w3.to_wei('10', 'gwei'),
            'data': w3.to_hex(text=message),  
            'nonce': w3.eth.get_transaction_count(accounts[0])  
        }

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        
        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"🚀 Transaction sent! Hash: {w3.to_hex(tx_hash)}")

        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")

    except Exception as e:
        print("❌ Error:", str(e))

# Example usage
log_to_blockchain("Hello, Kubernetes Blockchain!")
