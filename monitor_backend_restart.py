#!/usr/bin/env python3
"""
Monitor backend restart progress - test login every 30 seconds
"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def quick_login_test():
    """Quick test to see if login is working"""
    try:
        # Test with a simple login that should fail gracefully if working
        login_data = {
            'email_or_phone': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 401:
            # 401 = "Invalid credentials" means login endpoint is working!
            return "WORKING", "Login endpoint functional (401 Invalid credentials)"
        elif response.status_code == 500:
            error = response.json().get('error', '')
            if 'status' in error:
                return "RESTARTING", "Still has status column error"
            elif 'salt' in error:
                return "PARTIAL", "Status fixed but password issue"
            else:
                return "ERROR", f"Different 500 error: {error[:50]}"
        elif response.status_code == 400:
            return "WORKING", "Login endpoint functional (400 Bad request)"
        else:
            return "UNKNOWN", f"Unexpected status: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "TIMEOUT", "Backend not responding"
    except Exception as e:
        return "ERROR", f"Connection error: {str(e)[:50]}"

def monitor_restart():
    """Monitor backend restart progress"""
    print("🔄 Monitoring Backend Restart Progress")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    print()
    
    attempt = 1
    last_status = None
    
    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            status, message = quick_login_test()
            
            # Only print if status changed
            if status != last_status:
                if status == "WORKING":
                    print(f"🎉 {timestamp} - LOGIN IS WORKING! {message}")
                    print("\n✅ Backend restart complete!")
                    print("🧪 Now run: python simple_admin_setup.py")
                    break
                elif status == "PARTIAL":
                    print(f"⚡ {timestamp} - PROGRESS! {message}")
                elif status == "RESTARTING":
                    print(f"⏳ {timestamp} - Still restarting... {message}")
                else:
                    print(f"⚠️ {timestamp} - {status}: {message}")
                
                last_status = status
            else:
                # Same status, just show a dot
                print(".", end="", flush=True)
            
            time.sleep(15)  # Check every 15 seconds
            attempt += 1
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Monitoring stopped after {attempt} attempts")
            print("💡 Run 'python simple_admin_setup.py' to test manually")
            break
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
            break

if __name__ == "__main__":
    monitor_restart()