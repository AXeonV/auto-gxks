import requests
import time
import random
from bs4 import BeautifulSoup


class StudyTimeAutomator:
  def __init__(self):
    self.session = requests.Session()
    # 设置请求头，模拟真实浏览器
    self.session.headers.update({
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Accept-Encoding': 'gzip, deflate',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
    })

  def set_cookies(self, cookies_dict):
    """设置用户认证cookie"""
    for name, value in cookies_dict.items():
      self.session.cookies.set(name, value)

  def get_hidden_values(self, url):
    """获取页面中的隐藏字段值"""
    try:
      response = self.session.get(url)
      response.raise_for_status()

      soup = BeautifulSoup(response.text, 'html.parser')

      # 获取所有需要的隐藏字段值
      hidden_values = {}
      hidden_fields = ['hidNewId', 'hidPassLine', 'hidRefId', 'hidStudentId', 'hidStudyTime', 'hidSessionID']

      for field in hidden_fields:
        element = soup.find('input', {'id': field})
        if element:
          hidden_values[field] = element.get('value', '')
          print(f"找到隐藏字段 {field}: {hidden_values[field]}")
        else:
          print(f"警告: 未找到隐藏字段 {field}")

      return hidden_values

    except Exception as e:
      print(f"获取页面信息失败: {e}")
      return None

  def send_update_request(self, hidden_values, study_time):
    """发送更新学习时间的请求"""
    try:
      params = {
        'Id': hidden_values.get('hidNewId', ''),
        'pTime': study_time,
        'Mins': hidden_values.get('hidPassLine', ''),
        'refId': hidden_values.get('hidRefId', ''),
        'StudentId': hidden_values.get('hidStudentId', ''),
        'StydyTime': hidden_values.get('hidStudyTime', ''),
        'SessionId': hidden_values.get('hidSessionID', ''),
        '_': int(time.time() * 1000)
      }

      base_url = 'http://www.gaoxiaokaoshi.com/Study/updateTime.ashx'

      response = self.session.get(base_url, params=params)
      response.raise_for_status()

      print(f"成功发送学习时间更新请求: {study_time}秒")
      return True

    except Exception as e:
      print(f"发送更新请求失败: {e}")
      return False

  def get_study_url(self, id):
    return "http://www.gaoxiaokaoshi.com/Study/LibraryStudy.aspx?Id=%d&PlanId=32" % id

  def auto_study(self, start, end, total_minutes=45):
    """自动刷学习时长"""
    print("开始获取页面信息...")
    hidden_values_list = []

    for id in range(start, end + 1):
      url = self.get_study_url(id)
      hidden_values = self.get_hidden_values(url)
      if not hidden_values:
        print("获取 %d 课程的信息失败")
        continue
      if not hidden_values.get('hidNewId'):
        print("未找到hidNewId，无法继续")
        continue
      hidden_values_list.append(hidden_values)

    print(f"\n开始自动学习，目标时长: {total_minutes}分钟")

    total_seconds = total_minutes * 60
    current_time = 0

    while current_time <= total_seconds:
      if current_time % 30 == 0 and current_time > 0:
        for hidden_values in hidden_values_list:
          success = self.send_update_request(hidden_values, current_time)
          if not success:
            print("请求失败，尝试继续...")

      minutes = current_time // 60
      seconds = current_time % 60
      if current_time % 300 == 0:
        print(f"当前学习进度: {minutes}分{seconds}秒")

      time.sleep(1)
      current_time += 1

      if current_time % 60 == 0:
        time.sleep(random.uniform(0.1, 0.5))

    print(f"\n学习完成! 总计学习时长: {total_minutes}分钟")
    return True


def main():
  automator = StudyTimeAutomator()

  # 设置用户认证cookie（需要您提供实际的cookie值）
  # 请从浏览器开发者工具中复制实际的cookie信息
  user_cookies = {
    '.ASPXAUTH' : 'D2C3C37EFA67A7B0021087D4B520F10D43387A8B34B481348A213233EFF495AF21E82C0DD83AE5F9D132D5463CD53896EC7E968CBCB598E390734FA63869E47366EFD27C0C94E99435C50B319B9518DEA7A9894FB00727282A7F587CFE15E4AF41977B545646E0D268358A24',
    'ASP.NET_SessionId': '4q4n3brjkbfkoinkiaqkvzoq',
    'Clerk': 'ClerkID=3042596&UserName=12511307&ClerkName=%e5%88%98%e5%a4%a9%e4%bd%91&Pwd=000000&ClerkScore=0&DeptPath=%e5%8d%97%e6%96%b9%e7%a7%91%e6%8a%80%e5%a4%a7%e5%ad%a6%2f%e7%ae%a1%e7%90%86%e9%83%a8%e9%97%a8&Degree=0&CreateTime=2025-10-17+12%3a00%3a00&CompanyId=1124&ParentCompanyId=1&ManageRange=0&Ip=116.7.234.232&isRepeatLogin=True&SessionId=4q4n3brjkbfkoinkiaqkvzoq&GridHeight=610&PageSize=9&AdminPageSize=50'
  }

  if not user_cookies:
    print("请先设置用户认证cookie")
    print("从浏览器开发者工具中复制cookie信息并更新user_cookies字典")
    return

  automator.set_cookies(user_cookies)

  # 开始的时间和结束的时间
  automator.auto_study(1289, 1340, total_minutes=60)


if __name__ == "__main__":
  main()