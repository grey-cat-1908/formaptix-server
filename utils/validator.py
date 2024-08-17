def validate_tin(value: str) -> bool:
    if len(value) != 10 and len(value) != 12:
        return False

    value = list(map(int, value))

    if len(value) == 10:
        checksum = (
            (
                2 * value[0]
                + 4 * value[1]
                + 10 * value[2]
                + 3 * value[3]
                + 5 * value[4]
                + 9 * value[5]
                + 4 * value[6]
                + 6 * value[7]
                + 8 * value[8]
            )
            % 11
            % 10
        )
        return value[9] == checksum
    if len(value) == 12:
        checksum1 = (
            (
                7 * value[0]
                + 2 * value[1]
                + 4 * value[2]
                + 10 * value[3]
                + 3 * value[4]
                + 5 * value[5]
                + 9 * value[6]
                + 4 * value[7]
                + 6 * value[8]
                + 8 * value[9]
            )
            % 11
            % 10
        )
        checksum2 = (
            (
                3 * value[0]
                + 7 * value[1]
                + 2 * value[2]
                + 4 * value[3]
                + 10 * value[4]
                + 3 * value[5]
                + 5 * value[6]
                + 9 * value[7]
                + 4 * value[8]
                + 6 * value[9]
                + 8 * value[10]
            )
            % 11
            % 10
        )
        return value[10] == checksum1 and value[11] == checksum2

    return False


def validate_snils(value: str) -> bool:
    if len(value) == 11:
        checksum = 0
        for i in range(9):
            checksum += int(value[i]) * (9 - i)

        if checksum > 101:
            checksum = checksum % 101
        if checksum == 100 or checksum == 101:
            checksum = 0

        return checksum == int(value[9:])

    return False
