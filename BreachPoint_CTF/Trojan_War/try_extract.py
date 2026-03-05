import zipfile
from pathlib import Path
z='The Odyssey.zip'
print('Zip exists:', Path(z).exists())
candidates=['helen','Helen','helen123','odysseus','odysseus_journey','Princess','princess','BPCTF','bpctf','theprince','ancient','enduring','treasure','HelenOfTroy','helen_of_troy']
with zipfile.ZipFile(z) as zz:
    for p in candidates:
        try:
            zz.extractall(pwd=p.encode())
            print('Success',p)
            break
        except RuntimeError:
            pass
        except Exception as e:
            print('Err',p,e)
    else:
        print('No password found')
