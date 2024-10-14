import os


def clear_logs_folder(max_count_logs=10):
    dir_path = 'data/logs'
    if not os.path.isdir(dir_path):
        return True
    dir_list = sorted(os.listdir(dir_path), key=lambda s: os.path.getctime(os.path.join(dir_path, s)))
    for file in dir_list[:-max_count_logs]:
        os.remove(f'{dir_path}/{file}')
    return True
