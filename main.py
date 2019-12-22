import sys
# import scrape
from scrape import FureaiNet

if __name__ == "__main__":

    def main(args):
        if len(args) == 4:
            FureaiNet(args[1], args[2]).run()
        else:
            FureaiNet(13, 17).run()

    main(sys.argv)
