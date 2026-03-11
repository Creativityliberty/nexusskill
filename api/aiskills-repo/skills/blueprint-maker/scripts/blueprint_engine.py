"""
Blueprint Engine
=================
Core engine for generating structured blueprints across any domain.

Usage:
    from blueprint_engine import BlueprintEngine
    engine = BlueprintEngine(domain="product")
    blueprint = engine.generate(goal="Build a fitness app", constraints="6 months, $50k budget")
    engine.export(blueprint, "blueprint.md", format="markdown")
"""

import json
import yaml
import os
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Domain Templates Registry
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "business": ["startup", "business", "revenue", "market", "saas", "company", "profit", "customer", "sales",
                  "restaurant", "shop", "store", "franchise", "b2b", "b2c", "commerce", "venture"],
    "product": ["app", "feature", "ux", "ui", "mvp", "requirements", "mobile", "web", "platform", "software",
                "tool", "dashboard", "extension", "plugin"],
    "research": ["study", "hypothesis", "experiment", "data", "analysis", "paper", "research", "scientific",
                 "survey", "methodology", "variables"],
    "education": ["course", "curriculum", "learning", "teach", "training", "bootcamp", "workshop", "lesson",
                  "student", "education", "tutorial", "module"],
    "engineering": ["system", "api", "architecture", "infra", "backend", "frontend", "microservice", "database",
                    "server", "deploy", "ci/cd", "cloud", "docker", "kubernetes"],
}

# ---------------------------------------------------------------------------
# Blueprint Section Definitions
# ---------------------------------------------------------------------------

BLUEPRINT_SECTIONS = {
    "executive_summary": {
        "title": "📋 Executive Summary",
        "prompt": "Write a concise executive summary (1 paragraph) for: {goal}. Context: {constraints}",
        "required": True
    },
    "objectives": {
        "title": "🎯 Objectives",
        "prompt": "List the primary and 2-3 secondary objectives for: {goal}",
        "required": True
    },
    "analysis": {
        "title": "📊 Analysis",
        "prompt": "Provide a domain-specific analysis for: {goal}. Domain: {domain}. Include market/context analysis.",
        "required": True
    },
    "architecture": {
        "title": "🏗️ Architecture / Structure",
        "prompt": "Design the core architecture or structure for: {goal}. Break into major components or phases.",
        "required": True
    },
    "timeline": {
        "title": "📅 Timeline & Milestones",
        "prompt": "Create a phased timeline with milestones for: {goal}. Constraints: {constraints}",
        "required": True
    },
    "resources": {
        "title": "💰 Resources & Budget",
        "prompt": "Estimate the resources needed (people, tools, budget) for: {goal}. Constraints: {constraints}",
        "required": True
    },
    "risks": {
        "title": "⚠️ Risks & Mitigations",
        "prompt": "Identify top 5 risks and mitigation strategies for: {goal}",
        "required": True
    },
    "metrics": {
        "title": "📈 Success Metrics",
        "prompt": "Define KPIs and success metrics for: {goal}",
        "required": True
    },
    "appendix": {
        "title": "📎 Appendix",
        "prompt": "List useful references, tools, and resources for: {goal}",
        "required": False
    },
}

