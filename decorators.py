from time import time

def timer(f):
    def wrapper(*args, **kwargs):
        start = time()

        f(*args, **kwargs)

        print(f'{f.__name__}() demorou {time()-start:.2f}s para ser executada.')

    return wrapper