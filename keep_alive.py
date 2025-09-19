import api.eclock
from core.log import logger


def main():
    try:
        logger.info('开始保活……')
        api.eclock.get_user_info()
        api.eclock.get_user_join_clock()
        logger.info('保活成功')
    except Exception as e:
        print(e)
        logger.error('保活失败!', e)

if __name__ == '__main__':
    main()