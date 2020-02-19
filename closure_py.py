def outer_func(message):
    message = message

    def inner_func():
        print(message)

    return inner_func()


outer_func("Hello Closure")


"""
Closure: a Closure is iinner function which remembers and has accees to variables in the local scope
in which it was created. even outer function has finished executing.
"""

"""
When and why to use Closures:

    1. As closures are used as callback functions, they provide some sort of data hiding. 
        This helps us to reduce the use of global variables.
    2. When we have few functions in our code, closures prove to be efficient way. 
        But if we need to have many functions, then go for class (OOP).

"""


def outer_func1():
    name = "Variable Created in outer function"

    def inner_func1():
        print(name)

    return inner_func1


my_func1 = outer_func1()

print(my_func1)

my_func1()  # here outer function(outer_func1) is finished executing, but inner_func1 still able to access variable "name"


def outer_func2(message):
    message = message

    def inner_func2():
        print(message)

    return inner_func2


hi_func1 = outer_func2("hi")
hello_func1 = outer_func2("hello")


hi_func1()
hello_func1()

"More practical examples"

import logging

logging.basicConfig(filename="closure_py_log.log", level=logging.INFO)


def logger(func):
    def log_inner_func(*args):
        logging.info(f"Running {func.__name__} with argumenrs {args}")
        print(func(*args))

    return log_inner_func


def add(x, y):
    return x + y


def sub(x, y):
    return x - y


add_logger = logger(add)
sub_logger = logger(sub)

add_logger(3, 7)
add_logger(1, 7)
sub_logger(10, 2)
sub_logger(20, 10)
