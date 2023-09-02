# 创建密钥
from utils.util import * 
from utils.encryption_util import *

currId = get_machine_code()
end_time = offset_date_curtime(5)
encrypt_aes_uuid(currId,end_time)