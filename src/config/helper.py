def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def split_list_to_n_parts(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
