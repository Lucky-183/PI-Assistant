import os
from const_config import qqmusicpath
os.system(f'cd {qqmusicpath} && nohup npm start >> api.log 2>&1 &')
