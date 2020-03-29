import re
from collections import Counter
from tqdm import tqdm


def get_delimited_strings_count(str_arr, count, delimiter):
    strings_found = Counter({})
    regex = delimiter + "\w+"

    for str in tqdm(str_arr, total=count, desc='Loading'):
        found = re.findall(regex, str)
        strings_found = strings_found + Counter(found)

    return strings_found
