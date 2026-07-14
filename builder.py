#!/usr/bin/env python3
"""
builder.py - Meta-Orchestrator for "Pure Pull" E-Commerce Engine

This script uses a swarm of AI agents to generate the entire system codebase.
Run it once; it produces a fully functional monorepo with tests and CI/CD.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
import yaml

# ======================================================
# 1. CONFIGURATION
# ======================================================
REPO_ROOT = Path.cwd() / "pure-pull-ecommerce"
os.makedirs(REPO_ROOT, exist_ok=True)

# Environment variables (set them before running)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.2)

# ======================================================
# 2. TOOL DEFINITIONS (for agents to write files)
# ======================================================
def write_file(path: str, content: str) -> str:
    """Write content to a file inside the repo root."""
    full_path = REPO_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    return f"✅ Written {path}"

def read_blueprint() -> str:
    """Reads the system blueprint from the prompt (embedded)."""
    return """
    System: Multi-tenant SaaS that generates e-commerce stores with 'Pure Pull' marketing.
    Tech: Next.js 15, tRPC, PostgreSQL, CrewAI, LangGraph, DigitalOcean.
    Modules: Architect Swarm (research/ideation), Builder Swarm (infra), Marketing Swarm (compliant ads).
    Compliance: Zero-tolerance for urgency/scarcity/push tactics.
    """

write_tool = Tool(
    name="write_file",
    func=write_file,
    description="Writes a file to the repository. Input: 'path/to/file' and content separated by newline."
)

read_tool = Tool(
    name="read_blueprint",
    func=read_blueprint,
    description="Returns the system blueprint."
)

# ======================================================
# 3. AGENT DEFINITIONS
# ======================================================
architect_writer = Agent(
    role="Architect‑Writer",
    goal="Generate the core platform code: Next.js frontend, tRPC API, PostgreSQL schema, onboarding flows.",
    backstory="You are a senior full‑stack engineer. You produce production‑ready TypeScript and Python code.",
    tools=[write_tool, read_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)

builder_writer = Agent(
    role="Builder‑Writer",
    goal="Generate the store provisioning logic: dynamic store generator, subdomain deployment, Dockerfiles.",
    backstory="You are a DevOps expert and backend engineer. You write code that spins up isolated stores.",
    tools=[write_tool, read_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)

marketing_writer = Agent(
    role="Marketing‑Writer",
    goal="Implement the Marketing Swarm: copywriter, compliance gatekeeper (LangGraph), media pipelines.",
    backstory="You are an AI engineer specialised in agentic workflows and content generation.",
    tools=[write_tool, read_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)

devops_writer = Agent(
    role="DevOps‑Writer",
    goal="Generate CI/CD pipelines (GitHub Actions), Terraform scripts, and deployment automation.",
    backstory="You are a cloud architect. You write infrastructure‑as‑code and test harnesses.",
    tools=[write_tool, read_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)

# ======================================================
# 4. TASK DEFINITIONS
# ======================================================
task_architect = Task(
    description="""
    Using the blueprint, generate the entire backend and frontend core:
    1. PostgreSQL schema (models.py with SQLAlchemy or Prisma schema).
    2. Next.js 15 app with tRPC routers for tenants, users, subscriptions.
    3. Onboarding flow: Interviewer, Researcher, Scribe agents (CrewAI).
    4. Write all files under /backend and /frontend.
    5. Include migration scripts.
    Output: List of all file paths written.
    """,
    agent=architect_writer,
    expected_output="A list of generated files and their purposes."
)

task_builder = Task(
    description="""
    Generate the store provisioning system:
    1. Store generator that builds a Next.js e‑commerce site from templates.
    2. Deployment script (deploy_store.py) that calls DigitalOcean API.
    3. Shopping cart logic and Stripe integration.
    4. Write all under /scripts/ and /backend/services/.
    Output: List of generated files.
    """,
    agent=builder_writer,
    expected_output="List of files for store creation and deployment."
)

task_marketing = Task(
    description="""
    Implement the Marketing Swarm:
    1. Copywriter agent (CrewAI) that generates ad copy.
    2. Compliance agent (LangGraph) with zero‑tolerance rules (pure pull).
    3. Media generation pipeline (text, image, video) using DALL‑E/Runway.
    4. Funnel alignment (landing page generator).
    5. Write all under /backend/app/agents/marketing_swarm/.
    Include the compliance state machine code exactly as described.
    Output: List of files.
    """,
    agent=marketing_writer,
    expected_output="Complete marketing swarm with compliance."
)

task_devops = Task(
    description="""
    Generate DevOps automation:
    1. GitHub Actions CI: test, lint, build.
    2. GitHub Actions CD: deploy to Vercel (frontend) and DigitalOcean (backend).
    3. Dockerfiles for frontend and backend.
    4. Terraform scripts for DigitalOcean resources (droplet, DB, Spaces).
    5. Write all under /.github/, /infra/, and Dockerfiles.
    Output: List of generated files.
    """,
    agent=devops_writer,
    expected_output="CI/CD and infrastructure code."
)

# ======================================================
# 5. CREW EXECUTION
# ======================================================
crew = Crew(
    agents=[architect_writer, builder_writer, marketing_writer, devops_writer],
    tasks=[task_architect, task_builder, task_marketing, task_devops],
    process=Process.sequential,  # runs one after another to avoid conflicts
    verbose=True
)

print("🚀 Starting code generation...")
result = crew.kickoff()
print("✅ Generation complete. Results:")
print(result)

# ======================================================
# 6. POST‑PROCESSING: LOCK & TEST
# ======================================================
print("\n🔒 Locking dependencies...")
# Write lock files (Poetry, npm)
subprocess.run(["poetry", "lock"], cwd=REPO_ROOT / "backend", check=False)
subprocess.run(["npm", "install", "--package-lock-only"], cwd=REPO_ROOT / "frontend", check=False)

print("\n🧪 Running tests...")
# Run backend tests
subprocess.run(["poetry", "run", "pytest"], cwd=REPO_ROOT / "backend", check=False)
# Run frontend tests
subprocess.run(["npm", "test"], cwd=REPO_ROOT / "frontend", check=False)

# ======================================================
# 7. GIT INIT & COMMIT (optional)
# ======================================================
if input("\n🚀 Push to GitHub? (y/n): ").lower() == "y":
    repo_url = input("Enter GitHub repo URL (e.g., git@github.com:user/repo.git): ")
    subprocess.run(["git", "init"], cwd=REPO_ROOT)
    subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=REPO_ROOT)
    subprocess.run(["git", "add", "."], cwd=REPO_ROOT)
    subprocess.run(["git", "commit", "-m", "Initial commit from builder.py"], cwd=REPO_ROOT)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=REPO_ROOT)
    print("✅ Pushed to GitHub!")
else:
    print("📁 Repository ready at", REPO_ROOT)
