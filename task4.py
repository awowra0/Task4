import pandas as pd
import yaml
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def create_dfb(num=1):
    with open(f"./data/STORE{num}/books.yaml", "r", encoding="utf-8") as f: #orders.parquet users.csv
        data = yaml.safe_load(f)
        df = pd.json_normalize(data)
        for i in df.columns:
            df.rename(columns={i: i.removeprefix(":")}, inplace=True)
        df["publisher"] = df["publisher"].fillna(value="Unknown")
        df["year"] = df["year"].fillna(value=0)
        df["year"] = df["year"].replace({" ": 0, "-": 0, "": 0, "NULL": 0, "\t": 0})
        df = df.astype({"title": "string", "author": "string", "genre": "string", "publisher": "string", "year": "int64"})
        return df

def create_dfo(num=1):
    df = pd.read_parquet(f"./data/STORE{num}/orders.parquet")
    df = df.astype({"unit_price": "string"})
    currency = ["$"  if "USD" in i or "$" in i else "€" for i in df["unit_price"]]
    currency = pd.Series(currency)
    value = df["unit_price"].str.extract(r"([A-Za-z$€.\s]*)([0-9]+)([A-Za-z$€.\s]*)([0-9]*)([A-Za-z$€.\s]*)")
    value = value[1]+"."+value[3]+"0"
    value = value.astype("float")
    for i in range(len(value)):
        if currency[i] == "€":
            value[i] = value[i] * 1.2
    df["paid_price"] = df["quantity"] * value
    df["timestamp"] = df["timestamp"].str.replace(r"([AaPp]+)([.]*)([Mm]+)([.]*)","",regex=True).replace(r"([T]*)([0-9]*):([0-9]*)([:0-9]*([.0-9]*))","",regex=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"],format="mixed",utc=True,errors="coerce").dt.date
    df = df.drop(df[df["shipping"]==""].index).drop(df[df["shipping"]=="NULL"].index).drop(df[df["shipping"]==" "].index)
    df = df.dropna()
    df["shipping"] = df["shipping"]#.fillna("Unknown").replace({"NULL": "Unknown", "None": "Unknown", "":"Unknown"})
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    return df

def create_dfu(num=1):
    df = pd.read_csv(f"./data/STORE{num}/users.csv")
    df = df.astype({"name": "string", "address": "string", "phone": "string", "email": "string"})
    df["address"] = df["address"].fillna("Unknown")
    df["address"] = df["address"].replace({" ": "Unknown"})
    return _unite_duplicates(df)

def _unite_duplicates(dfu):
    dfu["new_id"] = dfu["id"]
    for i in (['email','address','name'],['phone','address','name'],['email','phone','name'],['email','address','phone']):
        dfu["new_id"] = dfu.groupby(i)["new_id"].transform('first')
    for i in (['email','address'],['email','phone'],['email','name'],['phone','address'],['phone','name'],['address','name'],):
        dfu["new_id"] = dfu.groupby(i)["new_id"].transform('first')
    return dfu

def unique_authors(dfb):
    authors = sorted([sorted(b.strip(" \t\n") for b in a.split(",")) for a in dfb["author"]])
    authors_unique = []
    for i in authors:
        if i not in authors_unique:
            authors_unique.append(i)
    return len(authors_unique)

def revenue(dfo):
    return dfo.groupby(by="timestamp", sort=True)["paid_price"].sum().sort_values(ascending=False)

def top5revenue(dfo):
    return revenue(dfo).head(5).index.tolist()

def daily_revenue(dfo):
    ax = dfo.groupby(by="timestamp", sort=True)["paid_price"].sum().plot(xlabel="Date", ylabel="Revenue ($)", title="Daily Revenue", 
                                                                    figsize=((12,8)), color="forestgreen")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(100))
    plt.show()
    return

def find_best_author(dfo, dfb):
    book_index = dfo.groupby(by="book_id", sort=True)["quantity"].sum().sort_values(ascending=False).index[0]
    return dfb.loc[dfb["id"] == book_index, "author"].values[0]

def find_top_customer(dfo, dfu):
    temp = dfo.groupby("user_id")["paid_price"].sum().sort_values(ascending=False)
    temp2 = pd.merge(temp, dfu[["id","new_id","name"]], left_index=True, right_on="id")
    temp3 = temp2.groupby("new_id")["paid_price"].sum().sort_values(ascending=False).index[0]
    return dfu.loc[dfu["new_id"] == temp3, ["id","name"]].values.tolist()

def find_duplicates(dfu):
    dfu_results = {"ALL": len(dfu)}
    df = dfu.drop_duplicates(keep="first")
    for i in (['email','address','name'],['phone','address','name'],['email','phone','name'],['email','address','phone'],
              ['email','address'],['email','phone'],['email','name'],['phone','address'],['phone','name'],['address','name']):
        df = df.drop_duplicates(subset=i,keep="first")
    dfu_results["UNIQUES"] = len(df)
    dfu_results["DUPLICATES"] = dfu_results['ALL'] - dfu_results['UNIQUES']
    return dfu_results

def show_all():
    for i in range(1,6):
        dfb = create_dfb(i)
        dfo = create_dfo(i)
        dfu = create_dfu(i)
        print(f"Top 5 days: {[i.strftime('%Y-%m-%d') for i in top5revenue(dfo)]}")
        print(f"Users: {find_duplicates(dfu)['UNIQUES']}")
        print(f"Sets of authors: {unique_authors(dfb)}")
        print(f"Best author set: {find_best_author(dfo, dfb)}")
        print(f"Top customer: {find_top_customer(dfo, dfu)}")
        daily_revenue(dfo)