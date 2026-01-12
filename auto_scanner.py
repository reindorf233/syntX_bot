import asyncio
import logging
from datetime import datetime
from telegram_bot import telegram_bot
from signal_generator import signal_generator
from database import db_manager
from config import config

class AutoScanner:
    def __init__(self):
        self.running = False
        self.scan_task = None
        self.last_scan_time = None
        self.broadcasted_signals = set()  # Track broadcasted signals to avoid duplicates
    
    async def start_scanner(self):
        """Start the auto-scanner background task"""
        if self.running:
            logging.warning("Auto-scanner is already running")
            return
        
        self.running = True
        self.scan_task = asyncio.create_task(self.scanner_loop())
        logging.info("Auto-scanner started")
    
    async def stop_scanner(self):
        """Stop the auto-scanner"""
        self.running = False
        if self.scan_task:
            self.scan_task.cancel()
            try:
                await self.scan_task
            except asyncio.CancelledError:
                pass
        logging.info("Auto-scanner stopped")
    
    async def scanner_loop(self):
        """Main scanner loop"""
        while self.running:
            try:
                await self.perform_scan()
                await asyncio.sleep(config.scan_interval_minutes * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in scanner loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def perform_scan(self):
        """Perform a single scan of all symbols"""
        try:
            logging.info("Starting auto-scan...")
            scan_start = datetime.now()
            
            # Get all signals
            all_signals = signal_generator.scan_all_symbols()
            
            if not all_signals:
                logging.info("No signals found in auto-scan")
                return
            
            # Filter for very strong signals (9-10/10) for broadcasting
            very_strong_signals = {
                symbol: signal for symbol, signal in all_signals.items()
                if signal['strength'] >= 9.0
            }
            
            # Filter for strong signals (7-8/10) for logging
            strong_signals = {
                symbol: signal for symbol, signal in all_signals.items()
                if 7.0 <= signal['strength'] < 9.0
            }
            
            # Broadcast very strong signals
            if very_strong_signals:
                await self.broadcast_signals(very_strong_signals)
            
            # Log scan results
            total_signals = len(all_signals)
            very_strong_count = len(very_strong_signals)
            strong_count = len(strong_signals)
            
            scan_duration = (datetime.now() - scan_start).total_seconds()
            
            logging.info(f"Auto-scan completed in {scan_duration:.2f}s: "
                        f"{total_signals} total signals, "
                        f"{very_strong_count} very strong, "
                        f"{strong_count} strong")
            
            # Update last scan time
            self.last_scan_time = datetime.now()
            
            # Clean up old broadcasted signals (older than 1 hour)
            await self.cleanup_broadcasted_signals()
            
        except Exception as e:
            logging.error(f"Error performing auto-scan: {e}")
    
    async def broadcast_signals(self, signals: dict):
        """Broadcast signals to public channel"""
        try:
            for symbol, signal in signals.items():
                # Create unique signal identifier
                signal_id = f"{symbol}_{signal['direction']}_{signal['strength']:.1f}_{signal['timestamp'].strftime('%Y%m%d_%H%M')}"
                
                # Check if already broadcasted
                if signal_id in self.broadcasted_signals:
                    logging.debug(f"Signal {signal_id} already broadcasted, skipping")
                    continue
                
                # Format message
                message = f"🚀 *AUTO ALERT - {signal['strength']}/10 SIGNAL*\n\n"
                message += signal_generator.format_signal_message(signal)
                
                # Add auto-scan disclaimer
                message += f"\n\n🤖 *This is an automated alert. Always do your own analysis.*"
                
                # Broadcast to channel
                await telegram_bot.broadcast_to_channel(message)
                
                # Mark as broadcasted
                self.broadcasted_signals.add(signal_id)
                
                # Save to database
                db_manager.save_signal(signal)
                
                logging.info(f"Broadcasted signal: {symbol} {signal['direction']} {signal['strength']}/10")
                
                # Small delay between broadcasts to avoid spam
                await asyncio.sleep(2)
                
        except Exception as e:
            logging.error(f"Error broadcasting signals: {e}")
    
    async def cleanup_broadcasted_signals(self):
        """Clean up old broadcasted signal IDs"""
        try:
            # Keep only recent signals (last hour)
            current_time = datetime.now()
            signals_to_remove = []
            
            for signal_id in self.broadcasted_signals:
                # Extract timestamp from signal_id
                try:
                    timestamp_str = signal_id.split('_')[-2] + '_' + signal_id.split('_')[-1]
                    signal_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M')
                    
                    # Remove if older than 1 hour
                    if (current_time - signal_time).total_seconds() > 3600:
                        signals_to_remove.append(signal_id)
                except:
                    # If we can't parse timestamp, remove it
                    signals_to_remove.append(signal_id)
            
            for signal_id in signals_to_remove:
                self.broadcasted_signals.discard(signal_id)
            
            if signals_to_remove:
                logging.info(f"Cleaned up {len(signals_to_remove)} old broadcasted signal IDs")
                
        except Exception as e:
            logging.error(f"Error cleaning up broadcasted signals: {e}")
    
    def get_scanner_status(self) -> dict:
        """Get current scanner status"""
        return {
            'running': self.running,
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'scan_interval_minutes': config.scan_interval_minutes,
            'broadcasted_signals_count': len(self.broadcasted_signals),
            'signal_threshold': config.signal_strength_threshold
        }
    
    async def force_scan(self):
        """Force an immediate scan"""
        logging.info("Force scan triggered")
        await self.perform_scan()

class ScheduledTasks:
    def __init__(self):
        self.tasks_running = False
        self.maintenance_task = None
    
    async def start_tasks(self):
        """Start scheduled maintenance tasks"""
        if self.tasks_running:
            return
        
        self.tasks_running = True
        self.maintenance_task = asyncio.create_task(self.maintenance_loop())
        logging.info("Scheduled tasks started")
    
    async def stop_tasks(self):
        """Stop scheduled tasks"""
        self.tasks_running = False
        if self.maintenance_task:
            self.maintenance_task.cancel()
            try:
                await self.maintenance_task
            except asyncio.CancelledError:
                pass
        logging.info("Scheduled tasks stopped")
    
    async def maintenance_loop(self):
        """Maintenance tasks loop"""
        while self.tasks_running:
            try:
                # Run maintenance every 24 hours
                await asyncio.sleep(24 * 60 * 60)  # 24 hours
                
                if not self.tasks_running:
                    break
                
                await self.perform_maintenance()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in maintenance loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def perform_maintenance(self):
        """Perform maintenance tasks"""
        try:
            logging.info("Starting maintenance tasks...")
            
            # Clean up old database data
            db_manager.cleanup_old_data(days=30)
            
            # Clean up old broadcasted signals
            if hasattr(auto_scanner, 'cleanup_broadcasted_signals'):
                await auto_scanner.cleanup_broadcasted_signals()
            
            # Log maintenance completion
            logging.info("Maintenance tasks completed")
            
        except Exception as e:
            logging.error(f"Error performing maintenance: {e}")

# Global instances
auto_scanner = AutoScanner()
scheduled_tasks = ScheduledTasks()
