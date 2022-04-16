import streamlit as st
import pandas as pd
import codecs
from notion_client import Client

file_csv = st.file_uploader("ファイルをアップロードしてください。", type="csv")

password = st.text_input("passwordを入力してください。")

if file_csv and password == "spin":
    with codecs.open(file_csv.name, "r", "Shift-JIS", "ignore") as file:
        backlog = pd.read_table(file, delimiter=",")

    
    task = backlog["件名"]
    
    task_end = backlog["期限日"]

    task_start = backlog["開始日"]
    
    import_btn = st.button("データをimport")
    
    TOKEN = "secret_mK8ECe51Y0K5C4PwJrEIfOstK7U0PtQGdNqARaxnMSw"
    notion = Client(auth=TOKEN)
    notion_db_id = "30ffa7111a464ed189ca2dca733a8ce3"  
    
    if import_btn:
        with st.spinner('import中...'):
            for num in range(len(task)):
                try:
                    end = task_end[num].replace('/', '-')
                except:
                    pass
                    
                try:
                    start = task_start[num].replace('/', '-')
                except:
                    pass
                    
                try:
                    notion.pages.create(
                        **{
                                'parent': {'database_id': notion_db_id},
                                'properties': {'名前': {'id': 'title',
                                                    'title': [{'annotations': {'bold': True,
                                                                            'code': False,
                                                                            'color': 'default',
                                                                            'italic': False,
                                                                            'strikethrough': False,
                                                                            'underline': False},
                                                            'href': None,
                                                            'plain_text': 'トップページ',
                                                            'text': {'content': task[num],
                                                                        'link': None},
                                                            'type': 'text'}],
                                                    'type': 'title'},
                                            '日付': {'date': {'end': end, 
                                                            'start': start,
                                                            'time_zone': None},
                                                    'id': 'd%7DRW',
                                                    'type': 'date'}},
                                
                            }
                        )
                except:
                    continue
        st.info("データのimportが完了しました！")
elif password and password != "spin":
    st.error("パスワードが違います！！！")

