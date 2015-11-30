from urllib.request import urlretrieve, urlopen
from os import getcwd, mkdir, listdir, walk
from os.path import join, isfile, exists
import zipfile
import dbf
import re

"""
Executing this file as a script will do the following:
1. Create subdirectories: data/zipped, data/unzipped, and data/csv
2. Download data from NHTSA's FTP servers for years past 2 years into data/zipped
3. Unzip downloaded data into data/unzipped
4. Convert data from DBF to CSV and place in data/csv
"""


"""
Creates suggested directory structure:

- data (defaults to subdir of this script)
    - zipped
    - unzipped
        - year (auto-created with `unzip_fars_files()`) 
            - DBF files
    - csv
        - years (auto-created with `dbf_to_csv()`)
            - CSV files

"""
def create_dir_structure(data_path=join(getcwd(), 'data')):
    
    # create the parent 'data' directory, if doesn't exist:
    if not exists(data_path):
        print("Creating %s"%data_path)
        mkdir(data_path)
    
    # subdirectory names and paths:
    dir_names = ['zipped', 'unzipped', 'csv']
    dir_paths = [join(data_path, dir_name) for dir_name in dir_names]
    
    for dir_path in dir_paths:
        if not exists(dir_path):
            print("Creating %s"%dir_path)
            mkdir(dir_path)
    
    return tuple(dir_paths)


"""
1. Downloads zipped files for given list of years
from NHTSA's FTP server to a given zipped_dir.
2. Skip already downloaded files, if in zipped_dir.
3. Alternatively, pass list_only=True to get list of files that would be downloaded

After running this function, you should have:
- data
    - zipped
        - FARS{year1}.zip
        - FARS{year2}.zip
        - ...
    - unzipped
        - (empty)
    - csv
        - (empty)
"""
def get_fars_files(zipped_dir, years=range(2004, 2015), preview=False):
    downloaded = []
    for year in years:
        remote_dir = "ftp://ftp.nhtsa.dot.gov/fars/%d/DBF/"%(year)
        with urlopen(remote_dir) as dir_index:

            # find zip filename, which starts with FARS, but is 
            # followed by 2digit or 4digits (year)
            # and sometimes has DBF in filename
            index = dir_index.read(50000)
            match = re.search('FARS(.*?)zip', str(index), flags=re.IGNORECASE)            
            filename = match.group(0)
            local_path = join(zipped_dir, filename)
            remote_path = join(remote_dir, filename)
            if isfile(local_path):
                continue
            if preview:
                # good for debugging: see what you'd download, before commiting
                downloaded.append(filename)
                continue
            else:
                # download the zip file
                print("Downloading %s"%filename)
                urlretrieve(remote_path, local_path) # raises error if file not found
                downloaded.append(filename)

    return downloaded


"""
Extract zip files to subdirectory "year"
under unzip_dir

After running this function, you should have:
- data
    - zipped
        - FARS{year1}.zip
        - FARS{year2}.zip
        - ...
    - unzipped
        - year1
            - file1.dbf
            - file2.dbf
            - ...
        - year2
            - ...
    - csv
        - (empty)
"""
def unzip_fars_files(zip_dir, unzip_dir):
    files = [f for f in listdir(zip_dir) if f.lower().startswith('fars') and f.lower().endswith('.zip')]
    years = []
    for filename in files:
        year = get_year_from_filename(filename)

        destination = join(unzip_dir, str(year))
        if not exists(destination):
            mkdir(destination)
            with zipfile.ZipFile(join(zip_dir, filename)) as f:
                print("Unzipping %s"%(filename))
                f.extractall(destination)
                years.append(year)
    return years


"""
Helper function to extract year from the filename,
where year is sometimes encoded as 2-digit, others as 4-digits.
Some examples:
FARS00.dbf
FARSDBF97.dbf
FARS1991.dbf
"""
def get_year_from_filename(filename):
    match = re.search('\d+', filename)
    if match:
        year = int(match.group(0))
        # infer millenium for 2-digit cases:
        if 0 <= year < 75:
            year += 2000
        elif 75 <= year <= 99:
            year += 1900
        return year
        
    return None


"""
Creates subdirectories under csv_dir
one for each year, just as under dbf_dir.
Converts DBF files to CSV files in the target directory.


After running this function, you should have:
- data
    - zipped
        - FARS{year1}.zip
        - FARS{year2}.zip
        - ...
    - unzipped
        - year1
            - file1.dbf
            - file2.dbf
            - ...
        - year2
            - ...
    - csv
        - year1
            - file1.csv
            - file2.csv
            - ...
        - year2
            - ...
"""

def dbf_to_csv(unzipped_dir, csv_dir, years=None, overwrite=False):
    if years == None:
            # diff the subdirectories of unzipped_dir and csv_dir
            # to see which years haven't been converted yet. 
            years = [year for year in listdir(unzipped_dir) if year not in listdir(csv_dir)]

    for year in years:
        year = str(year) # in case it's passed as integer
        destination_dir = join(csv_dir, year)
        origin_dir = join(unzipped_dir, year)

        if not exists(destination_dir):
            mkdir(destination_dir)

        dbfs = [f for f in listdir(origin_dir) if f.lower().endswith('.dbf')]
        for dbf_file in dbfs:
            destination_file = join(destination_dir, dbf_file[:-3]+'csv')
            origin_file = join(origin_dir, dbf_file)
            if exists(destination_file) and overwrite==False: 
                continue
            try:
                print("Converting %s from year %s"%(dbf_file, year))
                with dbf.Table(origin_file).open() as table:
                    dbf.export(table, destination_file) # as csv
            except:
                print("Error converting %s from year %s."%(dbf_file, year))
                continue



if __name__ == '__main__':

    # make dir structure and save paths to variables
    zipped_dir, unzipped_dir, csv_dir = create_dir_structure()

    # download files to zipped_dir
    years = [2013, 2014]
    # years = range(1975, 2015) # if you want all the years
    get_fars_files(zipped_dir, years=years)

    # unzip files to unzipped_dir
    unzip_fars_files(zipped_dir, unzipped_dir)
    
    # convert files to csv and place in csv_dir
    dbf_to_csv(unzipped_dir, csv_dir)