import zipfile


class Util:
    @staticmethod
    def unzip(source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

    #@staticmethod
    #def unzip(source_filename, dest_dir):
    #    with zipfile.ZipFile(source_filename) as zf:
    #        for name in zf.namelist():
    #            print name
    #            if name == 'page.xml':
    #                zf.extract(name, dest_dir)
    #                break
    #        zf.close()