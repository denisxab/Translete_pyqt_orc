#pyinstaller -F -w __main__.pyw && cd dist ren __main__.exe Translator.exe
try:
    import os
    import sys
    from Translator import main
    if __name__ == "__main__":
        main()
except ModuleNotFoundError:
    os.system("pip3 install -r requirements.txt")
    os.system(r"{}".format(__file__))
    sys.exit(0)

