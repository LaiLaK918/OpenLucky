#!/usr/bin/env python3
"""
OKX Historical Positions Report Generator

This script fetches all historical position data from OKX API and generates
a comprehensive history.md report in table format matching the official website.
"""

import os
import json
import configparser
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from decimal import Decimal, getcontext

import okx.Account as Account


# Set decimal precision for financial calculations
getcontext().prec = 10

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OKXHistoryGenerator:
    """OKX Historical Positions Report Generator"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize with OKX API configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Get OKX API credentials
        self.api_key = self.config.get('OKX', 'api_key')
        self.api_secret = self.config.get('OKX', 'api_secret')
        self.passphrase = self.config.get('OKX', 'api_passphrase')
        
        # Initialize OKX Account API
        self.account_api = Account.AccountAPI(
            api_key=self.api_key,
            api_secret_key=self.api_secret,
            passphrase=self.passphrase,
            use_server_time=False,
            flag='0'  # Live trading
        )
        
        logger.info("OKX History Generator initialized")

    def fetch_positions_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all historical positions data from OKX API
        
        Args:
            limit: Number of records per request (max 100)
            
        Returns:
            List of historical position records
        """
        all_positions = []
        after = None
        page_count = 0
        
        try:
            while True:
                page_count += 1
                logger.info(f"Fetching positions history page {page_count}...")
                
                # Prepare parameters
                params = {
                    'instType': 'SWAP',  # Focus on perpetual swaps
                    'limit': str(limit)
                }
                
                if after:
                    params['after'] = after
                
                # Make API request
                response = self.account_api.get_positions_history(**params)
                
                if response['code'] != '0':
                    logger.error(f"API Error: {response['msg']}")
                    break
                
                positions = response.get('data', [])
                
                if not positions:
                    logger.info("No more positions data available")
                    break
                
                all_positions.extend(positions)
                logger.info(f"Retrieved {len(positions)} positions from page {page_count}")
                
                # Set pagination parameter for next request
                after = positions[-1].get('uTime')
                
                # Break if we got less than the limit (last page)
                if len(positions) < limit:
                    break
                    
        except Exception as e:
            logger.error(f"Error fetching positions history: {e}")
            
        logger.info(f"Total positions retrieved: {len(all_positions)}")
        return all_positions

    def format_timestamp(self, timestamp: str) -> str:
        """
        Format timestamp to readable date format
        
        Args:
            timestamp: Unix timestamp in milliseconds
            
        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)
            return dt.strftime('%Y/%m/%d %H:%M:%S')
        except (ValueError, TypeError):
            return "N/A"

    def format_price(self, price: str) -> str:
        """
        Format price with appropriate decimal places
        
        Args:
            price: Price as string
            
        Returns:
            Formatted price string
        """
        try:
            if not price or price == '':
                return "N/A"
            
            decimal_price = Decimal(price)
            # Format with up to 6 decimal places, removing trailing zeros
            formatted = f"{decimal_price:.6f}".rstrip('0').rstrip('.')
            return formatted
        except (ValueError, TypeError):
            return "N/A"

    def format_pnl(self, pnl: str, pnl_ratio: str) -> tuple:
        """
        Format PnL and PnL ratio with color indicators
        
        Args:
            pnl: PnL amount as string
            pnl_ratio: PnL ratio as string
            
        Returns:
            Tuple of (formatted_pnl, formatted_ratio, is_positive)
        """
        try:
            if not pnl or pnl == '':
                return "N/A", "N/A", None
                
            pnl_decimal = Decimal(pnl)
            is_positive = pnl_decimal > 0
            
            # Format PnL amount
            formatted_pnl = f"{'+' if is_positive else ''}{pnl_decimal:.4f} USDT"
            
            # Format PnL ratio as percentage
            if pnl_ratio and pnl_ratio != '':
                ratio_decimal = Decimal(pnl_ratio) * 100
                formatted_ratio = f"{'+' if is_positive else ''}{ratio_decimal:.2f}%"
            else:
                formatted_ratio = "N/A"
                
            return formatted_pnl, formatted_ratio, is_positive
            
        except (ValueError, TypeError):
            return "N/A", "N/A", None

    def format_position_size(self, size: str, inst_id: str) -> str:
        """
        Format position size with currency
        
        Args:
            size: Position size as string
            inst_id: Instrument ID to extract currency
            
        Returns:
            Formatted position size string
        """
        try:
            if not size or size == '':
                return "N/A"
                
            # Extract base currency from instrument ID (e.g., BTC from BTC-USDT-SWAP)
            currency = inst_id.split('-')[0] if inst_id else ""
            formatted_size = f"{Decimal(size):,.0f} {currency}"
            return formatted_size
            
        except (ValueError, TypeError):
            return "N/A"

    def generate_markdown_report(self, positions: List[Dict[str, Any]]) -> str:
        """
        Generate markdown table report from positions data
        
        Args:
            positions: List of position records
            
        Returns:
            Markdown formatted report string
        """
        if not positions:
            return "# Historical Position Report\n\nNo historical position data available.\n"
        
        # Sort positions by close time (most recent first)
        sorted_positions = sorted(
            positions,
            key=lambda x: int(x.get('uTime', '0')),
            reverse=True
        )
        
        # Generate markdown content
        markdown_lines = [
            "# Historical Position Report",
            "",
            f"**Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Positions**: {len(positions)}",
            "",
            "## Position Details",
            "",
            "| Trading Pair | Position Status | Open Avg Price | Close Avg Price | Realized PnL | Realized PnL Ratio | Max Position Size | Closed Size | Open Time | Close Time |",
            "|-------------|-----------------|---------------|-----------------|-------------|-------------------|------------------|-------------|-----------|------------|"
        ]
        
        for position in sorted_positions:
            # Extract and format data
            inst_id = position.get('instId', 'N/A').replace('-USDT-SWAP', 'USDT Perpetual')
            lever = position.get('lever', 'N/A')
            if lever != 'N/A':
                inst_id += f"\n{lever}x"
            
            pos_status = "Fully Closed"  # All historical positions are closed
            
            open_price = self.format_price(position.get('openAvgPx', ''))
            close_price = self.format_price(position.get('closeAvgPx', ''))
            
            pnl_formatted, ratio_formatted, is_positive = self.format_pnl(
                position.get('pnl', ''),
                position.get('pnlRatio', '')
            )
            
            # Add color indicators using emoji for markdown
            if is_positive is True:
                pnl_formatted = f"🟢 {pnl_formatted}"
                ratio_formatted = f"🟢 {ratio_formatted}"
            elif is_positive is False:
                pnl_formatted = f"🔴 {pnl_formatted}"
                ratio_formatted = f"🔴 {ratio_formatted}"
            
            max_pos = self.format_position_size(
                position.get('openMaxPos', ''),
                position.get('instId', '')
            )
            
            closed_pos = self.format_position_size(
                position.get('closeTotalPos', ''),
                position.get('instId', '')
            )
            
            open_time = self.format_timestamp(position.get('cTime', ''))
            close_time = self.format_timestamp(position.get('uTime', ''))
            
            # Add table row
            row = f"| {inst_id} | {pos_status} | {open_price} | {close_price} | {pnl_formatted} | {ratio_formatted} | {max_pos} | {closed_pos} | {open_time} | {close_time} |"
            markdown_lines.append(row)
        
        # Add summary statistics
        total_pnl = sum(Decimal(pos.get('pnl', '0')) for pos in positions if pos.get('pnl'))
        profitable_positions = len([pos for pos in positions if Decimal(pos.get('pnl', '0')) > 0])
        win_rate = (profitable_positions / len(positions) * 100) if positions else 0
        
        markdown_lines.extend([
            "",
            "## Statistical Summary",
            "",
            f"- **Total Realized PnL**: {'+' if total_pnl > 0 else ''}{total_pnl:.4f} USDT",
            f"- **Profitable Positions**: {profitable_positions}",
            f"- **Loss Positions**: {len(positions) - profitable_positions}",
            f"- **Win Rate**: {win_rate:.2f}%",
            "",
            "---",
            "",
            "*Report generated automatically by OKX API*"
        ])
        
        return "\n".join(markdown_lines)

    def save_report(self, content: str, filename: str = "history.md"):
        """
        Save report content to markdown file
        
        Args:
            content: Markdown content to save
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def generate_report(self):
        """
        Main method to generate complete historical positions report
        """
        try:
            logger.info("Starting historical positions report generation...")
            
            # Fetch positions history
            positions = self.fetch_positions_history()
            
            if not positions:
                logger.warning("No historical positions data found")
                return
            
            # Generate markdown report
            markdown_content = self.generate_markdown_report(positions)
            
            # Save report
            self.save_report(markdown_content)
            
            logger.info("Historical positions report generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise


def main():
    """Main execution function"""
    try:
        generator = OKXHistoryGenerator()
        generator.generate_report()
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())