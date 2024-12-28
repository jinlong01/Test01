from time import sleep
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import wallet
from abi import *



def readfile():
    with open('wallets.txt', 'r') as f:
        content = f.readlines()
        lines = [line.rstrip('\n') for line in content]
        print('Wallets: ' + str(len(lines)))
        return lines


def send_money(web3, contract_address, private_key, amount, chainid):
    try:
        price = web3.eth.gas_price
        nonce = web3.eth.get_transaction_count(contract_address)
        value_send = int(amount - price * 22000)
        if value_send > 0:
            contract = web3.eth.contract(address=wallet, abi=abi)
            token_tx = contract.functions.transfer(wallet, amount).build_transaction({
        'chainId': chainid,
        'value': value_send,
        'gas': 22000,
        'gasPrice': price,
        'nonce': nonce})
            sign_txn = web3.eth.account.sign_transaction(token_tx, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)
            web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transaction has been sent to: {wallet}")
    except Exception as e:
        print(f"Error: {str(e)}") 


def main(lines):
    for line in lines:
        contract_address, private_key = line.split(',')[:2]
        contract_address = Web3.to_checksum_address(contract_address)

        for api, chain_id, chain_name in [
            ('https://bsc-dataseed.bnbchain.org', 56, 'BNB'),
            ("https://ethereum.publicnode.com", 1, 'ETH'),
            ("https://polygon-rpc.com", 137, 'MATIC'),
            ("https://api.roninchain.com/rpc", 2020, "RONIN"),
            ("https://moonbeam-rpc.publicnode.com", 1284, "GLMR"),
            ("https://rpc.pulsechain.com", 369, "PLS"),
            ("https://rpc.fantom.network", 250, "FTM"),
            ('https://evm.astar.network', 592, 'ASTR'),
            ('https://moonriver-rpc.publicnode.com', 1285, 'MOVR')
        ]:
            try:
                web3 = Web3(Web3.HTTPProvider(api))
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                balance = web3.eth.get_balance(contract_address)
                if balance > int(web3.to_wei(1, 'gwei') * 22000):
                    print(f'{chain_name}: Balance detected!')
                    send_money(web3, contract_address, private_key, balance, chainid=chain_id)
            except Exception as e:
                print(f"{chain_name} Error: {str(e)}")
    print(f'Processed private_key`s completed')
    input()
if __name__ == "__main__":
    main(readfile())
