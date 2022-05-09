import streamlit as st
import re, html
import os
import deepl
from dotenv import load_dotenv

load_dotenv()

# 環境変数を参照
DEEPL_AUTH_KEY=os.getenv("DEEPL_AUTH_KEY")
translator = deepl.Translator(DEEPL_AUTH_KEY) 

def formatHTML(s, reset=None):  # HTMLを整形する。第2引数があるときはすでにあるインデントを除去する。
    if reset is not None:  # 第2引数がある時。
        s = re.sub(r'(?<=>)\s+?(?=<)', "", s)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
    indentunit = "\t"  # インデントの1単位。
    tagregex = re.compile(r"(?s)<(?:\/?(\w+).*?\/?|!--.*?--)>|(?<=>).+?(?=<)")  # 開始タグと終了タグ、コメント、テキストノードすべてを抽出する正規表現オブジェクト。ただし<を含んだテキストノードはそこまでしか取得できない。
    replTag = repltagCreator(indentunit)  # マッチオブジェクトを処理する関数を取得。
    s = html.unescape(s)  # HTMLの文字参照をユニコードに戻す。
    s = tagregex.sub(replTag, s)  # script要素とstyle要素以外インデントを付けて整形する。
    return s.lstrip("\n")  # 先頭の改行を削除して返す。

def repltagCreator(indentunit):  # 開始タグと終了タグのマッチオブジェクトを処理する関数を返す。
    starttagregex = re.compile(r'<\w+.*?>')  # 開始タグ。
    endendtagregex = re.compile(r'<\/\w+>$')  # 終了タグで終わっているか。 
    noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "link", "param", "source", "wbr", "track"  # HTMLでは終了タグがなくなるタグ。
    c = 0  # インデントの数。
    starttagtype = ""  # 開始タグと終了タグが対になっているかを確認するため開始タグの要素型をクロージャに保存する。
    txtnodeflg = False  # テキストノードを処理したときに立てるフラグ。テキストノードが分断されたときのため。
    def replTag(m):  # 開始タグと終了タグのマッチオブジェクトを処理する関数。
        nonlocal c, starttagtype, txtnodeflg  # 変更するクロージャ変数。
        txt = m.group(0)  # マッチした文字列を取得。
        tagtype = m.group(1)  # 要素型を取得。Noneのときもある。
        tagtype = tagtype and tagtype.lower()  # 要素型を小文字にする。
        if tagtype in noendtags:  # 空要素の時。開始タグと区別がつかないのでまずこれを最初に判別する必要がある。
            txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
            starttagtype = ""  # 開始タグの要素型をリセットする。  
            txtnodeflg = False  # テキストノードのフラグを倒す。 
        elif txt.endswith("</{}>".format(tagtype)):  # 終了タグの時。
            c -= 1  # インデントの数を減らす。
            if tagtype!=starttagtype:  # 開始タグと同じ要素型ではない時。
                txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
            starttagtype = ""  # 開始タグの要素型をリセットする。
            txtnodeflg = False  # テキストノードのフラグを倒す。   
        elif starttagregex.match(txt) is not None:  # 開始タグの時。
            txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
            starttagtype = tagtype  # タグの要素型をクロージャに取得。
            c += 1  # インデントの数を増やす。
            txtnodeflg = False  # テキストノードのフラグを倒す。  
        elif txt.startswith("<!--"):  # コメントの時。
            pass  # そのまま返す。
        else:  # 上記以外はテキストノードと判断する。
            if not txt.strip():  # 改行や空白だけのとき。
                txt = ""  # 削除する。
            if "\n" in txt: # テキストノードが複数行に渡る時。
                txt = txt.rstrip("\n").replace("\n", "".join(["\n", indentunit*c]))  # 最後の改行を除いたあと全行をインデントする。
                if not txtnodeflg:  # 直前に処理したのがテキストノードではない時。
                    txt = "".join(["\n", indentunit*c, txt])  # 前を改行してインデントする。  
                if endendtagregex.search(txt):  # 終了タグで終わっている時。テキストノードに<があるときそうなる。
                    c -= 1  # インデントを一段上げる。
                    txt = endendtagregex.sub(lambda m: "".join(["\n", indentunit*c, m.group(0)]), txt)  # 終了タグの前を改行してインデントする。
                starttagtype = ""  # 開始タグの要素型をリセットする。開始タグと終了タグが一致しているままだと終了タグの前で改行されないため。
            elif not starttagtype:  # 単行、かつ、開始タグが一致していない時。
                txt = "".join(["\n", indentunit*c, txt])  # テキストノードの前で改行してインデントする。
            txtnodeflg = True  # テキストノードのフラグを立てる。
        return txt
    return replTag

def translate_head(html_head_text):
    title_start = html_head_text.find("<title>") + 7
    title_end = html_head_text.find("</title>")
    head_title_text = html_head_text[title_start:title_end]

    description_start = html_head_text.find('description" content') + 22
    description_end = html_head_text.find(">", description_start) - 1
    description_content = html_head_text[description_start:description_end]
    
    # 翻訳
    # translate_title = head_title_text
    translate_title = translator.translate_text(head_title_text, source_lang="JA", target_lang="EN-US").text
    if not description_content.isspace():
        translate_conte = translator.translate_text(description_content, source_lang="JA", target_lang="EN-US").text.replace('"', "'")
        # translate_conte = description_content
    
    translate_head_text = html_head_text.replace(head_title_text, translate_title).replace(description_content, translate_conte)
    return translate_head_text

def translate_body(html_body_text):
    open_tat_start = 0
    href_start = 0
    html_body_count = html_body_text.count("<")
    href_count = html_body_text.count("href")
    for _ in range(href_count):
        start_a = html_body_text.find("href", href_start)
        end_a = html_body_text.find(">", start_a)
        en_sl = html_body_text.find("/", start_a, end_a)
        if en_sl == -1:
            href_start = end_a
            continue
        replace_text = html_body_text[start_a:en_sl]
        html_body_text = html_body_text[:start_a] + html_body_text[start_a: end_a].replace(replace_text, replace_text + "/en", 1) + html_body_text[end_a:]
        href_start = end_a + 3
    for _ in range(html_body_count):
        open_tag = html_body_text.find(">", open_tat_start)
        close_tag = html_body_text.find("<", open_tag)
        text = html_body_text[open_tag+1:close_tag]
        if text and not text.isspace():
            # 翻訳
            # translate_text = text
            translate_text = translator.translate_text(text, source_lang="JA", target_lang="EN-US").text.replace('"', "'")
            html_body_text = html_body_text.replace(text, translate_text, 1)
        open_tat_start = close_tag
    return html_body_text