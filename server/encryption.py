def decryptCode(number: int) -> str:
    """
    Given an encrypted number, it will return the decrypted version

    :param number: encrypted number

    :return: decrypted string

    """
    if not isinstance(number, int):
        raise TypeError("number must be an integer")

    number_str = str(number)
    actual_num = ""
    for l in number_str:
        l = int(l)
        l += 4
        l = l % 10
        actual_num += str(l)
    number = int(actual_num)

    is_negative = number < 0
    number = abs(number)

    alphabet, base36 = ["0123456789abcdefghijklmnopqrstuvwxyz", ""]

    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    if is_negative:
        base36 = "-" + base36

    code = base36 or alphabet[0]
    code = (16 - len(code)) * "0" + code
    return code


def encryptCode(code: str) -> int:
    """
    Given a string, will return encrypted version

    :param code: string of data

    :return: encrypted code
    """
    temp = int(code, 36)
    temp = str(temp)
    code = ""
    for l in temp:
        l = int(l)
        l += 6
        l = l % 10
        code += str(l)
    return int(code)
