"""
AI-Powered Stock Analysis Assistant
Uses context from ML analysis to answer user questions
"""
from typing import Dict, List, Optional
import json


class StockAssistant:
    """
    AI assistant that provides intelligent responses about stock analysis
    using context from ML clustering and technical indicators
    """
    
    def __init__(self):
        self.context_templates = {
            "cluster_explanation": {
                "Buy the Dip": "This stock is currently oversold based on RSI and MACD indicators, but shows strong fundamental support. It's a potential value opportunity for patient investors.",
                "Momentum": "This stock is in a strong uptrend with increasing volume, indicating sustained buying pressure. Good for trend-following strategies.",
                "Breakout": "This stock is breaking out from a consolidation pattern with strong volume confirmation. Early entry opportunity.",
                "Reversal": "This stock is showing signs of trend reversal with divergence in indicators. Suitable for contrarian strategies.",
                "Consolidation": "This stock is trading in a range. Wait for breakout confirmation before entering.",
                "Avoid": "This stock shows weak technical signals and unclear direction. Better opportunities exist elsewhere."
            },
            "risk_levels": {
                "low": "Conservative approach with tight stop-loss. Suitable for risk-averse investors.",
                "medium": "Balanced risk-reward profile. Good for most retail investors.",
                "high": "Aggressive strategy with wider stops. Only for experienced traders."
            }
        }
    
    def generate_response(
        self,
        question: str,
        stock_data: Dict,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate intelligent response based on question and stock context
        
        Args:
            question: User's question
            stock_data: Stock analysis data from ML pipeline
            conversation_history: Previous conversation for context
            
        Returns:
            Dict with response and confidence
        """
        question_lower = question.lower()
        
        # Analyze question intent
        if any(word in question_lower for word in ["why", "kenapa", "mengapa"]):
            return self._explain_reasoning(stock_data)
        
        elif any(word in question_lower for word in ["risk", "risiko", "bahaya"]):
            return self._explain_risk(stock_data)
        
        elif any(word in question_lower for word in ["when", "kapan", "entry"]):
            return self._suggest_entry(stock_data)
        
        elif any(word in question_lower for word in ["target", "profit", "tp"]):
            return self._suggest_targets(stock_data)
        
        elif any(word in question_lower for word in ["compare", "bandingkan", "vs"]):
            return self._compare_stocks(stock_data)
        
        elif any(word in question_lower for word in ["strategy", "strategi", "cara"]):
            return self._suggest_strategy(stock_data)
        
        else:
            return self._general_analysis(stock_data)
    
    def _explain_reasoning(self, stock_data: Dict) -> Dict:
        """Explain why stock is in specific cluster"""
        cluster = stock_data.get("cluster_label", "Unknown")
        indicators = stock_data.get("indicators", {})
        confidence = stock_data.get("confidence", 0)
        
        base_explanation = self.context_templates["cluster_explanation"].get(
            cluster,
            "Analysis based on technical indicators."
        )
        
        # Add specific indicator insights
        insights = []
        
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            insights.append(f"RSI at {rsi:.1f} indicates oversold conditions")
        elif rsi > 70:
            insights.append(f"RSI at {rsi:.1f} shows overbought territory")
        
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            insights.append("MACD shows bullish momentum")
        else:
            insights.append("MACD indicates bearish pressure")
        
        volume_ratio = indicators.get("volume_ratio", 1)
        if volume_ratio > 1.5:
            insights.append(f"Volume {volume_ratio:.1f}x above average confirms the move")
        
        response = f"{base_explanation}\n\n"
        response += "Key Technical Signals:\n"
        response += "\n".join(f"• {insight}" for insight in insights)
        response += f"\n\nConfidence Level: {confidence*100:.0f}%"
        
        return {
            "response": response,
            "confidence": confidence,
            "type": "reasoning"
        }
    
    def _explain_risk(self, stock_data: Dict) -> Dict:
        """Explain risk profile"""
        trade_plan = stock_data.get("trade_plan", {})
        backtest = stock_data.get("backtest", {})
        
        entry = trade_plan.get("entry_price", 0)
        stop_loss = trade_plan.get("stop_loss", 0)
        risk_pct = abs((stop_loss - entry) / entry * 100) if entry > 0 else 0
        
        win_rate = backtest.get("win_rate", 0)
        max_drawdown = backtest.get("max_drawdown", 0)
        
        risk_level = "low" if risk_pct < 3 else "medium" if risk_pct < 5 else "high"
        
        response = f"Risk Analysis:\n\n"
        response += f"• Risk per trade: {risk_pct:.1f}% (from entry to stop-loss)\n"
        response += f"• Historical win rate: {win_rate:.1f}%\n"
        response += f"• Maximum historical drawdown: {max_drawdown:.1f}%\n"
        response += f"• Risk level: {risk_level.upper()}\n\n"
        response += self.context_templates["risk_levels"][risk_level]
        
        return {
            "response": response,
            "confidence": 0.85,
            "type": "risk_analysis"
        }
    
    def _suggest_entry(self, stock_data: Dict) -> Dict:
        """Suggest entry timing"""
        trade_plan = stock_data.get("trade_plan", {})
        indicators = stock_data.get("indicators", {})
        cluster = stock_data.get("cluster_label", "")
        
        entry = trade_plan.get("entry_price", 0)
        current = stock_data.get("current_price", 0)
        
        distance_pct = ((entry - current) / current * 100) if current > 0 else 0
        
        response = f"Entry Timing Suggestion:\n\n"
        response += f"• Recommended entry: Rp {entry:,.0f}\n"
        response += f"• Current price: Rp {current:,.0f}\n"
        
        if abs(distance_pct) < 1:
            response += f"• Status: ✅ GOOD ENTRY ZONE (within 1%)\n\n"
            response += "You can enter now with proper position sizing."
        elif distance_pct > 0:
            response += f"• Status: ⏳ WAIT ({distance_pct:.1f}% above entry)\n\n"
            response += f"Wait for price to pull back to Rp {entry:,.0f} area."
        else:
            response += f"• Status: 🚀 PRICE MOVED ({abs(distance_pct):.1f}% below entry)\n\n"
            response += "Price has moved. Consider waiting for next setup."
        
        # Add cluster-specific timing advice
        if cluster == "Buy the Dip":
            response += "\n💡 For dip-buying: Enter in stages as price stabilizes."
        elif cluster == "Momentum":
            response += "\n💡 For momentum: Enter on pullbacks to moving averages."
        elif cluster == "Breakout":
            response += "\n💡 For breakouts: Enter on volume confirmation above resistance."
        
        return {
            "response": response,
            "confidence": 0.80,
            "type": "entry_timing"
        }
    
    def _suggest_targets(self, stock_data: Dict) -> Dict:
        """Suggest profit targets"""
        trade_plan = stock_data.get("trade_plan", {})
        
        entry = trade_plan.get("entry_price", 0)
        tp1 = trade_plan.get("take_profit_1", 0)
        tp2 = trade_plan.get("take_profit_2", 0)
        rr_ratio = trade_plan.get("risk_reward_ratio", 0)
        
        response = f"Profit Target Strategy:\n\n"
        response += f"📍 Entry: Rp {entry:,.0f}\n\n"
        response += f"🎯 Target 1 (TP1): Rp {tp1:,.0f}\n"
        response += f"   → Take 50% profit here\n"
        response += f"   → Move stop-loss to breakeven\n\n"
        response += f"🎯 Target 2 (TP2): Rp {tp2:,.0f}\n"
        response += f"   → Take remaining 50% profit\n"
        response += f"   → Or trail stop-loss\n\n"
        response += f"📊 Risk/Reward Ratio: 1:{rr_ratio:.1f}\n\n"
        response += "💡 Pro Tip: Scale out gradually to lock in profits while letting winners run."
        
        return {
            "response": response,
            "confidence": 0.85,
            "type": "profit_targets"
        }
    
    def _suggest_strategy(self, stock_data: Dict) -> Dict:
        """Suggest trading strategy"""
        cluster = stock_data.get("cluster_label", "")
        trading_style = stock_data.get("trading_style", "Swing Trading")
        
        strategies = {
            "Buy the Dip": {
                "approach": "Value/Contrarian",
                "timeframe": "Medium-term (2-4 weeks)",
                "tips": [
                    "Enter in stages as price stabilizes",
                    "Look for volume drying up (capitulation)",
                    "Wait for first higher low before full position",
                    "Be patient - reversals take time"
                ]
            },
            "Momentum": {
                "approach": "Trend Following",
                "timeframe": "Short to Medium-term (1-3 weeks)",
                "tips": [
                    "Buy pullbacks to 20 EMA",
                    "Let profits run with trailing stops",
                    "Add to winners (pyramid)",
                    "Exit when momentum weakens"
                ]
            },
            "Breakout": {
                "approach": "Breakout Trading",
                "timeframe": "Short-term (1-2 weeks)",
                "tips": [
                    "Wait for volume confirmation",
                    "Enter on first pullback after breakout",
                    "Set tight stops below breakout level",
                    "Take profits quickly on first resistance"
                ]
            }
        }
        
        strategy = strategies.get(cluster, {
            "approach": "Adaptive",
            "timeframe": "Flexible",
            "tips": ["Follow the trade plan", "Manage risk strictly"]
        })
        
        response = f"Recommended Strategy: {strategy['approach']}\n\n"
        response += f"⏱️ Timeframe: {strategy['timeframe']}\n"
        response += f"📈 Style: {trading_style}\n\n"
        response += "Key Execution Tips:\n"
        response += "\n".join(f"{i+1}. {tip}" for i, tip in enumerate(strategy['tips']))
        
        return {
            "response": response,
            "confidence": 0.90,
            "type": "strategy"
        }
    
    def _general_analysis(self, stock_data: Dict) -> Dict:
        """General stock analysis summary"""
        ticker = stock_data.get("ticker", "").replace(".JK", "")
        name = stock_data.get("name", "")
        cluster = stock_data.get("cluster_label", "")
        confidence = stock_data.get("confidence", 0)
        reasoning = stock_data.get("reasoning", "")
        
        response = f"📊 {ticker} - {name}\n\n"
        response += f"🏷️ Classification: {cluster}\n"
        response += f"🎯 Confidence: {confidence*100:.0f}%\n\n"
        response += f"💭 AI Analysis:\n{reasoning}\n\n"
        response += "Ask me specific questions like:\n"
        response += "• 'Why is this stock classified as {}'?\n".format(cluster)
        response += "• 'What are the risks?'\n"
        response += "• 'When should I enter?'\n"
        response += "• 'What are the profit targets?'"
        
        return {
            "response": response,
            "confidence": confidence,
            "type": "general"
        }
    
    def _compare_stocks(self, stock_data: Dict) -> Dict:
        """Compare with other stocks (placeholder)"""
        response = "Stock comparison feature coming soon!\n\n"
        response += "This will allow you to compare:\n"
        response += "• Technical indicators\n"
        response += "• Risk/reward profiles\n"
        response += "• Historical performance\n"
        response += "• Cluster characteristics"
        
        return {
            "response": response,
            "confidence": 0.50,
            "type": "comparison"
        }


# Singleton instance
assistant = StockAssistant()


def get_ai_response(question: str, stock_data: Dict) -> Dict:
    """
    Get AI assistant response for a question about a stock
    
    Args:
        question: User's question
        stock_data: Stock analysis data
        
    Returns:
        Dict with response, confidence, and type
    """
    return assistant.generate_response(question, stock_data)
