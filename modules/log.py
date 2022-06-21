import json
import time
import datetime
import os


class Log:
    def __init__(self, base_dir="./logfile/"):
        self.base_dir = base_dir

        if not os.path.isdir(self.base_dir):
            os.mkdir(self.base_dir)

    def save(self, log):
        now = int(time.time())
        content = {}

        for player in log:
            content[player] = len(log[player]['history'])
        date_dir = datetime.datetime.fromtimestamp(now).strftime('%Y-%m') + "/"
        file_name = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d') + ".json"
        file_content = json.dumps(content, indent=4, ensure_ascii=False)

        path = self.base_dir + date_dir + file_name
        open(path, 'w', encoding='utf-8-sig').write(file_content)

        return {"status": True}

    def load(self, target_date):
        dirpath = self.base_dir + target_date + "/"

        if not os.path.isdir(dirpath):
            return {'status': False, 'message': "no data"}

        filelist = os.listdir(dirpath)
        total = {}

        for filename in filelist:
            filepath = dirpath + filename

            with open(filepath, 'r', encoding='utf-8-sig') as filedescriptor:
                data = filedescriptor.read()
                content = json.loads(data)

                for player in content:

                    # 유저가 이미 집계중이면 파일에 기록된 수하고 더함
                    if player in total:
                        total[player] = total[player] + content[player]

                    # 유저가 집계중이지 않으면 현재 파일에 기록된 수로 기록함
                    else:
                        total[player] = content[player]

        # 게임 많이한 순서로 정렬
        total = dict(sorted(total.items(), key=lambda item: item[1], reverse=True))

        return {'status': True, 'data': total}
