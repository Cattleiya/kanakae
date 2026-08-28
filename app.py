import streamlit as st
from sudachipy import dictionary
import jaconv
import unicodedata

tokenizer = dictionary.Dictionary().create()

MAX_CHARS = 5000

def convert_text(text):
    words = tokenizer.tokenize(text)

    readings = []

    for word in words:

        text = word.surface()

        normalized_text = unicodedata.normalize("NFKC", text)

        part_of_speech = word.part_of_speech()
        
        if (
            part_of_speech[0] == "補助記号"
            or part_of_speech[0] == "空白"
            or text.isdecimal()
            or (normalized_text.isascii() and normalized_text.isalpha())  
        ):
            readings.append((text, part_of_speech))
        else:
            readings.append((word.reading_form(), part_of_speech))

    result = ""

    previous_was_symbol = False

    for reading, part_of_speech in readings:
        if result == "":
            result = reading
        elif (
            part_of_speech[0] == "補助記号"
            or previous_was_symbol
        ):
            result = result + reading

        elif (
            part_of_speech[0] == "助動詞"
            or part_of_speech[0] == "接尾辞"
            or (
                part_of_speech[0] == "助詞"
                and part_of_speech[1] == "終助詞"
            )
        ):
            result = result + reading
        else:
            if reading.isspace() or result[-1].isspace():
                result = result + reading
            else:
                result = result + " " + reading 

        previous_was_symbol = part_of_speech[0] == "補助記号"

    result = jaconv.kata2hira(result)

    return result

def show_debug_info(text):
    words = tokenizer.tokenize(text)

    for word in words:
        debug_text = word.surface()

        st.write(
            "元の文字：", debug_text,
            "　実体：", repr(debug_text),
            "　読み：", word.reading_form(),
            "　読みの実体：", repr(word.reading_form()),
            "　品詞：", word.part_of_speech()
        )

st.set_page_config(
    page_title="かなかえ",
    page_icon="📖",
    layout="wide"
)

st.title("かなかえ")

st.write("読みやすい文章へ変換するソフト")

st.caption("Ver.1 試験運用中")

with st.expander("使い方"):
    st.write("1. 文章を入力します。")
    st.write("2. 「変換する」を押します。")
    st.write("3. 変換結果を確認します。")
    st.write("例：")
    st.write("今日は、「東京タワー」へ行きました。")
    st.write("↓")
    st.write("きょう は、「とうきょう たわー」へ いきました。")
    st.write("※ 漢字やカタカナをひらがな中心に変換し、単語などのまとまりが読みやすくなるようにスペースを入れます。")
    st.write("※ 英数字や記号は原則そのまま残します。")
    st.write("※ 日本語の文章を基本対象としています。")

with st.expander("試験運用について"):
    st.write("【このアプリの目的】")
    st.write("日本語の文章を、読みやすく区切られたひらがな中心の文章へ変換します。")

    st.write("【Ver.1で対応しないこと】")
    st.write("・外国語の自動判別")
    st.write("・固有名詞や特殊な読みの完全な変換")
    st.write("・珍しい記号の網羅的な対応")
    st.write("・数詞＋助数詞など、すべての自然な区切り")

original_text = st.text_area(
    "文章を入力してください",
    height=200,
    max_chars=MAX_CHARS
)

st.caption(f"{len(original_text)} / {MAX_CHARS}文字")

if st.button("変換する"):

    if not original_text.strip():
        st.warning("文章を入力してください。")

    else:
       with st.spinner("変換中..."):
        result_text = convert_text(original_text)
        st.subheader("変換結果")

        st.code(
                result_text,
                language=None,
                wrap_lines=True
            )

        st.caption("※ PCでは変換結果にマウスを合わせると、スマホでは変換結果をタップすると、右上にコピーアイコンが表示されます。")

        with st.expander("開発者モード（調査表示）"):
            show_debug_info(original_text)
