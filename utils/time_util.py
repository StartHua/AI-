from datetime import datetime, timedelta

# 计算日期的偏移量
def calculate_offset_date(base_date, offset_days):
    """
    计算日期的偏移量（增加或减少天数）。

    :param base_date: 基准日期
    :param offset_days: 偏移天数，正数表示增加天数，负数表示减少天数
    :return: 偏移后的日期
    """
    return base_date + timedelta(days=offset_days)

# 当前时间偏移几天
def offset_date_curtime(offset_days):
    return calculate_offset_date(datetime.now(),offset_days)

def concatenate_datetime_with_string(d:datetime):

    # 将 datetime 对象转换为字符串，可以使用 strftime 方法
    formatted_time = d.strftime("%Y-%m-%d %H:%M:%S")

    # 进行字符串拼接
    message = formatted_time

    return message    

def is_current_time_greater(input_time_str):
    # 将输入的时间字符串转换为 datetime 对象
    input_time = datetime.strptime(input_time_str, "%Y-%m-%d %H:%M:%S")
    
    # 获取当前时间的 datetime 对象
    current_time = datetime.now()
    
    # 比较当前时间是否大于输入时间
    if current_time > input_time:
        return True
    else:
        return False