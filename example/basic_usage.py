import json
from time import sleep
from xhs import XhsClient, DataFetchError, help
from playwright.sync_api import sync_playwright
from datetime import datetime
import json


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "../tests/stealth.min.js"
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


if __name__ == '__main__':
    cookie = "abRequestId=2417f562-de00-5f42-801b-500e7b6e6ac6; xsecappid=xhs-pc-web; webId=7a014ab7cbfc296c122bd7b7bb125d83; webBuild=3.15.9; a1=18bd777bac55f1ni8xoibdzainzclhmucfxn0dsza40000324384; websectiga=7750c37de43b7be9de8ed9ff8ea0e576519e8cd2157322eb972ecb429a7735d4; sec_poison_id=2ff69899-0bc4-442c-93ab-4293312792c3; gid=yYDfW048Y2SyyYDfWWWD0ifMS22iyI3YCl3DCu0fu03IuI48S1x678888qJ4qY48Y4fyjK0J; web_session=040069781c25d4515522e7a460374b68c1790f; cacheId=0eaee723-d1d9-48fa-80a6-a2b563e75e1d;"

    xhs_client = XhsClient(cookie, sign=sign)
    print(datetime.now())

    for _ in range(10):
        # 即便上面做了重试，还是有可能会遇到签名失败的情况，重试即可
        try:
            # note = xhs_client.get_note_by_id("635166870000000015021850")
            # print(json.dumps(note, indent=4))
            # break
            # print(help.get_imgs_url_from_note(note))

            # 用户列表
            user_list = []
            # 获取关键词笔记列表
            data = xhs_client.get_note_by_keyword("穿搭")
            origin_note_list = data['items']
            # 笔记浏览列表
            note_view_list = []
            # 笔记详情列表
            note_detail_list = []
            unique_ids = set()
            
            # 遍历原始列表
            for item in origin_note_list:
                note_id = item['id']
            
                if note_id not in unique_ids:
                    # Add the unique id to the set
                    unique_ids.add(note_id)
                    # Add the item to the new array
                    note_view_list.append(item)
                    # 查询笔记详情
                    note_detail_data = xhs_client.get_note_by_id(note_id)
                    # print(note_detail_data)
                    note_detail_list.append(note_detail_data)
            
            # Get today's date in the format 'YYYY-MM-DD'
            today_date = datetime.now().strftime('%Y-%m-%d')
            # 导出笔记浏览列表
            note_view_list_file_name = f'/result/{today_date}/note_view_list.json'
            with open(note_view_list_file_name, 'w') as json_file:
                json.dump(note_view_list, json_file)
            
            # 导出笔记详情列表
            note_detail_list_file_name = f'/result/{today_date}/note_detail_list.json'
            with open(note_detail_list_file_name, 'w') as json_file:
                json.dump(note_detail_list, json_file)
            break

        except DataFetchError as e:
            print(e)
            print("失败重试一下下")
