#!/usr/bin/env python3
"""
Day 3 Example: Direct Tool Calling
==================================

This shows how agents connect directly to tools.
Works fine for simple cases, but doesn't scale.
"""

print("=" * 60)
print("DIRECT TOOL CALLING EXAMPLE")
print("=" * 60)

# Simulating direct tool libraries
class GitLibrary:
    """Direct Git library"""
    def get_branches(self):
        return ["main", "dev", "feature-x"]
    
    def create_branch(self, name):
        return f"Created branch: {name}"

class AWSLibrary:
    """Direct AWS library"""
    def list_instances(self):
        return ["i-12345", "i-67890"]
    
    def start_instance(self, id):
        return f"Started instance: {id}"

class SlackLibrary:
    """Direct Slack library"""
    def send_message(self, channel, text):
        return f"Sent to #{channel}: {text}"


# Agent using direct libraries
class DevOpsAgent:
    """Agent with direct tool connections"""
    
    def __init__(self):
        print("  [Agent] Initializing direct connections...")
        # Each agent creates its own connections
        self.git = GitLibrary()
        self.aws = AWSLibrary()
        self.slack = SlackLibrary()
    
    def deploy(self):
        print("\n  [Agent] Deploying...")
        
        # Direct calls to each library
        branches = self.git.get_branches()
        print(f"    Git branches: {branches}")
        
        instances = self.aws.list_instances()
        print(f"    AWS instances: {instances}")
        
        self.slack.send_message("deployments", "Deployment started")
        print(f"    Slack notification sent")
        
        return "Deployment complete!"


print("\n📋 PROS OF DIRECT CALLING:")
print("  ✅ Simple - no middleware")
print("  ✅ Fast - direct connection")
print("  ✅ Full control over everything")

print("\n📋 CONS OF DIRECT CALLING:")
print("  ❌ Each agent duplicates code")
print("  ❌ Need multiple libraries (git, aws, slack)")
print("  ❌ Different error formats for each tool")
print("  ❌ Hard to maintain")

print("\n" + "=" * 60)
print("RUNNING THE AGENT:")
print("=" * 60)

agent = DevOpsAgent()
result = agent.deploy()
print(f"\n  Result: {result}")

print("\n" + "=" * 60)
print("THE PROBLEM:")
print("=" * 60)
print("""
If you have 3 agents (DevOps, Support, Analyst),
and each needs Git, AWS, and Slack:

  DevOps Agent  → Git, AWS, Slack (3 connections)
  Support Agent → Git, AWS, Slack (3 connections)  
  Analyst Agent → Git, AWS, Slack (3 connections)

  Total: 9 custom integrations!
  
Each integration needs:
  - Authentication code
  - Error handling
  - Testing
  - Documentation
  - Maintenance

This doesn't scale!
""")

print("=" * 60)
