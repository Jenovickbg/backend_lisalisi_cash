#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour l'endpoint USSD
Utilisation: python test_ussd.py
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_ussd_menu_principal():
    """Test du menu principal (text vide)"""
    print("\n=== Test 1: Menu principal (text='') ===")
    payload = {
        "sessionId": "test-session-123",
        "phoneNumber": "+237123456789",
        "text": ""
    }
    
    response = requests.post(f"{BASE_URL}/ussd", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_ussd_option_1():
    """Test de l'option 1 (consulter solde)"""
    print("\n=== Test 2: Option 1 (text='1') ===")
    payload = {
        "sessionId": "test-session-123",
        "phoneNumber": "+237123456789",
        "text": "1"
    }
    
    response = requests.post(f"{BASE_URL}/ussd", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_ussd_option_invalide():
    """Test d'une option invalide"""
    print("\n=== Test 3: Option invalide (text='99') ===")
    payload = {
        "sessionId": "test-session-123",
        "phoneNumber": "+237123456789",
        "text": "99"
    }
    
    response = requests.post(f"{BASE_URL}/ussd", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

if __name__ == "__main__":
    print("=" * 50)
    print("Tests de l'endpoint USSD")
    print("=" * 50)
    
    try:
        # Vérifier que le serveur est accessible
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print(f"ERREUR: Le serveur ne repond pas correctement (status: {health.status_code})")
            exit(1)
        
        print("OK: Serveur accessible")
        
        # Exécuter les tests
        test_ussd_menu_principal()
        test_ussd_option_1()
        test_ussd_option_invalide()
        
        print("\n" + "=" * 50)
        print("Tous les tests termines!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("ERREUR: Impossible de se connecter au serveur.")
        print("Assurez-vous que le serveur est demarre avec: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"ERREUR: {e}")
