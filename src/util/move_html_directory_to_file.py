import glob
import os
import os.path
import sys

"""Utility script that moves any directory with '.html' extension containing 'index.html'
 into a file with the same name.
 
 Usage:
 src/util/move_html_directory_to_file.py <ROOT DIRECTORY TO BE SEARCHED>
 """
 
root_dir = sys.argv[1]

all_file_count = 0
dir_count = 0
moved_count = 0
print('Going to check' + os.path.join(root_dir,'**/*.html'))

for fp in glob.glob(os.path.join(root_dir,'**/*.html'), recursive=True):
    all_file_count += 1
    if not os.path.isfile(fp):
        dir_count += 1
        # The directory at fp will have a file called index.html
        index_file = os.path.join(fp, 'index.html')
        if os.path.exists(index_file):
            # Move it to a temp loc first
            temp_loc = '/tmp/temp_file.html'
            os.rename(index_file, temp_loc)

            # Remove the directory
            if len(os.listdir(fp)) == 0:
                os.rmdir(fp)
                # Move the index.html to actual file path and location
                os.rename(temp_loc, fp)
                moved_count += 1
            else:
                print('Directory {} is not empty'.format(fp))

print('Found {0} total directories ending with .html. Fixed {1} index.html files'.format(dir_count, moved_count))