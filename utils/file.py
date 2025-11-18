"""File operation utilities"""


def tupleToStr(tup):
    output = ""
    for item in tup:
        if len(output):
            output = output + ", " + str(item)
        else:
            output = str(item)
    return output