# Domain-specific extra sections
DOMAIN_EXTRAS = {
    "business": {
        "business_model": {
            "title": "💼 Business Model Canvas",
            "prompt": "Create a Business Model Canvas (Value Prop, Channels, Revenue Streams, etc.) for: {goal}",
            "required": True
        },
        "competitive_analysis": {
            "title": "🏆 Competitive Analysis",
            "prompt": "Analyze 3-5 competitors for: {goal}. Strengths, weaknesses, differentiation.",
            "required": True
        }
    },
    "product": {
        "user_personas": {
            "title": "👤 User Personas",
            "prompt": "Define 2-3 user personas for: {goal}. Include demographics, pain points, goals.",
            "required": True
        },
        "feature_matrix": {
            "title": "📱 Feature Matrix",
            "prompt": "Create a prioritized feature matrix (Must-Have / Should-Have / Nice-to-Have) for: {goal}",
            "required": True
        },
        "tech_stack": {
            "title": "⚙️ Tech Stack",
            "prompt": "Recommend a tech stack for: {goal}. Frontend, backend, database, deployment.",
            "required": True
        }
    },
    "research": {
        "literature_review": {
            "title": "📚 Literature Review Plan",
            "prompt": "Outline a literature review strategy for: {goal}. Key areas, search terms, databases.",
            "required": True
        },
        "methodology": {
            "title": "🔬 Methodology",
            "prompt": "Design the research methodology for: {goal}. Type (qualitative/quantitative), sampling, instruments.",
            "required": True
        },
        "data_plan": {
            "title": "📊 Data Collection & Analysis Plan",
            "prompt": "Plan data collection and analysis for: {goal}. Tools, techniques, validation.",
            "required": True
        }
    },
    "education": {
        "learning_outcomes": {
            "title": "🎓 Learning Outcomes",
            "prompt": "Define clear learning outcomes using Bloom's Taxonomy for: {goal}",
            "required": True
        },
        "curriculum_map": {
            "title": "📚 Curriculum Map",
            "prompt": "Create a week-by-week or module-by-module curriculum map for: {goal}",
            "required": True
        },
        "assessment_strategy": {
            "title": "✏️ Assessment Strategy",
            "prompt": "Design formative and summative assessments for: {goal}",
            "required": True
        }
    },
    "engineering": {
        "system_design": {
            "title": "🖥️ System Design",
            "prompt": "Create a high-level system design with components and data flow for: {goal}",
            "required": True
        },
        "api_spec": {
            "title": "🔌 API Specification",
            "prompt": "Define the core API endpoints (REST/GraphQL) for: {goal}",
            "required": True
        },
        "deployment": {
            "title": "🚀 Deployment Strategy",
            "prompt": "Plan the deployment pipeline (CI/CD, staging, production) for: {goal}",
            "required": True
        }
    }
}


# ---------------------------------------------------------------------------
# Blueprint Engine
# ---------------------------------------------------------------------------

