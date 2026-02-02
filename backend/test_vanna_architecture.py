"""
Test script for the new Vanna-based architecture
Demonstrates streaming, caching, and performance improvements
"""

import asyncio
import aiohttp
import json
import time


async def test_streaming_query():
    """Test the streaming endpoint"""
    print("\n" + "="*50)
    print("TEST 1: Streaming Query")
    print("="*50 + "\n")
    
    url = "http://localhost:8000/api/query/stream"
    question = "Show me all students"
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"question": question},
            headers={"Accept": "text/event-stream"}
        ) as response:
            print(f"Status: {response.status}\n")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                
                if line.startswith('event: '):
                    event_type = line[7:]
                    print(f"📡 Event: {event_type}")
                
                elif line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    if isinstance(data, dict):
                        if 'stage' in data:
                            print(f"   ⏳ {data['message']}")
                        elif 'token' in data:
                            print(f"   🔤 SQL Token: {data['token']}", end='', flush=True)
                        elif 'sql' in data:
                            print(f"\n   ✅ SQL: {data['sql'][:50]}...")
                        elif 'results' in data:
                            print(f"   📊 Results: {data['results']['row_count']} rows")
                            print(f"   ⏱️  Time: {data['execution_time']:.2f}s")
                            print(f"   💾 Cached: {data['cached']}")
    
    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.2f}s\n")


async def test_cache_performance():
    """Test cache hit performance"""
    print("\n" + "="*50)
    print("TEST 2: Cache Performance")
    print("="*50 + "\n")
    
    url = "http://localhost:8000/api/query"
    question = "Show me all students enrolled in courses"
    
    # First request (cache miss)
    print("🔄 First request (cache miss)...")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"question": question}) as response:
            data = await response.json()
            elapsed = time.time() - start
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Cached: {data['cached']}")
            print(f"   Rows: {data['results']['row_count']}")
    
    # Wait a bit
    await asyncio.sleep(0.5)
    
    # Second request (cache hit)
    print("\n⚡ Second request (cache hit)...")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"question": question}) as response:
            data = await response.json()
            elapsed = time.time() - start
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Cached: {data['cached']}")
            print(f"   Speedup: {(data['execution_time'] / elapsed):.1f}x faster!")


async def test_cache_stats():
    """Test cache statistics endpoint"""
    print("\n" + "="*50)
    print("TEST 3: Cache Statistics")
    print("="*50 + "\n")
    
    url = "http://localhost:8000/api/cache/stats"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            stats = await response.json()
            
            print(f"📊 Cache Statistics:")
            print(f"   Size: {stats['size']}/{stats['max_size']}")
            print(f"   Hits: {stats['hits']}")
            print(f"   Misses: {stats['misses']}")
            print(f"   Hit Rate: {stats['hit_rate']}")
            print(f"   Time Saved: {stats['time_saved_seconds']}s")


async def test_concurrent_requests():
    """Test concurrent request handling"""
    print("\n" + "="*50)
    print("TEST 4: Concurrent Requests")
    print("="*50 + "\n")
    
    url = "http://localhost:8000/api/query"
    questions = [
        "Show me all students",
        "List all courses",
        "Show enrollments",
        "List instructors",
        "Show departments"
    ]
    
    print(f"🔄 Sending {len(questions)} concurrent requests...\n")
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(url, json={"question": q})
            for q in questions
        ]
        
        responses = await asyncio.gather(*tasks)
        results = [await r.json() for r in responses]
    
    elapsed = time.time() - start
    
    print(f"✅ All requests completed in {elapsed:.2f}s")
    print(f"   Average: {elapsed/len(questions):.2f}s per request")
    print(f"   Requests/second: {len(questions)/elapsed:.1f}")
    
    cached_count = sum(1 for r in results if r.get('cached', False))
    print(f"   Cached: {cached_count}/{len(questions)}")


async def main():
    """Run all tests"""
    print("\n🚀 Testing Vanna-based Architecture")
    print("="*50)
    
    try:
        # Test 1: Streaming
        await test_streaming_query()
        
        # Test 2: Cache performance
        await test_cache_performance()
        
        # Test 3: Cache stats
        await test_cache_stats()
        
        # Test 4: Concurrent requests
        await test_concurrent_requests()
        
        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
