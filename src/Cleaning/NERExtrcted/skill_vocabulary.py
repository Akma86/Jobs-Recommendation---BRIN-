# -*- coding: utf-8 -*-
"""
Skill vocabulary built from Dataset_CLO_OBE_SI_TelUJakarta.xlsx (Skill Catalogue sheet).
Each canonical skill (from RPS) is mapped to a list of real-world aliases/synonyms
that commonly appear in job postings (LinkedIn/Glassdoor style English text).

This is a STARTER dictionary (rule-based, no training needed). It's meant to be
expanded over time as you see more job posting vocabulary.
"""

SKILL_VOCAB = {
    # Accounting Information Systems
    "AIS Design": {"domain": "Accounting Information Systems", "aliases": ["AIS design", "accounting information system design"]},
    "Financial Reporting": {"domain": "Accounting Information Systems", "aliases": ["financial reporting", "financial statements"]},
    "Internal Control": {"domain": "Accounting Information Systems", "aliases": ["internal control", "internal controls", "SOX compliance"]},
    "Transaction Processing": {"domain": "Accounting Information Systems", "aliases": ["transaction processing", "TPS"]},

    # Business Process Modeling
    "BPMN": {"domain": "Business Process Modeling", "aliases": ["bpmn", "business process model and notation"]},
    "Process Analysis": {"domain": "Business Process Modeling", "aliases": ["process analysis", "business process analysis"]},
    "Process Mapping": {"domain": "Business Process Modeling", "aliases": ["process mapping", "process flow mapping"]},
    "Workflow Design": {"domain": "Business Process Modeling", "aliases": ["workflow design", "workflow automation"]},

    # Business Process Reengineering
    "BPR Methodology": {"domain": "Business Process Reengineering", "aliases": ["bpr", "business process reengineering", "business process redesign"]},
    "Change Management": {"domain": "Business Process Reengineering", "aliases": ["change management"]},
    "Performance Measurement": {"domain": "Business Process Reengineering", "aliases": ["performance measurement", "kpi tracking", "performance metrics"]},
    "Process Optimization": {"domain": "Business Process Reengineering", "aliases": ["process optimization", "process improvement", "continuous improvement", "lean six sigma"]},

    # Computer Networking
    "Network Security": {"domain": "Computer Networking", "aliases": ["network security", "firewall", "vpn", "network security engineer"]},
    "Network Topology": {"domain": "Computer Networking", "aliases": ["network topology", "network architecture", "network design"]},
    "TCP/IP Protocol": {"domain": "Computer Networking", "aliases": ["tcp/ip", "tcp ip", "networking protocols", "dns", "dhcp"]},

    # Data Mining
    "Association Rule": {"domain": "Data Mining", "aliases": ["association rule mining", "market basket analysis"]},
    "Classification": {"domain": "Data Mining", "aliases": ["classification model", "classification algorithm"]},
    "Clustering": {"domain": "Data Mining", "aliases": ["clustering", "k-means", "unsupervised learning"]},
    "Predictive Modeling": {"domain": "Data Mining", "aliases": ["predictive modeling", "predictive analytics", "forecasting model"]},

    # Data Warehouse & BI
    "Dashboard & Reporting": {"domain": "Data Warehouse & BI", "aliases": ["dashboard", "reporting", "power bi", "tableau", "looker", "data visualization"]},
    "Data Modeling": {"domain": "Data Warehouse & BI", "aliases": ["data modeling", "dimensional modeling", "star schema"]},
    "ETL Process": {"domain": "Data Warehouse & BI", "aliases": ["etl", "elt", "data pipeline", "data integration", "airflow", "dbt"]},
    "OLAP": {"domain": "Data Warehouse & BI", "aliases": ["olap", "online analytical processing", "cube analysis"]},

    # Database Systems
    "Database Design": {"domain": "Database Systems", "aliases": ["database design", "schema design", "erd", "entity relationship"]},
    "Normalization": {"domain": "Database Systems", "aliases": ["normalization", "database normalization"]},
    "Query Optimization": {"domain": "Database Systems", "aliases": ["query optimization", "query tuning", "index optimization"]},
    "SQL": {"domain": "Database Systems", "aliases": ["sql", "mysql", "postgresql", "postgres", "sql server", "oracle db", "t-sql", "pl/sql"]},

    # Enterprise Architecture
    "Architecture Modeling": {"domain": "Enterprise Architecture", "aliases": ["architecture modeling", "solution architecture"]},
    "EA Framework": {"domain": "Enterprise Architecture", "aliases": ["enterprise architecture framework", "zachman framework"]},
    "TOGAF": {"domain": "Enterprise Architecture", "aliases": ["togaf"]},

    # Enterprise Integration
    "API Design": {"domain": "Enterprise Integration", "aliases": ["api design", "rest api", "restful api", "graphql", "api development"]},
    "Web Services": {"domain": "Enterprise Integration", "aliases": ["web services", "soap", "microservices"]},

    # Enterprise Systems
    "ERP": {"domain": "Enterprise Systems", "aliases": ["erp", "enterprise resource planning"]},
    "SAP/Oracle": {"domain": "Enterprise Systems", "aliases": ["sap", "oracle erp", "sap fico", "sap mm", "netsuite"]},

    # IT Governance
    "COBIT": {"domain": "IT Governance", "aliases": ["cobit"]},
    "IT Performance Audit": {"domain": "IT Governance", "aliases": ["it audit", "it performance audit", "compliance audit"]},
    "ITIL": {"domain": "IT Governance", "aliases": ["itil", "it service management", "itsm"]},

    # IT Project Management
    "Agile/Scrum": {"domain": "IT Project Management", "aliases": ["agile", "scrum", "kanban", "scrum master", "sprint planning"]},
    "PMBOK": {"domain": "IT Project Management", "aliases": ["pmbok", "pmp", "project management professional"]},
    "Risk Management": {"domain": "IT Project Management", "aliases": ["risk management", "risk assessment", "risk mitigation"]},
    "WBS & Scheduling": {"domain": "IT Project Management", "aliases": ["work breakdown structure", "wbs", "project scheduling", "gantt chart", "ms project", "jira"]},

    # Information Security
    "Cryptography": {"domain": "Information Security", "aliases": ["cryptography", "encryption", "pki"]},
    "Cybersecurity": {"domain": "Information Security", "aliases": ["cybersecurity", "cyber security", "infosec", "information security"]},
    "Risk Assessment": {"domain": "Information Security", "aliases": ["security risk assessment", "vulnerability assessment", "penetration testing", "pentest"]},
    "Security Audit": {"domain": "Information Security", "aliases": ["security audit", "soc 2", "iso 27001"]},

    # Information Systems Fundamentals
    "Digital Transformation": {"domain": "Information Systems Fundamentals", "aliases": ["digital transformation"]},
    "IS Governance": {"domain": "Information Systems Fundamentals", "aliases": ["information systems governance", "it governance"]},
    "IS Strategy": {"domain": "Information Systems Fundamentals", "aliases": ["is strategy", "it strategy", "digital strategy"]},
    "IT Infrastructure": {"domain": "Information Systems Fundamentals", "aliases": ["it infrastructure", "infrastructure management"]},

    # Intelligent Systems
    "AI Application": {"domain": "Intelligent Systems", "aliases": ["artificial intelligence", "ai application", "ai engineer", "generative ai", "llm"]},
    "Decision Tree/KNN/SVM": {"domain": "Intelligent Systems", "aliases": ["decision tree", "knn", "svm", "random forest", "xgboost"]},
    "Machine Learning": {"domain": "Intelligent Systems", "aliases": ["machine learning", "ml", "scikit-learn", "sklearn", "deep learning", "tensorflow", "pytorch"]},
    "Neural Network": {"domain": "Intelligent Systems", "aliases": ["neural network", "cnn", "rnn", "lstm", "transformer model", "nlp"]},

    # Interaction Design
    "UI Prototyping": {"domain": "Interaction Design", "aliases": ["ui prototyping", "prototyping", "figma", "adobe xd", "sketch"]},
    "UX Research": {"domain": "Interaction Design", "aliases": ["ux research", "user research"]},
    "Usability Testing": {"domain": "Interaction Design", "aliases": ["usability testing", "a/b testing", "user testing"]},
    "Wireframing": {"domain": "Interaction Design", "aliases": ["wireframing", "wireframe"]},

    # Object-Oriented Programming
    "Class Design": {"domain": "Object-Oriented Programming", "aliases": ["class design", "object modeling"]},
    "Design Pattern": {"domain": "Object-Oriented Programming", "aliases": ["design pattern", "design patterns", "solid principles"]},
    "Java/Python": {"domain": "Object-Oriented Programming", "aliases": ["java", "python", "c++", "c#", "kotlin"]},
    "OOP Principles": {"domain": "Object-Oriented Programming", "aliases": ["object-oriented programming", "oop", "object oriented"]},

    # Operating Systems
    "File System": {"domain": "Operating Systems", "aliases": ["file system", "filesystem"]},
    "Linux Administration": {"domain": "Operating Systems", "aliases": ["linux", "linux administration", "unix", "shell scripting", "bash"]},
    "Memory Management": {"domain": "Operating Systems", "aliases": ["memory management"]},
    "Process Management": {"domain": "Operating Systems", "aliases": ["process management", "process scheduling"]},

    # Programming & Algorithm
    "Algorithm Design": {"domain": "Programming & Algorithm", "aliases": ["algorithm design", "algorithms", "algorithm development"]},
    "Data Structure": {"domain": "Programming & Algorithm", "aliases": ["data structures", "data structure"]},
    "Pseudocode": {"domain": "Programming & Algorithm", "aliases": ["pseudocode"]},

    # Software Engineering
    "CI/CD": {"domain": "Software Engineering", "aliases": ["ci/cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"]},
    "SDLC": {"domain": "Software Engineering", "aliases": ["sdlc", "software development life cycle"]},
    "Software Testing": {"domain": "Software Engineering", "aliases": ["software testing", "unit testing", "qa testing", "test automation", "selenium"]},
    "Version Control": {"domain": "Software Engineering", "aliases": ["git", "github", "gitlab", "version control", "bitbucket"]},

    # Systems Analysis & Design
    "Requirements Engineering": {"domain": "Systems Analysis & Design", "aliases": ["requirements engineering", "requirements gathering", "business requirements", "brd"]},
    "System Architecture": {"domain": "Systems Analysis & Design", "aliases": ["system architecture", "software architecture", "solution design"]},
    "UML Modeling": {"domain": "Systems Analysis & Design", "aliases": ["uml", "unified modeling language", "sequence diagram", "class diagram"]},
    "Use Case Design": {"domain": "Systems Analysis & Design", "aliases": ["use case", "use case design", "user story"]},

    # Web Development
    "Backend Development": {"domain": "Web Development", "aliases": ["backend development", "backend developer", "node.js", "django", "flask", "spring boot", "laravel", "express.js"]},
    "Web Framework": {"domain": "Web Development", "aliases": ["react", "angular", "vue", "vue.js", "next.js", "web framework", "frontend framework"]},
}

# Flatten into alias -> canonical skill lookup, sorted by length desc (longest match first)
def build_alias_index():
    alias_to_canonical = {}
    for canonical, info in SKILL_VOCAB.items():
        for alias in info["aliases"] + [canonical]:
            alias_to_canonical[alias.lower().strip()] = canonical
    return alias_to_canonical

if __name__ == "__main__":
    idx = build_alias_index()
    print(f"Total canonical skills: {len(SKILL_VOCAB)}")
    print(f"Total alias surface forms: {len(idx)}")
