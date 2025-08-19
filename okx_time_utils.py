#!/usr/bin/env python3
"""
OKX Time Utilities - Centralized time handling for all modules

This module provides unified time handling using OKX's official system time API
as recommended in the documentation. All modules should use this for time consistency.
"""

import requests
import time
from datetime import datetime, timezone
from typing import Optional


class OKXTimeUtils:
    """Unified OKX time handling utilities"""
    
    def __init__(self):
        self.okx_time_url = "https://www.okx.com/api/v5/public/time"
        self._cached_offset = 0.0  # Offset between local and OKX server time
        self._last_sync_time = 0
        self._sync_interval = 300  # Re-sync every 5 minutes
    
    def sync_with_okx_server(self) -> bool:
        """
        Synchronize local time with OKX server time
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            local_time_before = time.time()
            
            response = requests.get(self.okx_time_url, timeout=10)
            response.raise_for_status()
            
            local_time_after = time.time()
            network_delay = (local_time_after - local_time_before) / 2
            
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                server_timestamp_ms = int(data['data'][0]['ts'])
                server_time = server_timestamp_ms / 1000.0
                
                # Calculate offset accounting for network delay
                local_time_mid = local_time_before + network_delay
                self._cached_offset = server_time - local_time_mid
                self._last_sync_time = local_time_after
                
                print(f"Time sync successful. Offset: {self._cached_offset:.3f}s")
                return True
            else:
                print(f"OKX time API error: {data}")
                return False
                
        except Exception as e:
            print(f"Failed to sync with OKX server time: {e}")
            return False
    
    def get_okx_timestamp_ms(self) -> int:
        """
        Get current OKX server timestamp in milliseconds
        
        Returns:
            OKX server timestamp in milliseconds
        """
        # Auto-sync if needed
        if time.time() - self._last_sync_time > self._sync_interval:
            self.sync_with_okx_server()
        
        # Return adjusted time
        local_time = time.time()
        okx_time = local_time + self._cached_offset
        return int(okx_time * 1000)
    
    def get_okx_timestamp_seconds(self) -> float:
        """
        Get current OKX server timestamp in seconds (float)
        
        Returns:
            OKX server timestamp in seconds
        """
        return self.get_okx_timestamp_ms() / 1000.0
    
    def get_okx_datetime_utc(self) -> datetime:
        """
        Get current OKX server time as UTC datetime object
        
        Returns:
            OKX server time as UTC datetime
        """
        timestamp = self.get_okx_timestamp_seconds()
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    def get_okx_time_string(self, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
        """
        Get current OKX server time as formatted string
        
        Args:
            format_str: Time format string (default: "%Y-%m-%d %H:%M:%S UTC")
            
        Returns:
            Formatted OKX server time string
        """
        dt = self.get_okx_datetime_utc()
        return dt.strftime(format_str)
    
    def get_okx_iso_string(self) -> str:
        """
        Get current OKX server time in ISO format
        
        Returns:
            OKX server time in ISO format (e.g., "2025-08-08T00:15:30.123Z")
        """
        dt = self.get_okx_datetime_utc()
        return dt.isoformat().replace('+00:00', 'Z')
    
    def format_timestamp(self, timestamp_ms: int) -> str:
        """
        Format a timestamp (in milliseconds) to readable string
        
        Args:
            timestamp_ms: Timestamp in milliseconds
            
        Returns:
            Formatted time string in UTC
        """
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


# Global instance for easy access
okx_time = OKXTimeUtils()

def get_okx_current_time() -> str:
    """
    Convenience function to get current OKX server time string
    
    Returns:
        Current OKX server time in standard format
    """
    return okx_time.get_okx_time_string()

def get_okx_timestamp() -> int:
    """
    Convenience function to get current OKX server timestamp in milliseconds
    
    Returns:
        Current OKX server timestamp in milliseconds
    """
    return okx_time.get_okx_timestamp_ms()

def get_okx_iso_time() -> str:
    """
    Convenience function to get current OKX server time in ISO format
    
    Returns:
        Current OKX server time in ISO format
    """
    return okx_time.get_okx_iso_string()


if __name__ == "__main__":
    # Test the time utilities
    print("Testing OKX Time Utilities:")
    print("=" * 50)
    
    # Initialize and sync
    okx_time.sync_with_okx_server()
    
    # Test all time formats
    print(f"Current OKX time: {get_okx_current_time()}")
    print(f"ISO format: {get_okx_iso_time()}")
    print(f"Timestamp (ms): {get_okx_timestamp()}")
    print(f"Timestamp (s): {okx_time.get_okx_timestamp_seconds()}")
    
    # Test formatting
    test_ts = 1704876947000  # Example timestamp
    print(f"Formatted example timestamp: {okx_time.format_timestamp(test_ts)}")