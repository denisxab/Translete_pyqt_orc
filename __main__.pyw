# -*- coding: utf-8 -*-
# pyinstaller -F -w __main__.pyw
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C0301
# pylint: disable=R0902

try:
    import os
    import sys
    from Translator import main
    if __name__ == "__main__":
        main()
except ModuleNotFoundError:
    os.system("pip3 install -r requirements.txt")
    sys.exit(0)
