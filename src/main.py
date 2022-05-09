from httpx import main
import streamlit as st
from deep_l.translate_contentful_data import *
from backlog2notion.time_schedule_import import *

def main():
    with st.expander("DeepL"):
        st.header("DeepL")

        html_head = st.text_area(label=" (head）HTMLを入力してください。")
        
        html_body = st.text_area(label=" (body）HTMLを入力してください。")
        
        translate_btn = st.button("翻訳する")
        
        if translate_btn:
        
            html_head_text = html_head.replace("\n", "")
            
            html_body_text = html_body.replace("\n", "").replace("\xa0", "").replace("\t", "")
            
            try:
                with st.spinner('headデータを翻訳中です...'):
                    translate_head_text = translate_head(html_head_text)
                st.success('headデータの翻訳が終わりました。')
                
                format_head = formatHTML(translate_head_text)
            
                st.code(format_head, language='html')
            except:
                st.error("データがありません...")
                pass
            
            try:
                with st.spinner('bodyデータを翻訳中です...'):
                    translate_body_text = translate_body(html_body_text)
                st.success('bodyデータの翻訳が終わりました。')
                
                format_body = formatHTML(translate_body_text)
            
                st.code(format_body, language='html')
            except:
                st.error("データがありません...")
                pass
        
        text = st.text_area(label="翻訳したテキストを入力してください。")
        
        text_btn = st.button("テキストを翻訳する")   
        
        if text_btn:
            with st.spinner('テキストデータを翻訳中です...'):
                translate_text = translator.translate_text(text, source_lang="JA", target_lang="EN-US").text.replace('"', "'")
            st.success('テキストデータの翻訳が終わりました。')
            st.code(translate_text)
        
        

    with st.expander("Backlog"):
        st.header("Backlog")
        file_csv = st.file_uploader("ファイルをアップロードしてください。", type="csv")

        password = st.text_input("passwordを入力してください。")

        if file_csv and password == "spin":
            task, task_end, task_start = extraction_csv(file_csv)
            
            notion, notion_db_id = notion_api()
            
            import_btn = st.button("データをimport")
            
            if import_btn:
                with st.spinner('import中...'):
                    import_notion(task, task_end, task_start, notion, notion_db_id)
                st.info("データのimportが完了しました！")
        elif password and password != "spin":
            st.error("パスワードが違います！！！")


if __name__ == "__main__":
    main()