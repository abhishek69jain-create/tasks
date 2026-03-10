#!/usr/bin/env python3
"""
Admin script to create team member accounts
Usage: python create_user.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    print("=== QuickAssign - Create Team Member Account ===\n")
    
    name = input("Enter full name: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    # Check if user exists
    existing = await db.users.find_one({"email": email})
    if existing:
        print(f"\n❌ Error: User with email {email} already exists!")
        return
    
    # Ask for role
    print("\nSelect role:")
    print("1. Team Member (default)")
    print("2. Admin")
    role_choice = input("Enter choice (1 or 2): ").strip() or "1"
    
    role = "admin" if role_choice == "2" else "team_member"
    
    # Create user
    hashed_password = pwd_context.hash(password)
    user_doc = {
        "_id": ObjectId(),
        "email": email,
        "password": hashed_password,
        "name": name,
        "role": role,
        "createdAt": datetime.utcnow()
    }
    
    await db.users.insert_one(user_doc)
    
    print(f"\n✅ Success! User created:")
    print(f"   Name: {name}")
    print(f"   Email: {email}")
    print(f"   Role: {role}")
    print(f"\n📧 Share these credentials with the team member:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n⚠️  Ask them to change their password after first login!")

async def list_users():
    print("=== Current Team Members ===\n")
    users = await db.users.find().to_list(1000)
    
    if not users:
        print("No users found.")
        return
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['name']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Created: {user['createdAt'].strftime('%Y-%m-%d')}")
        print()

async def main():
    while True:
        print("\n" + "="*50)
        print("QuickAssign - User Management")
        print("="*50)
        print("1. Create new team member")
        print("2. List all team members")
        print("3. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            await create_user()
        elif choice == "2":
            await list_users()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        client.close()
