#!/usr/bin/env python3
"""
Main Trading Bot Orchestrator
Combines all modules to execute complete trading workflow at configurable intervals
"""

import os
import sys
import time
import logging
import configparser
import subprocess
from datetime import datetime, timedelta
import signal
import threading
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TradingBotOrchestrator:
    """Main orchestrator for automated trading workflow"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize the trading bot orchestrator"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Get execution interval from config
        self.interval_minutes = self.config.getint('EXECUTION', 'interval_minutes', fallback=15)
        self.interval_seconds = self.interval_minutes * 60
        
        self.running = False
        self.execution_thread = None
        self.last_execution_time = None
        self.execution_count = 0
        
        logger.info(f"Trading Bot initialized with {self.interval_minutes} minute interval")
        
    def execute_module(self, module_name: str, description: str) -> bool:
        """
        Execute a Python module and handle errors
        
        Args:
            module_name: Name of the Python file to execute
            description: Description of the module for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Executing {description}...")
            start_time = time.time()
            
            # Run the module as a subprocess
            result = subprocess.run(
                [sys.executable, module_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✓ {description} completed successfully in {execution_time:.2f}s")
                if result.stdout:
                    logger.debug(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"✗ {description} failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {description} timed out after 10 minutes")
            return False
        except Exception as e:
            logger.error(f"✗ {description} failed with exception: {e}")
            return False
    
    def execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        cycle_start_time = time.time()
        self.execution_count += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting Trading Cycle #{self.execution_count}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Generate account report
            success = self.execute_module(
                "okx_account.py",
                "Account Report Generation (okx_account.md)"
            )
            if not success:
                logger.error("Account report generation failed, skipping this cycle")
                return
            
            # Step 2: Generate market report
            success = self.execute_module(
                "okx_market.py",
                "Market Analysis Report (okx_market.md)"
            )
            if not success:
                logger.error("Market report generation failed, skipping this cycle")
                return
            
            # Step 3: AI analysis and decision making
            success = self.execute_module(
                "ai_analyze.py",
                "AI Trading Decision Analysis (decision.json)"
            )
            if not success:
                logger.error("AI analysis failed, skipping this cycle")
                return
            
            # Step 4: Execute trading decisions
            # Check if decision.json exists and has valid trades/closures
            try:
                import json
                with open('decision.json', 'r') as f:
                    decision = json.load(f)
                
                has_actions = bool(decision.get('trades') or decision.get('closures'))
                
                if has_actions:
                    logger.info("Trading actions found in decision.json")
                    success = self.execute_module(
                        "okx_execute.py",
                        "Trade Execution"
                    )
                    if success:
                        logger.info("✓ Trading actions executed successfully")
                    else:
                        logger.error("✗ Trade execution failed")
                else:
                    logger.info("No trading actions recommended by AI")
                    
            except Exception as e:
                logger.error(f"Error processing decision.json: {e}")
            
            # Calculate cycle execution time
            cycle_time = time.time() - cycle_start_time
            logger.info(f"\n✓ Trading Cycle #{self.execution_count} completed in {cycle_time:.2f}s")
            
            # Log next execution time
            next_execution = datetime.now() + timedelta(seconds=self.interval_seconds)
            logger.info(f"Next execution scheduled at: {next_execution.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Unexpected error in trading cycle: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def run_continuous(self):
        """Run the trading bot continuously"""
        self.running = True
        
        logger.info(f"\n{'*'*60}")
        logger.info("Trading Bot Started")
        logger.info(f"Execution interval: {self.interval_minutes} minutes")
        logger.info(f"Press Ctrl+C to stop")
        logger.info(f"{'*'*60}\n")
        
        # Execute first cycle immediately
        self.execute_trading_cycle()
        self.last_execution_time = time.time()
        
        # Continue with scheduled executions
        while self.running:
            try:
                # Calculate time until next execution
                elapsed = time.time() - self.last_execution_time
                time_to_wait = self.interval_seconds - elapsed
                
                if time_to_wait > 0:
                    # Show countdown every 30 seconds
                    while time_to_wait > 0 and self.running:
                        if int(time_to_wait) % 30 == 0 and int(time_to_wait) > 0:
                            minutes_left = int(time_to_wait / 60)
                            seconds_left = int(time_to_wait % 60)
                            logger.info(f"Next execution in {minutes_left}m {seconds_left}s")
                        
                        time.sleep(min(1, time_to_wait))
                        time_to_wait -= 1
                
                if self.running:
                    self.execute_trading_cycle()
                    self.last_execution_time = time.time()
                    
            except KeyboardInterrupt:
                logger.info("\nReceived interrupt signal, shutting down...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run_once(self):
        """Execute one trading cycle and exit"""
        logger.info("Executing single trading cycle...")
        self.execute_trading_cycle()
        logger.info("Single cycle execution completed")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        logger.info("Trading Bot stopped")
        
        # Log summary statistics
        if self.execution_count > 0:
            logger.info(f"\nExecution Summary:")
            logger.info(f"Total cycles executed: {self.execution_count}")
            logger.info(f"Bot stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    logger.info("\nReceived interrupt signal, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='OKX Trading Bot Orchestrator')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Execute one cycle and exit (default: run continuously)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        help='Override interval minutes from config.ini'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    args = parser.parse_args()
    
    # Create and configure orchestrator
    orchestrator = TradingBotOrchestrator(config_path=args.config)
    
    # Override interval if specified
    if args.interval:
        orchestrator.interval_minutes = args.interval
        orchestrator.interval_seconds = args.interval * 60
        logger.info(f"Overriding interval to {args.interval} minutes")
    
    # Run the bot
    try:
        if args.once:
            orchestrator.run_once()
        else:
            orchestrator.run_continuous()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()