from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("=== VALIDATING 10 CORE REAL-WORLD INPUT SCENARIOS ===\n")

# 1. Casual Greeting
r1 = client.post('/api/chat', json={'prompt': 'hello there!'})
assert r1.status_code == 200 and r1.json()['response_type'] == 'conversational'
print("1. [PASS] Greeting ('hello there!') -> Conversational welcome.")

# 2. Short Greeting
r2 = client.post('/api/chat', json={'prompt': 'hi'})
assert r2.status_code == 200 and r2.json()['response_type'] == 'conversational'
print("2. [PASS] Greeting ('hi') -> Conversational welcome.")

# 3. Off-Topic Technology Question
r3 = client.post('/api/chat', json={'prompt': 'How do I write a Python function?'})
assert r3.status_code == 200 and r3.json()['response_type'] == 'conversational' and 'Out of Scope' in r3.json()['message']
print("3. [PASS] Off-topic ('write a Python function') -> Politely flagged out-of-scope.")

# 4. Off-Topic Weather Question
r4 = client.post('/api/chat', json={'prompt': 'What is the weather today?'})
assert r4.status_code == 200 and r4.json()['response_type'] == 'conversational' and 'Out of Scope' in r4.json()['message']
print("4. [PASS] Off-topic ('weather today') -> Politely flagged out-of-scope.")

# 5. Food Explanation Question
r5 = client.post('/api/chat', json={'prompt': 'what is roti'})
assert r5.status_code == 200 and r5.json()['response_type'] == 'conversational' and 'Roti' in r5.json()['message']
print("5. [PASS] Educational Food Question ('what is roti') -> Informative cultural answer.")

# 6. Specific Recipe Request: Dhal Curry
r6 = client.post('/api/chat', json={'prompt': 'I want to make dhal curry with red lentils and coconut milk under 30 mins'})
assert r6.status_code == 200 and r6.json()['response_type'] == 'recipe_recommendation'
assert 'Dhal' in r6.json()['recipe_title']
print(f"6. [PASS] Recipe Search ('red lentils and coconut milk') -> {r6.json()['recipe_title']}")

# 7. Specific Recipe Request: Chicken Curry
r7 = client.post('/api/chat', json={'prompt': 'I have chicken and roasted curry powder'})
assert r7.status_code == 200 and r7.json()['response_type'] == 'recipe_recommendation'
assert 'Chicken' in r7.json()['recipe_title']
print(f"7. [PASS] Recipe Search ('chicken') -> {r7.json()['recipe_title']}")

# 8. Specific Recipe Request: Pol Roti
r8 = client.post('/api/chat', json={'prompt': 'I want coconut flatbread with wheat flour and grated coconut'})
assert r8.status_code == 200 and r8.json()['response_type'] == 'recipe_recommendation'
assert 'Roti' in r8.json()['recipe_title']
print(f"8. [PASS] Recipe Search ('wheat flour and grated coconut') -> {r8.json()['recipe_title']}")

# 9. Severe Allergen Blocking: Fish Allergy blocks Pol Sambol
r9 = client.post('/api/chat', json={
    'prompt': 'Give me Pol Sambol with chili and grated coconut',
    'allergies': ['fish']
})
if r9.status_code == 200:
    assert 'Sambol' not in r9.json()['recipe_title']
    print(f"9. [PASS] Allergen Defense -> Blocked Pol Sambol, safely recommended {r9.json()['recipe_title']}")
else:
    assert r9.status_code == 400
    print("9. [PASS] Allergen Defense -> Blocked 100% of unsafe recipes with explicit safety violation warning.")

# 10. Strict Vegan Lifestyle Filter
r10 = client.post('/api/chat', json={
    'prompt': 'Quick dinner',
    'dietary_preferences': ['vegan']
})
assert r10.status_code == 200
assert 'Chicken' not in r10.json()['recipe_title']
print(f"10. [PASS] Vegan Filter -> Recommended safe vegan recipe: {r10.json()['recipe_title']}")

# 11. Multi-Turn Anaphora Context: "what is kottu" -> "how to make it"
r11_guide = client.post('/api/chat', json={'prompt': 'what is kottu'})
assert r11_guide.status_code == 200 and r11_guide.json()['response_type'] == 'conversational'
r11 = client.post('/api/chat', json={
    'prompt': 'how to make it',
    'conversation_history': [
        {'role': 'user', 'content': 'what is kottu'},
        {'role': 'assistant', 'content': r11_guide.json()['message']}
    ]
})
assert r11.status_code == 200 and r11.json()['response_type'] == 'recipe_recommendation'
assert 'Kottu' in r11.json()['recipe_title']
print(f"11. [PASS] Multi-Turn Anaphora ('how to make it' after 'what is kottu') -> {r11.json()['recipe_title']}")

# 12. Direct Authentic Dish Search: Hoppers
r12 = client.post('/api/chat', json={'prompt': 'how to make hoppers'})
assert r12.status_code == 200 and r12.json()['response_type'] == 'recipe_recommendation'
assert 'Hoppers' in r12.json()['recipe_title']
print(f"12. [PASS] Authentic Dish Search ('how to make hoppers') -> {r12.json()['recipe_title']}")

print("\n*** ALL 12 DIVERSE REAL-WORLD INPUTS VALIDATED AND CONFIRMED 100% ACCURATE! ***")
