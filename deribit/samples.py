# ##################################################################
# SAMPLE USAGE
# ##################################################################

if __name__ == '__main__':

    # ####################
    # IMPORT
    # ####################

    import json
    import cProfile

    from .client import deltaClient  # facade

    # ####################
    # SOME API KEYS
    # ####################

    with open("/etc/config/delta.json") as config_file:
        config = json.load(config_file)
    key = config["KEY"]
    secret = config["SECRET"]

    # ####################
    # INSTANTIATE CLIENT
    # ####################

    delta = deltaClient(key=key, secret=secret)

    # Test with low expectations
    server_time = delta.send_request.server_time()
    print(server_time)

    account_summary = delta.send_request.account_summary()
    print(account_summary)

    pos_btc = delta.send_request.all_positions()

    # ####################
    # TEST : REQUESTS
    # ####################

    print("Requesting server_time.")
    server_time = delta.send_request.server_time()
    print(server_time)

    print("Requesting index_level.")
    index_level = delta.send_request.index_level("BTC")
    print(index_level)

    print("Requesting BTC index_level.")
    BTC_index_level = delta.send_request.btc_index()
    print(BTC_index_level)

    print("Requesting ETH index_level.")
    ETH_index_level = delta.send_request.eth_index()
    print(ETH_index_level)

    print("Requesting delta instruments.")
    instruments = delta.send_request.instruments("BTC")
    print(instruments)

    print("Requesting delta trades (from the last, going back up to last - count).")
    some_trades = delta.send_request.trades(["BTC-PERPETUAL", "ETH-PERPETUAL"])
    print(some_trades)

    print("Requesting all delta trades for given instruments.")
    futures = ["ETH-PERPETUAL", "BTC-PERPETUAL"]
    options = ["BTC-29NOV19-8000-C"]
    books = delta.send_request.orderbooks(futures)
    print(books)
