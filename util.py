import zipfile
import tempfile
import os
import shutil


class Util:
    @staticmethod
    def unzip(source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

    @staticmethod
    def remove_from_zip(zipfname, *filenames):
        tempdir = tempfile.mkdtemp()
        try:
            tempname = os.path.join(tempdir, 'new.zip')
            with zipfile.ZipFile(zipfname, 'r') as zipread:
                with zipfile.ZipFile(tempname, 'w') as zipwrite:
                    for item in zipread.infolist():
                        if item.filename not in filenames:
                            data = zipread.read(item.filename)
                            zipwrite.writestr(item, data)
            shutil.move(tempname, zipfname)
        finally:
            shutil.rmtree(tempdir)

    @staticmethod
    def append_to_zip(zip_file, filename):
        Util.remove_from_zip(zip_file, filename)
        z = zipfile.ZipFile(zip_file, "a")
        z.write(filename)
        z.close()

        #@staticmethod
        #def unzip(source_filename, dest_dir):
        #    with zipfile.ZipFile(source_filename) as zf:
        #        for name in zf.namelist():
        #            print name
        #            if name == 'page.xml':
        #                zf.extract(name, dest_dir)
        #                break
        #        zf.close()