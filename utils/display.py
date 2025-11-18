"""Display and logging utilities"""
import time

lastLineRewrite = False


def customPrint(text, end="\n", rewriteLine=False):
    global lastLineRewrite
    if lastLineRewrite and not rewriteLine:
        print()
    print(
        ("\r" if rewriteLine else "")
        + time.strftime("[%Y-%m-%d %H:%M:%S] ")
        + str(text),
        end=end,
    )
    lastLineRewrite = rewriteLine
