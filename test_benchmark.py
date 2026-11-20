#!/usr/bin/env python3
"""
Official Assessment & Evaluation Script
Project 8: Culinary Operations, Allergen & Recipe Manual Assistant
Tests Q1 through Q5 against the live RAG pipeline.
"""
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.rag.pipeline import CulinaryRAGPipeline

def run_tests():
    print("=" * 80)
    print("LE GRAND BISTRO - RAG SYSTEM COMPLIANCE & ACCURACY VERIFICATION")
    print("=" * 80)

    pipe = CulinaryRAGPipeline()
    pipe.initialize_and_index()

    tests = [
        {
            "id": "Q1",
            "type": "DOCUMENT_RETRIEVAL",
            "query": "What exact quantities, in grams, of dark couverture chocolate and heavy cream are required for a standard 20-portion batch of Signature Truffle Ganache?",
            "check": lambda res: (
                not res["is_external"]
                and "850" in res["answer"]
                and "620" in res["answer"]
                and any(c.get("page_num") == 10 for c in res["citations"])
            ),
            "expected": "850 grams dark chocolate, 620 grams heavy cream, Page 10 citation"
        },
        {
            "id": "Q2",
            "type": "DOCUMENT_RETRIEVAL",
            "query": "According to the Allergen Matrix, which dishes on the Autumn Tasting Menu contain tree nuts or sesame?",
            "check": lambda res: (
                not res["is_external"]
                and "Hazelnut Duck Terrine" in res["answer"]
                and "Lamb Rack" in res["answer"]
                and "Tahini Veloute" in res["answer"]
                and any(c.get("page_num") == 25 for c in res["citations"])
            ),
            "expected": "Tree Nuts: Terrine & Lamb Rack; Sesame: Tahini Veloute; Page 25 citation"
        },
        {
            "id": "Q3",
            "type": "EXTERNAL_SEARCH",
            "query": "At what time does the Eiffel Tower in Paris close to visitors during the winter season?",
            "check": lambda res: (
                res["is_external"]
                and ("11:00 PM" in res["answer"] or "23:00" in res["answer"])
                and len(res["citations"]) > 0
            ),
            "expected": "11:00 PM (23:00) closing, verified external URLs"
        },
        {
            "id": "Q4",
            "type": "DOCUMENT_RETRIEVAL",
            "query": "What is the mandatory minimum internal cooking temperature, in degrees Celsius, and the required holding time for sous-vide duck breast, as specified in the Food Safety section?",
            "check": lambda res: (
                not res["is_external"]
                and "57.5" in res["answer"]
                and "110" in res["answer"]
                and "Salmonella" in res["answer"]
                and any(c.get("page_num") == 40 for c in res["citations"])
            ),
            "expected": "57.5°C, 110 minutes, log-7 Salmonella pasteurization, Page 40 citation"
        },
        {
            "id": "Q5",
            "type": "EXTERNAL_SEARCH",
            "query": "What is the current Michelin-star rating of Noma in Copenhagen?",
            "check": lambda res: (
                res["is_external"]
                and "3 Michelin Stars" in res["answer"]
                and len(res["citations"]) > 0
            ),
            "expected": "3 Michelin Stars (awarded Sept 2021 by Michelin Guide Nordic Countries)"
        }
    ]

    all_passed = True
    for t in tests:
        print(f"\nEvaluating [{t['id']}]: {t['query']}")
        res = pipe.query(t["query"])
        passed = t["check"](res)
        status = "PASSED" if passed else "FAILED"
        print(f"Result: [{status}]")
        print(f"Source Type: {res['source_type']} (Is External: {res['is_external']})")
        print(f"Citations: {res['citations']}")
        print(f"Latency: {res['retrieval_stats'].get('latency_ms')} ms")
        if not passed:
            all_passed = False
            print(f"Expected: {t['expected']}")
            print(f"Answer: {res['answer']}")

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL ASSESSMENT QUESTIONS PASSED WITH 100% ACCURACY & SAFETY COMPLIANCE!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
