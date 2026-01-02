# app/services/market_data.py 수정
import yfinance as yf


class MarketService:
    @staticmethod
    async def fetch_ticker_data(ticker: str):
        stock = yf.Ticker(ticker)

        # 가격 정보 가져오기 (가장 안정적인 방식)
        history = stock.history(period="1d")
        if history.empty:
            current_price = 0.0
        else:
            current_price = history['Close'].iloc[-1]

        # 뉴스 가져오기 및 에러 방지 처리
        raw_news = stock.news[:5]
        news_list = []

        for n in raw_news:
            # yfinance 버전에 따라 'title' 또는 'content' -> 'title' 구조가 다를 수 있음
            title = n.get('title') or n.get('content', {}).get('title', 'No Title')
            link = n.get('link') or n.get('content', {}).get('pubDate', '#')
            news_list.append({"title": title, "link": link})

        return {
            "price": current_price,
            "news": news_list
        }