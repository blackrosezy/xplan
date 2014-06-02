import argparse
import sys, logging

from xplan import XPlan
from excel import Excel

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s') # include timestamp

def main():
    parser = argparse.ArgumentParser(description='XPlan import/export conditions')
    parser.add_argument('-i', '--import-zip', action='store_true', help='Import page.zip and generate excel file.')
    parser.add_argument('-o', '--export-zip', action='store_true', help='Export excel to page.zip')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.import_zip and args.export_zip:
        parser.print_help()
        sys.exit(1)

    if args.import_zip:
        p = XPlan()
        if p.load_zip():
            x = Excel()
            p.extract_objects()
            p.generate_obj_file()
            x.generate_xls_file(p.get_xplan_object())

        logging.info("[Complete]\n\n")

    if args.export_zip:
        p = XPlan()
        x = Excel()
        p.generate_zip_file(x.get_xplan_object())
        logging.info("[Complete]\n\n")


if __name__ == "__main__":
    main()


