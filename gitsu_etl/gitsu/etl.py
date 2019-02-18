import multiprocessing


def map_async(*args, **kwargs):
    with multiprocessing.Pool() as pool:
        proc = pool.map_async(*args, **kwargs)
        return proc.get()
