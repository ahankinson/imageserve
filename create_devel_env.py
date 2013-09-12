import os

os.makedirs('images')
f = open('foldernames.txt', 'r')
for fln in f.readlines():
    folder = os.path.join('images', fln.strip())
    os.makedirs(folder)
    for fl in xrange(100):
        filename = "testtiff-{0}.tiff".format(fl)
        t = open(os.path.join(folder, filename), 'w')
        t.close()
f.close()
