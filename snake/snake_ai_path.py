import main

debug = main.debug

if debug:
    import os
    from os.path import exists
    import logging
    file_path = "path_ai_log.txt"
    if exists(file_path):
        os.remove(file_path)
    logging.basicConfig(filename=file_path,
                                filemode='a',
                                format='',
                                datefmt='',
                                level=logging.INFO)

def get_action(snake, food, board_size):
    pass