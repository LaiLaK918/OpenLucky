#!/usr/bin/env python3
"""Execute OKX trades based on decision.json parameters"""

import json
import configparser
from okx.Trade import TradeAPI
from okx.Account import AccountAPI
import time
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, str]:
    """Load API credentials from config.ini"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    return {
        'api_key': config['OKX']['api_key'],
        'api_secret': config['OKX']['api_secret'],
        'api_passphrase': config['OKX']['api_passphrase']
    }


def load_decision() -> Dict[str, Any]:
    """Load trading decision from decision.json"""
    with open('decision.json', 'r') as f:
        return json.load(f)


def execute_closures(trade_api: TradeAPI, account_api: AccountAPI, closures: List[Dict[str, Any]]) -> None:
    """Execute position closures by placing market orders with retry mechanism"""
    for i, closure in enumerate(closures, 1):
        logger.info(f"[{i}/{len(closures)}] Closing position: {closure['instId']}")
        
        # Retry mechanism for getting positions
        max_retries = 3
        retry_delay = 2
        positions = None
        
        for attempt in range(max_retries):
            try:
                # Get current position to determine size and side
                positions = account_api.get_positions(instType='SWAP', instId=closure['instId'])
                if positions and positions.get('code') == '0':
                    break
                else:
                    logger.warning(f"Attempt {attempt + 1}: Invalid response getting position: {positions}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Error getting position info: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to get position info after {max_retries} attempts")
                    continue
        
        if positions and positions.get('code') == '0' and positions.get('data'):
            for pos in positions['data']:
                if float(pos['pos']) != 0:
                    # Determine closing side (opposite of position)
                    close_side = 'sell' if float(pos['pos']) > 0 else 'buy'
                    close_size = abs(float(pos['pos']))
                    
                    logger.info(f"Current position: {pos['pos']} contracts, closing with {close_side} {close_size}")
                    
                    # Retry mechanism for placing order
                    order_placed = False
                    for attempt in range(max_retries):
                        try:
                            # Place market order to close position
                            result = trade_api.place_order(
                                instId=closure['instId'],
                                tdMode='cross',
                                side=close_side,
                                ordType='market',
                                sz=str(int(close_size)),
                                posSide=closure.get('posSide', 'net')
                            )
                            
                            if result and result.get('code') == '0':
                                logger.info(f"✓ Position closed successfully: {result}")
                                order_placed = True
                                break
                            else:
                                logger.warning(f"Attempt {attempt + 1}: Order failed: {result}")
                                if attempt < max_retries - 1:
                                    time.sleep(retry_delay)
                                    
                        except Exception as e:
                            logger.error(f"Attempt {attempt + 1}: Error placing close order: {e}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                            else:
                                logger.error(f"Failed to close position after {max_retries} attempts")
                    
                    if not order_placed:
                        logger.error(f"Unable to close position for {closure['instId']}")
                else:
                    logger.info(f"No position to close for {closure['instId']}")
        else:
            logger.error(f"No valid position data found for {closure['instId']}")
        
        # Delay between different instruments to avoid rate limits
        if i < len(closures):
            time.sleep(1.0)


def execute_trades(trade_api: TradeAPI, account_api: AccountAPI, trades: List[Dict[str, Any]]) -> None:
    """Execute trade orders with retry mechanism"""
    for i, trade in enumerate(trades, 1):
        logger.info(f"[{i}/{len(trades)}] Placing order: {trade['instId']} {trade['side']} {trade['sz']} contracts")
        
        # Use all parameters from decision.json as provided
        order_params = {
            'instId': trade['instId'],
            'tdMode': trade['tdMode'],
            'side': trade['side'],
            'ordType': trade['ordType'],
            'sz': trade['sz'],
            'posSide': 'net'  # Add position side for net mode
        }
        
        # Handle leverage setting based on OKX best practices
        if 'lever' in trade:
            logger.info(f"Checking leverage requirement: {trade['lever']}x for {trade['instId']}")
            
            try:
                # Check current leverage first
                leverage_info = account_api.get_leverage(instId=trade['instId'], mgnMode=trade['tdMode'])
                current_lever = None
                if leverage_info and leverage_info.get('code') == '0' and leverage_info.get('data'):
                    current_lever = leverage_info['data'][0].get('lever')
                    logger.info(f"Current leverage: {current_lever}x")
                
                # Only try to set leverage if it's different and no positions exist
                if current_lever != trade['lever']:
                    # Check for existing positions
                    positions = account_api.get_positions(instType='SWAP', instId=trade['instId'])
                    has_position = False
                    if positions and positions.get('code') == '0' and positions.get('data'):
                        has_position = any(float(pos['pos']) != 0 for pos in positions['data'])
                    
                    if not has_position:
                        logger.info(f"Setting leverage to {trade['lever']}x for {trade['instId']}")
                        lever_result = account_api.set_leverage(
                            instId=trade['instId'],
                            lever=trade['lever'],
                            mgnMode=trade['tdMode']
                        )
                        if lever_result and lever_result.get('code') == '0':
                            logger.info(f"✓ Leverage set successfully to {trade['lever']}x")
                        else:
                            logger.warning(f"⚠ Could not set leverage: {lever_result}")
                            logger.info(f"  Continuing with current leverage ({current_lever}x)")
                    else:
                        logger.warning(f"⚠ Position exists for {trade['instId']}, cannot change leverage")
                        logger.info(f"  Continuing with current leverage ({current_lever}x)")
                else:
                    logger.info(f"✓ Leverage already set to {trade['lever']}x")
                
            except Exception as e:
                logger.error(f"Error handling leverage: {e}")
                logger.info("Continuing without leverage adjustment")
            
            time.sleep(0.5)
        
        # Add TP/SL if specified in decision.json
        if 'attachAlgoOrds' in trade:
            algo = trade['attachAlgoOrds']
            attach_algo_ord = {}
            
            # Add all algo parameters from decision.json
            if 'tpTriggerPx' in algo:
                attach_algo_ord['tpTriggerPx'] = algo['tpTriggerPx']
            if 'tpOrdPx' in algo:
                attach_algo_ord['tpOrdPx'] = algo['tpOrdPx']
            if 'slTriggerPx' in algo:
                attach_algo_ord['slTriggerPx'] = algo['slTriggerPx']
            if 'slOrdPx' in algo:
                attach_algo_ord['slOrdPx'] = algo['slOrdPx']
            if 'tpTriggerPxType' in algo:
                attach_algo_ord['tpTriggerPxType'] = algo['tpTriggerPxType']
            if 'slTriggerPxType' in algo:
                attach_algo_ord['slTriggerPxType'] = algo['slTriggerPxType']
            
            if attach_algo_ord:
                order_params['attachAlgoOrds'] = [attach_algo_ord]
        
        # Place order with retry mechanism
        max_retries = 3
        retry_delay = 2
        order_placed = False
        
        for attempt in range(max_retries):
            try:
                result = trade_api.place_order(**order_params)
                
                if result and result.get('code') == '0':
                    logger.info(f"✓ Order placed successfully: {result}")
                    order_placed = True
                    break
                else:
                    logger.warning(f"Attempt {attempt + 1}: Order failed: {result}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Error placing order: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to place order after {max_retries} attempts")
        
        if not order_placed:
            logger.error(f"Unable to place order for {trade['instId']}")
        
        # Delay between different trades
        if i < len(trades):
            time.sleep(1.0)


def main():
    """Main execution function"""
    try:
        # Load configurations
        config = load_config()
        decision = load_decision()
        
        # Initialize APIs
        trade_api = TradeAPI(
            api_key=config['api_key'],
            api_secret_key=config['api_secret'],
            passphrase=config['api_passphrase'],
            flag='0'  # 0 for real trading
        )
        
        account_api = AccountAPI(
            api_key=config['api_key'],
            api_secret_key=config['api_secret'],
            passphrase=config['api_passphrase'],
            flag='0'  # 0 for real trading
        )
        
        # Check and set account configuration
        try:
            # Get current account configuration
            account_config = account_api.get_account_config()
            if account_config and account_config.get('code') == '0' and account_config.get('data'):
                config_data = account_config['data'][0]
                pos_mode = config_data.get('posMode')
                logger.info(f"Current position mode: {pos_mode}")
                
                # If position mode is not 'net_mode', try to set it
                if pos_mode != 'net_mode':
                    logger.info("Setting position mode to net_mode...")
                    result = account_api.set_position_mode(posMode='net_mode')
                    if result and result.get('code') == '0':
                        logger.info("✓ Position mode set to net_mode successfully")
                    else:
                        logger.warning(f"Could not set position mode: {result}")
            else:
                logger.warning(f"Could not get account config: {account_config}")
                
        except Exception as e:
            logger.error(f"Error checking account configuration: {e}")
            logger.info("Continuing with default settings...")
        
        # Execute closures first if any
        if 'closures' in decision and decision['closures']:
            logger.info("=== Executing Closures ===")
            execute_closures(trade_api, account_api, decision['closures'])
            logger.info("")
        
        # Execute trades
        if 'trades' in decision and decision['trades']:
            logger.info("=== Executing Trades ===")
            execute_trades(trade_api, account_api, decision['trades'])
            logger.info("")
        
        logger.info("Execution completed!")
        logger.info(f"Reason: {decision.get('reason', 'No reason provided')}")
        
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()