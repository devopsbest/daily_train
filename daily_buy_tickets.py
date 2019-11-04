import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import pandas
import arrow

Max_Time_Out = 30
Time_Out = 10
sh_to_sz = "18002400"
sz_to_sh = "06001200"
sh_to_sz_train = "G7026|G7260|G7062|G7226|G7028"
sh_station = 'cc_from_station_上海_check'
sz_to_sh_train = "D3125|G7001|G7037|G7039"
sz_station = 'cc_from_station_苏州_check'

time_id = "cc_start_time"
now = arrow.now().format('YYYY-MM-DD HH:MM:SS')

option = webdriver.ChromeOptions()

option.add_argument('disable-infobars')
# option.binary_location="/Applications/AppleTools /Google Chrome.app/Contents/MacOS/Google Chrome"
option.add_argument('headless')

sh_to_sz_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E4%B8%8A%E6%B5%B7,SHH&ts=%E8%8B%8F%E5%B7%9E,SZH&date={}&flag=N,N,Y"
sz_to_sh_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E8%8B%8F%E5%B7%9E,SZH&ts=%E4%B8%8A%E6%B5%B7,SHH&date={}&flag=N,N,Y"

driver = webdriver.Chrome(chrome_options=option)

driver.set_page_load_timeout(Max_Time_Out)


def open_page(url):
    try:
        driver.get(url)
    except TimeoutError:
        print("cannot open the page for {} seconds".format(Max_Time_Out))
        driver.execute_script('window.stop()')


def find_element(obj):
    WebDriverWait(driver, Time_Out).until(EC.visibility_of_element_located((By.ID, obj)))
    element = WebDriverWait(driver, Time_Out).until(lambda x: driver.find_element(By.ID, obj))
    return element


def type(obj, value):
    find_element(obj).clear()
    find_element(obj).send_keys(value)


def clickat(obj):
    WebDriverWait(driver, Time_Out).until(EC.element_to_be_clickable((By.ID, obj)))
    find_element(obj).click()


def toggle_checkbox(station_id):
    inputs = driver.find_elements_by_tag_name("input")
    for input in inputs:
        if input.get_attribute("value") == 'G':
            input.click()
        if input.get_attribute("value") == 'D':
            input.click()
        if input.get_attribute("id") == station_id:
            input.click()


def get_today():
    today = arrow.now()
    if today.weekday() not in [5, 6]:
        return today.format('YYYY-MM-DD')


def get_next_day():
    next_day = arrow.now().shift(days=+1)
    if next_day.weekday() not in [5, 6]:
        return next_day.format('YYYY-MM-DD')


def get_next_two_monday():
    next_two_monday = [arrow.now().shift(days=x).format('YYYY-MM-DD') for x in range(1, 15) if
                       arrow.now().shift(days=x).weekday() == 0]
    return next_two_monday


def get_next_two_friday():
    next_two_friady = [arrow.now().shift(days=x).format('YYYY-MM-DD') for x in range(1, 15) if
                       arrow.now().shift(days=x).weekday() == 4]
    return next_two_friady


def select_time(obj, time_zone, station_id):
    '''

    :param driver:
    :param obj:
    :return:

    <select class="select-small" id="cc_start_time">
    <option value="00002400">00:00--24:00</option>
<option value="00000600">00:00--06:00</option>
<option value="06001200">06:00--12:00</option>
<option value="12001800">12:00--18:00</option>
<option value="18002400">18:00--24:00</option>
</select>
    '''

    start_time = find_element(obj)
    get_start = Select(start_time)
    get_start.select_by_value(time_zone)
    toggle_checkbox(station_id)
    time.sleep(3)


def get_trains(url, city_time, station_id, trains):
    open_page(url)
    select_time(time_id, city_time, station_id)
    ht = driver.page_source
    html_pd = pandas.read_html(ht)

    pd = html_pd[1]

    pd3 = pd[pd['车次'].str.contains(trains, na=False)]

    coloum_list = ["车次", "二等座", "无座"]
    # print(pd3[coloum_list])

    return pd3[coloum_list]


def generate_df_html(arg):
    html_str = ""
    html_temp = """
                <h2>{}</h2>

            <div>
                <h4></h4>
                {}

            </div>
            <hr>
    """

    for k in arg.keys():
        df_html = arg[k].to_html(escape=False)

        html_str = html_str + html_temp.format(k, df_html)

    return html_str