class BlueprintEngine:
    """
    Generates structured blueprints for any domain.
    
    Example:
        engine = BlueprintEngine()
        domain = engine.detect_domain("I want to build a fitness app")
        blueprint = engine.generate(
            domain=domain,
            goal="Build a fitness tracking mobile app",
            constraints="6 months, 3 developers, $50k"
        )
        engine.export(blueprint, "fitness_app_blueprint.md")
    """

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"

    def detect_domain(self, user_input):
        """Auto-detect the project domain from user input."""
        text = user_input.lower()
        scores = {}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[domain] = score
        
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "custom"
        return best

    def get_sections(self, domain):
        """Get all sections for a domain (shared + domain-specific)."""
        sections = dict(BLUEPRINT_SECTIONS)
        
        # Insert domain-specific extras after "analysis"
        if domain in DOMAIN_EXTRAS:
            extras = DOMAIN_EXTRAS[domain]
            # Build ordered result
            ordered = {}
            for key, sec in sections.items():
                ordered[key] = sec
                if key == "analysis":
                    ordered.update(extras)
            sections = ordered
        
        return sections

    def generate(self, domain="custom", goal="", constraints="", audience="",
                 project_name=None, call_llm=None):
        """
        Generate a complete blueprint.
        
        Args:
            domain: Detected or specified domain
            goal: User's primary goal
            constraints: Budget, timeline, resource limits
            audience: Target audience
            project_name: Optional project name
            call_llm: Optional LLM function(prompt) -> response
        """
        if not project_name:
            project_name = goal[:50].strip()
        
        sections = self.get_sections(domain)
        blueprint = {
            "meta": {
                "project_name": project_name,
                "domain": domain,
                "goal": goal,
                "constraints": constraints,
                "audience": audience,
                "generated_at": datetime.now().isoformat(),
                "generator": "blueprint-maker v1.0"
            },
            "sections": {}
        }
        
        ctx = {
            "goal": goal,
            "constraints": constraints or "No specific constraints",
            "audience": audience or "General",
            "domain": domain
        }
        
        for key, sec in sections.items():
            prompt = sec["prompt"].format(**ctx)
            
            if call_llm:
                content = call_llm(prompt)
            else:
                # Generate placeholder content for offline use
                content = self._generate_placeholder(key, sec, ctx)
            
            blueprint["sections"][key] = {
                "title": sec["title"],
                "content": content,
                "required": sec["required"]
            }
        
        return blueprint

    def _generate_placeholder(self, key, section, ctx):
        """Generate intelligent placeholder content when no LLM is available."""
        placeholders = {
            "executive_summary": f"This blueprint outlines the plan for: **{ctx['goal']}**. "
                                 f"Domain: {ctx['domain'].title()}. Constraints: {ctx['constraints']}.",
            "objectives": f"- **Primary**: {ctx['goal']}\n- Secondary: Establish market presence\n"
                          f"- Secondary: Build sustainable growth model\n- Secondary: Achieve measurable impact",
            "analysis": f"### {ctx['domain'].title()} Analysis\n\n"
                        f"A thorough analysis of the landscape for: {ctx['goal']}.\n\n"
                        f"**Key factors to consider:**\n"
                        f"- Market size and growth trajectory\n"
                        f"- Target audience: {ctx['audience']}\n"
                        f"- Competitive landscape\n"
                        f"- Regulatory considerations",
            "architecture": f"### Core Components\n\n"
                            f"```\n"
                            f"┌──────────────┐    ┌──────────────┐    ┌──────────────┐\n"
                            f"│   Phase 1    │───▶│   Phase 2    │───▶│   Phase 3    │\n"
                            f"│  Foundation  │    │    Build     │    │   Launch     │\n"
                            f"└──────────────┘    └──────────────┘    └──────────────┘\n"
                            f"```",
            "timeline": f"| Phase | Duration | Milestone |\n|---|---|---|\n"
                        f"| Phase 1: Foundation | Weeks 1-4 | Setup & planning complete |\n"
                        f"| Phase 2: Build | Weeks 5-12 | Core deliverable ready |\n"
                        f"| Phase 3: Launch | Weeks 13-16 | Go to market |",
            "resources": f"### Team\n- 1 Project Lead\n- 2-3 Domain Specialists\n\n"
                         f"### Budget\n- Estimated: Based on constraints ({ctx['constraints']})\n\n"
                         f"### Tools\n- Project management, communication, domain-specific tools",
            "risks": f"| Risk | Probability | Impact | Mitigation |\n|---|---|---|---|\n"
                     f"| Scope creep | High | High | Define clear boundaries early |\n"
                     f"| Resource constraints | Medium | High | Prioritize MVP features |\n"
                     f"| Market timing | Medium | Medium | Rapid iteration cycles |\n"
                     f"| Technical debt | Low | High | Code reviews, testing |\n"
                     f"| Team turnover | Low | Medium | Documentation, knowledge sharing |",
            "metrics": f"### KPIs\n"
                       f"- Completion rate: % of milestones hit on time\n"
                       f"- Quality: Stakeholder satisfaction score\n"
                       f"- Efficiency: Budget utilization\n"
                       f"- Impact: Domain-specific metric for {ctx['goal']}",
            "appendix": f"### References\n- [To be populated with domain-specific resources]\n\n"
                        f"### Tools & Links\n- Project management: Notion / Linear / Jira\n"
                        f"- Communication: Slack / Discord",
        }
        
        # Domain-specific placeholders
        domain_placeholders = {
            "business_model": "### Business Model Canvas\n\n"
                             "| Block | Description |\n|---|---|\n"
                             "| Value Proposition | Core value delivered |\n"
                             "| Customer Segments | Target audience |\n"
                             "| Channels | How value reaches customers |\n"
                             "| Revenue Streams | How money is made |\n"
                             "| Key Resources | Critical assets |\n"
                             "| Key Activities | Core operations |\n"
                             "| Key Partners | Strategic partnerships |\n"
                             "| Cost Structure | Major cost drivers |",
            "competitive_analysis": "### Competitive Landscape\n\n"
                                   "| Competitor | Strengths | Weaknesses | Our Advantage |\n|---|---|---|---|\n"
                                   "| Competitor A | Established brand | Slow innovation | Agility |\n"
                                   "| Competitor B | Large user base | Poor UX | Better design |\n"
                                   "| Competitor C | Low cost | Limited features | Quality |",
            "user_personas": "### Persona 1: Primary User\n"
                            "- **Age**: 25-35\n- **Pain Points**: [specific frustrations]\n"
                            "- **Goals**: [what they want to achieve]\n\n"
                            "### Persona 2: Secondary User\n"
                            "- **Age**: 35-50\n- **Pain Points**: [specific frustrations]\n"
                            "- **Goals**: [what they want to achieve]",
            "feature_matrix": "| Feature | Priority | Effort | Phase |\n|---|---|---|---|\n"
                             "| Core feature 1 | Must-Have | M | Phase 1 |\n"
                             "| Core feature 2 | Must-Have | L | Phase 1 |\n"
                             "| Enhancement 1 | Should-Have | M | Phase 2 |\n"
                             "| Nice feature 1 | Nice-to-Have | S | Phase 3 |",
            "tech_stack": "### Recommended Stack\n\n"
                         "| Layer | Technology | Rationale |\n|---|---|---|\n"
                         "| Frontend | React / Next.js | Modern, large ecosystem |\n"
                         "| Backend | Python / FastAPI | Rapid development |\n"
                         "| Database | PostgreSQL | Reliable, scalable |\n"
                         "| Deployment | Docker + Cloud | Portable, scalable |",
            "literature_review": "### Search Strategy\n"
                                "- **Databases**: Google Scholar, PubMed, IEEE\n"
                                "- **Keywords**: [domain-specific terms]\n"
                                "- **Inclusion criteria**: [define]\n"
                                "- **Time range**: Last 5 years",
            "methodology": "### Research Design\n"
                          "- **Type**: [Qualitative / Quantitative / Mixed]\n"
                          "- **Sample size**: [estimate]\n"
                          "- **Instruments**: [surveys, interviews, etc.]\n"
                          "- **Analysis method**: [statistical / thematic]",
            "data_plan": "### Data Collection\n"
                        "- **Sources**: [primary / secondary]\n"
                        "- **Tools**: [survey tools, instruments]\n"
                        "- **Timeline**: [collection period]\n\n"
                        "### Analysis\n"
                        "- **Method**: [statistical / qualitative coding]\n"
                        "- **Software**: [SPSS, NVivo, Python]",
            "learning_outcomes": "### By completion, learners will:\n"
                                "1. **Remember**: Key concepts and terminology\n"
                                "2. **Understand**: Core principles and relationships\n"
                                "3. **Apply**: Techniques to real-world problems\n"
                                "4. **Analyze**: Complex scenarios critically\n"
                                "5. **Create**: Original solutions and artifacts",
            "curriculum_map": "| Week/Module | Topic | Activities | Assessment |\n|---|---|---|---|\n"
                             "| Module 1 | Introduction & Foundations | Lectures, readings | Quiz |\n"
                             "| Module 2 | Core Concepts | Workshops, labs | Project milestone |\n"
                             "| Module 3 | Advanced Topics | Case studies | Presentation |\n"
                             "| Module 4 | Capstone | Independent project | Final submission |",
            "assessment_strategy": "### Formative (70%)\n"
                                  "- Weekly check-ins\n- Peer feedback\n- Practice exercises\n\n"
                                  "### Summative (30%)\n"
                                  "- Final project\n- Comprehensive exam\n- Portfolio submission",
            "system_design": "### High-Level Architecture\n\n"
                            "```\n"
                            "┌─────────┐    ┌──────────┐    ┌──────────┐\n"
                            "│ Client  │───▶│ API GW   │───▶│ Services │\n"
                            "└─────────┘    └──────────┘    └──────────┘\n"
                            "                                    │\n"
                            "                               ┌────┴────┐\n"
                            "                               │   DB    │\n"
                            "                               └─────────┘\n"
                            "```",
            "api_spec": "### Core Endpoints\n\n"
                       "| Method | Path | Description |\n|---|---|---|\n"
                       "| GET | /api/v1/items | List all items |\n"
                       "| POST | /api/v1/items | Create item |\n"
                       "| GET | /api/v1/items/:id | Get item by ID |\n"
                       "| PUT | /api/v1/items/:id | Update item |\n"
                       "| DELETE | /api/v1/items/:id | Delete item |",
            "deployment": "### Pipeline\n\n"
                         "```\nCode → Lint → Test → Build → Stage → Approve → Production\n```\n\n"
                         "### Environments\n"
                         "- **Dev**: Local Docker Compose\n"
                         "- **Staging**: Cloud preview deployment\n"
                         "- **Production**: Cloud with auto-scaling",
        }
        
        return placeholders.get(key, f"*[Content for {section['title']}]*")

    def export(self, blueprint, filepath, fmt="markdown"):
        """Export blueprint to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if fmt == "markdown":
            content = self._to_markdown(blueprint)
        elif fmt == "yaml":
            content = yaml.dump(blueprint, default_flow_style=False, allow_unicode=True)
        elif fmt == "json":
            content = json.dumps(blueprint, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unknown format: {fmt}")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 Blueprint exported to {path} ({fmt})")
        return content

    def _to_markdown(self, blueprint):
        """Convert blueprint dict to markdown."""
        meta = blueprint["meta"]
        lines = [
            f"# Blueprint: {meta['project_name']}",
            "",
            f"> **Domain**: {meta['domain'].title()} | "
            f"**Generated**: {meta['generated_at'][:10]} | "
            f"**Engine**: {meta['generator']}",
            "",
            "---",
            ""
        ]
        
        for key, sec in blueprint["sections"].items():
            lines.append(f"## {sec['title']}")
            lines.append("")
            lines.append(sec["content"])
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)

    def to_dag_tasks(self, blueprint):
        """
        Convert blueprint phases into DAG-compatible tasks.
        Returns a list of task dicts for dag-taskview.
        """
        tasks = []
        prev_id = None
        
        # Extract phases from architecture section
        arch = blueprint["sections"].get("architecture", {})
        timeline = blueprint["sections"].get("timeline", {})
        
        # Create tasks from sections
        phase_sections = ["analysis", "architecture", "timeline", "resources"]
        for i, key in enumerate(blueprint["sections"]):
            sec = blueprint["sections"][key]
            task_id = key.replace(" ", "_")
            
            task = {
                "id": task_id,
                "name": sec["title"].split(" ", 1)[-1] if " " in sec["title"] else sec["title"],
                "status": "pending",
                "deps": [prev_id] if prev_id else []
            }
            tasks.append(task)
            prev_id = task_id
        
        return tasks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Blueprint Maker — Universal Project Architect")
    parser.add_argument("--domain", default="auto", help="Domain: business/product/research/education/engineering/custom/auto")
    parser.add_argument("--goal", required=True, help="Project goal (one sentence)")
    parser.add_argument("--constraints", default="", help="Budget, timeline, resource constraints")
    parser.add_argument("--audience", default="", help="Target audience")
    parser.add_argument("--output", default="blueprint.md", help="Output file path")
    parser.add_argument("--format", default="markdown", choices=["markdown", "yaml", "json"], help="Output format")
    
    args = parser.parse_args()
    
    engine = BlueprintEngine()
    
    # Auto-detect domain
    domain = args.domain
    if domain == "auto":
        domain = engine.detect_domain(args.goal)
        print(f"🔍 Auto-detected domain: {domain}")
    
    # Generate
    print(f"🏗️  Generating {domain} blueprint...")
    blueprint = engine.generate(
        domain=domain,
        goal=args.goal,
        constraints=args.constraints,
        audience=args.audience
    )
    
    # Export
    engine.export(blueprint, args.output, fmt=args.format)
    
    # Show summary
    print(f"\n✅ Blueprint generated!")
    print(f"   Domain: {domain}")
    print(f"   Sections: {len(blueprint['sections'])}")
    print(f"   Output: {args.output}")


if __name__ == "__main__":
    main()
