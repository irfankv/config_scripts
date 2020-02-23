# import logging

# logging.basicConfig(filename="log_ex.log", level=logging.DEBUG,
#                     format="%(asctime)s:%(level)s:%(message)s", datefmt='%d-%b-%y %H:%M:%S')


# logging.debug('Admin logged in')

import logging

logging.basicConfig(filename="log_ex.log",
                    format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
logging.info('Admin logged in')

name = "Irfan"
logging.error(f'{name} raised an error')