def get_html_msg(df):
    head = \
        """
        <head>
            <meta charset="utf-8">
            <STYLE TYPE="text/css" MEDIA=screen>

                table.dataframe {
                    border-collapse: collapse;
                    border: 2px solid #a19da2;
                    /*居中显示整个表格*/
                    margin: left;
                }

                table.dataframe thead {
                    border: 2px solid #91c6e1;
                    background: #f1f1f1;
                    padding: 10px 10px 10px 10px;
                    color: #333333;
                }

                table.dataframe tbody {
                    border: 2px solid #91c6e1;
                    padding: 10px 10px 10px 10px;
                }

                table.dataframe tr {

                }

                table.dataframe th {
                    vertical-align: top;
                    font-size: 14px;
                    padding: 10px 10px 10px 10px;
                    color: #105de3;
                    font-family: arial;
                    text-align: center;
                }

                table.dataframe td {
                    text-align: center;
                    padding: 10px 10px 10px 10px;
                }

                # body {
                #     font-family: 宋体;
                # }

                # h1 {
                #     color: #5db446
                # }

                div.header h2 {
                    color: #0002e3;
                    font-family: 黑体;
                }

                div.content h2 {
                    text-align: left;
                    font-size: 18px;
                    # text-shadow: 2px 2px 1px #de4040;
                    #color: #fff;
                    color:#008eb7
                    font-weight: bold;
                    #background-color: #008eb7;
                    # line-height: 1.5;
                    # margin: 20px 0;
                    # box-shadow: 10px 10px 5px #888888;
                    # border-radius: 5px;
                }

                h3 {
                    font-size: 22px;
                    background-color: rgba(0, 2, 227, 0.71);
                    text-shadow: 2px 2px 1px #de4040;
                    color: rgba(239, 241, 234, 0.99);
                    line-height: 1.5;
                }

                h4 {
                    color: #e10092;
                    font-family: 楷体;
                    font-size: 20px;
                    text-align: center;
                }

            </STYLE>
        </head>
        """

    # 构造模板的附件（100）

    message = """
    Dear,
    The following is the status of your train, please don't forget buy your tickets! it query at {}
  """.format(now)
    body = \
        """
        <body>

        <div align="left" class="header">
            <!--标题部分的信息-->
            <h1 align="left">{}</h1>
        </div>

        <hr>

        <div class="content">
            <!--正文内容-->

            {}
            <p style="text-align: left">
                It sent automatically, please don't replay this mail, Thanks!
            </p>
        </div>
        </body>
        """.format(message, df)
    html_msg = "<html>" + head + body + "</html>"
    print(html_msg)
    # 这里是将HTML文件输出，作为测试的时候，查看格式用的，正式脚本中可以注释掉
    fout = open('{}.html'.format(get_today()), 'w', encoding='UTF-8', newline='')
    fout.write(html_msg)
    fout.close()
    return html_msg


import os


def write_htmls(df_list):
    HEADER = '''
        <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
        '''
    FOOTER = '''
            </body>
        </html>
        '''

    with open(os.path.join(os.getcwd(), 'test.html'), 'w') as f:
        f.write(HEADER)

        for afaf in df_list:
            # f.write('<h1><strong>' + '自定义dataframe名' +'</strong></h1>')
            f.write(afaf.to_html(classes='classname'))
        f.write(FOOTER)


import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

MAIL_HOST = "smtp.office365.com"
SMTP_PORT = 587
mail_user = "auto@eaaa.com"
mail_password = "test"


def sent_mails(label, content):
    try:

        def addimg(img_src, imgid):
            fp = open(img_src, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Conteng-ID', imgid)
            return msgImage

        msg_text = MIMEText(content, "html", "utf-8")
        # 创建MIMEMultipart对象，采用related定义内嵌资源
        msg = MIMEMultipart('related')
        msg.attach(msg_text)
        # msg.attach(addimg(picture, label))

        server = smtplib.SMTP(MAIL_HOST, SMTP_PORT)
        server.starttls()

        server.login(mail_user, mail_password)
        me = mail_user

        # msg = MIMEText("hello", 'text', 'utf-8')
        msg['From'] = me
        msg['To'] = "@.com"
        msg['Cc'] = "@.com"
        msg['Subject'] = Header("Tickets reminder on {}".format(now), 'utf-8')
        server.sendmail(me, "m@aaa.com", msg.as_string())
        server.close()
        print("pass")
        return True

    except Exception:
        print("fail")
        return False


if __name__ == "__main__":
    today = get_today()
    next_day = get_next_day()
    mondays = get_next_two_monday()
    fridays = get_next_two_friday()

    df_list = []
    #
    next_suzhou_to_shanghai = get_trains(sz_to_sh_url.format(next_day), sz_to_sh, sz_station, sz_to_sh_train)
    df_list.append(next_suzhou_to_shanghai)
    today_shanghai_to_suzhou = get_trains(sh_to_sz_url.format(today), sh_to_sz, sh_station, sh_to_sz_train)
    df_list.append(today_shanghai_to_suzhou)

    suzhou_to_shanghai_next_monday = get_trains(sz_to_sh_url.format(mondays[0]), sz_to_sh, sz_station, sz_to_sh_train)
    df_list.append(suzhou_to_shanghai_next_monday)

    suzhou_to_shanghai_next_next_monday = get_trains(sz_to_sh_url.format(mondays[1]), sz_to_sh, sz_station,
                                                     sz_to_sh_train)
    df_list.append(suzhou_to_shanghai_next_next_monday)
    #

    shanghai_to_suzhou_next_friday = get_trains(sh_to_sz_url.format(fridays[0]), sh_to_sz, sh_station, sh_to_sz_train)
    df_list.append(shanghai_to_suzhou_next_friday)

    shanghai_to_suzhou_next_next_friday = get_trains(sh_to_sz_url.format(fridays[1]), sh_to_sz, sh_station,
                                                     sh_to_sz_train)
    df_list.append(shanghai_to_suzhou_next_next_friday)

    driver.quit()

    print(df_list)

    write_htmls(df_list)

    import collections

    # 通过OrderedDict类创建的字典是有序的
    messages = collections.OrderedDict()

    messages["Tomorrow suzhou to shanghai,{}".format(next_day)] = next_suzhou_to_shanghai
    messages["today shanghai to suzhou,{}".format(today)] = today_shanghai_to_suzhou
    messages["next monday suzhou to shanghai,{}".format(mondays[0])] = suzhou_to_shanghai_next_monday
    messages["next friday shanghai to suzhou,{}".format(fridays[0])] = shanghai_to_suzhou_next_friday
    messages["next next monday suzhou to shanghai,{}".format(mondays[1])] = suzhou_to_shanghai_next_next_monday
    messages["next next friday shanghai to suzhou,{}".format(fridays[1])] = shanghai_to_suzhou_next_next_friday

    html_text = generate_df_html(messages)

    #
    final_html = get_html_msg(html_text)

    sent_mails("{} train stations".format(today), final_html)
