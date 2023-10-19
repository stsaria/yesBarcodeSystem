import configparser, traceback, platform, tkinter, main, time, datetime, hashlib, os
from etc import file_identification_rewriting
import PySimpleGUI as sg

while True:
    try:
        sg.theme("SystemDefault1")
        root = tkinter.Tk()
        monitor_height, monitor_width = root.winfo_screenheight(), root.winfo_screenwidth()
        root.withdraw()
        break
    except:
        error = traceback.format_exc()
        print("This is Gui-error -----\n"+error+"-----------------------")
        continue

layout_attendance = [
        [sg.Text("Tansore -Attendance System-", font=('',15))],
        [sg.Text("バーコード:"), sg.Input(key="barcodeattendance")],
        [sg.Multiline(key="statusattendance", expand_x=True, expand_y=True,  pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="バーコードを読み込んでください\n", autoscroll=True)]
        ]
layout_csv_edit = [
        [sg.Text('内容変更', font=('',15)), sg.Text('注:・何も入力しない場合は空になります\n・BackUpファイルは一個しかありません\n2回変えると一回目のデータは消えます')],
        [sg.Text('バーコード'), sg.InputText(key='barcodeedit')],
        [sg.Text('名前'), sg.InputText(key='name')],
        [sg.Text('Email("/"区切り)'), sg.InputText(key='email')],
        [sg.Multiline(key="statusedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), default_text="情報を書いてください\n", autoscroll=True)],
        [sg.Button('変更',key='edit')]
        ]
layout_csv_view = [
        [sg.Text('CSV VIEW', font=('',15)), sg.Button('勤怠情報送信',key='sendcsv'), sg.Text(key="statussendcsv")],
        [sg.Text('空はいま登録されてないバーコードです')],
        [sg.Multiline(key="csv", expand_x=True, expand_y=True, pad=((0,0),(0,0)), disabled=True, font=('Arial',15), autoscroll=True)]
        ]
layout_setting = [
        [sg.Text('設定', font=('',15))],
        [sg.Text('_____________________________________________________________________________________________________________________')],
        [sg.Text('パスワード設定', font=('',13))],
        [sg.Text('パスワード再設定'), sg.Input(key="repassword"), sg.Button("設定", key="passwordsetting")],
        [sg.Text('_____________________________________________________________________________________________________________________')],
        [sg.Text(f"コンピューター情報\nOS:{platform.system()} {platform.release()}\nPython:{platform.python_version()}")],
        [sg.Text('_____________________________________________________________________________________________________________________')],
        [sg.Text('作成者 : stsaria\nライセンス : LGPL Licence v3.0(Githubにも記載)')],
        [sg.Text('_____________________________________________________________________________________________________________________')],
        [sg.Text(key="settingstatus")]
        ]
layout_direct_edit_file = [
        [sg.Text('Direct Edit File', font=('',15)), sg.Text(key="statusdirectedit")],
        [sg.Text('警告：直接ファイルを書き換えることは推奨されていません , 出席履歴ファイルは書き換えれません')],
        [sg.Combo(['barcodes.csv', 'setting.ini'], key='selectfile', default_value="ファイルを選択してください", enable_events=True, readonly=True)],
        [sg.Multiline(key="inputedit", expand_x=True, expand_y=True, pad=((0,0),(0,0)), font=('',15), autoscroll=True)],
        [sg.Button('書き換え',key='directedit'), sg.Button('再取得(巻き戻し)',key='regetfile')]
        ]
layout_main = [
        [sg.Text("管理者パスワード"), sg.Input(key="password"), sg.Text(key="statuslogin")],
        [sg.Button("ログイン", key="login"), sg.Button("ログアウト", key="logout"), sg.Button("終了(再起動)", key="exit"), sg.Text(key="time", font=('Arial',15))],
        [sg.TabGroup([[
        sg.Tab("勤怠", layout_attendance),
        sg.Tab("CSV編集", layout_csv_edit, visible=False, key='editab'),
        sg.Tab("CSV閲覧", layout_csv_view, visible=False, key='csvviewtab'),
        sg.Tab("直接編集", layout_direct_edit_file, visible=False, key='directeditfiletab'),
        sg.Tab("設定", layout_setting, visible=False, key='settingtab')
        ]], size=(monitor_width, monitor_height))]
        ]

def gui():
    while True:
        try:
            with open("./barcodes/setting.ini", encoding='utf-8') as f:
                text = f.read()
            if not "location" in text:
                file_identification_rewriting("./barcodes/setting.ini", "[etc]", "[etc]\nlocation = 未設定な施設\n")
            ini = configparser.ConfigParser()
            path = os.getcwd() + os.sep + 'barcodes/setting.ini'
            ini.read(path, 'UTF-8')
            password = ini["admin"]["password"]
            mail_address = ini["gmail"]["mail_address"]
            app_pass = ini["gmail"]["app_pass"]
            location = ini["etc"]["location"]
            title = [ini["title_setting"]["arriving"], ini["title_setting"]["gohome"]]
            text = [ini["text_setting"]["arriving"], ini["text_setting"]["gohome"]]
            etc = [int(ini["etc"]["send_csv_deadline_day"]), int(ini["etc"]["send_csv_deadline_time"]), int(ini["etc"]["arriving_deadline_time"]), int(ini["etc"]["arriving_isolation_period_min"])]
            break
        except:
            print("error:ini file read")
            time.sleep(1)
    while True:
        try:
            window = sg.Window("Yes Barcode System", layout_main, margins=(0,0), size=(monitor_width, monitor_height), resizable=True, finalize=True, no_titlebar=True, location=(0,0)).Finalize()
            window.Maximize()
            window["barcodeattendance"].set_focus()
            break
        except:
            error = traceback.format_exc()
            print("This is Gui-error -----\n"+error+"-----------------------")
            continue
    login = False
    while True:
        dt_now = datetime.datetime.now()
        format_dt_now = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        final_send_csv_season = ["", "", ""]
        if os.path.isfile("./barcodes/csvlog.txt"):
            f = open('./barcodes/csvlog.txt', 'r')
            alltxt = f.readlines()
            f.close()
            final_send_csv_season = alltxt[-1].strip().split("/")
        event, values = window.read(timeout=50)
        window["time"].update(format_dt_now)
        if event == sg.WIN_CLOSED or event == "exit":
            break
        elif " " in values["barcodeattendance"]:
            try:
                status = values["statusattendance"] + "\n"
                window["statusattendance"].update(status)
                result, error = main.attendance(values["barcodeattendance"].replace(" ", ""))
                if result == 0:
                    status = status + "勤怠しました\n"
                elif result == 1:
                    status = status + "原因不明なエラーが発生しました\nエラーを報告しました\nerror: "+error+"\n"
                elif result == 2:
                    status = status + "正しいバーコードを読み込んでください\n"
                elif result == 3:
                    status = status + "リストから名前が見つかりませんでした\n"
                elif result == 4:
                    status = status + f"{str(etc[3])}分の動作は許されません\n"
                window["statusattendance"].update(status)
            except:
                error = traceback.format_exc()
                print(error)
                window["statusattendance"].update(status + "GUIで原因不明なエラーが発生しました\nerror : "+error)
            window["statusattendance"].update(status + "\n\nバーコードを読み込んでください")
            window["barcodeattendance"].update("")
        elif event == 'edit':
            status = values["statusedit"] + "\n"
            if login == False:
                status = status + "管理者ではありません\n"
                window["statusedit"].update(status)
                continue
            else:
                try:
                    with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                        text = f.read()
                    with open(f"barcodes/barcodes.csv.backup", encoding="utf-8", mode="w") as f:
                        f.write(text)
                    result, error = main.edit(values["barcodeedit"], values["name"], values["email"])
                    if result == 0:
                        status = status + "編集しました\nbarcodes/barcodes.csv.backupがバックアップファイルです"
                    elif result == 1:
                        status = status + "原因不明なエラーが発生しました\nエラーを報告しました\nerror: "+error+"\n"
                    elif result == 2:
                        status = status + "正しいバーコードを入力してください\n"
                    window["statusedit"].update(status)
                except:
                    error = traceback.format_exc()
                    print(error)
                    window["statusedit"].update(status + "GUIで原因不明なエラーが発生しました\nerror : "+error)
            window["statusedit"].update(status + "\n\n情報を書いてください")
            window["barcodeedit"].update("")
            window["name"].update("")
            window["email"].update("")
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
            if values["selectfile"] == "barcodes.csv":
                window["inputedit"].update("".join(text_list))
        elif event == 'sendcsv' or int(format_dt_now.split(" ")[0].split("/")[2]) >= etc[0] and int(format_dt_now.split(" ")[1].split(":")[0]) >= etc[1] and not [format_dt_now.split(" ")[0].split("/")[0], format_dt_now.split(" ")[0].split("/")[1]] == [final_send_csv_season[0], final_send_csv_season[1]]:
            if event == 'sendcsv' and login == False:
                window["statussendcsv"].update("管理者ではありません\n")
                continue
            try:
                result = main.send_csv(dt_now=dt_now)
                if result == 0:
                    window["statussendcsv"].update("送信しました")
                elif result == 1:
                    window["statussendcsv"].update("原因不明なエラーが発生しました")
            except:
                error = traceback.format_exc()
                print(error)
                window["statussendcsv"].update("GUIで原因不明なエラーが発生しました")
        elif event == 'login':
            if login == True:
                window["statuslogin"].update("すでにログインしています")
                continue
            elif values["password"] == "":
                window["statuslogin"].update("パスワードが空です")
                continue
            input_password = hashlib.sha256(values["password"].encode()).hexdigest()
            if password == input_password:
                window["password"].update("")
                window["statuslogin"].update("ログインしました")
                window["editab"].update(visible=True)
                window["csvviewtab"].update(visible=True)
                window["settingtab"].update(visible=True)
                window["directeditfiletab"].update(visible=True)
                login = True
            else:
                window["statuslogin"].update("パスワードが違います")
                continue
            with open("barcodes/barcodes.csv", encoding="utf-8") as f:
                text_list = f.readlines()
            window["csv"].update("".join(text_list[1:]).replace(",name,email", ",空"))
            if values["selectfile"] == "barcodes.csv":
                window["inputedit"].update("".join(text_list))
        elif event == 'logout':
            if login != True:
                window["statuslogin"].update("ログインしていません")
                continue
            login = False
            window["editab"].update(visible=False)
            window["csvviewtab"].update(visible=False)
            window["settingtab"].update(visible=False)
            window["directeditfiletab"].update(visible=False)
            window["statuslogin"].update("ログアウトしました")
            window["inputedit"].update("")
            window["csv"].update("")
        elif event == "passwordsetting":
            try:
                if login != True:
                    window["settingstatus"].update("管理者ではありません\n")
                    continue
                window["repassword"].update("")
                result = main.setting_password(values["repassword"])
                window["settingstatus"].update("パスワードを変更しました 再起動してください\n")
            except:
                error = traceback.format_exc()
                print(error)
                window["settingstatus"].update("原因不明なエラーが発生しました\nerror : "+error+"\n")
        elif event == "selectfile":
            with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                text = f.read()
            window["inputedit"].update(text)
        elif event == "directedit":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                continue
            try:
                if not "." in values["selectfile"]:
                    window["statusdirectedit"].update("選択したファイル名が空です")
                    continue
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8", mode="w") as f:
                    f.write(values["inputedit"])
                if not values["inputedit"] == text:
                    with open(f"barcodes/"+values["selectfile"]+".backup", encoding="utf-8", mode="w") as f:
                        f.write(text)
                if values["selectfile"] == "barcodes.csv":
                    window["csv"].update(values["inputedit"].replace(",name,email", ",空"))
                window["statusdirectedit"].update("書き換えに成功しました\n再起動してください\n(一個前のバックアップはbarcodes/"+values["selectfile"]+".backupにあります)")
            except:
                error = traceback.format_exc()
                print(error)
                window["statusdirectedit"].update("書き換えに失敗しました")
        elif event == "regetfile":
            if login == False:
                window["statusdirectedit"].update("管理者ではありません")
                continue
            try:
                if not "." in values["selectfile"]:
                    window["statusdirectedit"].update("選択したファイル名が空です")
                    continue
                with open(f"barcodes/"+values["selectfile"], encoding="utf-8") as f:
                    text = f.read()
                window["inputedit"].update(text)
                window["statusdirectedit"].update("ファイルを再取得しました")
            except:
                error = traceback.format_exc()
                print(error)
                window["statusdirectedit"].update("ファイルの再取得に失敗しました")