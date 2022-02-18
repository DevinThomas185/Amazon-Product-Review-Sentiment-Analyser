import datetime

result = {}
result["date_last_analysed"] = "2020-04-04"

if (datetime.datetime.now() - datetime.datetime.strptime(result["date_last_analysed"], "%Y-%m-%d")).days >= 30:
    print("Y")
else:
    print("N")