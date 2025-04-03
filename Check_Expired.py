from notion_client import Client
import requests

NOTION_TOKEN = "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"
DATABASE_ID = "1c8ecb65249380a9ba12e330b94f542c"
CHECK_BILI_API = "https://www.bilibili.com/video/"

# 创建 Notion 客户端
notion = Client(auth=NOTION_TOKEN)


def get_all_bv_ids():
    """
    从 Notion 数据库中获取所有 BV 号
    """
    bv_ids = []
    try:
        response = notion.databases.query(database_id=DATABASE_ID)
        for result in response["results"]:
            bv_id = result["properties"]["BV"]["rich_text"][0]["text"]["content"]
            page_id = result["id"]
            bv_ids.append((bv_id, page_id))
    except Exception as e:
        print(f"获取 BV 号时出错: {str(e)}")
    return bv_ids


def check_video(bv_id):
    """
    检查视频是否失效，通过检查页面标题判断
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def load_cookies(cookie_file):
        cookies = {}
        with open(cookie_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                fields = line.strip().split("\t")
                if len(fields) >= 7:
                    domain, domain_specified, path, secure, expiry, name, value = fields
                    cookies[name] = value
        return cookies

    cookies = load_cookies("Cookies/2.txt")
    res = requests.get(CHECK_BILI_API + bv_id, headers=headers, cookies=cookies)

    # 导入 BeautifulSoup 用于解析 HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(res.text, 'html.parser')

    # 获取页面标题
    title = soup.title.string if soup.title else ""

    # 检查标题是否为失效视频的标题
    return title.strip() == "视频去哪了呢？_哔哩哔哩_bilibili"
def update_notion_page(page_id):
    """
    更新 Notion 页面，将 Expired 设置为 True
    """
    try:
        notion.pages.update(page_id=page_id, properties={"Expired": {"checkbox": True}})
        print(f"更新页面成功: {page_id}")
    except Exception as e:
        print(f"更新页面失败: {str(e)}")


def main():
    bv_ids = get_all_bv_ids()
    for bv_id, page_id in bv_ids:
        if check_video(bv_id):
            print(f"视频失效: {bv_id}")
            update_notion_page(page_id)
        else:
            print(f"视频有效: {bv_id}")


if __name__ == "__main__":
    main()
