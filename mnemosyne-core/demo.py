import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def run_sdd_demo():
    print("--- Project Mnemosyne SDD Architecture Demo ---")
    
    # 1. Ingest Memories
    memories = [
        {
            "content": "今天在西湖边喝了龙井茶，微风拂面，感觉非常宁静。",
            "metadata": {"location": "Hangzhou, China", "category": "lifestyle", "sentiment": 0.9}
        },
        {
            "content": "正在阅读关于量子计算的文章，其中的纠缠态概念非常深奥。",
            "metadata": {"category": "study", "topic": "quantum_physics"}
        }
    ]

    print("\n[Phase 1] Ingesting memories...")
    for mem in memories:
        res = requests.post(f"{BASE_URL}/ingest", json=mem)
        if res.status_code == 200:
            print(f"✅ Saved: {mem['content'][:20]}...")

    # 2. Semantic Search
    print("\n[Phase 2] Testing Semantic Search...")
    query_data = {"query": "我最近在看什么科学类的内容？", "n_results": 1}
    res = requests.post(f"{BASE_URL}/query", json=query_data)
    if res.status_code == 200:
        match = res.json()[0]
        print(f"🔍 Found: {match['content']} (Dist: {match['distance']:.4f})")

    # 3. RAG Chat
    print("\n[Phase 3] Testing RAG Chat...")
    chat_data = {"message": "总结一下我今天的心情。"}
    res = requests.post(f"{BASE_URL}/chat", json=chat_data)
    if res.status_code == 200:
        print(f"🤖 Mnemosyne Response: {res.json()['answer']}")
    else:
        print("❌ Chat failed. Make sure server is running.")

    # 4. List and Delete
    print("\n[Phase 4] Testing List and Delete...")
    res = requests.get(f"{BASE_URL}/memories", params={"limit": 5})
    if res.status_code == 200:
        mems = res.json()
        print(f"📋 Found {len(mems)} memories in storage.")
        if mems:
            mid = mems[0]['id']
            print(f"🗑️ Deleting memory: {mid}")
            del_res = requests.delete(f"{BASE_URL}/memories/{mid}")
            print(f"✅ Delete status: {del_res.json()['status']}")


if __name__ == "__main__":
    run_sdd_demo()
