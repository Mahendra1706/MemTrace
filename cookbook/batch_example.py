"""
run_llm.py — Example usage of MemTrace library.

Shows both modes:
  1. Batch mode  → pass a conversation list
  2. Live mode   → interactive terminal chat

Requires: export GROQ_API_KEY='gsk_...'
Get a free key at: https://console.groq.com/keys
"""

import os
from memtrace import MemTrace

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("❌  GROQ_API_KEY not set.")
    exit(1)

# ── Choose a mode ─────────────────────────────────────────────────────────────

MODE = "batch"   # change to "chat" for live terminal mode

# ── Batch mode ────────────────────────────────────────────────────────────────

if MODE == "batch":
    mt = MemTrace(
        api_key=api_key,
        model="llama-3.3-70b-versatile", 
        stm_capacity=2,                    
    )

    mt.run([
        "I am parking in spot B-14 today.",
        "My lunch order number is #1234.",
        "Today's temp Wi-Fi password is guest99.",  
        "What is my lunch order number?",            
        "Where did I park today?",                   
    ])

# ── Live chat mode ────────────────────────────────────────────────────────────

elif MODE == "chat":
    mt = MemTrace(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        stm_capacity=10,  
    )

    mt.chat()   
