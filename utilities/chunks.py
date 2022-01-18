def split(items_in_list, chunk_size):
    """
    Partition an input list into smaller lists.
    :param items_in_list: The list of items to be split.
    :param chunk_size: The number of items in each returned list.
    :return: List
    """
    for i in range(0, len(items_in_list), chunk_size):
        yield items_in_list[i:i + chunk_size]

# .