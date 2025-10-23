#!/usr/bin/env python3
"""
AI Analysis Module for Cryptocurrency Trading Decisions

This module integrates xAI SDK with OKX API data to generate structured trading decisions.
Uses grok-4-fast-non-reasoning model with structured outputs for reliable JSON responses.
"""

import os
import json
import configparser
import requests
from datetime import datetime
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import user, system
from okx_time_utils import get_okx_current_time


class TradeSide(str, Enum):
    """Trading side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration"""
    MARKET = "market"


class TradingMode(str, Enum):
    """Trading mode enumeration"""
    CROSS = "cross"


class PositionSide(str, Enum):
    """Position side enumeration"""
    NET = "net"


class TriggerPriceType(str, Enum):
    """Trigger price type enumeration"""
    MARK = "mark"


class AttachAlgoOrds(BaseModel):
    """Attached algorithm orders for take profit and stop loss"""
    tpTriggerPx: Optional[str] = Field(None, description="Take profit trigger price")
    tpOrdPx: str = Field("-1", description="Take profit order price, -1 for market order")
    slTriggerPx: Optional[str] = Field(None, description="Stop loss trigger price")
    slOrdPx: str = Field("-1", description="Stop loss order price, -1 for market order")
    tpTriggerPxType: TriggerPriceType = Field(TriggerPriceType.MARK, description="Take profit trigger price type")
    slTriggerPxType: TriggerPriceType = Field(TriggerPriceType.MARK, description="Stop loss trigger price type")


class TradeOrder(BaseModel):
    """Trading order structure"""
    instId: Optional[str] = Field(None, description="Trading pair symbol, e.g., BTC-USDT-SWAP")
    tdMode: TradingMode = Field(TradingMode.CROSS, description="Margin mode, fixed as cross")
    side: Optional[TradeSide] = Field(None, description="Trading side: buy or sell")
    ordType: OrderType = Field(OrderType.MARKET, description="Order type, fixed as market")
    sz: Optional[str] = Field(None, description="Contract size")
    lever: Optional[str] = Field(None, description="Leverage multiplier")
    attachAlgoOrds: Optional[AttachAlgoOrds] = Field(None, description="Take profit and stop loss orders")


class ClosePosition(BaseModel):
    """Close position structure"""
    instId: Optional[str] = Field(None, description="Trading pair symbol to close position")
    posSide: PositionSide = Field(PositionSide.NET, description="Position side, fixed as net")


class TradingDecision(BaseModel):
    """Complete trading decision structure"""
    trades: Optional[List[TradeOrder]] = Field(None, description="List of trading orders to execute")
    closures: Optional[List[ClosePosition]] = Field(None, description="List of positions to close")
    reason: str = Field(..., description="Analysis reasoning and decision explanation")


