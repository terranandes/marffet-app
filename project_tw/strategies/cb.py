
from enum import Enum
from pydantic import BaseModel

class CBSignal(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    WATCH_SELL = "WATCH_SELL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class CBMyAdvice(BaseModel):
    signal: CBSignal
    action_short: str
    action_detail: str
    color: str # For frontend UI

class CBStrategy:
    def __init__(self):
        pass

    def calculate_premium(self, cb_price: float, stock_price: float, conversion_price: float) -> float:
        """
        Calculate Conversion Premium Rate (%).
        Formula: (CB Market Price - Parity Price) / Parity Price
        Parity Price = (Stock Price / Conversion Price) * 100
        """
        if conversion_price == 0 or stock_price == 0:
            return 0.0
            
        parity_price = (stock_price / conversion_price) * 100
        premium = ((cb_price - parity_price) / parity_price) * 100
        return premium

    def evaluate(self, premium_rate: float) -> CBMyAdvice:
        """
        Evaluate logic based on User Provided Rules.
        Input: premium_rate (float) in Percentage (e.g., 5.0 for 5%)
        """
        i2 = premium_rate
        
        if i2 < -1:
            return CBMyAdvice(
                signal=CBSignal.STRONG_BUY,
                action_short="馬上買入CB, 賣出現股",
                action_detail="套利警報：訊號出現！立即精算所有交易成本，確認利潤空間。(或有轉換價值)",
                color="red" # Red for urgent/hot in Taiwan stock UI usually means 'up' but here 'action'
            )
        elif i2 < 3.5:
            return CBMyAdvice(
                signal=CBSignal.BUY,
                action_short="考慮買入CB, 賣出現股",
                action_detail="最佳買點：此時買入CB的性價比最高，是建立多頭部位的首選。",
                color="orange"
            )
        elif i2 < 7:
            return CBMyAdvice(
                signal=CBSignal.HOLD,
                action_short="中立",
                action_detail="安心持有：價格合理，享受CB攻守兼備的特性。",
                color="green"
            )
        elif i2 < 15:
            return CBMyAdvice(
                signal=CBSignal.WATCH_SELL,
                action_short="考慮賣出CB, 買入現股",
                action_detail="評估信心 (1)：保險費開始變貴，問自己：是否該為了更高報酬而放棄保險？",
                color="blue"
            )
        elif i2 < 30:
            return CBMyAdvice(
                signal=CBSignal.SELL,
                action_short="賣出CB, 買入現股",
                action_detail="評估信心 (2)：保險費很貴！若非極度看好後市，持有現股機會成本高。",
                color="purple"
            )
        else:
            return CBMyAdvice(
                signal=CBSignal.STRONG_SELL,
                action_short="馬上賣出CB, 買入現股",
                action_detail="強烈行動訊號：保險費極貴！將「帳面獲利」轉化為「實際報酬潛力」。",
                color="black"
            )
