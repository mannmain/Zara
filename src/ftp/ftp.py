from datetime import datetime
import ftplib
import json
import time


def upload_file(ftp_host, ftp_user, ftp_password):
    try:
        with open('ftp/json.json', 'r', encoding='UTF-8') as file:
            json_file = json.load(file)
    except:
        return False
    if len(json_file) >= 1:
        def progress():
            def callback(block):
                callback.uploaded += len(block)
            callback.uploaded = 0
            return callback



        while True:
            try:
                with ftplib.FTP(ftp_host, ftp_user, ftp_password) as ftp, open('ftp/json.json', 'rb') as file_to_upload:
                    print(f'nice connect to ftp {datetime.now().strftime("%m.%d %H:%M")}')
                    filename = f'Import_{datetime.now().strftime("%Y_%m_%d_%H_%M")}.json'
                    ftp.storbinary("STOR " + filename, file_to_upload, 1024, progress())
                    print(f'nice upload {filename} {datetime.now().strftime("%m.%d %H:%M")}')
                    # with open(f'last_uploads/{filename}', 'w', encoding='utf-8') as file:
                    #     json.dump(json_file, file)
                break
            except:
                print(f'error with upload file {datetime.now().strftime("%m.%d %H:%M")}')
                time.sleep(3600)
        return len(json_file)


def main():
    upload_file()


if __name__ == '__main__':
    # with open('json_0.json', 'r', encoding='UTF-8') as file:
    #     json_file = json.load(file)
    # with open('json_1.json', 'r', encoding='UTF-8') as file:
    #     json_file += json.load(file)
    # with open('json_2.json', 'r', encoding='UTF-8') as file:
    #     json_file += json.load(file)
    # with open('json_3.json', 'r', encoding='UTF-8') as file:
    #     json_file += json.load(file)
    #
    # with open('json.json', 'w', encoding='UTF-8') as file:
    #     json.dump(json_file, file)
    # ###################
    # with open('json.json', 'r', encoding='UTF-8') as file:
    #     json_file = json.load(file)
    # print(len(json_file))
    # for i in json_file:
    #     c = 0
    #     for j in json_file:
    #         if i['externalId'] == j['externalId']:
    #             c += 1
    #             if c == 2:
    #                 print('wgoihweg')
    #                 print(i['externalId'])
    main()
