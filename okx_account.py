#!/usr/bin/env python3
"""OKX API Reporter - Fetch account and SWAP information and generate MD report"""

import configparser
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from okx_time_utils import get_okx_current_time, okx_time
import okx.Account as Account
import okx.Trade as Trade
import okx.PublicData as PublicData


class OKXReporter:
    """OKX API Reporter for fetching account and SWAP information"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize OKX API client with configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize OKX API clients
        self.api_key = self.config.get('OKX', 'api_key')
        self.secret_key = self.config.get('OKX', 'api_secret')
        self.passphrase = self.config.get('OKX', 'api_passphrase')
        
        # Initialize API clients
        self.account_api = Account.AccountAPI(
            api_key=self.api_key,
            api_secret_key=self.secret_key,
            passphrase=self.passphrase,
            use_server_time=False,
            flag='0'  # 0: Production, 1: Demo
        )
        
        self.trade_api = Trade.TradeAPI(
            api_key=self.api_key,
            api_secret_key=self.secret_key,
            passphrase=self.passphrase,
            use_server_time=False,
            flag='0'
        )
        
        self.public_api = PublicData.PublicAPI(
            api_key=self.api_key,
            api_secret_key=self.secret_key,
            passphrase=self.passphrase,
            use_server_time=False,
            flag='0'
        )
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_account_balance(self, ccy: Optional[str] = "USDT") -> Dict[str, Any]:
        """
        Fetch account balance information
        
        Args:
            ccy: Currency filter (default: USDT)
            
        Returns:
            Account balance data
        """
        try:
            params = {}
            if ccy:
                params['ccy'] = ccy
            
            response = self.account_api.get_account_balance(**params)
            return response
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return {}
    
    def get_account_config(self) -> Dict[str, Any]:
        """
        Fetch account configuration
        
        Returns:
            Account configuration data
        """
        try:
            response = self.account_api.get_account_config()
            return response
        except Exception as e:
            self.logger.error(f"Error fetching account config: {e}")
            return {}
    
    def get_trade_fee(self, inst_type: str = "SWAP", inst_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch trade fee information
        
        Args:
            inst_type: Instrument type (SWAP for perpetual futures)
            inst_id: Specific instrument ID
            
        Returns:
            Trade fee data
        """
        try:
            params = {'instType': inst_type}
            if inst_id:
                params['instId'] = inst_id
            
            response = self.account_api.get_fee_rates(**params)
            return response
        except Exception as e:
            self.logger.error(f"Error fetching trade fee: {e}")
            return {}
    
    def get_funding_rate(self, inst_id: str) -> Dict[str, Any]:
        """
        Fetch funding rate information
        
        Args:
            inst_id: Instrument ID (e.g., 'BTC-USDT-SWAP')
            
        Returns:
            Funding rate data
        """
        try:
            response = self.public_api.get_funding_rate(instId=inst_id)
            return response
        except Exception as e:
            self.logger.error(f"Error fetching funding rate: {e}")
            return {}
    
    def get_pending_orders(self, inst_type: str = "SWAP", inst_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch pending orders
        
        Args:
            inst_type: Instrument type (SWAP for perpetual futures)
            inst_id: Specific instrument ID
            
        Returns:
            Pending orders data
        """
        try:
            params = {'instType': inst_type}
            if inst_id:
                params['instId'] = inst_id
            
            response = self.trade_api.get_order_list(**params)
            return response
        except Exception as e:
            self.logger.error(f"Error fetching pending orders: {e}")
            return {}
    
    def get_positions(self, inst_type: str = "SWAP", inst_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch current positions with TP/SL information from algo orders
        
        Args:
            inst_type: Instrument type (SWAP for perpetual futures)
            inst_id: Specific instrument ID
            
        Returns:
            Current positions data with TP/SL information
        """
        try:
            params = {'instType': inst_type}
            if inst_id:
                params['instId'] = inst_id
            
            response = self.account_api.get_positions(**params)
            
            # Get TP/SL information from both OCO and conditional algo orders
            try:
                tp_sl_map = {}
                
                # Query OCO orders (one-cancels-the-other)
                oco_orders = self.trade_api.order_algos_list(instType=inst_type, ordType='oco')
                if oco_orders and oco_orders.get('code') == '0' and oco_orders.get('data'):
                    for order in oco_orders['data']:
                        inst_id_key = order.get('instId')
                        if inst_id_key:
                            tp_sl_map[inst_id_key] = {
                                'tpTriggerPx': order.get('tpTriggerPx', ''),
                                'slTriggerPx': order.get('slTriggerPx', ''),
                                'tpTriggerPxType': order.get('tpTriggerPxType', ''),
                                'slTriggerPxType': order.get('slTriggerPxType', ''),
                                'tpOrdPx': order.get('tpOrdPx', ''),
                                'slOrdPx': order.get('slOrdPx', '')
                            }
                
                # Query conditional orders (one-way stop orders)
                conditional_orders = self.trade_api.order_algos_list(instType=inst_type, ordType='conditional')
                if conditional_orders and conditional_orders.get('code') == '0' and conditional_orders.get('data'):
                    for order in conditional_orders['data']:
                        inst_id_key = order.get('instId')
                        if inst_id_key:
                            # If already exists from OCO, update; otherwise create new
                            if inst_id_key not in tp_sl_map:
                                tp_sl_map[inst_id_key] = {
                                    'tpTriggerPx': '',
                                    'slTriggerPx': '',
                                    'tpTriggerPxType': '',
                                    'slTriggerPxType': '',
                                    'tpOrdPx': '',
                                    'slOrdPx': ''
                                }
                            
                            # Update with conditional order data
                            if order.get('tpTriggerPx'):
                                tp_sl_map[inst_id_key]['tpTriggerPx'] = order.get('tpTriggerPx', '')
                                tp_sl_map[inst_id_key]['tpTriggerPxType'] = order.get('tpTriggerPxType', '')
                                tp_sl_map[inst_id_key]['tpOrdPx'] = order.get('tpOrdPx', '')
                            if order.get('slTriggerPx'):
                                tp_sl_map[inst_id_key]['slTriggerPx'] = order.get('slTriggerPx', '')
                                tp_sl_map[inst_id_key]['slTriggerPxType'] = order.get('slTriggerPxType', '')
                                tp_sl_map[inst_id_key]['slOrdPx'] = order.get('slOrdPx', '')
                
                # Merge TP/SL info into positions data
                if response and response.get('code') == '0' and response.get('data'):
                    for position in response['data']:
                        inst_id_key = position.get('instId')
                        if inst_id_key in tp_sl_map:
                            position.update(tp_sl_map[inst_id_key])
                        else:
                            # Ensure TP/SL fields exist even if empty
                            position.update({
                                'tpTriggerPx': '',
                                'slTriggerPx': '',
                                'tpTriggerPxType': '',
                                'slTriggerPxType': '',
                                'tpOrdPx': '',
                                'slOrdPx': ''
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error fetching TP/SL information: {e}")
            
            return response
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return {}
    
    def get_positions_history(self, inst_type: str = "SWAP", days: int = 7) -> Dict[str, Any]:
        """
        Fetch historical positions (last 7 days) using the positions-history API
        
        Args:
            inst_type: Instrument type (SWAP for perpetual futures)
            days: Number of days to look back
            
        Returns:
            Historical positions data filtered for the last 7 days
        """
        try:
            # Calculate timestamp for 7 days ago using OKX server time
            okx_now_ms = okx_time.get_okx_timestamp_ms()
            seven_days_ago_ms = okx_now_ms - (days * 24 * 60 * 60 * 1000)
            
            # Use the positions-history API directly
            params = {
                'instType': inst_type,
                'limit': '100'
            }
            
            # Get positions history
            response = self.account_api.get_positions_history(**params)
            
            # Process and filter the data for last 7 days
            if response and 'data' in response:
                processed_data = []
                for pos in response['data']:
                    # Filter by close time (last 7 days)
                    close_time = pos.get('uTime', '')
                    if close_time and int(close_time) >= seven_days_ago_ms:
                        # Convert to website format
                        processed_pos = {
                            'instId': pos.get('instId', ''),
                            'posStatus': 'Fully Closed (全部平仓)',
                            'openAvgPx': pos.get('openAvgPx', ''),
                            'closeAvgPx': pos.get('closeAvgPx', ''),
                            'realizedPnl': pos.get('pnl', ''),
                            'pnlRatio': f"{float(pos.get('pnlRatio', 0)) * 100:.2f}%" if pos.get('pnlRatio') else '',
                            'maxPos': pos.get('openMaxPos', ''),
                            'closedPos': pos.get('closeTotalPos', ''),
                            'openTime': self.format_timestamp(pos.get('cTime', '')),
                            'closeTime': self.format_timestamp(pos.get('uTime', '')),
                            'lever': pos.get('lever', '')
                        }
                        processed_data.append(processed_pos)
                
                return {'code': '0', 'data': processed_data}
            
            return response
        except Exception as e:
            self.logger.error(f"Error fetching positions history: {e}")
            return {}
    
    
    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp to readable date"""
        try:
            if timestamp:
                from datetime import datetime
                dt = datetime.fromtimestamp(int(timestamp) / 1000)
                return dt.strftime('%Y/%m/%d %H:%M:%S')
            return ''
        except:
            return ''
    
    def get_account_bills(self, inst_type: str = "SWAP") -> Dict[str, Any]:
        """Fetch account bills as fallback for position history"""
        try:
            params = {'instType': inst_type, 'limit': '100'}
            return self.account_api.get_account_bills(**params)
        except Exception as e:
            self.logger.error(f"Error fetching account bills: {e}")
            return {}
    
    def get_fills_history(self, inst_type: str = "SWAP", days: int = 7) -> Dict[str, Any]:
        """
        Fetch transaction details for trading statistics
        
        Args:
            inst_type: Instrument type (SWAP for perpetual futures)
            days: Number of days to look back
            
        Returns:
            Fill history data
        """
        try:
            params = {'instType': inst_type, 'limit': '100'}
            return self.trade_api.get_fills_history(**params)
        except Exception as e:
            self.logger.error(f"Error fetching fills history: {e}")
            return {}
    
    def get_trading_statistics(self, inst_type: str = "SWAP", days: int = 7) -> Dict[str, Any]:
        """
        Calculate trading statistics from historical data
        
        Args:
            inst_type: Instrument type 
            days: Number of days to analyze
            
        Returns:
            Trading statistics dictionary
        """
        try:
            # Get historical positions data
            positions_data = self.get_positions_history(inst_type=inst_type, days=days)
            fills_data = self.get_fills_history(inst_type=inst_type, days=days)
            
            stats = {
                'total_positions': 0,
                'profitable_positions': 0,
                'losing_positions': 0,
                'total_pnl': 0.0,
                'total_profit': 0.0,
                'total_loss': 0.0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'avg_pnl': 0.0,
                'profit_loss_ratio': 0.0,
                'max_profit': 0.0,
                'max_loss': 0.0,
                'avg_holding_time': 0.0,
                'total_trades': 0,
                'instruments_traded': set()
            }
            
            # Process positions data
            if positions_data and 'data' in positions_data:
                positions = positions_data['data']
                profits = []
                losses = []
                holding_times = []
                
                
                for pos in positions:
                    try:
                        # Try different field names for PnL
                        pnl = float(pos.get('realizedPnl', pos.get('pnl', pos.get('closePnl', 0))))
                        inst_id = pos.get('instId', '')
                        
                        stats['total_positions'] += 1
                        stats['total_pnl'] += pnl
                        
                        if inst_id:
                            stats['instruments_traded'].add(inst_id)
                        
                        if pnl > 0:
                            stats['profitable_positions'] += 1
                            stats['total_profit'] += pnl
                            profits.append(pnl)
                            stats['max_profit'] = max(stats['max_profit'], pnl)
                        elif pnl < 0:
                            stats['losing_positions'] += 1
                            stats['total_loss'] += abs(pnl)
                            losses.append(abs(pnl))
                            stats['max_loss'] = max(stats['max_loss'], abs(pnl))
                        
                        # Calculate holding time
                        open_time_str = pos.get('openTime', '')
                        close_time_str = pos.get('closeTime', '')
                        if open_time_str and close_time_str:
                            try:
                                # Parse datetime strings
                                open_dt = datetime.strptime(open_time_str, '%Y/%m/%d %H:%M:%S')
                                close_dt = datetime.strptime(close_time_str, '%Y/%m/%d %H:%M:%S')
                                holding_time = (close_dt - open_dt).total_seconds() / 3600  # Hours
                                holding_times.append(holding_time)
                            except:
                                pass
                    except (ValueError, TypeError):
                        continue
                
                # Calculate ratios and averages
                if stats['total_positions'] > 0:
                    stats['win_rate'] = (stats['profitable_positions'] / stats['total_positions']) * 100
                    stats['avg_pnl'] = stats['total_pnl'] / stats['total_positions']
                
                if profits:
                    stats['avg_profit'] = sum(profits) / len(profits)
                
                if losses:
                    stats['avg_loss'] = sum(losses) / len(losses)
                
                if stats['avg_loss'] > 0:
                    stats['profit_loss_ratio'] = stats['avg_profit'] / stats['avg_loss']
                
                if holding_times:
                    stats['avg_holding_time'] = sum(holding_times) / len(holding_times)
            
            # Process fills data for additional statistics
            if fills_data and 'data' in fills_data:
                stats['total_trades'] = len(fills_data['data'])
            
            # Convert set to count
            stats['instruments_traded'] = len(stats['instruments_traded'])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating trading statistics: {e}")
            return {}
    
    def get_instrument_statistics(self, inst_type: str = "SWAP", days: int = 7) -> Dict[str, Any]:
        """
        Calculate per-instrument PnL statistics
        
        Args:
            inst_type: Instrument type
            days: Number of days to analyze
            
        Returns:
            Per-instrument statistics dictionary
        """
        try:
            # Get historical positions data
            positions_data = self.get_positions_history(inst_type=inst_type, days=days)
            
            instrument_stats = {}
            
            if positions_data and 'data' in positions_data:
                positions = positions_data['data']
                
                for pos in positions:
                    try:
                        inst_id = pos.get('instId', '')
                        if not inst_id:
                            continue
                        
                        # Initialize instrument stats if not exists
                        if inst_id not in instrument_stats:
                            instrument_stats[inst_id] = {
                                'total_pnl': 0.0,
                                'long_pnl': 0.0,
                                'short_pnl': 0.0,
                                'total_positions': 0,
                                'long_positions': 0,
                                'short_positions': 0
                            }
                        
                        # Get PnL value
                        pnl = float(pos.get('realizedPnl', pos.get('pnl', pos.get('closePnl', 0))))
                        
                        # Determine position side
                        pos_side = pos.get('posSide', '')
                        # If posSide is not available, try to determine from other fields
                        if not pos_side:
                            # Check if position was opened as buy or sell
                            open_avg_px = float(pos.get('openAvgPx', 0))
                            close_avg_px = float(pos.get('closeAvgPx', 0))
                            if open_avg_px > 0 and close_avg_px > 0:
                                # If close price > open price and PnL > 0, it was a long position
                                # If close price < open price and PnL > 0, it was a short position
                                if (close_avg_px > open_avg_px and pnl > 0) or (close_avg_px < open_avg_px and pnl < 0):
                                    pos_side = 'long'
                                else:
                                    pos_side = 'short'
                        
                        # Update statistics
                        instrument_stats[inst_id]['total_pnl'] += pnl
                        instrument_stats[inst_id]['total_positions'] += 1
                        
                        if pos_side == 'long':
                            instrument_stats[inst_id]['long_pnl'] += pnl
                            instrument_stats[inst_id]['long_positions'] += 1
                        elif pos_side == 'short':
                            instrument_stats[inst_id]['short_pnl'] += pnl
                            instrument_stats[inst_id]['short_positions'] += 1
                        else:
                            # If we can't determine side, add to long by default
                            instrument_stats[inst_id]['long_pnl'] += pnl
                            instrument_stats[inst_id]['long_positions'] += 1
                            
                    except (ValueError, TypeError):
                        continue
            
            return instrument_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating instrument statistics: {e}")
            return {}
    
    def filter_empty_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out empty values from dictionary"""
        if isinstance(data, dict):
            return {k: self.filter_empty_values(v) for k, v in data.items() 
                    if v not in [None, '', ' ', [], {}, 'N/A'] and str(v).strip()}
        elif isinstance(data, list):
            return [self.filter_empty_values(item) for item in data if item]
        else:
            return data
    
    def format_parameter_list(self, data: Dict[str, Any], title: str, filter_usdt_only: bool = False) -> str:
        """Format data as parameter list with descriptions"""
        md_content = f"## {title}\n\n"
        
        if not data or 'data' not in data:
            md_content += "No data available\n\n"
            return md_content
        
        # Parameter descriptions mapping
        param_descriptions = {
            'adjEq': 'Adjusted / Effective equity in USD',
            'imr': 'Initial margin requirement in USD',
            'isoEq': 'Isolated margin equity in USD',
            'mgnRatio': 'Maintenance margin ratio in USD',
            'mmr': 'Maintenance margin requirement in USD',
            'notionalUsd': 'Notional value of positions in USD',
            'ordFrozen': 'Cross margin frozen for pending orders in USD',
            'totalEq': 'The total amount of equity in USD',
            'uTime': 'Update time of account information, millisecond format of Unix timestamp',
            'details': 'Detailed asset information in all currencies',
            'availBal': 'Available balance of currency',
            'availEq': 'Available equity of currency',
            'bal': 'Balance at the account level',
            'ccy': 'Currency',
            'crossLiab': 'Cross liabilities of currency',
            'disEq': 'Discount equity of currency in USD',
            'eq': 'Equity of currency',
            'eqUsd': 'Equity in USD of currency',
            'frozenBal': 'Frozen balance of currency',
            'interest': 'Accrued interest of currency',
            'isoLiab': 'Isolated liabilities of currency',
            'isoUpl': 'Isolated unrealized profit and loss of currency',
            'liab': 'Liabilities of currency',
            'maxLoan': 'Max loan of currency',
            'notionalLever': 'Leverage of currency',
            'rewardBal': 'Reward balance',
            'smtSyncEq': 'Smart sync equity',
            'spotInUseAmt': 'Spot in use amount',
            'stgyEq': 'Strategy equity',
            'twap': 'Risk indicator of auto liability repayment',
            'upl': 'Cross-margin info of unrealized profit and loss at the account level in USD',
            'uplLiab': 'Liabilities due to Unrealized loss of currency',
            'category': 'Account category',
            'acctLv': 'Account level',
            'autoLoan': 'Auto loan enabled',
            'ctIsoMode': 'Contract isolated mode',
            'greeksType': 'Greeks type',
            'level': 'Account level',
            'levelTmp': 'Temporary account level',
            'mgnIsoMode': 'Margin isolated mode',
            'posMode': 'Position mode',
            'spotOffsetType': 'Spot offset type',
            'uid': 'User ID',
            'label': 'Account label',
            'maker': 'Maker fee rate',
            'taker': 'Taker fee rate',
            'delivery': 'Delivery fee rate',
            'exercise': 'Exercise fee rate',
            'instType': 'Instrument type',
            'instId': 'Instrument ID',
            'fundingRate': 'Funding rate',
            'fundingTime': 'Funding time',
            'cashBal': 'Cash balance',
            'accAvgPx': 'Account average price',
            'spotBal': 'Spot balance',
            'spotUpl': 'Spot unrealized PnL',
            'spotUplRatio': 'Spot unrealized PnL ratio',
            'totalPnl': 'Total PnL',
            'totalPnlRatio': 'Total PnL ratio',
            'openAvgPx': 'Open average price',
            'acctStpMode': 'Account STP mode',
            'enableSpotBorrow': 'Enable spot borrow',
            'ip': 'IP address',
            'kycLv': 'KYC level',
            'liquidationGear': 'Liquidation gear',
            'mainUid': 'Main user ID',
            'opAuth': 'Operation authority',
            'perm': 'Permissions',
            'roleType': 'Role type',
            'spotBorrowAutoRepay': 'Spot borrow auto repay',
            'spotRoleType': 'Spot role type',
            'spotTraderInsts': 'Spot trader instruments',
            'traderInsts': 'Trader instruments',
            'type': 'Type',
            'fiat': 'Fiat currency',
            'makerU': 'Maker fee rate (USDT)',
            'takerU': 'Taker fee rate (USDT)',
            'makerUSDC': 'Maker fee rate (USDC)',
            'takerUSDC': 'Taker fee rate (USDC)',
            'ruleType': 'Rule type',
            'ts': 'Timestamp',
        }
        
        def format_item(key: str, value: Any, indent: int = 0) -> str:
            """Format a single item with description"""
            if value in [None, '', ' ', [], {}, 'N/A'] or (isinstance(value, str) and not value.strip()):
                return ""
            
            spaces = "  " * indent
            description = param_descriptions.get(key, "")
            desc_text = f" - {description}" if description else ""
            
            if isinstance(value, dict):
                filtered_value = self.filter_empty_values(value)
                if not filtered_value:
                    return ""
                result = f"{spaces}- **{key}**{desc_text}:\n"
                for sub_key, sub_value in filtered_value.items():
                    sub_result = format_item(sub_key, sub_value, indent + 1)
                    if sub_result:
                        result += sub_result
                return result
            elif isinstance(value, list):
                filtered_value = self.filter_empty_values(value)
                if not filtered_value:
                    return ""
                result = f"{spaces}- **{key}**{desc_text}:\n"
                for i, item in enumerate(filtered_value):
                    if isinstance(item, dict):
                        result += f"{spaces}  - Item {i + 1}:\n"
                        for sub_key, sub_value in item.items():
                            sub_result = format_item(sub_key, sub_value, indent + 2)
                            if sub_result:
                                result += sub_result
                    else:
                        result += f"{spaces}  - {item}\n"
                return result
            else:
                return f"{spaces}- **{key}** = {value}{desc_text}\n"
        
        # Format the main data
        main_data = data.get('data', [])
        
        # Check if we should convert to table format
        if isinstance(main_data, list) and len(main_data) > 0:
            # For account balance with details, extract USDT info
            if 'details' in main_data[0] and filter_usdt_only:
                details = main_data[0].get('details', [])
                usdt_details = [d for d in details if d.get('ccy') == 'USDT']
                if usdt_details:
                    # Show USDT details
                    for detail in usdt_details:
                        filtered_detail = self.filter_empty_values(detail)
                        for key, value in filtered_detail.items():
                            result = format_item(key, value)
                            if result:
                                md_content += result
                    md_content += "\n"
            else:
                # Normal list processing
                for i, item in enumerate(main_data):
                    if isinstance(item, dict):
                        filtered_item = self.filter_empty_values(item)
                        if filtered_item:
                            if len(main_data) > 1:
                                md_content += f"### Record {i + 1}\n\n"
                            for key, value in filtered_item.items():
                                result = format_item(key, value)
                                if result:
                                    md_content += result
                            md_content += "\n"
        elif isinstance(main_data, dict):
            filtered_data = self.filter_empty_values(main_data)
            for key, value in filtered_data.items():
                result = format_item(key, value)
                if result:
                    md_content += result
        
        return md_content + "\n"
    
    
    def format_table(self, data: Dict[str, Any], title: str, headers: List[str]) -> str:
        """Format data as AI-friendly table with clean headers"""
        md_content = f"## {title}\n\n"
        
        if not data or 'data' not in data or not data['data']:
            md_content += "No data available\n\n"
            return md_content
        
        # Parameter descriptions for AI (English only, no HTML)
        param_descriptions = {
            'instId': 'Instrument ID',
            'pos': 'Position Size',
            'markPx': 'Mark Price',
            'avgPx': 'Average Price',
            'liqPx': 'Liquidation Price',
            'bePx': 'Break-even Price',
            'upl': 'Unrealized PnL',
            'mgnRatio': 'Margin Ratio',
            'imr': 'Initial Margin',
            'lever': 'Leverage',
            'tpTriggerPx': 'Take Profit Price',
            'slTriggerPx': 'Stop Loss Price',
            'posStatus': 'Position Status',
            'openAvgPx': 'Open Average Price',
            'closeAvgPx': 'Close Average Price',
            'realizedPnl': 'Realized PnL',
            'pnlRatio': 'PnL Ratio',
            'maxPos': 'Max Position Size',
            'closedPos': 'Closed Position Size',
            'openTime': 'Open Time',
            'closeTime': 'Close Time',
        }
        
        # Create clean table header
        header_with_desc = []
        for header in headers:
            desc = param_descriptions.get(header, header)
            header_with_desc.append(f"{header} ({desc})")
        
        # Build table
        md_content += "| " + " | ".join(header_with_desc) + " |\n"
        md_content += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        main_data = data.get('data', [])
        if isinstance(main_data, list):
            for item in main_data:
                if isinstance(item, dict):
                    row = []
                    for header in headers:
                        value = item.get(header, "")
                        
                        # TP/SL data is now directly available in position data
                        
                        if not value or str(value).strip() == "":
                            value = "N/A"
                        elif isinstance(value, (dict, list)):
                            value = "N/A"
                        
                        row.append(str(value))
                    md_content += "| " + " | ".join(row) + " |\n"
        
        return md_content + "\n"
    
    def format_trading_statistics(self, stats: Dict[str, Any]) -> str:
        """Format trading statistics as markdown"""
        md_content = "## Trading Performance Analysis (Past 7 Days)\n\n"
        
        if not stats:
            md_content += "No trading statistics available\n\n"
            return md_content
        
        # Overall Performance Summary
        md_content += "### Overall Performance Summary\n\n"
        md_content += f"- **Total Positions**: {stats.get('total_positions', 0)}\n"
        md_content += f"- **Total PnL**: {stats.get('total_pnl', 0.0):.2f} USDT\n"
        md_content += f"- **Total Profit**: {stats.get('total_profit', 0.0):.2f} USDT\n"
        md_content += f"- **Total Loss**: {stats.get('total_loss', 0.0):.2f} USDT\n"
        md_content += f"- **Instruments Traded**: {stats.get('instruments_traded', 0)}\n"
        md_content += f"- **Total Trades**: {stats.get('total_trades', 0)}\n\n"
        
        # Win/Loss Analysis
        md_content += "### Win/Loss Analysis\n\n"
        md_content += f"- **Profitable Positions**: {stats.get('profitable_positions', 0)}\n"
        md_content += f"- **Losing Positions**: {stats.get('losing_positions', 0)}\n"
        md_content += f"- **Win Rate**: {stats.get('win_rate', 0.0):.2f}%\n"
        md_content += f"- **Loss Rate**: {100 - stats.get('win_rate', 0.0):.2f}%\n\n"
        
        # Average Performance
        md_content += "### Average Performance\n\n"
        md_content += f"- **Average PnL**: {stats.get('avg_pnl', 0.0):.2f} USDT\n"
        md_content += f"- **Average Profit**: {stats.get('avg_profit', 0.0):.2f} USDT\n"
        md_content += f"- **Average Loss**: {stats.get('avg_loss', 0.0):.2f} USDT\n"
        md_content += f"- **Profit/Loss Ratio**: {stats.get('profit_loss_ratio', 0.0):.2f}\n"
        md_content += f"- **Average Holding Time**: {stats.get('avg_holding_time', 0.0):.2f} hours\n\n"
        
        # Risk Metrics
        md_content += "### Risk Metrics\n\n"
        md_content += f"- **Maximum Single Profit**: {stats.get('max_profit', 0.0):.2f} USDT\n"
        md_content += f"- **Maximum Single Loss**: {stats.get('max_loss', 0.0):.2f} USDT\n"
        
        # Add interpretation based on statistics
        md_content += "### Performance Interpretation\n\n"
        win_rate = stats.get('win_rate', 0.0)
        profit_loss_ratio = stats.get('profit_loss_ratio', 0.0)
        
        if win_rate > 50:
            md_content += f"- **Positive Win Rate**: {win_rate:.1f}% win rate indicates good trade selection\n"
        elif win_rate > 0:
            md_content += f"- **Below Average Win Rate**: {win_rate:.1f}% win rate suggests room for improvement\n"
        
        if profit_loss_ratio > 1:
            md_content += f"- **Favorable Risk/Reward**: {profit_loss_ratio:.2f} ratio means average profits exceed average losses\n"
        elif profit_loss_ratio > 0:
            md_content += f"- **Suboptimal Risk/Reward**: {profit_loss_ratio:.2f} ratio indicates larger average losses than profits\n"
        
        total_pnl = stats.get('total_pnl', 0.0)
        if total_pnl > 0:
            md_content += f"- **Profitable Period**: Overall positive PnL of {total_pnl:.2f} USDT\n"
        else:
            md_content += f"- **Loss Period**: Overall negative PnL of {total_pnl:.2f} USDT\n"
        
        md_content += "\n"
        return md_content
    
    def format_instrument_statistics(self, inst_stats: Dict[str, Any]) -> str:
        """Format per-instrument statistics as markdown"""
        md_content = "## Per-Instrument PnL Analysis\n\n"
        
        if not inst_stats:
            md_content += "No instrument statistics available\n\n"
            return md_content
        
        # Sort instruments by total PnL (descending)
        sorted_instruments = sorted(inst_stats.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
        
        # Create table header
        md_content += "| Instrument | Total PnL | Long PnL | Short PnL | Total Positions |\n"
        md_content += "| --- | --- | --- | --- | --- |\n"
        
        for inst_id, stats in sorted_instruments:
            total_pnl = stats['total_pnl']
            long_pnl = stats['long_pnl']
            short_pnl = stats['short_pnl']
            total_positions = stats['total_positions']
            
            # Format PnL values with color indication
            total_pnl_str = f"{total_pnl:+.2f} USDT"
            long_pnl_str = f"{long_pnl:+.2f} USDT"
            short_pnl_str = f"{short_pnl:+.2f} USDT"
            
            md_content += f"| {inst_id} | {total_pnl_str} | {long_pnl_str} | {short_pnl_str} | {total_positions} |\n"
        
        # Add summary statistics
        md_content += "\n### Instrument Performance Summary\n\n"
        
        # Find best and worst performing instruments
        if sorted_instruments:
            best_inst = sorted_instruments[0]
            worst_inst = sorted_instruments[-1]
            
            if best_inst[1]['total_pnl'] > 0:
                md_content += f"- **Best Performing**: {best_inst[0]} ({best_inst[1]['total_pnl']:+.2f} USDT)\n"
            
            if worst_inst[1]['total_pnl'] < 0:
                md_content += f"- **Worst Performing**: {worst_inst[0]} ({worst_inst[1]['total_pnl']:+.2f} USDT)\n"
            
            # Count profitable vs unprofitable instruments
            profitable_instruments = sum(1 for _, stats in sorted_instruments if stats['total_pnl'] > 0)
            unprofitable_instruments = sum(1 for _, stats in sorted_instruments if stats['total_pnl'] < 0)
            
            md_content += f"- **Profitable Instruments**: {profitable_instruments}\n"
            md_content += f"- **Unprofitable Instruments**: {unprofitable_instruments}\n"
            
            # Calculate long vs short performance
            total_long_pnl = sum(stats['long_pnl'] for _, stats in sorted_instruments)
            total_short_pnl = sum(stats['short_pnl'] for _, stats in sorted_instruments)
            
            md_content += f"- **Total Long PnL**: {total_long_pnl:+.2f} USDT\n"
            md_content += f"- **Total Short PnL**: {total_short_pnl:+.2f} USDT\n"
        
        md_content += "\n"
        return md_content

    def generate_report(self, output_file: str = "okx_account.md") -> None:
        """Generate AI-friendly MD report"""
        try:
            md_content = f"# OKX Account Report\n\n"
            md_content += f"Generated on: {get_okx_current_time()}\n\n"
            
            # Account Balance and USDT Information
            self.logger.info("Fetching account balance...")
            balance_data = self.get_account_balance(ccy="USDT")
            md_content += self.format_parameter_list(balance_data, "Account Balance and USDT Asset Information", filter_usdt_only=True)
            
            # SWAP Fee Information
            self.logger.info("Fetching trade fees...")
            fee_data = self.get_trade_fee()
            md_content += self.format_parameter_list(fee_data, "SWAP Fee Information")
            
            # Current SWAP Positions
            self.logger.info("Fetching current positions...")
            positions_data = self.get_positions()
            position_headers = ['instId', 'pos', 'markPx', 'avgPx', 'liqPx', 'bePx', 'upl', 'mgnRatio', 'imr', 'lever', 'tpTriggerPx', 'slTriggerPx']
            md_content += self.format_table(positions_data, "Current SWAP Positions", position_headers)
            
            # Trading Performance Analysis (replaced historical positions table)
            self.logger.info("Calculating trading statistics...")
            trading_stats = self.get_trading_statistics()
            md_content += self.format_trading_statistics(trading_stats)
            
            # Per-Instrument PnL Analysis
            self.logger.info("Calculating per-instrument statistics...")
            instrument_stats = self.get_instrument_statistics()
            md_content += self.format_instrument_statistics(instrument_stats)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            self.logger.info(f"Report generated successfully: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise


def main():
    """Main function to run the OKX reporter"""
    reporter = OKXReporter()
    reporter.generate_report()
    print("OKX report generated: okx_account.md")


if __name__ == "__main__":
    main()