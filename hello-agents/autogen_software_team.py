import streamlit as st
import requests
import time
import os

os.environ["HTTP_PROXY"] = "http://172.31.179.177:7890"
os.environ["HTTPS_PROXY"] = "http://172.31.179.177:7890"
os.environ["http_proxy"] = "http://172.31.179.177:7890"
os.environ["https_proxy"] = "http://172.31.179.177:7890"

# 函数：获取比特币当前价格和24小时变化
def get_bitcoin_data():
    try:
        # 请求CoinGecko的比特币数据API
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true'
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        print(data)
        # 解析数据
        current_price = data['bitcoin']['usd']
        price_change_24h = data['bitcoin']['usd_24h_change']
        return current_price, price_change_24h
    except requests.exceptions.RequestException as e:
        st.error("无法获取数据，请稍后重试。")
        print("请求错误：", e)  # 记录错误信息
        return None, None

# Streamlit应用
def main():
    st.title("比特币实时价格显示应用")
    
    refresh_button = st.button("刷新价格")
    
    if refresh_button:
        # 更新价格
        st.session_state.price_data = None  # 清理缓存以便重新加载

    # 检查是否已有价格数据
    if 'price_data' not in st.session_state or st.session_state.price_data is None:
        with st.spinner("正在加载价格数据..."):
            current_price, price_change_24h = get_bitcoin_data()
            print(current_price)
            print(price_change_24h)

            if current_price is not None and price_change_24h is not None:
                st.session_state.price_data = (current_price, price_change_24h)
            else:
                return  # 在获取数据失败时退出

    # 获取价格数据
    current_price, price_change_24h = st.session_state.price_data

    # 显示当前价格
    st.subheader(f"当前比特币价格: ${current_price:.2f} USD")

    # 计算涨跌额
    price_change_amount = (price_change_24h / 100) * current_price
    st.subheader(f"24小时价格变化: {price_change_24h:.2f}%")
    st.write(f"涨跌额: ${price_change_amount:.2f} USD")

if __name__ == "__main__":
    main()