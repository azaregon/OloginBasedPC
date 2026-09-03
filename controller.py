import time


start_time = time.time()


end_time = start_time + 30 



while True:
    time_now = time.time()
    # print("Time left: ", end_time - time_now)
    if time_now > end_time:
        import login_window

    time.sleep(1)