class AIAnalyzer:
    """AI-powered trading analysis using xAI SDK"""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize AI analyzer with configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize xAI client
        self.xai_api_key = self.config.get('XAI', 'api_key')
        self.model = self.config.get('XAI', 'model', fallback='grok-4-fast-non-reasoning')
        self.client = Client(
            api_key=self.xai_api_key,
            timeout=3600  # Extended timeout for reasoning models
        )
        
        # OKX API configuration
        self.okx_api_key = self.config.get('OKX', 'api_key')
        self.okx_secret = self.config.get('OKX', 'api_secret')
        self.okx_passphrase = self.config.get('OKX', 'api_passphrase')
        
        # Load static content
        self.prompt_content = self._load_file("prompt.md")
        self.okx_account_content = self._load_file("okx_account.md")
        self.okx_market_content = self._load_file("okx_market.md")
        self.trade_rules_content = self._load_file("trade_rules.md")
    
    def _load_file(self, filepath: str) -> str:
        """
        Load content from file
        
        Args:
            filepath: Path to file
            
        Returns:
            File content as string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: File {filepath} not found")
            return ""
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return ""
    
    
    def prepare_prompt(self) -> tuple[str, str]:
        """
        Prepare system and user prompts with current data
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Extract system and user prompts from prompt.md
        content = self.prompt_content
        
        # Split by markdown headers
        if "## system_prompt" in content and "## user_prompt" in content:
            parts = content.split("## system_prompt")[1].split("## user_prompt")
            system_prompt = parts[0].strip()
            user_template = parts[1].strip()
        else:
            # Fallback if structure is different
            system_prompt = "You are a cryptocurrency trading expert. Analyze the provided data and make trading decisions."
            user_template = content
        
        # Ensure system prompt requests proper JSON structure
        system_prompt += "\n\nIMPORTANT: You must respond with a single, valid JSON object that matches this exact structure:\n"
        system_prompt += '{"trades": [array of trade orders or null], "closures": [array of position closures or null], "reason": "your analysis explanation"}\n'
        system_prompt += "Do not include any text before or after the JSON. The response must be valid JSON only."
        
        # Get current time from OKX (using unified time utils)
        current_time = get_okx_current_time()
        
        # Format user prompt with variables
        user_prompt = user_template.format(
            current_time=current_time,
            okx_account=self.okx_account_content,
            okx_market=self.okx_market_content,
            trade_rules=self.trade_rules_content
        )
        
        return system_prompt, user_prompt
    
    def analyze_and_decide(self) -> dict:
        """
        Perform AI analysis and generate trading decision
        
        Returns:
            Structured trading decision as dictionary
        """
        try:
            # Prepare prompts
            system_prompt, user_prompt = self.prepare_prompt()
            
            print(f"DEBUG: System prompt length: {len(system_prompt)} chars")
            print(f"DEBUG: User prompt length: {len(user_prompt)} chars")
            
            # Create chat session
            chat = self.client.chat.create(model=self.model)
            chat.append(system(system_prompt))
            chat.append(user(user_prompt))
            
            print("DEBUG: Sending request to xAI API...")
            
            # Get structured response using sample() method (official recommended approach)
            try:
                response = chat.sample()
                print(f"DEBUG: Raw API response received: {repr(response)}")
                print(f"DEBUG: Response type: {type(response)}")
                print(f"DEBUG: Response content length: {len(response.content)} chars")
                
                # Parse JSON manually
                import json
                try:
                    decision_data = json.loads(response.content)
                    print(f"DEBUG: JSON parsed successfully")
                    
                    # Validate with Pydantic
                    decision = TradingDecision(**decision_data)
                    print(f"DEBUG: Pydantic validation successful")
                    
                except json.JSONDecodeError as json_error:
                    print(f"DEBUG: JSON decode error: {json_error}")
                    print(f"DEBUG: Raw content: {repr(response.content)}")
                    
                    # Try to fix common JSON issues
                    try:
                        # Fix missing closing bracket in arrays
                        fixed_content = response.content
                        if '}]' not in fixed_content and '}}' in fixed_content:
                            fixed_content = fixed_content.replace('}}', '}]}', 1)
                            print(f"DEBUG: Attempting to fix JSON with missing bracket")
                            decision_data = json.loads(fixed_content)
                            print(f"DEBUG: Fixed JSON parsed successfully")
                        else:
                            raise json_error
                    except:
                        raise Exception(f"Failed to parse JSON response: {json_error}")
                except Exception as validation_error:
                    print(f"DEBUG: Pydantic validation error: {validation_error}")
                    print(f"DEBUG: Parsed data: {decision_data}")
                    raise Exception(f"Failed to validate response structure: {validation_error}")
                    
            except Exception as sample_error:
                print(f"DEBUG: Sample error occurred: {sample_error}")
                print(f"DEBUG: Sample error type: {type(sample_error)}")
                raise sample_error
            
            # Convert to dictionary for JSON serialization
            decision_dict = decision.model_dump(exclude_none=True)
            
            # Add metadata
            decision_dict['_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'model': self.model,
                'analysis_type': 'ai_structured_output'
            }
            
            return decision_dict
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {repr(e)}")
            
            # Return fallback decision
            return {
                'trades': None,
                'closures': None,
                'reason': f"Analysis failed due to error: {str(e)}. No trading action recommended.",
                '_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'model': self.model,
                    'analysis_type': 'error_fallback',
                    'error': str(e)
                }
            }
    
    def save_decision(self, decision: dict, output_file: str = "decision.json") -> bool:
        """
        Save trading decision to JSON file
        
        Args:
            decision: Trading decision dictionary
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(decision, f, indent=2, ensure_ascii=False)
            print(f"Trading decision saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving decision to {output_file}: {e}")
            return False
    
    def run_analysis(self, output_file: str = "decision.json") -> dict:
        """
        Run complete analysis pipeline
        
        Args:
            output_file: Output file path for decision
            
        Returns:
            Trading decision dictionary
        """
        print("Starting AI trading analysis...")
        print(f"Using model: {self.model}")

        # Perform analysis
        decision = self.analyze_and_decide()
        
        # Save to file
        self.save_decision(decision, output_file)
        
        # Print summary
        print("\n=== Analysis Summary ===")
        print(f"Timestamp: {decision.get('_metadata', {}).get('timestamp', 'N/A')}")
        print(f"Decision: {decision.get('reason', 'No reason provided')}")
        
        if decision.get('trades'):
            print(f"Trades to execute: {len(decision['trades'])}")
            for i, trade in enumerate(decision['trades'], 1):
                print(f"  {i}. {trade.get('side', 'N/A')} {trade.get('instId', 'N/A')} "
                      f"size={trade.get('sz', 'N/A')} lever={trade.get('lever', 'N/A')}")
        
        if decision.get('closures'):
            print(f"Positions to close: {len(decision['closures'])}")
            for i, closure in enumerate(decision['closures'], 1):
                print(f"  {i}. Close {closure.get('instId', 'N/A')}")
        
        if not decision.get('trades') and not decision.get('closures'):
            print("No trading actions recommended")
        
        return decision


def main():
    """Main function for standalone execution"""
    try:
        analyzer = AIAnalyzer()
        decision = analyzer.run_analysis()
        return decision
    except Exception as e:
        print(f"Error in main execution: {e}")
        return None


if __name__ == "__main__":
    main()