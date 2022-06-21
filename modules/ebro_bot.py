import pprint
import time
import datetime


rule_text = {'F': '플렉스', 'T': '탱커', 'D': '딜러', 'H': '힐러'}


class EBRO_bot:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.channel_list = []
        self.channel_id_list = []
        self.messages = []
        self.player = {}

        self.inited = False

    def init(self):
        guild = self.driver.guilds[0]
        text_channels = guild.text_channels

        self.channel_list = list(filter(lambda channel: channel.name in self.config['channel_list'], text_channels))
        self.channel_id_list = list(map(lambda channel: channel.id, self.channel_list))

        self.inited = True

    def new_activate_detect(self, member, payload):
        now = int(time.time())
        now_string = datetime.datetime.fromtimestamp(now).strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
        nickname = member.nick
        rule_name = payload.emoji.name

        # 관전자 제외
        if rule_name == "👀":
            return

        # 플레이어가 없을경우 새로 등록
        if not nickname in self.player:
            self.player[nickname] = {}
            self.player[nickname]['history'] = []
            self.player[nickname]['nickname'] = nickname

        self.player[nickname]['history'] = self.player[nickname]['history'] + [rule_name]
        print("[*] " + now_string + " : " + nickname + "님 금일 게임 횟수 : " + str(len(self.player[nickname]['history'])))

    def activate_detect(self, activate_type, member, payload):
        now = int(time.time())
        now_string = datetime.datetime.fromtimestamp(now).strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
        nickname = member.display_name + "#" + member.discriminator
        rule_name = payload.emoji.name

        # 관전자 제외
        if rule_name == "👀":
            return

        # 플레이어가 없을경우 새로 등록
        if not nickname in self.player:
            self.player[nickname] = {}
            self.player[nickname]['rule_choiced'] = []
            self.player[nickname]['nickname'] = nickname

        # 역할을 선택했을 경우
        if activate_type == 'on':

            # 첫 역할선택일 경우
            if not 'play_started' in self.player[nickname]:
                self.player[nickname]['play_started'] = now

            # 해당 플레이어의 선택한 역할 리스트에 추가
            self.player[nickname]['rule_choiced'] = self.player[nickname]['rule_choiced'] + [rule_name]

        # 역할선택을 취소했을 경우
        elif activate_type == 'off' and nickname in self.player:

            # 선택한 역할의 수가 1개 이상일 경우
            if len(self.player[nickname]['rule_choiced']) >= 2:
                self.player[nickname]['rule_choiced'].remove(rule_name)

            # 역할을 모두 취소했을 경우
            elif len(self.player[nickname]['rule_choiced']) <= 1:
                self.player[nickname]['play_ended'] = now
                self.player[nickname]['rule_choiced'].remove(rule_name)
                history = self.player[nickname].copy()

                # 오늘 처음 게임한게 아닐 경우
                if 'history' in self.player[nickname]:
                    history.pop('history')
                    history.pop('rule_choiced')

                # 오늘 처음 게임했을 경우
                else:
                    self.player[nickname]['history'] = []

                self.player[nickname]['history'] = self.player[nickname]['history'] + [history]
                self.player[nickname]['rule_choiced'] = []

                self.player[nickname].pop('play_started')
                self.player[nickname].pop('play_ended')

                print("[*] " + now_string + " : " + nickname + "님 금일 게임 횟수 : " + str(len(self.player[nickname]['history'])))
